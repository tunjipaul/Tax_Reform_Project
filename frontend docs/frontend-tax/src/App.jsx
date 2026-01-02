import React, { useState } from 'react';
import { ChatProvider } from './contexts/ChatContext';
import AppLayout from './components/layouts/AppLayout';
import MainContent from './components/MainContent';
import { useDarkMode } from './hooks/useDarkMode';

const App = () => {
  const [isDarkMode, toggleDarkMode] = useDarkMode();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const handleMenuToggle = () => setIsMobileMenuOpen(prev => !prev);
  const handleMenuClose = () => setIsMobileMenuOpen(false);

  return (
    <ChatProvider>
      <AppLayout 
        isDarkMode={isDarkMode}
        isMobileMenuOpen={isMobileMenuOpen}
        onMenuClose={handleMenuClose}
      >
        <MainContent 
          isDarkMode={isDarkMode}
          onDarkModeToggle={toggleDarkMode}
          onMenuToggle={handleMenuToggle}
        />
      </AppLayout>
    </ChatProvider>
  );
};

export default App;