import {useEffect } from 'react';
import { 
  Plus, 
  MessageSquare, 
  Bookmark, 
  History, 
  Settings, 
  User,
  Crown,
  ChevronRight,
  X
} from 'lucide-react';

const Sidebar = ({ 
  variant = 'default',
  currentUser,
  recentChats = [],
  onNewChat,
  onChatSelect,
  isDarkMode = false,
  isOpen = false,
  onClose
}) => {
  const getSidebarStyles = () => {
    if (variant === 'dark') return 'bg-green-900 text-white';
    return isDarkMode ? 'bg-gray-800 border-r border-gray-700' : 'bg-gray-50 border-r border-gray-200';
  };

  const menuItems = [
    { icon: <History className="w-5 h-5" />, label: 'History', action: 'history' },
    { icon: <Bookmark className="w-5 h-5" />, label: 'Saved Queries', action: 'saved' },
    { icon: <Settings className="w-5 h-5" />, label: 'Settings', action: 'settings' },
  ];

  const handleNewChatClick = () => {
    if (onNewChat) {
      onNewChat();
    }
    if (onClose) {
      onClose(); // Close mobile menu after action
    }
  };

  const handleChatClick = (chat) => {
    if (onChatSelect) {
      onChatSelect(chat);
    }
    if (onClose) {
      onClose(); // Close mobile menu after action
    }
  };

  // Prevent body scroll when mobile menu is open
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }
    return () => {
      document.body.style.overflow = 'unset';
    };
  }, [isOpen]);

  return (
    <>
      {/* Mobile Overlay */}
      {isOpen && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 z-40 md:hidden"
          onClick={onClose}
          aria-hidden="true"
        />
      )}

      {/* Sidebar */}
      <div className={`
        ${getSidebarStyles()}
        flex flex-col h-screen w-64
        fixed md:static inset-y-0 left-0 z-50
        transform transition-transform duration-300 ease-in-out
        ${isOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'}
      `}>
        {/* Mobile Close Button */}
        <div className="md:hidden flex justify-end p-4">
          <button
            onClick={onClose}
            className={`p-2 rounded-lg transition-colors ${
              isDarkMode ? 'hover:bg-gray-700' : 'hover:bg-gray-200'
            }`}
            aria-label="Close menu"
          >
            <X className={`w-6 h-6 ${isDarkMode ? 'text-gray-300' : 'text-gray-600'}`} />
          </button>
        </div>

        {/* Header */}
        <div className="p-4">
          <div className="flex items-center gap-3 mb-6">
            <div className="w-10 h-10 bg-green-600 rounded-lg flex items-center justify-center">
              <MessageSquare className="w-6 h-6 text-white" />
            </div>
            <div>
              <h2 className={`font-semibold ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>
                Tax Assistant
              </h2>
              <p className={`text-xs ${isDarkMode ? 'text-gray-400' : 'text-gray-500'}`}>
                NIGERIA REFORM GUIDE
              </p>
            </div>
          </div>

          {/* New Chat Button */}
          <button
            onClick={handleNewChatClick}
            className="w-full py-3 px-4 bg-green-600 text-white rounded-lg flex items-center gap-2 font-medium transition-colors hover:bg-green-700"
          >
            <Plus className="w-5 h-5" />
            New Chat
          </button>
        </div>

        {/* Recent Chats / Menu */}
        <div className="flex-1 overflow-y-auto px-4">
          {recentChats.length > 0 && (
            <div className="mb-6">
              <h3 className={`text-xs font-semibold uppercase mb-3 ${
                isDarkMode ? 'text-gray-400' : 'text-gray-500'
              }`}>
                LIBRARY
              </h3>
              <div className="space-y-1">
                {recentChats.map((chat, index) => (
                  <button
                    key={index}
                    onClick={() => handleChatClick(chat)}
                    className={`w-full px-3 py-2 rounded-lg text-left text-sm transition-colors flex items-center gap-2 ${
                      chat.active
                        ? 'bg-green-50 text-green-600 dark:bg-green-900/30 dark:text-green-400'
                        : isDarkMode
                          ? 'text-gray-300 hover:bg-gray-700'
                          : 'text-gray-700 hover:bg-gray-100'
                    }`}
                  >
                    {chat.icon && <span>{chat.icon}</span>}
                    <span className="truncate flex-1">{chat.title}</span>
                    {chat.active && <ChevronRight className="w-4 h-4 flex-shrink-0" />}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Menu Items */}
          <div className="space-y-1 mb-6">
            <h3 className={`text-xs font-semibold uppercase mb-3 ${
              isDarkMode ? 'text-gray-400' : 'text-gray-500'
            }`}>
              MENU
            </h3>
            {menuItems.map((item, index) => (
              <button
                key={index}
                className={`w-full px-3 py-2 rounded-lg text-left text-sm transition-colors flex items-center gap-3 ${
                  isDarkMode
                    ? 'text-gray-300 hover:bg-gray-700'
                    : 'text-gray-700 hover:bg-gray-100'
                }`}
              >
                {item.icon}
                <span>{item.label}</span>
              </button>
            ))}
          </div>
        </div>

        {/* User Profile / Upgrade */}
        <div className={`p-4 border-t ${isDarkMode ? 'border-gray-700' : 'border-gray-200'}`}>
          {currentUser ? (
            <div className="flex items-center gap-3">
              <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                isDarkMode ? 'bg-gray-700' : 'bg-gray-200'
              }`}>
                <User className={`w-5 h-5 ${isDarkMode ? 'text-gray-300' : 'text-gray-600'}`} />
              </div>
              <div className="flex-1 min-w-0">
                <p className={`text-sm font-medium truncate ${
                  isDarkMode ? 'text-white' : 'text-gray-900'
                }`}>
                  {currentUser.name}
                </p>
                <p className={`text-xs truncate ${
                  isDarkMode ? 'text-gray-400' : 'text-gray-500'
                }`}>
                  {currentUser.plan}
                </p>
              </div>
            </div>
          ) : (
            <div className="bg-green-600 rounded-lg p-4">
              <div className="flex items-center gap-2 mb-2">
                <Crown className="w-5 h-5 text-yellow-400" />
                <h3 className="font-semibold text-white">Upgrade to Pro</h3>
              </div>
              <p className="text-xs text-green-200 mb-3">
                Get advanced analysis and unlimited queries.
              </p>
              <button className="w-full py-2 bg-white text-green-600 rounded-lg text-sm font-medium hover:bg-green-50 transition-colors">
                Subscribe
              </button>
            </div>
          )}
        </div>
      </div>
    </>
  );
};

export default Sidebar;