"""
转录服务
"""
import asyncio
import shutil
import tempfile
import os
from datetime import datetime
from typing import Optional, List, Dict
from pathlib import Path
from faster_whisper import WhisperModel
from backend.app.models.schemas import TaskInfo, SubtitleSegment
from backend.app.utils.config import MODELS_DIR, WHISPER_MODELS
from backend.app.utils.helpers import generate_task_id
from backend.app.services.subtitle_service import subtitle_service

try:
    from huggingface_hub import snapshot_download
    HAS_HF_HUB = True
except ImportError:
    HAS_HF_HUB = False


# faster-whisper 模型所需的文件名列表
MODEL_FILES = [
    "model.bin",
    "config.json",
    "tokenizer.json",
    "vocabulary.txt",
    "preprocessor_config.json",
]


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

    def process_task(self, task_id: str):
        """
        处理转录任务（同步执行，在线程池中运行）

        注意：使用同步方法（而非 async），让 FastAPI 的 BackgroundTasks 将其
        放在线程池中执行，避免阻塞事件循环，确保状态轮询可以正常响应。

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

            # 执行转录（同步，在线程池中运行）
            segments, info = self._transcribe(
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

            # 自动保存 SRT 文件到 outputs/ 目录
            output_path, output_filename = subtitle_service.save_srt_file(segments, task.model)
            task.output_path = output_path
            task.output_filename = output_filename

            task.status = "completed"
            task.progress = 100
            task.current_step = "完成"
            task.complete_time = datetime.now()

            # 删除上传的临时文件（不再需要保存）
            if task.file_path and os.path.exists(task.file_path):
                try:
                    os.remove(task.file_path)
                except Exception as e:
                    print(f"Failed to delete uploaded file: {e}")

        except Exception as e:
            # 处理错误
            task.status = "failed"
            task.error = str(e)
            task.current_step = "失败"
            task.complete_time = datetime.now()

            # 清理上传的临时文件
            if task.file_path and os.path.exists(task.file_path):
                try:
                    os.remove(task.file_path)
                except Exception:
                    pass

    def _load_model(self, model_name: str, use_gpu: bool) -> WhisperModel:
        """
        加载 Whisper 模型

        Args:
            model_name: 模型名称（tiny/base/small/medium/large）
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

        # 查找模型路径（仅查找干净目录结构：models/model_name/）
        model_path = self._find_model_path(model_name)

        # 加载模型 - 传入的是本地目录路径，不会触发自动下载
        model = WhisperModel(
            model_path,
            device=device,
            compute_type=compute_type,
        )

        # 缓存模型
        self.model_cache[cache_key] = model
        return model

    def _find_model_path(self, model_name: str) -> str:
        """
        查找模型路径（仅支持干净目录结构：models/model_name/）

        优先级：
        1. 已存在的干净目录 -> 直接返回
        2. 不存在 -> 自动下载到干净目录后返回

        Args:
            model_name: 模型名称

        Returns:
            str: 模型目录路径（如 D:/project/models/tiny）
        """
        clean_model_path = MODELS_DIR / model_name

        # 1. 如果干净目录已存在且包含必要文件，直接返回
        if clean_model_path.exists() and self._has_model_files(clean_model_path):
            return str(clean_model_path)

        # 2. 否则自动下载模型到干净目录
        if HAS_HF_HUB:
            print(f"Model '{model_name}' not found locally. Downloading...")
            self._download_model_to_clean_dir(model_name)
            # 下载完成后再次检查
            if clean_model_path.exists() and self._has_model_files(clean_model_path):
                print(f"Model '{model_name}' downloaded successfully to {clean_model_path}")
                return str(clean_model_path)
            else:
                print(f"Warning: Download completed but required files not found in {clean_model_path}")
        else:
            print("Warning: huggingface_hub not available, cannot auto-download model.")

        # 3. 回退：返回模型名称字符串，让 faster-whisper 自行处理
        return model_name

    def _download_model_to_clean_dir(self, model_name: str):
        """
        将模型直接下载到干净目录结构（与官网手动下载格式一致）

        目录结构：models/model_name/model.bin, config.json, ...

        Args:
            model_name: 模型名称
        """
        try:
            repo_id = f"Systran/faster-whisper-{model_name}"
            clean_model_path = MODELS_DIR / model_name

            # 如果目录已存在但文件不完整，先删除
            if clean_model_path.exists():
                shutil.rmtree(clean_model_path)

            # 创建干净目录
            clean_model_path.mkdir(parents=True, exist_ok=True)

            # 使用系统临时目录作为 HF 缓存（避免在 models/ 下生成 blobs/refs/snapshots）
            with tempfile.TemporaryDirectory() as tmp_cache_dir:
                # 使用 snapshot_download 直接下载到本地目录
                # local_dir 参数指定文件的最终位置
                # cache_dir 参数指向临时目录，避免污染 models/
                snapshot_download(
                    repo_id=repo_id,
                    local_dir=str(clean_model_path),
                    cache_dir=tmp_cache_dir,
                    local_files_only=False,
                )

            # 清理 huggingface_hub 在 local_dir 中留下的 .cache/ 目录
            cache_subdir = clean_model_path / ".cache"
            if cache_subdir.exists():
                shutil.rmtree(cache_subdir)

            # 清理无关文件（可选保留）
            # 保留 .gitattributes 不影响使用，但可以删除 README 等非必需文件
            for filename in ["README.md"]:
                f = clean_model_path / filename
                if f.exists():
                    f.unlink()

        except Exception as e:
            print(f"Failed to download model '{model_name}': {e}")
            # 清理可能产生的空目录或不完整文件
            if clean_model_path.exists():
                shutil.rmtree(clean_model_path)

    def _has_model_files(self, dir_path: Path) -> bool:
        """
        检查目录中是否包含模型所需的关键文件

        Args:
            dir_path: 目录路径

        Returns:
            bool: 是否包含必需的模型文件
        """
        # 至少需要 model.bin 和 config.json
        has_model_bin = (dir_path / "model.bin").exists()
        has_config = (dir_path / "config.json").exists()
        return has_model_bin and has_config

    def _transcribe(
        self,
        model: WhisperModel,
        file_path: str,
        language: Optional[str]
    ) -> tuple[List[SubtitleSegment], any]:
        """
        执行转录（同步，在线程池中运行）

        注意：faster_whisper 的 transcribe() 返回一个生成器，实际转录在遍历
        segments 时发生。由于 process_task 整体在线程池中运行，这里可以直接
        同步执行，不会阻塞主事件循环。

        Args:
            model: Whisper 模型
            file_path: 文件路径
            language: 语言代码

        Returns:
            tuple: (字幕分段列表, 转录信息)
        """
        # 执行转录
        segments, info = model.transcribe(
            file_path,
            language=language,
            task="transcribe",
            beam_size=5,
            vad_filter=True
        )

        # 遍历生成器，消耗所有转录结果并转换为字幕分段格式
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
        downloaded = self._is_model_downloaded(model_name)

        return {
            "name": model_name,
            "size": model_config["size"],
            "languages": model_config["languages"],
            "downloaded": downloaded
        }

    def _is_model_downloaded(self, model_name: str) -> bool:
        """
        检查模型是否已下载（仅检查干净目录结构：models/model_name/）

        Args:
            model_name: 模型名称

        Returns:
            bool: 是否已下载
        """
        clean_model_path = MODELS_DIR / model_name
        if clean_model_path.exists():
            return self._has_model_files(clean_model_path)
        return False

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
