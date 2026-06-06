"""
转录服务

核心功能：
1. 支持 80 维和 128 维梅尔频谱模型（通过 preprocessor_config.json 检测）
2. 自动在 config.json 中添加 num_mel_bins 字段，确保 faster-whisper 正确识别
3. 优化多语言支持和 VAD filter 参数
4. 统计推理时间并在输出文件名中体现
"""
import asyncio
import shutil
import tempfile
import os
import json
import time
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
        language: Optional[str]
    ) -> str:
        """
        创建转录任务

        Args:
            file_id: 文件 ID
            file_path: 文件路径
            filename: 文件名
            model: 模型名称
            language: 语言代码

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

        # 记录总处理开始时间
        total_start_time = time.time()

        try:
            # 更新任务状态
            task.status = "processing"
            task.current_step = "加载模型"
            task.progress = 10

            # 加载模型（CPU 推理）
            model = self._load_model(task.model)

            # 记录推理开始时间
            inference_start_time = time.time()

            # 更新进度
            task.current_step = "开始转录"
            task.progress = 20

            # 执行转录
            segments, info = self._transcribe(
                model,
                task.file_path,
                task.language
            )

            # 计算推理时间
            inference_time = time.time() - inference_start_time
            total_time = time.time() - total_start_time

            # 更新进度
            task.current_step = "处理结果"
            task.progress = 90

            # 保存结果
            task.segments = segments
            task.detected_language = info.language

            # 自动保存 SRT 文件到 outputs/ 目录（包含推理时间）
            output_path, output_filename = subtitle_service.save_srt_file(
                segments, task.model, inference_time
            )
            task.output_path = output_path
            task.output_filename = output_filename

            task.status = "completed"
            task.progress = 100
            task.current_step = "完成"
            task.complete_time = datetime.now()

            print(f"Task {task_id} completed: inference={inference_time:.1f}s, total={total_time:.1f}s")

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
            print(f"Task {task_id} failed: {e}")

            # 清理上传的临时文件
            if task.file_path and os.path.exists(task.file_path):
                try:
                    os.remove(task.file_path)
                except Exception:
                    pass

    def _load_model(self, model_name: str) -> WhisperModel:
        """
        加载 Whisper 模型（CPU 推理）

        Args:
            model_name: 模型名称

        Returns:
            WhisperModel: 加载的模型
        """
        # 检查模型缓存
        cache_key = model_name
        if cache_key in self.model_cache:
            return self.model_cache[cache_key]

        # 固定使用 CPU 推理，compute_type 为 int8（量化，省内存）
        device = "cpu"
        compute_type = "int8"

        # 查找模型路径
        model_path = self._find_model_path(model_name)

        # 关键：确保 config.json 中有正确的 num_mel_bins 字段
        self._ensure_num_mel_bins(model_path)

        # 加载模型
        model = WhisperModel(
            model_path,
            device=device,
            compute_type=compute_type,
            local_files_only=True,
        )

        # 缓存模型
        self.model_cache[cache_key] = model
        return model

    def _ensure_num_mel_bins(self, model_path: str):
        """
        确保 config.json 中有正确的 num_mel_bins 字段
        
        标准 Whisper 模型 (tiny/base/small/medium) 使用 80 维梅尔频谱
        large-v3 和 distil 模型使用 128 维梅尔频谱
        
        检测逻辑：
        1. 如果 preprocessor_config.json 存在，读取其中的 feature_size
        2. 如果 config.json 中没有 num_mel_bins，添加正确的值
        3. 如果两个文件都不存在，使用默认 80

        Args:
            model_path: 模型目录路径
        """
        config_path = Path(model_path) / "config.json"
        preproc_path = Path(model_path) / "preprocessor_config.json"
        
        if not config_path.exists():
            return  # 无 config.json 则跳过

        # 读取当前 config.json
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except Exception as e:
            print(f"Warning: Could not read config.json at {config_path}: {e}")
            return

        # 如果已经有 num_mel_bins，则不需要修改
        if "num_mel_bins" in config:
            return

        # 从 preprocessor_config.json 读取 feature_size
        detected_mel_bins = 80  # 默认值
        if preproc_path.exists():
            try:
                with open(preproc_path, 'r', encoding='utf-8') as f:
                    preproc = json.load(f)
                feature_size = preproc.get("feature_size", 80)
                detected_mel_bins = int(feature_size)
            except Exception as e:
                print(f"Warning: Could not read preprocessor_config.json at {preproc_path}: {e}")

        # 添加 num_mel_bins 到 config.json
        config["num_mel_bins"] = detected_mel_bins
        
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            print(f"Updated {config_path.name}: num_mel_bins = {detected_mel_bins}")
        except Exception as e:
            print(f"Warning: Could not write config.json at {config_path}: {e}")

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

    def _get_repo_id(self, model_name: str) -> str:
        """
        根据模型名称获取正确的 HuggingFace repo_id

        Args:
            model_name: 模型名称

        Returns:
            str: HuggingFace repo_id
        """
        # Distil 模型使用不同的命名格式（仅支持英语）
        if model_name == "distil-large-v3.5":
            # 特殊处理：distil-large-v3.5 使用不同的 repo（官方 CTranslate2 版本）
            return "distil-whisper/distil-large-v3.5-ct2"
        elif model_name.startswith("distil-"):
            # distil-large-v2 -> Systran/faster-distil-whisper-large-v2
            model_suffix = model_name.replace("distil-", "")
            return f"Systran/faster-distil-whisper-{model_suffix}"

        # Turbo 模型：必须使用 CTranslate2 格式的预转换仓库
        # 注意：openai/whisper-large-v3-turbo 是 .safetensors 格式，faster-whisper 不支持！
        # 必须使用已转换为 CTranslate2 格式的仓库（model.bin 而非 model.safetensors）
        if model_name == "large-v3-turbo":
            return "mobiuslabsgmbh/faster-whisper-large-v3-turbo"

        # 其他模型使用标准格式
        return f"Systran/faster-whisper-{model_name}"

    def _download_model_to_clean_dir(self, model_name: str):
        """
        将模型直接下载到干净目录结构（与官网手动下载格式一致）

        目录结构：models/model_name/model.bin, config.json, ...

        Args:
            model_name: 模型名称
        """
        try:
            # 根据模型名称确定正确的 HuggingFace repo_id
            repo_id = self._get_repo_id(model_name)
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

        # 可选：检查文件大小，确保 model.bin 不是空文件或损坏文件
        if has_model_bin:
            model_bin_size = (dir_path / "model.bin").stat().st_size
            if model_bin_size < 1024 * 1024:  # 小于 1MB 可能是损坏的
                print(f"Warning: model.bin in {dir_path} is too small ({model_bin_size} bytes), may be corrupted")
                return False

        return has_model_bin and has_config

    def _transcribe(
        self,
        model: WhisperModel,
        file_path: str,
        language: Optional[str]
    ) -> tuple[List[SubtitleSegment], any]:
        """
        执行转录（同步，在线程池中运行）

        语言参数处理：
        - "auto" 或 None -> 传 None 给 faster-whisper，让其自动检测语言
        - 其他值如 "zh", "en", "ko" -> 强制指定语言

        VAD 参数：
        - 使用宽松的 VAD 配置，min_silence_duration_ms 设为 2000ms
        - 避免过度切分音频导致漏识别

        Args:
            model: Whisper 模型
            file_path: 文件路径
            language: 语言代码

        Returns:
            tuple: (字幕分段列表, 转录信息)
        """
        # 处理语言参数：'auto' -> None（自动检测），其他保持原值
        whisper_language = None if (language is None or language == 'auto') else language

        # 执行转录
        # VAD 参数优化：
        # - min_silence_duration_ms: 静音检测阈值，越大越宽松
        # - speech_pad_ms: 语音段前后填充，避免切分过碎
        segments, info = model.transcribe(
            file_path,
            language=whisper_language,
            task="transcribe",
            beam_size=5,
            vad_filter=True,
            vad_parameters=dict(
                min_silence_duration_ms=2000,  # 2秒静音才视为静音段
                speech_pad_ms=400,              # 语音段前后各填充 400ms
            ),
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
