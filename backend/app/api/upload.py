"""
文件上传 API
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from backend.app.models.schemas import UploadResponse
from backend.app.services.file_service import FileService
from backend.app.utils.helpers import format_file_size

router = APIRouter()
file_service = FileService()

# 全局存储上传文件信息（生产环境应使用数据库）
uploaded_files = {}


@router.post("/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """
    上传音视频文件

    Args:
        file: 上传的文件

    Returns:
        UploadResponse: 上传响应

    Raises:
        HTTPException: 文件格式不支持或文件过大
    """
    try:
        # 读取文件内容
        file_content = await file.read()

        # 保存文件
        file_id, file_path, file_size = await file_service.save_upload_file(
            file_content,
            file.filename
        )

        # 获取文件时长
        duration = await file_service.get_file_duration(file_path)

        # 存储文件信息
        uploaded_files[file_id] = {
            "file_path": file_path,
            "filename": file.filename,
            "file_size": file_size,
            "duration": duration
        }

        return UploadResponse(
            file_id=file_id,
            filename=file.filename,
            file_size=file_size,
            duration=duration
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件上传失败: {str(e)}")
