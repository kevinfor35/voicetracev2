"""
配置管理
"""
import os
from pathlib import Path

# 项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

# 目录配置
MODELS_DIR = BASE_DIR / "models"
UPLOADS_DIR = BASE_DIR / "uploads"
OUTPUTS_DIR = BASE_DIR / "outputs"

# 确保目录存在
MODELS_DIR.mkdir(parents=True, exist_ok=True)
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

# 支持的音视频格式
SUPPORTED_FORMATS = {
    # 音频格式
    ".mp3", ".wav", ".flac", ".ogg", ".m4a", ".wma", ".aac",
    # 视频格式
    ".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv", ".webm"
}

# Whisper 模型配置
WHISPER_MODELS = {
    "tiny": {
        "size": "39 MB",
        "languages": ["auto", "zh", "en", "ja", "ko", "fr", "de", "es", "ru", "it", "pt"]
    },
    "base": {
        "size": "74 MB",
        "languages": ["auto", "zh", "en", "ja", "ko", "fr", "de", "es", "ru", "it", "pt"]
    },
    "small": {
        "size": "244 MB",
        "languages": ["auto", "zh", "en", "ja", "ko", "fr", "de", "es", "ru", "it", "pt"]
    },
    "medium": {
        "size": "769 MB",
        "languages": ["auto", "zh", "en", "ja", "ko", "fr", "de", "es", "ru", "it", "pt"]
    },
    "large": {
        "size": "1550 MB",
        "languages": ["auto", "zh", "en", "ja", "ko", "fr", "de", "es", "ru", "it", "pt"]
    }
}

# 语言代码映射
LANGUAGE_NAMES = {
    "auto": "自动检测",
    "zh": "中文",
    "en": "英文",
    "ja": "日语",
    "ko": "韩语",
    "fr": "法语",
    "de": "德语",
    "es": "西班牙语",
    "ru": "俄语",
    "it": "意大利语",
    "pt": "葡萄牙语"
}

# 文件大小限制（字节）
MAX_FILE_SIZE = 500 * 1024 * 1024  # 500MB
