import { useState, useEffect, useCallback } from 'react';
import Sidebar from '../Sidebar';
import { useChatContext } from '../../contexts/ChatContext';
import { MOCK_USER } from '../../constants';
import { getContainerClasses } from '../../utils/classNames';
import { fetchSessions, loadSession } from '../../services/api';

const AppLayout = ({ isDarkMode, isMobileMenuOpen, onMenuClose, children }) => {
  const { handleNewChat, messages, handleLoadSession } = useChatContext();
  const [recentChats, setRecentChats] = useState([]);

  const loadSessions = useCallback(async () => {
    const result = await fetchSessions();
    if (result.success && result.data) {
      const chats = result.data.map((session, index) => ({
        title: session.title,
        session_id: session.session_id,
        message_count: session.message_count,
        last_active: session.last_active,
        active: index === 0
      }));
      setRecentChats(chats);
    }
  }, []);

  useEffect(() => {
    loadSessions();
  }, [loadSessions]);

  useEffect(() => {
    if (messages.length > 0) {
      const timer = setTimeout(loadSessions, 1000);
      return () => clearTimeout(timer);
    }
  }, [messages.length, loadSessions]);

  const handleNewChatWithRefresh = useCallback(() => {
    handleNewChat();
    setTimeout(loadSessions, 500);
  }, [handleNewChat, loadSessions]);

  const handleChatSelect = useCallback(async (chat) => {
    if (!chat.session_id) return;
    
    const result = await loadSession(chat.session_id);
    if (result.success && result.data) {
      handleLoadSession(result.data.messages);
      setRecentChats(prev => prev.map(c => ({
        ...c,
        active: c.session_id === chat.session_id
      })));
    }
  }, [handleLoadSession]);

  return (
    <div className={getContainerClasses(isDarkMode) + ' flex h-screen'}>
      <Sidebar 
        variant="light"
        recentChats={recentChats}
        currentUser={MOCK_USER}
        onNewChat={handleNewChatWithRefresh}
        onChatSelect={handleChatSelect}
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