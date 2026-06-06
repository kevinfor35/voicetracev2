/**
 * 主页面组件
 */
import React, { useState, useEffect } from 'react';
import { FileUpload } from '../components/FileUpload';
import { ConfigPanel, Config } from '../components/ConfigPanel';
import { ProgressDisplay } from '../components/ProgressDisplay';
import { SubtitleViewer } from '../components/SubtitleViewer';
import {
  uploadApi,
  transcribeApi,
  subtitleApi,
  StatusResponse,
  SubtitleSegment,
} from '../api';
import { Upload as UploadIcon, Download, RotateCcw } from 'lucide-react';

const Home: React.FC = () => {
  // 状态管理
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [config, setConfig] = useState<Config>({
    model: 'base',
    language: 'auto',
    useGpu: false,
  });
  const [taskId, setTaskId] = useState<string | null>(null);
  const [status, setStatus] = useState<StatusResponse | null>(null);
  const [segments, setSegments] = useState<SubtitleSegment[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // 轮询任务状态
  useEffect(() => {
    if (!taskId || status?.status === 'completed' || status?.status === 'failed') {
      return;
    }

    const interval = setInterval(async () => {
      try {
        const statusResponse = await transcribeApi.getStatus(taskId);
        setStatus(statusResponse);

        // 如果完成，获取字幕结果
        if (statusResponse.status === 'completed') {
          const subtitleResponse = await subtitleApi.getSubtitle(taskId);
          setSegments(subtitleResponse.segments);
        }
      } catch (err) {
        console.error('查询状态失败:', err);
      }
    }, 1000);

    return () => clearInterval(interval);
  }, [taskId, status?.status]);

  // 处理文件选择
  const handleFileSelect = (file: File) => {
    setSelectedFile(file);
    setError(null);
    // 重置状态
    setTaskId(null);
    setStatus(null);
    setSegments([]);
  };

  // 处理文件移除
  const handleFileRemove = () => {
    setSelectedFile(null);
    setTaskId(null);
    setStatus(null);
    setSegments([]);
    setError(null);
  };

  // 开始转录
  const handleStartTranscribe = async () => {
    if (!selectedFile) {
      setError('请先选择文件');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // 上传文件
      const uploadResponse = await uploadApi.upload(selectedFile);

      // 启动转录任务
      const transcribeResponse = await transcribeApi.start({
        file_id: uploadResponse.file_id,
        model: config.model,
        language: config.language === 'auto' ? undefined : config.language,
        use_gpu: config.useGpu,
      });

      setTaskId(transcribeResponse.task_id);
      setStatus({
        task_id: transcribeResponse.task_id,
        status: transcribeResponse.status,
        progress: 0,
        current_step: '初始化',
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : '启动转录失败');
    } finally {
      setLoading(false);
    }
  };

  // 下载字幕
  const handleDownload = async () => {
    if (!taskId) return;

    try {
      await subtitleApi.download(taskId);
    } catch (err) {
      setError(err instanceof Error ? err.message : '下载字幕失败');
    }
  };

  // 重置
  const handleReset = () => {
    setSelectedFile(null);
    setTaskId(null);
    setStatus(null);
    setSegments([]);
    setError(null);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* 顶部导航栏 */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center">
                <UploadIcon className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">VoiceTrace</h1>
                <p className="text-sm text-gray-500">智能语音转字幕</p>
              </div>
            </div>
            {segments.length > 0 && (
              <button
                onClick={handleReset}
                className="flex items-center space-x-2 px-4 py-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <RotateCcw className="w-4 h-4" />
                <span>重新开始</span>
              </button>
            )}
          </div>
        </div>
      </header>

      {/* 主要内容 */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* 左侧：文件上传和配置 */}
          <div className="lg:col-span-1 space-y-6">
            {/* 文件上传 */}
            <div className="bg-white border border-gray-200 rounded-lg p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">
                上传文件
              </h2>
              <FileUpload
                onFileSelect={handleFileSelect}
                selectedFile={selectedFile}
                onFileRemove={handleFileRemove}
              />
            </div>

            {/* 参数配置 */}
            <ConfigPanel onConfigChange={setConfig} config={config} />

            {/* 开始按钮 */}
            {selectedFile && !taskId && (
              <button
                onClick={handleStartTranscribe}
                disabled={loading}
                className={`
                  w-full py-3 rounded-lg font-medium transition-all
                  ${loading
                    ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                    : 'bg-blue-600 text-white hover:bg-blue-700'
                  }
                `}
              >
                {loading ? '处理中...' : '开始转录'}
              </button>
            )}

            {/* 错误提示 */}
            {error && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                <p className="text-sm text-red-700">{error}</p>
              </div>
            )}
          </div>

          {/* 右侧：进度和结果 */}
          <div className="lg:col-span-2 space-y-6">
            {/* 进度显示 */}
            {status && !segments.length && <ProgressDisplay status={status} />}

            {/* 字幕浏览 */}
            {segments.length > 0 && (
              <div className="bg-white border border-gray-200 rounded-lg p-6">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-lg font-semibold text-gray-900">
                    字幕结果 ({segments.length} 条)
                  </h2>
                  <button
                    onClick={handleDownload}
                    className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                  >
                    <Download className="w-4 h-4" />
                    <span>下载 SRT</span>
                  </button>
                </div>
                <SubtitleViewer segments={segments} />
              </div>
            )}

            {/* 空状态 */}
            {!status && !segments.length && (
              <div className="bg-white border border-gray-200 rounded-lg p-12">
                <div className="text-center">
                  <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <UploadIcon className="w-8 h-8 text-gray-400" />
                  </div>
                  <h3 className="text-lg font-medium text-gray-900 mb-2">
                    开始使用 VoiceTrace
                  </h3>
                  <p className="text-gray-500">
                    上传音视频文件，选择转录参数，即可开始转录
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
};

export default Home;
