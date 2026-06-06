/**
 * 参数配置组件
 * 
 * 说明：
 * - 语言检测默认使用自动检测，无需手动选择
 * - distil 模型仅支持英语，不支持多语言
 * - 推荐使用 large-v3-turbo 进行多语言快速转录
 */
import React, { useState, useEffect } from 'react';
import { Settings, Zap, AlertTriangle, CheckCircle } from 'lucide-react';
import { subtitleApi, ModelInfo } from '../api';

interface ConfigPanelProps {
  onConfigChange: (config: Config) => void;
  config: Config;
}

export interface Config {
  model: string;
  language: string; // 始终为 'auto'，自动检测
}

export const ConfigPanel: React.FC<ConfigPanelProps> = ({
  onConfigChange,
  config,
}) => {
  const [models, setModels] = useState<ModelInfo[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadModels();
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

  const handleModelChange = (model: string) => {
    // 语言始终使用自动检测
    onConfigChange({ ...config, model, language: 'auto' });
  };

  // 判断模型是否支持多语言
  const isMultilingualModel = (modelName: string): boolean => {
    // .en 后缀和 distil 前缀的模型仅支持英语
    if (modelName.endsWith('.en')) return false;
    if (modelName.startsWith('distil-')) return false;
    return true;
  };

  // 获取模型推荐标签
  const getModelBadge = (modelName: string): { text: string; color: string } | null => {
    if (modelName === 'large-v3-turbo') {
      return { text: '推荐', color: 'bg-purple-100 text-purple-700' };
    }
    if (modelName === 'base') {
      return { text: '默认', color: 'bg-blue-100 text-blue-700' };
    }
    if (modelName.startsWith('distil-')) {
      return { text: '仅英语', color: 'bg-orange-100 text-orange-700' };
    }
    if (modelName.endsWith('.en')) {
      return { text: '仅英语', color: 'bg-orange-100 text-orange-700' };
    }
    return null;
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
        
        {/* 模型说明 */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 mb-3">
          <p className="text-sm text-blue-700">
            <strong>提示：</strong>语言检测默认使用自动识别，无需手动选择。
          </p>
          <p className="text-xs text-blue-600 mt-1">
            • <strong>large-v3-turbo</strong>：多语言+快速，性价比最高<br/>
            • <strong>base/tiny</strong>：速度快，语言检测准确<br/>
            • <strong>distil-*</strong>：仅支持英语！
          </p>
        </div>

        <div className="grid grid-cols-1 gap-2 max-h-96 overflow-y-auto">
          {models.map((model) => {
            const isMultilingual = isMultilingualModel(model.name);
            const badge = getModelBadge(model.name);
            
            return (
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
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <p className="font-medium capitalize">{model.name}</p>
                      {badge && (
                        <span className={`text-xs px-2 py-0.5 rounded ${badge.color}`}>
                          {badge.text}
                        </span>
                      )}
                    </div>
                    <p className="text-sm text-gray-500 mt-1">
                      大小: {model.size} 
                      {isMultilingual ? ' • 多语言' : ' • 仅英语'}
                    </p>
                  </div>
                  <div className="flex items-center">
                    {model.downloaded ? (
                      <CheckCircle className="w-5 h-5 text-green-500" />
                    ) : (
                      <span className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded">
                        未下载
                      </span>
                    )}
                  </div>
                </div>
                
                {/* 非多语言模型警告 */}
                {!isMultilingual && config.model === model.name && (
                  <div className="mt-2 flex items-center gap-1 text-orange-600 text-xs">
                    <AlertTriangle className="w-3 h-3" />
                    <span>此模型仅支持英语转录，非英语音频将输出英文</span>
                  </div>
                )}
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
};
