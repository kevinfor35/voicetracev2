"""
字幕管理 API
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from backend.app.models.schemas import SubtitleResponse, ModelsResponse, ModelInfo
from backend.app.services.transcribe_service import transcribe_service
from backend.app.services.subtitle_service import subtitle_service

router = APIRouter()


@router.get("/subtitle/{task_id}", response_model=SubtitleResponse)
async def get_subtitle(task_id: str):
    """
    获取字幕结果

    Args:
        task_id: 任务 ID

    Returns:
        SubtitleResponse: 字幕响应

    Raises:
        HTTPException: 任务不存在或未完成
    """
    task = transcribe_service.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    if task.status != "completed":
        raise HTTPException(status_code=400, detail=f"任务未完成，当前状态: {task.status}")

    if not task.segments:
        raise HTTPException(status_code=404, detail="字幕结果不存在")

    return SubtitleResponse(
        task_id=task.task_id,
        model=task.model,
        language=task.detected_language or "unknown",
        segments=task.segments
    )


@router.get("/download/{task_id}")
async def download_subtitle(task_id: str):
    """
    下载 SRT 字幕文件

    Args:
        task_id: 任务 ID

    Returns:
        FileResponse: 文件响应

    Raises:
        HTTPException: 任务不存在或未完成
    """
    task = transcribe_service.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    if task.status != "completed":
        raise HTTPException(status_code=400, detail=f"任务未完成，当前状态: {task.status}")

    if not task.segments:
        raise HTTPException(status_code=404, detail="字幕结果不存在")

    # 生成并保存 SRT 文件
    file_path, filename = subtitle_service.save_srt_file(
        task.segments,
        task.model
    )

    # 返回文件
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="text/plain"
    )


@router.get("/models", response_model=ModelsResponse)
async def get_models():
    """
    获取可用模型列表

    Returns:
        ModelsResponse: 模型列表响应
    """
    models = transcribe_service.get_all_models()
    return ModelsResponse(
        models=[ModelInfo(**model) for model in models]
    )
