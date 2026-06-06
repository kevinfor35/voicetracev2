# VoiceTrace

基于 Faster-Whisper 的智能语音转字幕系统，支持多语言识别和多种模型选择。

## 功能特性

- **多语言支持**：支持中文、英文、日语、韩语等 99 种语言自动识别
- **多种模型**：支持 tiny、base、small、medium、large-v3、large-v3-turbo、distil 等模型
- **自动下载**：模型文件自动下载至 `models/` 目录，也支持手动放置
- **SRT 导出**：自动生成 SRT 字幕文件，文件名包含模型名和推理时间
- **在线预览**：网页端实时预览字幕内容
- **友好界面**：简洁美观的 Web 界面，支持拖拽上传

## 技术栈

- **后端**：FastAPI + Faster-Whisper
- **前端**：React + TypeScript + Vite + Tailwind CSS
- **音频处理**：FFmpeg

## 项目结构

```
voicetracev2/
├── backend/                    # 后端代码
│   └── app/
│       ├── api/               # API 路由
│       │   ├── transcribe.py  # 转录任务 API
│       │   ├── subtitle.py    # 字幕管理 API
│       │   └── upload.py       # 文件上传 API
│       ├── models/
│       │   └── schemas.py      # 数据模型
│       ├── services/
│       │   ├── transcribe_service.py  # 转录服务（核心逻辑）
│       │   ├── subtitle_service.py    # 字幕服务
│       │   └── file_service.py        # 文件服务
│       └── utils/
│           ├── config.py       # 配置
│           └── helpers.py     # 辅助函数
├── frontend/                   # 前端代码
│   └── src/
│       ├── api/               # API 调用封装
│       ├── components/        # React 组件
│       │   ├── ConfigPanel.tsx    # 参数配置
│       │   ├── FileUpload.tsx     # 文件上传
│       │   ├── ProgressDisplay.tsx # 进度显示
│       │   └── SubtitleViewer.tsx  # 字幕浏览
│       └── pages/
│           └── Home.tsx       # 主页面
├── models/                     # Whisper 模型存放目录
│   ├── tiny/
│   ├── base/
│   ├── large-v3/
│   └── large-v3-turbo/
├── outputs/                    # 生成的 SRT 字幕文件
├── main.py                     # 后端入口
└── pyproject.toml             # Python 依赖
```

## 快速开始

### 1. 安装依赖

```bash
# 安装后端依赖
uv sync

# 安装前端依赖
cd frontend
npm install
cd ..
```

### 2. 启动服务

```bash
# 启动后端（后端端口 8000）
uv run python main.py

# 新开终端，启动前端（前端端口 5173）
cd frontend
npm run dev
```

### 3. 使用

1. 访问 http://localhost:5173
2. 上传音视频文件（支持 MP3、WAV、MP4、AVI、MKV 等格式）
3. 选择模型（语言自动检测）
4. 点击"开始转录"
5. 转录完成后在线浏览字幕或下载 SRT 文件

## 支持的模型

| 模型 | 大小 | 多语言 | 说明 |
|------|------|--------|------|
| tiny | 39 MB | ✅ | 速度最快，语言检测准确 |
| base | 74 MB | ✅ | 平衡速度与精度（默认） |
| small | 244 MB | ✅ | 较好的精度 |
| medium | 769 MB | ✅ | 良好的多语言支持 |
| large-v2 | 1.5 GB | ✅ | 最佳多语言识别 |
| large-v3 | 1.6 GB | ✅ | 最新版本，性能最佳 |
| **large-v3-turbo** | 1.6 GB | ✅ | **推荐！多语言+快速** |
| distil-large-v2 | 769 MB | ❌ | **仅英语！速度快 6 倍** |
| distil-large-v3 | 800 MB | ❌ | **仅英语！速度快 6 倍** |

### ⚠️ 重要说明

**Distil 模型（distil-large-v2、distil-large-v3 等）仅支持英语转录！**

根据 Hugging Face 官方文档：
> "Distil-Whisper is only available for English speech recognition."

如果使用 distil 模型转录非英语音频，输出将是英文或乱码。如需多语言支持，请使用：
- **large-v3-turbo**（推荐）：结合了 distil 的速度和多语言支持
- **base/tiny**：速度快，语言检测准确
- **large-v3**：最佳多语言识别

### 模型下载

