/**
 * 测试组件
 */
import React from 'react';

const TestComponent: React.FC = () => {
  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold">测试组件</h1>
      <p className="mt-2">如果你能看到这个，说明 React 正常工作</p>
    </div>
  );
};

export default TestComponent;
