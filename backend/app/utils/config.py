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
# 
# 模型命名规则：
# - 基础模型（多语言）: tiny, base, small, medium, large
# - 英文专用模型（.en）: tiny.en, base.en, small.en, medium.en
# - Large 版本: large-v2, large-v3
# - Distil 蒸馏模型（仅英语）: distil-large-v2, distil-large-v3
# - Turbo 模型（多语言+快速）: large-v3-turbo
#
# 多语言支持说明：
# - 不带 .en 后缀的模型支持多语言（99种语言）
# - .en 后缀的模型仅支持英文，体积更小，速度更快
# - large-v2/large-v3 对多语言支持最好，包括韩语等小语种
# - distil 模型是蒸馏版本，仅支持英语！体积约为原模型的一半，速度快约6倍
# - large-v3-turbo 是 OpenAI 发布的新模型，结合了 distil 的速度和多语言支持
#
# 重要：模型文件格式
# - faster-whisper 使用 CTranslate2 格式（.bin 文件）
# - 不支持 HuggingFace 原生 .safetensors 格式！
# - 所有模型目录结构必须是：
#   models/<模型名>/
#       ├── model.bin        ← CTranslate2 格式的权重文件（不是 .safetensors！）
#       ├── config.json      ← 模型配置
#       ├── tokenizer.json   ← 分词器配置
#       └── preprocessor_config.json  ← 音频预处理配置（部分模型需要）

WHISPER_MODELS = {
    # === 基础多语言模型 ===
    "tiny": {
        "size": "39 MB",
        "languages": ["auto", "zh", "en", "ja", "ko", "fr", "de", "es", "ru", "it", "pt"],
        "description": "基础小模型，速度最快，语言检测准确",
        "multilingual": True
    },
    "base": {
        "size": "74 MB",
        "languages": ["auto", "zh", "en", "ja", "ko", "fr", "de", "es", "ru", "it", "pt"],
        "description": "基础模型，平衡速度与精度（默认推荐）",
        "multilingual": True
    },
    "small": {
        "size": "244 MB",
        "languages": ["auto", "zh", "en", "ja", "ko", "fr", "de", "es", "ru", "it", "pt"],
        "description": "小型模型，较好的精度",
        "multilingual": True
    },
    "medium": {
        "size": "769 MB",
        "languages": ["auto", "zh", "en", "ja", "ko", "fr", "de", "es", "ru", "it", "pt"],
        "description": "中型模型，良好的多语言支持",
        "multilingual": True
    },
    # === 英文专用模型 ===
    "tiny.en": {
        "size": "39 MB",
        "languages": ["en"],
        "description": "仅英文，速度最快",
        "multilingual": False
    },
    "base.en": {
        "size": "74 MB",
        "languages": ["en"],
        "description": "仅英文，平衡速度与精度",
        "multilingual": False
    },
    "small.en": {
        "size": "244 MB",
        "languages": ["en"],
        "description": "仅英文，较好的精度",
        "multilingual": False
    },
    "medium.en": {
        "size": "769 MB",
        "languages": ["en"],
        "description": "仅英文，高精度",
        "multilingual": False
    },
    # === Large 版本（最佳多语言支持）===
    "large-v2": {
        "size": "1.5 GB",
        "languages": ["auto", "zh", "en", "ja", "ko", "fr", "de", "es", "ru", "it", "pt", "ar", "hi"],
        "description": "Large v2，最佳多语言识别",
        "multilingual": True
    },
    "large-v3": {
        "size": "1.6 GB",
        "languages": ["auto", "zh", "en", "ja", "ko", "fr", "de", "es", "ru", "it", "pt", "ar", "hi"],
        "description": "Large v3，最新版本，最佳性能",
        "multilingual": True
    },
    # === Turbo 模型（多语言+快速，推荐）===
    "large-v3-turbo": {
        "size": "1.6 GB",
        "languages": ["auto", "zh", "en", "ja", "ko", "fr", "de", "es", "ru", "it", "pt", "ar", "hi"],
        "description": "Turbo 版本，速度约快3-4倍，多语言支持（推荐）",
        "multilingual": True
    },
    # === Distil 蒸馏模型（仅支持英语！）===
    "distil-large-v2": {
        "size": "769 MB",
        "languages": ["en"],
        "description": "仅英语！蒸馏 Large v2，速度快6倍",
        "multilingual": False
    },
    "distil-large-v3": {
        "size": "800 MB",
        "languages": ["en"],
        "description": "仅英语！蒸馏 Large v3，速度快6倍",
        "multilingual": False
    },
    "distil-large-v3.5": {
        "size": "850 MB",
        "languages": ["en"],
        "description": "仅英语！蒸馏 Large v3.5，最新优化版本",
        "multilingual": False
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
    "pt": "葡萄牙语",
    "ar": "阿拉伯语",
    "hi": "印地语"
}

# 文件大小限制（字节）
MAX_FILE_SIZE = 500 * 1024 * 1024  # 500MB
