/**
 * 参数配置组件
 */
import React, { useState, useEffect } from 'react';
import { Settings, Cpu, Globe, Zap } from 'lucide-react';
import { subtitleApi, ModelInfo } from '../api';

interface ConfigPanelProps {
  onConfigChange: (config: Config) => void;
  config: Config;
}

export interface Config {
  model: string;
  language: string;
  useGpu: boolean;
}

export const ConfigPanel: React.FC<ConfigPanelProps> = ({
  onConfigChange,
  config,
}) => {
  const [models, setModels] = useState<ModelInfo[]>([]);
  const [gpuAvailable, setGpuAvailable] = useState(false);
  const [loading, setLoading] = useState(true);

  // 语言选项
  const languages = [
    { code: 'auto', name: '自动检测' },
    { code: 'zh', name: '中文' },
    { code: 'en', name: '英文' },
    { code: 'ja', name: '日语' },
    { code: 'ko', name: '韩语' },
    { code: 'fr', name: '法语' },
    { code: 'de', name: '德语' },
    { code: 'es', name: '西班牙语' },
    { code: 'ru', name: '俄语' },
    { code: 'it', name: '意大利语' },
    { code: 'pt', name: '葡萄牙语' },
  ];

  useEffect(() => {
    loadModels();
    checkGpu();
  }, []);

  const loadModels = async () => {
    try {
      const response = await subtitleApi.getModels();
      setModels(response.models);
    } catch (error) {
      console.error('加载模型列表失败:', error);
    } finally {
      setLoading(false);
    }
  };

  const checkGpu = async () => {
    try {
      // 简单的 GPU 检测
      // 实际应该调用后端 API 检测
      setGpuAvailable(false);
    } catch (error) {
      console.error('检测 GPU 失败:', error);
    }
  };

  const handleModelChange = (model: string) => {
    onConfigChange({ ...config, model });
  };

  const handleLanguageChange = (language: string) => {
    onConfigChange({ ...config, language });
  };

  const handleGpuToggle = () => {
    if (!gpuAvailable) {
      alert('GPU 不可用，请检查 CUDA 环境');
      return;
    }
    onConfigChange({ ...config, useGpu: !config.useGpu });
  };

  if (loading) {
    return (
      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <p className="text-gray-500">加载配置中...</p>
      </div>
    );
  }

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-6 space-y-6">
      <div className="flex items-center space-x-2">
        <Settings className="w-5 h-5 text-blue-600" />
        <h3 className="text-lg font-semibold text-gray-900">转录参数配置</h3>
      </div>

      {/* 模型选择 */}
      <div className="space-y-2">
        <label className="flex items-center space-x-2 text-sm font-medium text-gray-700">
          <Zap className="w-4 h-4" />
          <span>选择模型</span>
        </label>
        <div className="grid grid-cols-1 gap-2">
          {models.map((model) => (
            <button
              key={model.name}
              onClick={() => handleModelChange(model.name)}
              className={`
                p-3 rounded-lg border text-left transition-all
                ${config.model === model.name
                  ? 'border-blue-500 bg-blue-50 text-blue-700'
                  : 'border-gray-200 hover:border-gray-300 bg-white text-gray-700'
                }
              `}
            >
              <div className="flex justify-between items-center">
                <div>
                  <p className="font-medium capitalize">{model.name}</p>
                  <p className="text-sm text-gray-500">大小: {model.size}</p>
                </div>
                {model.downloaded ? (
                  <span className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded">
                    已下载
                  </span>
                ) : (
                  <span className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded">
                    未下载
                  </span>
                )}
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* 语言选择 */}
      <div className="space-y-2">
        <label className="flex items-center space-x-2 text-sm font-medium text-gray-700">
          <Globe className="w-4 h-4" />
          <span>选择语言</span>
        </label>
        <select
          value={config.language}
          onChange={(e) => handleLanguageChange(e.target.value)}
          className="w-full p-3 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        >
          {languages.map((lang) => (
            <option key={lang.code} value={lang.code}>
              {lang.name}
            </option>
          ))}
        </select>
      </div>

      {/* GPU 加速 */}
      <div className="space-y-2">
        <label className="flex items-center space-x-2 text-sm font-medium text-gray-700">
          <Cpu className="w-4 h-4" />
          <span>GPU 加速</span>
        </label>
        <button
          onClick={handleGpuToggle}
          className={`
            w-full p-3 rounded-lg border transition-all
            ${config.useGpu
              ? 'border-blue-500 bg-blue-50'
              : 'border-gray-200 bg-white'
            }
          `}
        >
          <div className="flex justify-between items-center">
            <div className="flex items-center space-x-2">
              <div
                className={`
                  w-12 h-6 rounded-full transition-all relative
                  ${config.useGpu ? 'bg-blue-500' : 'bg-gray-300'}
                `}
              >
                <div
                  className={`
                    absolute top-1 w-4 h-4 rounded-full bg-white transition-all
                    ${config.useGpu ? 'left-7' : 'left-1'}
                  `}
                />
              </div>
              <span className={config.useGpu ? 'text-blue-700' : 'text-gray-700'}>
                {config.useGpu ? '已启用' : '未启用'}
              </span>
            </div>
            {!gpuAvailable && (
              <span className="text-xs text-red-600">GPU 不可用</span>
            )}
          </div>
        </button>
        {!gpuAvailable && (
          <p className="text-xs text-gray-500">
            提示: 需要安装 CUDA 环境才能使用 GPU 加速
          </p>
        )}
      </div>
    </div>
  );
};
