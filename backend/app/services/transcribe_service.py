"""
转录服务
"""
import asyncio
from datetime import datetime
from typing import Optional, List, Dict
from pathlib import Path
from faster_whisper import WhisperModel
from backend.app.models.schemas import TaskInfo, SubtitleSegment
from backend.app.utils.config import MODELS_DIR, WHISPER_MODELS
from backend.app.utils.helpers import generate_task_id


class TranscribeService:
    """转录服务"""

    def __init__(self):
        # 任务存储（内存存储，生产环境应使用数据库）
        self.tasks: Dict[str, TaskInfo] = {}
        # 模型缓存
        self.model_cache: Dict[str, WhisperModel] = {}

    def create_task(
        self,
        file_id: str,
        file_path: str,
        filename: str,
        model: str,
        language: Optional[str],
        use_gpu: bool
    ) -> str:
        """
        创建转录任务

        Args:
            file_id: 文件 ID
            file_path: 文件路径
            filename: 文件名
            model: 模型名称
            language: 语言代码
            use_gpu: 是否使用 GPU

        Returns:
            str: 任务 ID
        """
        task_id = generate_task_id()
        task = TaskInfo(
            task_id=task_id,
            file_id=file_id,
            file_path=file_path,
            filename=filename,
            model=model,
            language=language,
            use_gpu=use_gpu,
            status="pending",
            progress=0,
            current_step="等待处理",
            create_time=datetime.now()
        )
        self.tasks[task_id] = task
        return task_id

    def get_task(self, task_id: str) -> Optional[TaskInfo]:
        """
        获取任务信息

        Args:
            task_id: 任务 ID

        Returns:
            TaskInfo: 任务信息，如果不存在则返回 None
        """
        return self.tasks.get(task_id)

    async def process_task(self, task_id: str):
        """
        处理转录任务（异步执行）

        Args:
            task_id: 任务 ID
        """
        task = self.tasks.get(task_id)
        if not task:
            return

        try:
            # 更新任务状态
            task.status = "processing"
            task.current_step = "加载模型"
            task.progress = 10

            # 加载模型
            model = self._load_model(task.model, task.use_gpu)

            # 更新进度
            task.current_step = "开始转录"
            task.progress = 20

            # 执行转录
            segments, info = await self._transcribe(
                model,
                task.file_path,
                task.language
            )

            # 更新进度
            task.current_step = "处理结果"
            task.progress = 90

            # 保存结果
            task.segments = segments
            task.detected_language = info.language
            task.status = "completed"
            task.progress = 100
            task.current_step = "完成"
            task.complete_time = datetime.now()

        except Exception as e:
            # 处理错误
            task.status = "failed"
            task.error = str(e)
            task.current_step = "失败"
            task.complete_time = datetime.now()

    def _load_model(self, model_name: str, use_gpu: bool) -> WhisperModel:
        """
        加载 Whisper 模型

        Args:
            model_name: 模型名称
            use_gpu: 是否使用 GPU

        Returns:
            WhisperModel: 加载的模型
        """
        # 检查模型缓存
        cache_key = f"{model_name}_{use_gpu}"
        if cache_key in self.model_cache:
            return self.model_cache[cache_key]

        # 设置设备
        device = "cuda" if use_gpu else "cpu"
        compute_type = "float16" if use_gpu else "int8"

        # 加载模型
        model = WhisperModel(
            model_name,
            device=device,
            compute_type=compute_type,
            download_root=str(MODELS_DIR)
        )

        # 缓存模型
        self.model_cache[cache_key] = model
        return model

    async def _transcribe(
        self,
        model: WhisperModel,
        file_path: str,
        language: Optional[str]
    ) -> tuple[List[SubtitleSegment], any]:
        """
        执行转录

        Args:
            model: Whisper 模型
            file_path: 文件路径
            language: 语言代码

        Returns:
            tuple: (字幕分段列表, 转录信息)
        """
        # 在线程池中执行转录（避免阻塞）
        loop = asyncio.get_event_loop()
        segments, info = await loop.run_in_executor(
            None,
            lambda: model.transcribe(
                file_path,
                language=language,
                task="transcribe",
                beam_size=5,
                vad_filter=True
            )
        )

        # 转换为字幕分段格式
        subtitle_segments = []
        for i, segment in enumerate(segments, start=1):
            subtitle_segments.append(
                SubtitleSegment(
                    index=i,
                    start=segment.start,
                    end=segment.end,
                    text=segment.text.strip()
                )
            )

        return subtitle_segments, info

    def get_model_info(self, model_name: str) -> dict:
        """
        获取模型信息

        Args:
            model_name: 模型名称

        Returns:
            dict: 模型信息
        """
        if model_name not in WHISPER_MODELS:
            return None

        model_config = WHISPER_MODELS[model_name]

        # 检查模型是否已下载
        model_path = MODELS_DIR / f"model--guillaumekln--faster-whisper-{model_name}"
        downloaded = model_path.exists()

        return {
            "name": model_name,
            "size": model_config["size"],
            "languages": model_config["languages"],
            "downloaded": downloaded
        }

    def get_all_models(self) -> List[dict]:
        """
        获取所有可用模型信息

        Returns:
            List[dict]: 模型信息列表
        """
        models = []
        for model_name in WHISPER_MODELS.keys():
            model_info = self.get_model_info(model_name)
            if model_info:
                models.append(model_info)
        return models


# 全局转录服务实例
transcribe_service = TranscribeService()
