import React, { useState } from 'react';
import { Send, ArrowUp, Paperclip, Type, Mic, Plus } from 'lucide-react';

const ChatInput = ({ 
  onSend, 
  placeholder = "Ask a question about the 2024 Tax Reform...",
  disabled = false,
  variant = 'default',
  isDarkMode = false
}) => {
  const [message, setMessage] = useState('');
  const [charCount, setCharCount] = useState(0);
  const maxChars = 2000;

  const handleSubmit = (e) => {
    e.preventDefault();
    if (message.trim() && !disabled) {
      onSend(message);
      setMessage('');
      setCharCount(0);
    }
  };

  const handleChange = (e) => {
    const value = e.target.value;
    if (value.length <= maxChars) {
      setMessage(value);
      setCharCount(value.length);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <div className={`px-6 pb-6 ${isDarkMode ? 'bg-gray-900' : 'bg-gray-50'}`}>
      <div className="max-w-4xl mx-auto">
        <form onSubmit={handleSubmit} className={`rounded-xl shadow-sm ${
          isDarkMode 
            ? 'bg-gray-800 border border-gray-700' 
            : 'bg-white border border-gray-200'
        }`}>
          {/* Input Area */}
          <div className="relative">
            {variant === 'with-attachments' && (
              <button 
                type="button"
                className={`absolute left-4 top-4 p-2 rounded-lg transition-colors ${
                  isDarkMode ? 'hover:bg-gray-700' : 'hover:bg-gray-100'
                }`}
              >
                <Plus className={`w-5 h-5 ${isDarkMode ? 'text-gray-400' : 'text-gray-400'}`} />
              </button>
            )}
            
            <textarea
              value={message}
              onChange={handleChange}
              onKeyDown={handleKeyDown}
              placeholder={placeholder}
              disabled={disabled}
              rows={1}
              className={`w-full px-6 py-4 bg-transparent focus:outline-none resize-none ${
                variant === 'with-attachments' ? 'pl-14' : ''
              } ${
                isDarkMode 
                  ? 'text-gray-200 placeholder-gray-500' 
                  : 'text-gray-900 placeholder-gray-400'
              }`}
              style={{ minHeight: '60px', maxHeight: '200px' }}
            />
          </div>

          {/* Bottom Bar */}
          <div className="flex items-center justify-between px-6 pb-4 pt-2">
            <div className="flex items-center gap-2">
              {variant === 'advanced' && (
                <>
                  <button 
                    type="button"
                    className={`p-2 rounded-lg transition-colors ${
                      isDarkMode ? 'hover:bg-gray-700' : 'hover:bg-gray-100'
                    }`}
                    title="Attach file"
                  >
                    <Paperclip className={`w-5 h-5 ${
                      isDarkMode ? 'text-gray-400' : 'text-gray-400'
                    }`} />
                  </button>
                  <button 
                    type="button"
                    className={`p-2 rounded-lg transition-colors ${
                      isDarkMode ? 'hover:bg-gray-700' : 'hover:bg-gray-100'
                    }`}
                    title="Text formatting"
                  >
                    <Type className={`w-5 h-5 ${
                      isDarkMode ? 'text-gray-400' : 'text-gray-400'
                    }`} />
                  </button>
                  <button 
                    type="button"
                    className={`p-2 rounded-lg transition-colors ${
                      isDarkMode ? 'hover:bg-gray-700' : 'hover:bg-gray-100'
                    }`}
                    title="Voice input"
                  >
                    <Mic className={`w-5 h-5 ${
                      isDarkMode ? 'text-gray-400' : 'text-gray-400'
                    }`} />
                  </button>
                </>
              )}
              
              <p className={`text-xs ${isDarkMode ? 'text-gray-500' : 'text-gray-500'}`}>
                {variant === 'simple' 
                  ? 'AI can make mistakes. Please verify important information with official gazetted documents.'
                  : `${charCount} / ${maxChars}`
                }
              </p>
            </div>

            <button
              type="submit"
              disabled={!message.trim() || disabled}
              className={`w-10 h-10 rounded-lg flex items-center justify-center transition-colors ${
                message.trim() && !disabled
                  ? 'bg-green-600 hover:bg-green-700' 
                  : isDarkMode
                    ? 'bg-gray-700 cursor-not-allowed'
                    : 'bg-gray-300 cursor-not-allowed'
              }`}
            >
              {variant === 'arrow' ? (
                <ArrowUp className="w-5 h-5 text-white" />
              ) : (
                <Send className="w-5 h-5 text-white" />
              )}
            </button>
          </div>
        </form>

      
        {variant !== 'simple' && (
          <p className={`text-xs text-center mt-3 ${
            isDarkMode ? 'text-gray-500' : 'text-gray-500'
          }`}>
            AI-generated responses. Please consult a professional for critical tax advice.
          </p>
        )}
      </div>
    </div>
  );
};

export default ChatInput;