import React from 'react';
import { Bot } from 'lucide-react';

const LoadingIndicator = ({ message = "Analyzing Finance Act 2024 Database..." }) => {
  return (
    <div className="flex gap-3 mb-6">
      <div className="w-10 h-10 bg-green-600 rounded-full flex items-center justify-center flex-shrink-0">
        <Bot className="w-6 h-6 text-white" />
      </div>

      <div className="flex flex-col max-w-3xl">
        <div className="flex items-center gap-2 mb-2">
          <span className="text-sm font-medium text-gray-900">Tax Assistant</span>
          <span className="text-xs text-yellow-600 flex items-center gap-1">
            <span className="animate-pulse">●</span> Thinking...
          </span>
        </div>

        <div className="rounded-2xl px-6 py-4 bg-white border border-gray-200">
          <p className="text-sm text-gray-600 flex items-center gap-2 mb-4">
            <span className="flex gap-1">
              <span className="w-2 h-2 bg-green-600 rounded-full animate-bounce"></span>
              <span className="w-2 h-2 bg-green-600 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></span>
              <span className="w-2 h-2 bg-green-600 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></span>
            </span>
            {message}
          </p>

          {/* Skeleton Loading */}
          <div className="space-y-2">
            <div className="h-4 bg-gray-200 rounded animate-pulse"></div>
            <div className="h-4 bg-gray-200 rounded animate-pulse w-5/6"></div>
            <div className="h-4 bg-gray-200 rounded animate-pulse w-4/6"></div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoadingIndicator;