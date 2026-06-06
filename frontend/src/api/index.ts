/**
 * API 调用封装
 */
const API_BASE_URL = 'http://localhost:8000/api';

/**
 * 文件上传 API
 */
export const uploadApi = {
  /**
   * 上传文件
   */
  async upload(file: File): Promise<UploadResponse> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_BASE_URL}/upload`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || '文件上传失败');
    }

    return response.json();
  },
};

/**
 * 转录任务 API
 */
export const transcribeApi = {
  /**
   * 启动转录任务
   */
  async start(request: TranscribeRequest): Promise<TranscribeResponse> {
    const response = await fetch(`${API_BASE_URL}/transcribe`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || '启动转录失败');
    }

    return response.json();
  },

  /**
   * 查询任务状态
   */
  async getStatus(taskId: string): Promise<StatusResponse> {
    const response = await fetch(`${API_BASE_URL}/status/${taskId}`);

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || '查询状态失败');
    }

    return response.json();
  },
};

/**
 * 字幕管理 API
 */
export const subtitleApi = {
  /**
   * 获取字幕结果
   */
  async getSubtitle(taskId: string): Promise<SubtitleResponse> {
    const response = await fetch(`${API_BASE_URL}/subtitle/${taskId}`);

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || '获取字幕失败');
    }

    return response.json();
  },

  /**
   * 下载字幕文件
   */
  async download(taskId: string): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/download/${taskId}`);

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || '下载字幕失败');
    }

    // 获取文件名
    const contentDisposition = response.headers.get('content-disposition');
    let filename = 'subtitle.srt';
    if (contentDisposition) {
      const filenameMatch = contentDisposition.match(/filename="(.+)"/);
      if (filenameMatch) {
        filename = filenameMatch[1];
      }
    }

    // 下载文件
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
  },

  /**
   * 获取可用模型列表
   */
  async getModels(): Promise<ModelsResponse> {
    const response = await fetch(`${API_BASE_URL}/models`);

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || '获取模型列表失败');
    }

    return response.json();
  },
};

/**
 * 类型定义
 */
export interface UploadResponse {
  file_id: string;
  filename: string;
  file_size: number;
  duration?: number;
}

export interface TranscribeRequest {
  file_id: string;
  model: string;
  language?: string;
  use_gpu: boolean;
}

export interface TranscribeResponse {
  task_id: string;
  status: string;
}

export interface StatusResponse {
  task_id: string;
  status: string;
  progress: number;
  current_step: string;
  error?: string;
}

export interface SubtitleSegment {
  index: number;
  start: number;
  end: number;
  text: string;
}

export interface SubtitleResponse {
  task_id: string;
  model: string;
  language: string;
  segments: SubtitleSegment[];
}

export interface ModelInfo {
  name: string;
  size: string;
  languages: string[];
  downloaded: boolean;
}

export interface ModelsResponse {
  models: ModelInfo[];
}
