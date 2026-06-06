"""
辅助函数
"""
import uuid
import os
from datetime import datetime
from pathlib import Path
from typing import Optional
import subprocess


def generate_task_id() -> str:
    """生成唯一的任务 ID"""
    return str(uuid.uuid4())


def generate_file_id() -> str:
    """生成唯一的文件 ID"""
    return str(uuid.uuid4())


def format_timestamp(seconds: float) -> str:
    """
    将秒数格式化为 SRT 时间戳格式
    格式: HH:MM:SS,mmm
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def get_audio_duration(file_path: str) -> Optional[float]:
    """
    获取音视频文件的时长（秒）
    使用 ffprobe 获取时长信息
    """
    try:
        # 尝试使用 ffprobe 获取时长
        result = subprocess.run(
            [
                "ffprobe",
                "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                file_path
            ],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            return float(result.stdout.strip())
    except Exception:
        pass

    # 如果 ffprobe 失败，返回 None
    return None


def format_file_size(size_bytes: int) -> str:
    """格式化文件大小显示"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"


def is_supported_format(filename: str) -> bool:
    """检查文件格式是否支持"""
    from backend.app.utils.config import SUPPORTED_FORMATS
    ext = Path(filename).suffix.lower()
    return ext in SUPPORTED_FORMATS


def generate_output_filename(model: str) -> str:
    """
    生成输出文件名
    格式: {model}_{YYYYMMDD_HHMMSS}.srt
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{model}_{timestamp}.srt"


def check_gpu_available() -> bool:
    """检查 GPU 是否可用"""
    try:
        import torch
        return torch.cuda.is_available()
    except ImportError:
        # 如果 torch 未安装，尝试检查 CUDA 环境
        try:
            result = subprocess.run(
                ["nvidia-smi"],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False


def cleanup_old_files(directory: Path, max_age_hours: int = 24):
    """
    清理旧文件
    删除超过指定小时数的文件
    """
    if not directory.exists():
        return

    now = datetime.now()
    for file_path in directory.iterdir():
        if file_path.is_file():
            file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
            age_hours = (now - file_time).total_seconds() / 3600
            if age_hours > max_age_hours:
                try:
                    file_path.unlink()
                except Exception:
                    pass
