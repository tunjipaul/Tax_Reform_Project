import { Bot } from 'lucide-react';

const LoadingIndicator = ({ 
  message = "Analyzing Finance Act 2024 Database...",
  isDarkMode = false 
}) => {
  return (
    <div className="flex gap-3 mb-6">
      <div className="w-10 h-10 bg-green-600 rounded-full flex items-center justify-center flex-shrink-0">
        <Bot className="w-6 h-6 text-white" />
      </div>

      <div className="flex flex-col max-w-3xl">
        <div className="flex items-center gap-2 mb-2">
          <span className={`text-sm font-medium ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>
            Tax Assistant
          </span>
          <span className="text-xs text-yellow-600 flex items-center gap-1">
            <span className="animate-pulse">•</span> Thinking...
          </span>
        </div>

        <div className={`rounded-2xl px-6 py-4 border ${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'}`}>
          <p className={`text-sm flex items-center gap-2 mb-4 ${isDarkMode ? 'text-gray-400' : 'text-gray-600'}`}>
            <span className="flex gap-1">
              <span className="w-2 h-2 bg-green-600 rounded-full animate-bounce"></span>
              <span className="w-2 h-2 bg-green-600 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></span>
              <span className="w-2 h-2 bg-green-600 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></span>
            </span>
            {message}
          </p>

          <div className="space-y-2">
            <div className={`h-4 rounded animate-pulse ${isDarkMode ? 'bg-gray-700' : 'bg-gray-200'}`}></div>
            <div className={`h-4 rounded animate-pulse w-5/6 ${isDarkMode ? 'bg-gray-700' : 'bg-gray-200'}`}></div>
            <div className={`h-4 rounded animate-pulse w-4/6 ${isDarkMode ? 'bg-gray-700' : 'bg-gray-200'}`}></div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoadingIndicator;