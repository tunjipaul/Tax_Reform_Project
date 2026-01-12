import { Building2, Moon, Sun, Plus, User, Menu } from 'lucide-react';
import { cn, getBgColor, getTextColor, getBorderColor, getHoverBg } from '../utils/classNames';

const Header = ({ 
  variant = 'default', 
  onNewChat, 
  showNewChat = true, 
  onDarkModeToggle, 
  isDarkMode = false,
  onMenuToggle
}) => {
  const getHeaderStyles = () => {
    if (variant === 'primary') return 'bg-green-700 text-white';
    return cn(
      getBgColor(isDarkMode, 'bg-white', 'bg-gray-800'),
      'border-b',
      getBorderColor(isDarkMode)
    );
  };

  return (
    <header className={cn('px-4 sm:px-6 py-4 flex items-center justify-between', getHeaderStyles())}>
      <div className="flex items-center gap-3">
        <button
          onClick={onMenuToggle}
          className={cn('md:hidden p-2 rounded-lg transition-colors', getHoverBg(isDarkMode))}
          aria-label="Open menu"
        >
          <Menu className={cn('w-6 h-6', getTextColor(isDarkMode, 'text-gray-600', 'text-gray-300'))} />
        </button>

        <div className="flex items-center gap-3">
          <div className={cn(
            'w-10 h-10 rounded-lg flex items-center justify-center',
            variant === 'primary' ? 'bg-white' : 'bg-green-600'
          )}>
            <Building2 className={cn('w-6 h-6', variant === 'primary' ? 'text-green-600' : 'text-white')} />
          </div>
          <div className="hidden sm:block">
            <h1 className={cn(
              'text-xl font-semibold',
              variant === 'primary' ? 'text-white' : getTextColor(isDarkMode)
            )}>
              Nigeria Tax Reform Assistant
            </h1>
            {variant === 'simple' && (
              <p className={cn('text-sm', getTextColor(isDarkMode, 'text-gray-500', 'text-gray-400'))}>
                Powered by FIRS Guidelines
              </p>
            )}
          </div>
        </div>
      </div>
      
      <div className="flex items-center gap-2 sm:gap-3">
        {variant === 'default' && (
          <>
            <button 
              onClick={onDarkModeToggle}
              className={cn('p-2 rounded-lg transition-colors', getHoverBg(isDarkMode))}
              aria-label={isDarkMode ? "Switch to light mode" : "Switch to dark mode"}
              title={isDarkMode ? "Switch to light mode" : "Switch to dark mode"}
            >
              {isDarkMode ? (
                <Sun className="w-5 h-5 text-gray-300" />
              ) : (
                <Moon className="w-5 h-5 text-gray-600" />
              )}
            </button>

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

            <button 
              className={cn('p-2 rounded-lg transition-colors', getHoverBg(isDarkMode))}
              aria-label="User profile"
            >
              <User className={cn('w-5 h-5', getTextColor(isDarkMode, 'text-gray-600', 'text-gray-300'))} />
            </button>
          </>
        )}
      </div>
    </header>
  );
};

export default Header;