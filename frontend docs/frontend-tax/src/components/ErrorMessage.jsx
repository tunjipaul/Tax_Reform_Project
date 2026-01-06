import { Bot, AlertTriangle, RefreshCw } from 'lucide-react';

const ErrorMessage = ({ 
  message = "We encountered a network issue while retrieving the latest tax exemption data. Please check your connection and try again.",
  onRetry,
  isDarkMode = false 
}) => {
  return (
    <div className="flex gap-3 mb-6">
      <div className="w-10 h-10 bg-green-600 rounded-full flex items-center justify-center flex-shrink-0">
        <Bot className="w-6 h-6 text-white" />
      </div>

      <div className="flex flex-col max-w-3xl">
        <div className="flex items-center gap-2 mb-2">
          <span className={`text-sm font-medium ${
            isDarkMode ? 'text-white' : 'text-gray-900'
          }`}>
            Tax Assistant
          </span>
          <span className="text-xs text-red-600 flex items-center gap-1 uppercase font-semibold">
            ERROR
          </span>
        </div>

        <div className={`rounded-2xl px-6 py-4 border-l-4 border-red-500 ${
          isDarkMode ? 'bg-red-900/20' : 'bg-red-50'
        }`}>
          <div className="flex items-start gap-2">
            <AlertTriangle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <p className={`font-semibold mb-1 ${
                isDarkMode ? 'text-red-400' : 'text-red-900'
              }`}>
                Response Interrupted
              </p>
              <p className={`text-sm ${
                isDarkMode ? 'text-red-300' : 'text-red-700'
              }`}>
                {message}
              </p>
              
              {onRetry && (
                <button 
                  onClick={onRetry}
                  className={`mt-3 px-4 py-2 border rounded-lg text-sm font-medium transition-colors flex items-center gap-2 ${
                    isDarkMode
                      ? 'bg-gray-800 border-red-500 text-red-400 hover:bg-gray-700'
                      : 'bg-white border-red-300 text-red-700 hover:bg-red-50'
                  }`}
                >
                  <RefreshCw className="w-4 h-4" />
                  Try Again
                </button>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ErrorMessage;