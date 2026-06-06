
# VoiceTrace

基于 **faster-whisper** 和 **FastAPI** 的智能语音转字幕 Web 应用，提供高效准确的音视频转录服务。

## ✨ 功能特性

- 🎵 **多格式支持**：支持常见音视频格式（MP3、WAV、MP4、AVI、MKV 等）
- 🚀 **GPU 加速**：支持 CUDA 加速，大幅提升转录速度
- 🌍 **多语言识别**：支持中文、英文、日语、韩语等多种语言，支持自动检测
- 📦 **模型管理**：支持多种 Whisper 模型（tiny、base、small、medium、large），自动下载到本地
- ✏️ **在线编辑**：支持在线预览和编辑字幕内容
- 📥 **便捷导出**：一键下载 SRT 格式字幕文件，文件名格式为 `{模型名}_{时间戳}.srt`

## 🛠️ 技术栈

### 后端
- **框架**: FastAPI 0.136+
- **引擎**: faster-whisper 1.2+（CTranslate2 优化的 Whisper 模型）
- **服务器**: Uvicorn ASGI
- **语言**: Python 3.14+

### 前端
- **框架**: React 18 + TypeScript
- **构建工具**: Vite 6+
- **样式**: Tailwind CSS 3+
- **图标**: Lucide React

## 📁 项目结构

```
voicetracev2/
├── backend/                  # 后端代码
│   └── app/
│       ├── api/              # API 路由
│       │   ├── upload.py     # 文件上传接口
│       │   ├── transcribe.py # 转录任务接口
│       │   └── subtitle.py   # 字幕管理接口
│       ├── services/         # 业务逻辑
│       │   ├── file_service.py      # 文件处理服务
│       │   ├── transcribe_service.py # 转录服务
│       │   └── subtitle_service.py  # 字幕服务
│       ├── models/           # 数据模型
│       │   └── schemas.py    # Pydantic 模型定义
│       └── utils/            # 工具函数
│           ├── config.py     # 配置管理
│           └── helpers.py    # 辅助函数
├── frontend/                 # 前端代码
│   └── src/
│       ├── components/       # React 组件
│       │   ├── FileUpload.tsx      # 文件上传组件
│       │   ├── ConfigPanel.tsx     # 参数配置组件
│       │   ├── ProgressDisplay.tsx # 进度显示组件
│       │   └── SubtitleViewer.tsx  # 字幕浏览组件
│       ├── pages/            # 页面组件
│       │   └── Home.tsx      # 主页面
│       ├── api/              # API 调用封装
│       │   └── index.ts      # API 接口定义
│       └── App.tsx           # 应用入口
├── models/                   # Whisper 模型存储目录（自动创建）
├── uploads/                  # 上传文件临时存储（自动创建）
├── outputs/                  # 输出文件存储（自动创建）
├── main.py                   # 后端入口文件
├── pyproject.toml            # Python 项目配置
└── README.md                 # 项目说明文档
```

## 🚀 快速开始

### 环境要求

- Python 3.14+
- Node.js 20+
- CUDA（可选，用于 GPU 加速）

### 安装依赖

```bash
# 安装后端依赖
uv sync

# 安装前端依赖
cd frontend
npm install
```

### 启动服务

```bash
# 启动后端服务（运行在 http://localhost:8000）
uv run python main.py

# 启动前端服务（运行在 http://localhost:5173）
cd frontend
npm run dev
```

### 访问应用

打开浏览器访问 http://localhost:5173

## 📖 使用说明

1. **上传文件**：拖拽或点击选择音视频文件
2. **配置参数**：
   - 选择模型（tiny/base/small/medium/large）
   - 选择语言（自动检测/中文/英文/日语/韩语等）
   - 启用 GPU 加速（需 CUDA 环境）
3. **开始转录**：点击"开始转录"按钮
4. **查看进度**：实时显示转录进度和状态
5. **编辑字幕**：转录完成后可在线编辑字幕内容
6. **下载字幕**：点击"下载 SRT"按钮导出字幕文件

## 🌐 API 接口

### 文件上传
```
POST /api/upload
Content-Type: multipart/form-data
```

### 启动转录
```
POST /api/transcribe
Content-Type: application/json

{
  "file_id": "string",
  "model": "tiny|base|small|medium|large",
  "language": "string (可选)",
  "use_gpu": false
}
```

### 查询状态
```
GET /api/status/{task_id}
```

### 获取字幕
```
GET /api/subtitle/{task_id}
```

### 下载字幕
```
GET /api/download/{task_id}
```

### 获取模型列表
```
GET /api/models
```

## 📝 模型说明

| 模型 | 大小 | 精度 | 速度 |
|------|------|------|------|
| tiny | 39 MB | 较低 | 最快 |
| base | 74 MB | 中等 | 较快 |
| small | 244 MB | 较高 | 中等 |
| medium | 769 MB | 高 | 较慢 |
| large | 1550 MB | 最高 | 最慢 |

## ⚠️ 注意事项

1. 首次使用时，模型会自动下载到 `models` 目录
2. 也可手动下载模型文件放置到 `models` 目录
3. GPU 加速需要安装 CUDA 环境
4. 文件大小限制：500MB
5. 支持的语言：中文、英文、日语、韩语、法语、德语、西班牙语、俄语、意大利语、葡萄牙语

## 📄 许可证

MIT License
