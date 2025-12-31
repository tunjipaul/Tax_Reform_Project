import React, { useEffect } from 'react';
import { Building2, Moon, Sun, Plus, User, Settings, Bell, HelpCircle } from 'lucide-react';

const Header = ({ variant = 'default', onNewChat, showNewChat = true, onDarkModeToggle, isDarkMode = false }) => {

  useEffect(() => {
    if (isDarkMode) {
      document.documentElement.classList.add('dark');
      document.documentElement.style.colorScheme = 'dark';
    } else {
      document.documentElement.classList.remove('dark');
      document.documentElement.style.colorScheme = 'light';
    }
  }, [isDarkMode]);
  
  const toggleDarkMode = () => {
    const newDarkMode = !isDarkMode;
    localStorage.setItem('darkMode', newDarkMode.toString());
    if (newDarkMode) {
      document.documentElement.classList.add('dark');
      document.documentElement.style.colorScheme = 'dark';
      document.body.style.backgroundColor = '#111827';
      document.body.style.color = '#ffffff';
    } else {
      document.documentElement.classList.remove('dark');
      document.documentElement.style.colorScheme = 'light';

      document.body.style.backgroundColor = '#f9fafb';
      document.body.style.color = '#111827';
    }
    
    // Trigger re-render by forcing a style recalculation
    document.documentElement.offsetHeight;
    if (onDarkModeToggle) {
      onDarkModeToggle(newDarkMode);
    }
  };

  const getHeaderStyles = () => {
    if (variant === 'primary') return 'bg-green-700 text-white';
    if (variant === 'simple') return isDarkMode ? 'bg-gray-800 border-b border-gray-700' : 'bg-white border-b border-gray-200';
    return isDarkMode ? 'bg-gray-800 border-b border-gray-700' : 'bg-white border-b border-gray-200';
  };

  return (
    <header className={`px-6 py-4 flex items-center justify-between ${getHeaderStyles()}`}>
      <div className="flex items-center gap-3">
        <div className={`w-10 h-10 ${variant === 'primary' ? 'bg-white' : 'bg-green-600'} rounded-lg flex items-center justify-center`}>
          <Building2 className={`w-6 h-6 ${variant === 'primary' ? 'text-green-600' : 'text-white'}`} />
        </div>
        <div>
          <h1 className={`text-xl font-semibold ${
            variant === 'primary' ? 'text-white' : isDarkMode ? 'text-white' : 'text-gray-900'
          }`}>
            Nigeria Tax Reform Assistant
          </h1>
          {variant === 'simple' && (
            <p className={`text-sm ${isDarkMode ? 'text-gray-400' : 'text-gray-500'}`}>
              Powered by FIRS Guidelines
            </p>
          )}
        </div>
      </div>
      
      <div className="flex items-center gap-3">
        {variant === 'default' && (
          <>
            <button 
              onClick={toggleDarkMode}
              className={`p-2 rounded-lg transition-colors ${
                isDarkMode ? 'hover:bg-gray-700' : 'hover:bg-gray-100'
              }`}
              title={isDarkMode ? "Switch to light mode" : "Switch to dark mode"}
            >
              {isDarkMode ? (
                <Sun className={`w-5 h-5 ${isDarkMode ? 'text-gray-300' : 'text-gray-600'}`} />
              ) : (
                <Moon className={`w-5 h-5 ${isDarkMode ? 'text-gray-300' : 'text-gray-600'}`} />
              )}
            </button>

            {showNewChat && (
              <button 
                onClick={onNewChat}
                className="px-4 py-2 bg-green-600 text-white rounded-lg flex items-center gap-2 hover:bg-green-700 transition-colors font-medium"
              >
                <Plus className="w-5 h-5" />
                New Chat
              </button>
            )}

            {/* User Profile */}
            <button className={`p-2 rounded-lg transition-colors ${
              isDarkMode ? 'hover:bg-gray-700' : 'hover:bg-gray-100'
            }`}>
              <User className={`w-5 h-5 ${isDarkMode ? 'text-gray-300' : 'text-gray-600'}`} />
            </button>
          </>
        )}
        
        {variant === 'simple' && (
          <>
            <button className={`p-2 rounded-lg transition-colors ${
              isDarkMode ? 'hover:bg-gray-700' : 'hover:bg-gray-100'
            }`}>
              <Settings className={`w-5 h-5 ${isDarkMode ? 'text-gray-300' : 'text-gray-600'}`} />
            </button>
            <button className={`p-2 rounded-lg transition-colors ${
              isDarkMode ? 'hover:bg-gray-700' : 'hover:bg-gray-100'
            }`}>
              <HelpCircle className={`w-5 h-5 ${isDarkMode ? 'text-gray-300' : 'text-gray-600'}`} />
            </button>
          </>
        )}

        {variant === 'primary' && (
          <>
            <button className="p-2 hover:bg-green-600 rounded-lg transition-colors">
              <Bell className="w-5 h-5 text-white" />
            </button>
            <button className="p-2 hover:bg-green-600 rounded-lg transition-colors">
              <HelpCircle className="w-5 h-5 text-white" />
            </button>
          </>
        )}
      </div>
    </header>
  );
};

export default Header;