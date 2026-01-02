import React from 'react';
import Sidebar from '../Sidebar';
import { useChatContext } from '../../contexts/ChatContext';
import { MOCK_RECENT_CHATS, MOCK_USER } from '../../constants';
import { getContainerClasses } from '../../utils/classNames';

const AppLayout = ({ isDarkMode, isMobileMenuOpen, onMenuClose, children }) => {
  const { handleNewChat } = useChatContext();

  return (
    <div className={getContainerClasses(isDarkMode) + ' flex h-screen'}>
      <Sidebar 
        variant="light"
        recentChats={MOCK_RECENT_CHATS}
        currentUser={MOCK_USER}
        onNewChat={handleNewChat}
        isDarkMode={isDarkMode}
        isOpen={isMobileMenuOpen}
        onClose={onMenuClose}
      />
      
      <div className="flex-1 flex flex-col min-w-0">
        {children}
      </div>
    </div>
  );
};

export default AppLayout;