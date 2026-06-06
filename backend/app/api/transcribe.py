"""
转录任务 API
"""
from fastapi import APIRouter, BackgroundTasks, HTTPException
from backend.app.models.schemas import (
    TranscribeRequest,
    TranscribeResponse,
    StatusResponse
)
from backend.app.services.transcribe_service import transcribe_service
from backend.app.services.file_service import FileService

router = APIRouter()
file_service = FileService()


@router.post("/transcribe", response_model=TranscribeResponse)
async def start_transcribe(
    request: TranscribeRequest,
    background_tasks: BackgroundTasks
):
    """
    启动转录任务

    Args:
        request: 转录请求
        background_tasks: 后台任务

    Returns:
        TranscribeResponse: 转录响应

    Raises:
        HTTPException: 文件不存在或参数错误
    """
    # 验证模型参数
    from backend.app.utils.config import WHISPER_MODELS
    if request.model not in WHISPER_MODELS:
        raise HTTPException(status_code=400, detail=f"不支持的模型: {request.model}")

    # 这里需要从文件 ID 获取文件路径
    # 由于我们使用内存存储，这里简化处理
    # 生产环境应该从数据库查询
    # 暂时假设文件路径存储在全局变量中
    from backend.app.api.upload import uploaded_files
    if request.file_id not in uploaded_files:
        raise HTTPException(status_code=404, detail="文件不存在")

    file_info = uploaded_files[request.file_id]

    # 创建转录任务
    task_id = transcribe_service.create_task(
        file_id=request.file_id,
        file_path=file_info["file_path"],
        filename=file_info["filename"],
        model=request.model,
        language=request.language,
        use_gpu=request.use_gpu
    )

    # 在后台执行转录任务
    background_tasks.add_task(
        transcribe_service.process_task,
        task_id
    )

    return TranscribeResponse(
        task_id=task_id,
        status="pending"
    )


@router.get("/status/{task_id}", response_model=StatusResponse)
async def get_task_status(task_id: str):
    """
    查询转录任务状态

    Args:
        task_id: 任务 ID

    Returns:
        StatusResponse: 状态响应

    Raises:
        HTTPException: 任务不存在
    """
    task = transcribe_service.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    return StatusResponse(
        task_id=task.task_id,
        status=task.status,
        progress=task.progress,
        current_step=task.current_step,
        error=task.error
    )