模型会在首次使用时自动下载到 `models/` 目录。下载的文件会整理成干净的目录结构：

```
models/
└── tiny/
    ├── model.bin
    ├── config.json
    └── ...
```

也可以手动下载模型文件放置到对应目录。

### 模型文件命名规范

| 模型名称 | models/ 目录 | HuggingFace repo_id |
|---------|-------------|---------------------|
| tiny | models/tiny/ | Systran/faster-whisper-tiny |
| base | models/base/ | Systran/faster-whisper-base |
| small | models/small/ | Systran/faster-whisper-small |
| medium | models/medium/ | Systran/faster-whisper-medium |
| large-v2 | models/large-v2/ | Systran/faster-whisper-large-v2 |
| large-v3 | models/large-v3/ | Systran/faster-whisper-large-v3 |
| large-v3-turbo | models/large-v3-turbo/ | openai/whisper-large-v3-turbo |
| distil-large-v2 | models/distil-large-v2/ | Systran/faster-distil-whisper-large-v2 |
| distil-large-v3 | models/distil-large-v3/ | Systran/faster-distil-whisper-large-v3 |

## 支持的语言

系统默认使用**自动检测**，无需手动选择语言。支持 99 种语言，包括：

- 中文（zh）
- 英文（en）
- 日语（ja）
- 韩语（ko）
- 法语（fr）
- 德语（de）
- 西班牙语（es）
- 俄语（ru）
- 意大利语（it）
- 葡萄牙语（pt）
- 阿拉伯语（ar）
- 印地语（hi）
- ... 等

## SRT 文件命名

生成的文件名格式：`{模型名}_{时间戳}_{推理时长}.srt`

示例：
- `large-v3_20260606_221027_03m45s.srt`
- `base_20260606_234512_01m20s.srt`

## API 接口

### 上传文件
```
POST /api/upload
Content-Type: multipart/form-data
```

### 启动转录
```
POST /api/transcribe
Content-Type: application/json

{
  "file_id": "xxx",
  "model": "base",
  "language": "auto"  // 可选，默认自动检测
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

## 配置说明

### 模型目录
模型存放在项目根目录的 `models/` 文件夹下，每个模型一个子目录。

### 输出目录
生成的 SRT 字幕文件保存在 `outputs/` 目录。

### 临时文件
上传的文件在转录完成后会自动删除，不占用额外空间。

## 常见问题

### Q: distil 模型识别中文/韩文输出英文？
A: **distil 模型仅支持英语！** 请使用 `large-v3-turbo`（推荐）或 `base`、`large-v3` 等多语言模型。

### Q: 模型下载失败怎么办？
A: 可以手动下载模型。将模型文件（model.bin、config.json、tokenizer.json 等）放置到 `models/{模型名}/` 目录下即可。**注意：必须是 CTranslate2 格式的 .bin 文件，不是 .safetensors！**

### Q: 下载的模型是 .safetensors 文件能用吗？
A: **不能直接用。faster-whisper 不支持 .safetensors 格式。** 解决方法：
1. 重新下载正确的 CTranslate2 格式版本（见上方的 HuggingFace 仓库链接）
2. 或者使用 `ct2-transformers-converter` 命令将 .safetensors 转换为 .bin 格式

### Q: distil-large-v3 和 large-v3-turbo 有什么区别？
A: 关键区别在于**语言支持**：
- `distil-large-v3`：**仅支持英语**（蒸馏版本，已删除多语言能力）
- `large-v3-turbo`：**支持 99 种语言**（推荐用于中文/韩文等多语言场景）

两者速度接近，但 large-v3-turbo 支持多语言，是真正的性价比之王。

### Q: 韩语识别不准确？
A: 建议使用 `large-v3` 或 `large-v3-turbo` 模型，这些模型对小语种支持更好。同时确保音频清晰，背景噪音较少。

### Q: 转录结果为空？
A: 请检查：1) 音频是否有声音内容；2) 音频是否清晰（背景噪音过大会影响识别）；3) 尝试使用更大的模型（如 large-v3）。

### Q: 哪个模型性价比最高？
A: 
- **多语言场景**：推荐 `large-v3-turbo`，速度快且支持多语言
- **英语场景**：推荐 `distil-large-v3`，速度最快
- **快速预览**：推荐 `base` 或 `tiny`，速度快且语言检测准确
