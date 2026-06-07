# VoiceTrace

一款**开源、离线、基于 CPU 运算**的语音转字幕工具，专为视频创作者打造。支持多语言识别、推理速度快、可导出标准 SRT 字幕文件，帮助创作者摆脱剪映 SVIP 和达芬奇付费限制，轻松实现口播转字幕。

## 项目定位

剪映自动生成字幕需要 SVIP，达芬奇免费版没有字幕生成功能——这正是 VoiceTrace 要解决的问题。

**核心价值：**
- 🆓 **完全免费**：开源项目，无任何付费限制
- 🖥️ **离线运行**：无需联网，数据安全可控
- 🚀 **CPU 友好**：无需 GPU，普通电脑即可运行
- ⚡ **快速推理**：基于 Faster-Whisper，速度提升约 4 倍

**目标用户：**
- 自媒体创作者、UP 主、短视频博主
- 有口播转字幕需求但不想充 SVIP 的个人用户
- 需要批量处理音视频字幕的内容创作者

## 功能特性

- **多语言支持**：支持中文、英文、日语、韩语等数十种主流语言自动检测
- **多种模型**：提供 tiny、base、small、medium、large-v3、large-v3-turbo、distil 等多种模型选择
- **离线运行**：模型文件本地存储，无需联网即可使用
- **快速推理**：基于 Faster-Whisper 引擎，推理速度显著提升
- **SRT 导出**：自动生成标准 SRT 字幕文件，文件名包含模型名和推理时间
- **在线预览**：网页端实时预览字幕内容，方便校对
- **友好界面**：简洁美观的 Web 界面，支持拖拽上传

## 技术栈

- **后端**：FastAPI + Faster-Whisper
- **前端**：React + TypeScript + Vite + Tailwind CSS

## 关于 Faster-Whisper

本项目基于 [Faster-Whisper](https://github.com/SYSTRAN/faster-whisper) 构建，它是 OpenAI Whisper 的高效实现版本。

**Faster-Whisper 核心特性：**

- **4倍速度提升**：使用 CTranslate2 推理引擎，相比原始 Whisper 快约 4 倍
- **低内存占用**：内存占用仅为原始 Whisper 的约一半
- **高精度**：保持与原版 Whisper 相同的识别精度
- **多语言支持**：支持数十种主流语言的语音识别
- **模型格式**：使用 CTranslate2 格式（`.bin` 文件），不支持 `.safetensors`

更多信息请访问 [Faster-Whisper GitHub 仓库](https://github.com/SYSTRAN/faster-whisper)。

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
| tiny | 39 MB | ✅ | 速度最快，适合快速预览 |
| base | 74 MB | ✅ | 平衡速度与精度（默认推荐） |
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

### 手动下载模型

如果自动下载失败或网络受限，可以手动下载模型文件。

**步骤 1：选择模型并获取下载地址**

根据需要的模型，访问对应的 HuggingFace 仓库：

| 模型名称 | HuggingFace 仓库链接 |
|---------|---------------------|
| tiny | https://huggingface.co/Systran/faster-whisper-tiny |
| base | https://huggingface.co/Systran/faster-whisper-base |
| small | https://huggingface.co/Systran/faster-whisper-small |
| medium | https://huggingface.co/Systran/faster-whisper-medium |
| large-v2 | https://huggingface.co/Systran/faster-whisper-large-v2 |
| large-v3 | https://huggingface.co/Systran/faster-whisper-large-v3 |
| large-v3-turbo | https://huggingface.co/mobiuslabsgmbh/faster-whisper-large-v3-turbo |
| distil-large-v2 | https://huggingface.co/Systran/faster-distil-whisper-large-v2 |
| distil-large-v3 | https://huggingface.co/Systran/faster-distil-whisper-large-v3 |

**步骤 2：下载必需的文件**

进入上述仓库页面后，下载以下文件（缺一不可）：

- `model.bin` - 模型权重文件（核心文件）
- `config.json` - 模型配置文件
- `tokenizer.json` - 分词器配置
- `preprocessor_config.json` - 音频预处理配置（部分模型需要）
- `vocabulary.txt` - 词汇表文件

**步骤 3：创建目录结构并放置文件**

在项目根目录的 `models/` 文件夹下创建与模型名同名的子目录，然后将下载的所有文件放入该目录：

```
voicetracev2/
└── models/
    └── base/                    # 模型名作为目录名
        ├── model.bin            # 必需
        ├── config.json          # 必需
        ├── tokenizer.json       # 必需
        ├── preprocessor_config.json  # 必需（部分模型）
        └── vocabulary.txt       # 必需
```

**示例：手动安装 base 模型**

1. 访问 https://huggingface.co/Systran/faster-whisper-base
2. 下载 `model.bin`、`config.json`、`tokenizer.json`、`preprocessor_config.json`、`vocabulary.txt`
3. 在 `models/` 目录下创建 `base/` 文件夹
4. 将所有下载的文件放入 `models/base/` 目录

**注意事项：**

- ⚠️ **必须下载 CTranslate2 格式的模型（.bin 文件）**，不支持 `.safetensors` 格式！
- ⚠️ 目录名称必须与模型名完全一致（如 `large-v3-turbo` 对应目录 `models/large-v3-turbo/`）
- ⚠️ 确保所有必需文件都已下载，缺少任何一个都会导致模型加载失败

### 模型文件命名规范

| 模型名称 | models/ 目录 | HuggingFace repo_id |
|---------|-------------|---------------------|
| tiny | models/tiny/ | Systran/faster-whisper-tiny |
| base | models/base/ | Systran/faster-whisper-base |
| small | models/small/ | Systran/faster-whisper-small |
| medium | models/medium/ | Systran/faster-whisper-medium |
| large-v2 | models/large-v2/ | Systran/faster-whisper-large-v2 |
| large-v3 | models/large-v3/ | Systran/faster-whisper-large-v3 |
| large-v3-turbo | models/large-v3-turbo/ | mobiuslabsgmbh/faster-whisper-large-v3-turbo |
| distil-large-v2 | models/distil-large-v2/ | Systran/faster-distil-whisper-large-v2 |
| distil-large-v3 | models/distil-large-v3/ | Systran/faster-distil-whisper-large-v3 |

## 支持的语言

系统默认使用**自动检测**，无需手动选择语言。支持数十种主流语言，包括：

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
- `large-v3-turbo`：**支持多语言**（推荐用于中文/韩文等多语言场景）

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

### Q: 项目用到 FFmpeg 吗？
A: 项目仅在获取音视频时长时调用 `ffprobe`（FFmpeg 工具集的一部分），这是可选功能。如果系统没有安装 FFmpeg，项目仍然可以正常运行，只是无法显示时长信息。音频解码由 faster-whisper 内部完成，无需额外的 FFmpeg 配置。

## 致谢

感谢 [Faster-Whisper](https://github.com/SYSTRAN/faster-whisper) 项目提供的高效推理引擎，以及 [OpenAI Whisper](https://github.com/openai/whisper) 提供的优秀语音识别模型。
