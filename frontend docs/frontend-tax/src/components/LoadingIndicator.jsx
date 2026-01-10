import { Bot } from 'lucide-react';
import { cn, getBgColor, getTextColor, getBorderColor } from '../utils/classNames';

const LoadingIndicator = ({ 
  message = "Searching tax reform documents...",
  isDarkMode = false 
}) => {
  return (
    <div className="flex gap-3 mb-6">
      <div className="w-10 h-10 bg-green-600 rounded-full flex items-center justify-center flex-shrink-0">
        <Bot className="w-6 h-6 text-white" />
      </div>

      <div className="flex flex-col max-w-3xl">
        <div className="flex items-center gap-2 mb-2">
          <span className={cn('text-sm font-medium', getTextColor(isDarkMode))}>
            Tax Assistant
          </span>
          <span className="text-xs text-yellow-600 flex items-center gap-1">
            <span className="animate-pulse">•</span> Thinking...
          </span>
        </div>

        <div className={cn(
          'rounded-2xl px-6 py-4 border',
          getBgColor(isDarkMode, 'bg-white', 'bg-gray-800'),
          getBorderColor(isDarkMode)
        )}>
          <p className={cn('text-sm flex items-center gap-2 mb-4', getTextColor(isDarkMode, 'text-gray-600', 'text-gray-400'))}>
            <span className="flex gap-1">
              <span className="w-2 h-2 bg-green-600 rounded-full animate-bounce"></span>
              <span className="w-2 h-2 bg-green-600 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></span>
              <span className="w-2 h-2 bg-green-600 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></span>
            </span>
            {message}
          </p>

          <div className="space-y-2">
            <div className={cn('h-4 rounded animate-pulse', getBgColor(isDarkMode, 'bg-gray-200', 'bg-gray-700'))}></div>
            <div className={cn('h-4 rounded animate-pulse w-5/6', getBgColor(isDarkMode, 'bg-gray-200', 'bg-gray-700'))}></div>
            <div className={cn('h-4 rounded animate-pulse w-4/6', getBgColor(isDarkMode, 'bg-gray-200', 'bg-gray-700'))}></div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoadingIndicator;