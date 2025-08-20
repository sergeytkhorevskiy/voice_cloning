from typing import Dict, Any, List

RETRO_STYLES: Dict[str, Dict[str, Any]] = {
    "vintage_radio": {
        "description": "Старе радіо 1930-40х років",
        "cutoff_freq": 2000,  # Hz
        "filter_order": 6,
        "sample_rate": 16000,
        "am_modulation": True,
        "carrier_freq": 1000,  # Hz
        "noise_level": 0.02,
        "compression_threshold": 0.3,
        "compression_ratio": 2.5
    },
    
    "vinyl_record": {
        "description": "Вінілові платівки 1950-60х років",
        "cutoff_freq": 3500,  # Hz
        "filter_order": 4,
        "sample_rate": 22050,
        "crackle_enabled": True,
        "crackle_density": 1000,  # кількість crackle точок
        "crackle_intensity": 0.1,
        "warmth_boost": True,
        "warmth_freq_range": [800, 2000],  # Hz
        "warmth_gain": 0.3,
        "compression_threshold": 0.4,
        "compression_ratio": 3.0
    },
    
    "cassette_tape": {
        "description": "Касетні магнітофони 1970-80х років",
        "cutoff_freq": 3000,  # Hz
        "filter_order": 4,
        "sample_rate": 22050,
        "wow_freq": 0.5,  # Hz
        "flutter_freq": 5.0,  # Hz
        "wow_intensity": 0.001,
        "flutter_intensity": 0.0005,
        "hiss_level": 0.015,
        "compression_threshold": 0.35,
        "compression_ratio": 2.8
    },
    
    "telephone": {
        "description": "Старий телефон 1920-30х років",
        "cutoff_freq": 1500,  # Hz
        "filter_order": 8,
        "sample_rate": 8000,
        "bandpass": True,
        "bandpass_range": [300, 3400],  # Hz
        "noise_level": 0.025,
        "compression_threshold": 0.25,
        "compression_ratio": 2.0
    },
    
    "gramophone": {
        "description": "Грамофон 1900-1920х років",
        "cutoff_freq": 1800,  # Hz
        "filter_order": 6,
        "sample_rate": 11025,
        "mechanical_noise": True,
        "noise_level": 0.03,
        "distortion_level": 0.15,
        "compression_threshold": 0.2,
        "compression_ratio": 1.8
    },
    
    "enhanced_basic": {
        "description": "Покращений базовий ретро стиль",
        "cutoff_freq": 2500,  # Hz
        "filter_order": 4,
        "sample_rate": 22050,
        "high_pass_cutoff": 80,  # Hz
        "reverb_enabled": True,
        "reverb_delay": 0.1,  # seconds
        "reverb_decay": 0.3,
        "distortion_level": 0.1,
        "compression_threshold": 0.3,
        "compression_ratio": 2.0
    }
}

def get_style_config(style_name: str) -> Dict[str, Any]:
    return RETRO_STYLES.get(style_name, RETRO_STYLES["enhanced_basic"])

def print_available_styles() -> None:
    print("🎵 Доступні ретро стилі:")
    for style_name, config in RETRO_STYLES.items():
        print(f"   • {style_name}: {config['description']}")
    print()

def create_custom_style(name: str, description: str, **kwargs: Any) -> Dict[str, Any]:
    custom_style = {
        "description": description,
        "cutoff_freq": kwargs.get("cutoff_freq", 2500),
        "filter_order": kwargs.get("filter_order", 4),
        "sample_rate": kwargs.get("sample_rate", 22050),
        "compression_threshold": kwargs.get("compression_threshold", 0.3),
        "compression_ratio": kwargs.get("compression_ratio", 2.0),
        "noise_level": kwargs.get("noise_level", 0.01),
        "distortion_level": kwargs.get("distortion_level", 0.05)
    }
    
    for key, value in kwargs.items():
        if key not in custom_style:
            custom_style[key] = value
    
    return custom_style

def get_style_names() -> List[str]:
    return list(RETRO_STYLES.keys())

def get_style_descriptions() -> Dict[str, str]:
    return {name: config["description"] for name, config in RETRO_STYLES.items()}

_STYLE_CACHE: Dict[str, Dict[str, Any]] = {}

def get_cached_style_config(style_name: str) -> Dict[str, Any]:
    if style_name not in _STYLE_CACHE:
        _STYLE_CACHE[style_name] = get_style_config(style_name)
    return _STYLE_CACHE[style_name]

if __name__ == "__main__":
    print_available_styles()
    
    # Приклад створення кастомного стилю
    custom_style = create_custom_style(
        "my_retro",
        "Мій кастомний ретро стиль",
        cutoff_freq=2800,
        filter_order=5,
        sample_rate=24000,
        compression_threshold=0.35,
        compression_ratio=2.2,
        noise_level=0.015,
        distortion_level=0.08
    )
    
    print("🎛️ Приклад кастомного стилю:")
    for key, value in custom_style.items():
        print(f"   {key}: {value}")
    
    print(f"\n📊 Доступні стилі: {get_style_names()}")
    print(f"📝 Опис стилів: {get_style_descriptions()}")