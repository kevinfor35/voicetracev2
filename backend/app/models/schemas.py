"""
数据模型定义
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


# 文件上传相关模型
class UploadResponse(BaseModel):
    """文件上传响应"""
    file_id: str
    filename: str
    file_size: int
    duration: Optional[float] = None


# 转录任务相关模型
class TranscribeRequest(BaseModel):
    """转录请求"""
    file_id: str
    model: str  # tiny, base, small, medium, large
    language: Optional[str] = None  # 语言代码，None/auto 表示自动检测


class TranscribeResponse(BaseModel):
    """转录响应"""
    task_id: str
    status: str  # pending, processing, completed, failed


class StatusResponse(BaseModel):
    """状态查询响应"""
    task_id: str
    status: str
    progress: int  # 0-100
    current_step: str
    error: Optional[str] = None


# 字幕相关模型
class SubtitleSegment(BaseModel):
    """字幕分段"""
    index: int
    start: float  # 开始时间（秒）
    end: float  # 结束时间（秒）
    text: str


class SubtitleResponse(BaseModel):
    """字幕响应"""
    task_id: str
    model: str
    language: str
    segments: List[SubtitleSegment]


# 模型信息相关模型
class ModelInfo(BaseModel):
    """模型信息"""
    name: str
    size: str
    languages: List[str]
    downloaded: bool


class ModelsResponse(BaseModel):
    """模型列表响应"""
    models: List[ModelInfo]


# 内部数据模型（用于任务管理）
class TaskInfo(BaseModel):
    """任务信息"""
    task_id: str
    file_id: str
    file_path: str
    filename: str
    model: str
    language: Optional[str]
    status: str
    progress: int
    current_step: str
    error: Optional[str] = None
    create_time: datetime
    complete_time: Optional[datetime] = None
    segments: Optional[List[SubtitleSegment]] = None
    detected_language: Optional[str] = None
    output_path: Optional[str] = None
    output_filename: Optional[str] = None
