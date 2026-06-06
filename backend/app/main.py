"""
FastAPI 应用入口
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.api import upload, transcribe, subtitle

# 创建 FastAPI 应用
app = FastAPI(
    title="VoiceTrace",
    description="智能语音转字幕 Web 应用",
    version="1.0.0"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应设置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(upload.router, prefix="/api", tags=["文件上传"])
app.include_router(transcribe.router, prefix="/api", tags=["转录任务"])
app.include_router(subtitle.router, prefix="/api", tags=["字幕管理"])


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "Welcome to VoiceTrace API",
        "docs": "/docs",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}
