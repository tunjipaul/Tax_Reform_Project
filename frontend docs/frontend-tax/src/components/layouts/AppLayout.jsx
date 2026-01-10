import { useState, useEffect, useCallback } from 'react';
import Sidebar from '../Sidebar';
import { useChatContext } from '../../contexts/ChatContext';
import { MOCK_USER } from '../../constants';
import { getContainerClasses } from '../../utils/classNames';
import { fetchSessions, loadSession } from '../../services/api';

const AppLayout = ({ isDarkMode, isMobileMenuOpen, onMenuClose, children }) => {
  const { handleNewChat, messages, handleLoadSession } = useChatContext();
  const [recentChats, setRecentChats] = useState([]);

  // Fetch sessions from backend
  const loadSessions = useCallback(async () => {
    const result = await fetchSessions();
    if (result.success && result.data) {
      // Transform to sidebar format
      const chats = result.data.map((session, index) => ({
        title: session.title,
        session_id: session.session_id,
        message_count: session.message_count,
        last_active: session.last_active,
        active: index === 0 // Most recent is active
      }));
      setRecentChats(chats);
    }
  }, []);

  // Load sessions on mount and when messages change
  useEffect(() => {
    loadSessions();
  }, [loadSessions]);

  // Refresh sessions after sending a message (debounced)
  useEffect(() => {
    if (messages.length > 0) {
      const timer = setTimeout(loadSessions, 1000);
      return () => clearTimeout(timer);
    }
  }, [messages.length, loadSessions]);

  const handleNewChatWithRefresh = useCallback(() => {
    handleNewChat();
    // Refresh sessions list after creating new chat
    setTimeout(loadSessions, 500);
  }, [handleNewChat, loadSessions]);

  // Handle clicking on a previous chat
  const handleChatSelect = useCallback(async (chat) => {
    if (!chat.session_id) return;
    
    const result = await loadSession(chat.session_id);
    if (result.success && result.data) {
      handleLoadSession(result.data.messages);
      // Update active state in sidebar
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