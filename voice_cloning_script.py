from TTS.api import TTS
from pydub import AudioSegment
from retro_effects_config import RETRO_STYLES, get_style_config, print_available_styles
import numpy as _np
from scipy import signal as _signal
from typing import Tuple

def _segment_to_float32(seg: AudioSegment) -> Tuple[_np.ndarray, int]:
    sr = seg.frame_rate
    seg = seg.set_channels(1).set_sample_width(2)  # mono, int16
    x = _np.frombuffer(seg.raw_data, dtype=_np.int16).astype(_np.float32) / 32768.0
    return x, sr

def _float32_to_segment(x: _np.ndarray, sr: int) -> AudioSegment:
    x = _np.clip(x, -1.0, 1.0).astype(_np.float32)
    x16 = (x * 32767.0).astype(_np.int16).tobytes()
    return AudioSegment(data=x16, sample_width=2, frame_rate=sr, channels=1)

def _safe_bandpass(x: _np.ndarray, sr: int, lo_hz: float, hi_hz: float, order: int = 2) -> _np.ndarray:
    nyq = sr / 2.0
    lo = max(1.0, float(lo_hz)) / nyq
    hi = min(float(hi_hz), nyq - 100.0) / nyq
    
    if not (0 < lo < hi < 1):
        wn = min(float(hi_hz), nyq - 100.0) / nyq
        sos = _signal.butter(2, wn, btype="low", output="sos")
        return _signal.sosfiltfilt(sos, x).astype(_np.float32)
    
    sos = _signal.butter(order, [lo, hi], btype="band", output="sos")
    return _signal.sosfiltfilt(sos, x).astype(_np.float32)

def _safe_lowpass(x: _np.ndarray, sr: int, cutoff_hz: float, order: int = 2) -> _np.ndarray:
    nyq = sr / 2.0
    wn = min(float(cutoff_hz), nyq - 100.0) / nyq
    wn = max(wn, 50.0/nyq)  # keep > 0
    sos = _signal.butter(order, wn, btype="low", output="sos")
    return _signal.sosfiltfilt(sos, x).astype(_np.float32)

def _add_hiss(x: _np.ndarray, rms_db: float = -35.0, seed: int = 0) -> _np.ndarray:
    rng = _np.random.default_rng(int(seed))
    std = 10.0 ** (float(rms_db) / 20.0)
    return (x + rng.normal(0, std, size=x.shape).astype(_np.float32)).astype(_np.float32)

def _peak_normalize(x: _np.ndarray, target_db: float = -3.0) -> _np.ndarray:
    peak = float(_np.max(_np.abs(x))) + 1e-9
    gain = 10.0 ** (float(target_db) / 20.0)
    return (x / peak) * gain

_SAFE_STYLE_MAP = {
    "vintage_radio":  {"mode": "band", "lo": 200, "hi": 3800, "hiss_db": -35, "target_db": -3},
    "vinyl_record":   {"mode": "low",  "cut": 5000, "hiss_db": -34, "target_db": -3},
    "cassette_tape":  {"mode": "low",  "cut": 6000, "hiss_db": -32, "target_db": -3.5},
    "telephone":      {"mode": "band", "lo": 300, "hi": 3400, "hiss_db": -30, "target_db": -4},
    "gramophone":     {"mode": "band", "lo": 400, "hi": 3000, "hiss_db": -28, "target_db": -4},
    "enhanced_basic": {"mode": "low",  "cut": 4500, "hiss_db": -35, "target_db": -3},
}

def _apply_safe_style(x: _np.ndarray, sr: int, style_name: str) -> _np.ndarray:
    cfg = _SAFE_STYLE_MAP.get(style_name)
    if not cfg:
        return x
    if cfg["mode"] == "band":
        x = _safe_bandpass(x, sr, cfg["lo"], cfg["hi"], order=2)
    else:
        x = _safe_lowpass(x, sr, cfg["cut"], order=2)
    x = _add_hiss(x, rms_db=cfg["hiss_db"])
    x = _peak_normalize(x, cfg["target_db"])
    return x

