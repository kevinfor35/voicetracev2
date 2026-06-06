/**
 * 字幕浏览和编辑组件
 */
import React, { useState } from 'react';
import { SubtitleSegment } from '../api';
import { Edit2, Save, X, Clock } from 'lucide-react';

interface SubtitleViewerProps {
  segments: SubtitleSegment[];
  onSegmentsChange?: (segments: SubtitleSegment[]) => void;
}

export const SubtitleViewer: React.FC<SubtitleViewerProps> = ({
  segments,
  onSegmentsChange,
}) => {
  const [editingIndex, setEditingIndex] = useState<number | null>(null);
  const [editText, setEditText] = useState<string>('');

  const formatTime = (seconds: number): string => {
    const minutes = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const handleEdit = (index: number, text: string) => {
    setEditingIndex(index);
    setEditText(text);
  };

  const handleSave = () => {
    if (editingIndex !== null && onSegmentsChange) {
      const newSegments = segments.map((seg) =>
        seg.index === editingIndex ? { ...seg, text: editText } : seg
      );
      onSegmentsChange(newSegments);
    }
    setEditingIndex(null);
    setEditText('');
  };

  const handleCancel = () => {
    setEditingIndex(null);
    setEditText('');
  };

  return (
    <div className="space-y-3 max-h-[600px] overflow-y-auto">
      {segments.map((segment) => (
        <div
          key={segment.index}
          className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
        >
          <div className="flex items-start justify-between mb-2">
            <div className="flex items-center space-x-2">
              <span className="bg-blue-100 text-blue-700 text-xs font-medium px-2 py-1 rounded">
                #{segment.index}
              </span>
              <div className="flex items-center space-x-1 text-xs text-gray-500">
                <Clock className="w-3 h-3" />
                <span>
                  {formatTime(segment.start)} - {formatTime(segment.end)}
                </span>
              </div>
            </div>
            {editingIndex !== segment.index && onSegmentsChange && (
              <button
                onClick={() => handleEdit(segment.index, segment.text)}
                className="p-1 hover:bg-gray-100 rounded transition-colors"
              >
                <Edit2 className="w-4 h-4 text-gray-500" />
              </button>
            )}
          </div>

          {editingIndex === segment.index ? (
            <div className="space-y-2">
              <textarea
                value={editText}
                onChange={(e) => setEditText(e.target.value)}
                className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                rows={3}
              />
              <div className="flex justify-end space-x-2">
                <button
                  onClick={handleCancel}
                  className="flex items-center space-x-1 px-3 py-1 text-sm text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
                >
                  <X className="w-4 h-4" />
                  <span>取消</span>
                </button>
                <button
                  onClick={handleSave}
                  className="flex items-center space-x-1 px-3 py-1 text-sm text-white bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors"
                >
                  <Save className="w-4 h-4" />
                  <span>保存</span>
                </button>
              </div>
            </div>
          ) : (
            <p className="text-gray-800 leading-relaxed">{segment.text}</p>
          )}
        </div>
      ))}
    </div>
  );
};
