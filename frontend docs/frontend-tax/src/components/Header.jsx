import React from 'react';
import { Building2, Moon, Sun, Plus, User, Menu } from 'lucide-react';

const Header = ({ 
  variant = 'default', 
  onNewChat, 
  showNewChat = true, 
  onDarkModeToggle, 
  isDarkMode = false,
  onMenuToggle // New prop for mobile menu
}) => {
  // Variant styles with dark mode support
  const getHeaderStyles = () => {
    if (variant === 'primary') return 'bg-green-700 text-white';
    if (variant === 'simple') return isDarkMode ? 'bg-gray-800 border-b border-gray-700' : 'bg-white border-b border-gray-200';
    return isDarkMode ? 'bg-gray-800 border-b border-gray-700' : 'bg-white border-b border-gray-200';
  };

  return (
    <header className={`px-4 sm:px-6 py-4 flex items-center justify-between ${getHeaderStyles()}`}>
      <div className="flex items-center gap-3">
        {/* Mobile Hamburger Menu */}
        <button
          onClick={onMenuToggle}
          className={`md:hidden p-2 rounded-lg transition-colors ${
            isDarkMode ? 'hover:bg-gray-700' : 'hover:bg-gray-100'
          }`}
          aria-label="Open menu"
        >
          <Menu className={`w-6 h-6 ${isDarkMode ? 'text-gray-300' : 'text-gray-600'}`} />
        </button>

        {/* Logo and Title */}
        <div className="flex items-center gap-3">
          <div className={`w-10 h-10 ${variant === 'primary' ? 'bg-white' : 'bg-green-600'} rounded-lg flex items-center justify-center`}>
            <Building2 className={`w-6 h-6 ${variant === 'primary' ? 'text-green-600' : 'text-white'}`} />
          </div>
          <div className="hidden sm:block">
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
      </div>
      
      <div className="flex items-center gap-2 sm:gap-3">
        {variant === 'default' && (
          <>
            {/* Dark Mode Toggle */}
            <button 
              onClick={onDarkModeToggle}
              className={`p-2 rounded-lg transition-colors ${
                isDarkMode ? 'hover:bg-gray-700' : 'hover:bg-gray-100'
              }`}
              aria-label={isDarkMode ? "Switch to light mode" : "Switch to dark mode"}
              title={isDarkMode ? "Switch to light mode" : "Switch to dark mode"}
            >
              {isDarkMode ? (
                <Sun className="w-5 h-5 text-gray-300" />
              ) : (
                <Moon className="w-5 h-5 text-gray-600" />
              )}
            </button>

            {/* New Chat Button - Hidden on small mobile */}
            {showNewChat && (
              <button 
                onClick={onNewChat}
                className="hidden sm:flex px-4 py-2 bg-green-600 text-white rounded-lg items-center gap-2 hover:bg-green-700 transition-colors font-medium"
                aria-label="Start new chat"
              >
                <Plus className="w-5 h-5" />
                <span className="hidden md:inline">New Chat</span>
              </button>
            )}

            {/* User Profile */}
            <button 
              className={`p-2 rounded-lg transition-colors ${
                isDarkMode ? 'hover:bg-gray-700' : 'hover:bg-gray-100'
              }`}
              aria-label="User profile"
            >
              <User className={`w-5 h-5 ${isDarkMode ? 'text-gray-300' : 'text-gray-600'}`} />
            </button>
          </>
        )}
      </div>
    </header>
  );
};

export default Header;