"""
VoiceTrace 后端服务入口
"""
import uvicorn
from backend.app.main import app


def main():
    """启动 FastAPI 服务"""
    uvicorn.run(
        "backend.app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )


if __name__ == "__main__":
    main()

