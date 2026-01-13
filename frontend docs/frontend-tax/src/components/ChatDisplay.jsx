import { useRef, useEffect } from 'react';
import { Bot, User, Copy, RefreshCw, Share2, ThumbsUp } from 'lucide-react';

const ChatDisplay = ({ messages, isLoading, isDarkMode = false }) => {
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  return (
    <div className="space-y-6">
      <div className="text-center">
        <span className={`text-xs px-3 py-1 rounded-full ${
          isDarkMode 
            ? 'text-gray-400 bg-gray-800' 
            : 'text-gray-500 bg-gray-200'
        }`}>
          Today, {new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </span>
      </div>

      {messages.length === 0 && !isLoading && (
        <div className="flex flex-col items-center justify-center py-20">
          <div className={`w-16 h-16 rounded-full flex items-center justify-center mb-4 ${
            isDarkMode ? 'bg-green-900/30' : 'bg-green-100'
          }`}>
            <Bot className="w-8 h-8 text-green-600" />
          </div>
          <h3 className={`text-xl font-semibold mb-2 ${
            isDarkMode ? 'text-white' : 'text-gray-900'
          }`}>
            Ask me anything about Nigeria's new tax laws
          </h3>
          <p className={`text-center max-w-md ${
            isDarkMode ? 'text-gray-400' : 'text-gray-600'
          }`}>
            I can help with VAT compliance, CIT rates, and exemption lists.
          </p>
        </div>
      )}

      {messages.map((msg, index) => (
        <div key={index} className={`flex gap-3 ${msg.isUser ? 'justify-end' : 'justify-start'}`}>
          {!msg.isUser && (
            <div className="w-10 h-10 bg-green-600 rounded-full flex items-center justify-center shrink-0">
              <Bot className="w-6 h-6 text-white" />
            </div>
          )}

          <div className={`flex flex-col ${msg.isUser ? 'items-end' : 'items-start'} max-w-3xl`}>
            {!msg.isUser && (
              <span className={`text-sm font-medium mb-2 ${
                isDarkMode ? 'text-white' : 'text-gray-900'
              }`}>
                Tax Assistant
              </span>
            )}
            
            {msg.isUser && (
              <span className={`text-xs mb-2 ${
                isDarkMode ? 'text-gray-400' : 'text-gray-500'
              }`}>
                You
              </span>
            )}

            <div className={`rounded-2xl px-6 py-4 ${
              msg.isUser 
                ? 'bg-green-600 text-white' 
                : isDarkMode
                  ? 'bg-gray-800 border border-gray-700'
                  : 'bg-white border border-gray-200'
            }`}>
              <p className={`whitespace-pre-wrap ${
                msg.isUser ? 'text-white' : isDarkMode ? 'text-gray-200' : 'text-gray-900'
              }`}>
                {msg.text}
              </p>

              {msg.source && !msg.isUser && (
                <div className={`mt-4 pt-4 ${
                  isDarkMode ? 'border-t border-gray-700' : 'border-t border-gray-200'
                }`}>
                  <div className="flex items-center gap-2 text-sm">
                    <span className={`font-semibold ${
                      isDarkMode ? 'text-white' : 'text-gray-900'
                    }`}>
                      SOURCE
                    </span>
                  </div>
                  <p className={`text-sm mt-2 ${
                    isDarkMode ? 'text-gray-400' : 'text-gray-600'
                  }`}>
                    {msg.source}
                  </p>
                </div>
              )}
            </div>

            {msg.showActions && !msg.isUser && (
              <div className="flex items-center gap-2 mt-2">
                <button className={`p-2 rounded-lg transition-colors group ${
                  isDarkMode ? 'hover:bg-gray-700' : 'hover:bg-gray-100'
                }`}>
                  <Copy className={`w-4 h-4 ${
                    isDarkMode 
                      ? 'text-gray-400 group-hover:text-gray-300' 
                      : 'text-gray-500 group-hover:text-gray-700'
                  }`} />
                </button>
                <button className={`p-2 rounded-lg transition-colors group ${
                  isDarkMode ? 'hover:bg-gray-700' : 'hover:bg-gray-100'
                }`}>
                  <RefreshCw className={`w-4 h-4 ${
                    isDarkMode 
                      ? 'text-gray-400 group-hover:text-gray-300' 
                      : 'text-gray-500 group-hover:text-gray-700'
                  }`} />
                </button>
                <button className={`p-2 rounded-lg transition-colors group ${
                  isDarkMode ? 'hover:bg-gray-700' : 'hover:bg-gray-100'
                }`}>
                  <Share2 className={`w-4 h-4 ${
                    isDarkMode 
                      ? 'text-gray-400 group-hover:text-gray-300' 
                      : 'text-gray-500 group-hover:text-gray-700'
                  }`} />
                </button>
                <button className={`p-2 rounded-lg transition-colors group ${
                  isDarkMode ? 'hover:bg-gray-700' : 'hover:bg-gray-100'
                }`}>
                  <ThumbsUp className={`w-4 h-4 ${
                    isDarkMode 
                      ? 'text-gray-400 group-hover:text-gray-300' 
                      : 'text-gray-500 group-hover:text-gray-700'
                  }`} />
                </button>
              </div>
            )}

            {msg.timestamp && (
              <span className={`text-xs mt-1 ${
                isDarkMode ? 'text-gray-500' : 'text-gray-400'
              }`}>
                {msg.timestamp}
              </span>
            )}
          </div>

          {msg.isUser && (
            <div className={`w-10 h-10 rounded-full flex items-center justify-center shrink-0 ${
              isDarkMode ? 'bg-gray-700' : 'bg-gray-300'
            }`}>
              <User className={`w-6 h-6 ${
                isDarkMode ? 'text-gray-400' : 'text-gray-600'
              }`} />
            </div>
          )}
        </div>
      ))}

      <div ref={messagesEndRef} />
    </div>
  );
};

export default ChatDisplay;