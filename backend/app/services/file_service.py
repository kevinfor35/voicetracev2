"""
文件处理服务
"""
import os
import shutil
from pathlib import Path
from typing import Optional
from backend.app.utils.config import UPLOADS_DIR, MAX_FILE_SIZE
from backend.app.utils.helpers import (
    generate_file_id,
    get_audio_duration,
    is_supported_format
)


class FileService:
    """文件处理服务"""

    @staticmethod
    async def save_upload_file(file_content: bytes, filename: str) -> tuple[str, str, int]:
        """
        保存上传的文件

        Args:
            file_content: 文件内容（字节）
            filename: 原始文件名

        Returns:
            tuple: (file_id, file_path, file_size)

        Raises:
            ValueError: 文件格式不支持或文件过大
        """
        # 检查文件格式
        if not is_supported_format(filename):
            raise ValueError(f"不支持的文件格式: {filename}")

        # 检查文件大小
        file_size = len(file_content)
        if file_size > MAX_FILE_SIZE:
            raise ValueError(f"文件过大，最大支持 {MAX_FILE_SIZE // (1024*1024)} MB")

        # 生成文件 ID
        file_id = generate_file_id()

        # 构建保存路径
        file_ext = Path(filename).suffix
        save_filename = f"{file_id}{file_ext}"
        file_path = UPLOADS_DIR / save_filename

        # 保存文件
        with open(file_path, "wb") as f:
            f.write(file_content)

        return file_id, str(file_path), file_size

    @staticmethod
    async def get_file_duration(file_path: str) -> Optional[float]:
        """
        获取文件时长

        Args:
            file_path: 文件路径

        Returns:
            float: 时长（秒），如果无法获取则返回 None
        """
        return get_audio_duration(file_path)

    @staticmethod
    def delete_file(file_path: str):
        """
        删除文件

        Args:
            file_path: 文件路径
        """
        try:
            path = Path(file_path)
            if path.exists():
                path.unlink()
        except Exception:
            pass

    @staticmethod
    def file_exists(file_path: str) -> bool:
        """
        检查文件是否存在

        Args:
            file_path: 文件路径

        Returns:
            bool: 文件是否存在
        """
        return Path(file_path).exists()
