/**
 * 进度显示组件
 */
import React from 'react';
import { Loader, CheckCircle, XCircle, Clock } from 'lucide-react';
import { StatusResponse } from '../api';

interface ProgressDisplayProps {
  status: StatusResponse | null;
}

export const ProgressDisplay: React.FC<ProgressDisplayProps> = ({ status }) => {
  if (!status) {
    return null;
  }

  const getStatusIcon = () => {
    switch (status.status) {
      case 'pending':
        return <Clock className="w-6 h-6 text-yellow-500" />;
      case 'processing':
        return <Loader className="w-6 h-6 text-blue-500 animate-spin" />;
      case 'completed':
        return <CheckCircle className="w-6 h-6 text-green-500" />;
      case 'failed':
        return <XCircle className="w-6 h-6 text-red-500" />;
      default:
        return <Clock className="w-6 h-6 text-gray-500" />;
    }
  };

  const getStatusColor = () => {
    switch (status.status) {
      case 'pending':
        return 'bg-yellow-50 border-yellow-200';
      case 'processing':
        return 'bg-blue-50 border-blue-200';
      case 'completed':
        return 'bg-green-50 border-green-200';
      case 'failed':
        return 'bg-red-50 border-red-200';
      default:
        return 'bg-gray-50 border-gray-200';
    }
  };

  const getStatusText = () => {
    switch (status.status) {
      case 'pending':
        return '等待处理';
      case 'processing':
        return '处理中';
      case 'completed':
        return '已完成';
      case 'failed':
        return '失败';
      default:
        return '未知状态';
    }
  };

  return (
    <div className={`border rounded-lg p-6 ${getStatusColor()}`}>
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-3">
          {getStatusIcon()}
          <div>
            <h3 className="text-lg font-semibold text-gray-900">
              {getStatusText()}
            </h3>
            <p className="text-sm text-gray-600">{status.current_step}</p>
          </div>
        </div>
        <div className="text-right">
          <p className="text-2xl font-bold text-gray-900">{status.progress}%</p>
        </div>
      </div>

      {/* 进度条 */}
      <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
        <div
          className={`
            h-full rounded-full transition-all duration-500
            ${status.status === 'processing' ? 'bg-blue-500' : ''}
            ${status.status === 'completed' ? 'bg-green-500' : ''}
            ${status.status === 'failed' ? 'bg-red-500' : ''}
            ${status.status === 'pending' ? 'bg-yellow-500' : ''}
          `}
          style={{ width: `${status.progress}%` }}
        />
      </div>

      {/* 错误信息 */}
      {status.error && (
        <div className="mt-4 p-3 bg-red-100 border border-red-300 rounded-lg">
          <p className="text-sm text-red-700">
            <strong>错误:</strong> {status.error}
          </p>
        </div>
      )}

      {/* 处理步骤说明 */}
      {status.status === 'processing' && (
        <div className="mt-4 space-y-2">
          <div className="flex items-center space-x-2 text-sm text-gray-600">
            <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse" />
            <span>正在处理音频...</span>
          </div>
          <p className="text-xs text-gray-500">
            请勿关闭页面，处理完成后将自动显示结果
          </p>
        </div>
      )}
    </div>
  );
};