def apply_retro_effects(audio_segment: AudioSegment) -> AudioSegment:
    x, sr = _segment_to_float32(audio_segment)
    x = _apply_safe_style(x, sr, "enhanced_basic")
    return _float32_to_segment(x, sr)

def apply_advanced_retro_effects(audio_segment: AudioSegment, style: str = "vintage_radio") -> AudioSegment:
    x, sr = _segment_to_float32(audio_segment)
    print(f"  Обробка {style}: {len(x)} семплів, {sr} Hz")
    print(f"  До обробки: max={_np.max(_np.abs(x)):.3f}")
    x = _apply_safe_style(x, sr, style)
    print(f"  Після обробки: max={_np.max(_np.abs(x)):.3f}")
    return _float32_to_segment(x, sr)

def process_audio_with_retro_effects(voice_file: str = "sample/voice_raw.wav") -> None:
    print("🎵 Застосовуємо ретро ефекти...")
    try:
        voice = AudioSegment.from_wav(voice_file)
        print(f"✅ Завантажено аудіо: {len(voice)} мс, {voice.frame_rate} Hz")
        print_available_styles()
        for style_name in RETRO_STYLES.keys():
            try:
                print(f"🎵 Створюємо {style_name} стиль...")
                retro = apply_advanced_retro_effects(voice, style_name)
                config = get_style_config(style_name)
                sample_rate = config.get("sample_rate", 22050)
                retro = retro.set_frame_rate(sample_rate)
                retro = retro.set_channels(1)  # Моно для аутентичності
                output_file = f"sample/optimized_retro_{style_name}.wav"
                retro.export(output_file, format="wav")
                print(f"   ✅ Збережено: {output_file}")
            except Exception as e:
                print(f"   ❌ Помилка створення {style_name}: {e}")
                continue
        
        try:
            print("\n🎵 Створюємо базовий покращений варіант...")
            retro_basic = apply_retro_effects(voice)
            retro_basic = retro_basic.set_frame_rate(22050)
            retro_basic = retro_basic.set_channels(1)
            retro_basic.export("sample/optimized_retro_enhanced.wav", format="wav")
            print("   ✅ Збережено: sample/optimized_retro_enhanced.wav")
        except Exception as e:
            print(f"   ❌ Помилка створення базового варіанту: {e}")
        
        print("\n✅ Оптимізована обробка завершена!")
        print("📝 Створені файли:")
        print("   - sample/optimized_retro_enhanced.wav (базовий покращений)")
        for style_name in RETRO_STYLES.keys():
            print(f"   - sample/optimized_retro_{style_name}.wav ({RETRO_STYLES[style_name]['description']})")
        
    except Exception as e:
        print(f"❌ Помилка: {e}")

if __name__ == "__main__":
    try:
        # Використовуємо your_tts
        print("🎤 Генеруємо голос з your_tts...")
        tts = TTS(model_name="tts_models/multilingual/multi-dataset/your_tts", progress_bar=False, gpu=False)
        
        text = """Will could see the tightness around Gareds mouth, the barely suppressed anger in his eyes under the thick 
        black hood of his cloak. Gared had spent forty years in the Nights Watch, man and boy, and he was not accustomed to 
        being made light of. Yet it was more than that. Under the wounded pride, Will could sense something else in the older man.
        You could taste it; a nervous tension that came perilous close to fear. Will shared his unease. He had been four years on 
        the Wall. The first time he had been sent beyond, all the old stories had come rushing back, and his bowels had turned to
        water. He had laughed about it afterward. He was a veteran of a hundred rangings by now, and the endless dark wilderness 
        that the southron called the haunted forest had no more terrors for him."""
        
        tts.tts_to_file(
            text=text,
            speaker_wav="sample/sample.wav",
            language="en",
            file_path="sample/voice_raw.wav"
        )
        print("✅ Голос згенеровано: sample/voice_raw.wav")
        
    except Exception as e:
        print(f"❌ Помилка з your_tts: {e}")
        print("⚠️ Використовуємо існуючий voice_raw.wav...")
    
    # Обробляємо з ретро ефектами
    process_audio_with_retro_effects()