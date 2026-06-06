"""
字幕服务
"""
from pathlib import Path
from datetime import datetime
from typing import List, Optional
from backend.app.models.schemas import SubtitleSegment
from backend.app.utils.config import OUTPUTS_DIR
from backend.app.utils.helpers import format_timestamp, generate_output_filename


class SubtitleService:
    """字幕服务"""

    @staticmethod
    def generate_srt_content(segments: List[SubtitleSegment]) -> str:
        """
        生成 SRT 格式的字幕内容

        Args:
            segments: 字幕分段列表

        Returns:
            str: SRT 格式的字幕内容
        """
        srt_lines = []
        for segment in segments:
            # 序号
            srt_lines.append(str(segment.index))
            # 时间轴
            start_time = format_timestamp(segment.start)
            end_time = format_timestamp(segment.end)
            srt_lines.append(f"{start_time} --> {end_time}")
            # 字幕文本
            srt_lines.append(segment.text)
            # 空行分隔
            srt_lines.append("")

        return "\n".join(srt_lines)

    @staticmethod
    def save_srt_file(
        segments: List[SubtitleSegment],
        model: str,
        inference_time: Optional[float] = None
    ) -> tuple[str, str]:
        """
        保存 SRT 字幕文件

        Args:
            segments: 字幕分段列表
            model: 模型名称
            inference_time: 推理时间（秒），如果提供则加入文件名

        Returns:
            tuple: (文件路径, 文件名)
        """
        # 生成文件名（包含推理时间）
        filename = generate_output_filename(model, inference_time)
        file_path = OUTPUTS_DIR / filename

        # 生成 SRT 内容
        srt_content = SubtitleService.generate_srt_content(segments)

        # 保存文件
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(srt_content)

        return str(file_path), filename

    @staticmethod
    def read_srt_file(file_path: str) -> str:
        """
        读取 SRT 文件内容

        Args:
            file_path: 文件路径

        Returns:
            str: 文件内容
        """
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

    @staticmethod
    def update_segment_text(
        segments: List[SubtitleSegment],
        index: int,
        new_text: str
    ) -> List[SubtitleSegment]:
        """
        更新字幕分段文本

        Args:
            segments: 字幕分段列表
            index: 分段序号
            new_text: 新文本

        Returns:
            List[SubtitleSegment]: 更新后的字幕分段列表
        """
        for segment in segments:
            if segment.index == index:
                segment.text = new_text
                break
        return segments


# 全局字幕服务实例
subtitle_service = SubtitleService()
