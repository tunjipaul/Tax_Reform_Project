import React, { useState } from 'react';
import Header from './components/Header';
import Sidebar from './components/Sidebar';
import Welcome from './components/Welcome';
import ChatDisplay from './components/ChatDisplay';
import ChatInput from './components/ChatInput';
import LoadingIndicator from './components/LoadingIndicator';
import ErrorMessage from './components/ErrorMessage';
import SourceCitation from './components/SourceCitation';
import SuggestedActions from './components/SuggestedActions';

// Custom Hooks
import { useDarkMode } from './hooks/useDarkMode';
import { useChat } from './hooks/useChat';

// Constants
import {
  MOCK_RECENT_CHATS,
  MOCK_USER,
  MOCK_SOURCES,
  INITIAL_SUGGESTIONS,
  FOLLOWUP_SUGGESTIONS
} from './constants';

// Utilities
import { getContainerClasses } from './utils/classNames';

/**
 * Main App Component
 * Manages overall application state and layout
 */
const App = () => {
  const [showWelcome, setShowWelcome] = useState(true);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  
  // Custom hooks for dark mode and chat management
  const [isDarkMode, toggleDarkMode] = useDarkMode();
  const {
    messages,
    isLoading,
    error,
    showSources,
    sendMessage,
    retry,
    clearMessages
  } = useChat();

  /**
   * Handle sending a new message
   */
  const handleSendMessage = (text) => {
    setShowWelcome(false);
    sendMessage(text);
  };

  /**
   * Handle starting a new chat
   */
  const handleNewChat = () => {
    setShowWelcome(true);
    clearMessages();
    setIsMobileMenuOpen(false); // Close mobile menu
  };

  /**
   * Handle welcome card click
   */
  const handleWelcomeCardClick = (card) => {
    handleSendMessage(card.title);
  };

  /**
   * Handle suggestion selection
   */
  const handleSuggestionSelect = (suggestion) => {
    handleSendMessage(suggestion.text);
  };

  /**
   * Toggle mobile menu
   */
  const handleMenuToggle = () => {
    setIsMobileMenuOpen(prev => !prev);
  };

  /**
   * Close mobile menu
   */
  const handleMenuClose = () => {
    setIsMobileMenuOpen(false);
  };

  return (
    <div className={getContainerClasses(isDarkMode) + ' flex h-screen'}>
      {/* Sidebar - Mobile overlay + Desktop static */}
      <Sidebar 
        variant="light"
        recentChats={MOCK_RECENT_CHATS}
        currentUser={MOCK_USER}
        onNewChat={handleNewChat}
        isDarkMode={isDarkMode}
        isOpen={isMobileMenuOpen}
        onClose={handleMenuClose}
      />

      {/* Main Content */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Header */}
        <Header 
          variant="default"
          onNewChat={handleNewChat}
          showNewChat={!showWelcome}
          onDarkModeToggle={toggleDarkMode}
          onMenuToggle={handleMenuToggle}
          isDarkMode={isDarkMode}
        />

        {/* Content Area */}
        {showWelcome ? (
          <>
            <div className="flex-1 overflow-y-auto">
              <Welcome 
                onCardClick={handleWelcomeCardClick} 
                isDarkMode={isDarkMode} 
              />
              
              {/* Suggested Actions on Welcome Screen */}
              <div className="max-w-4xl mx-auto px-4 sm:px-6 pb-8">
                <h3 className={`text-sm font-semibold mb-3 ${
                  isDarkMode ? 'text-gray-300' : 'text-gray-700'
                }`}>
                  Quick Questions:
                </h3>
                <SuggestedActions 
                  suggestions={INITIAL_SUGGESTIONS}
                  onSelect={handleSuggestionSelect}
                  isDarkMode={isDarkMode}
                />
              </div>
            </div>
            
            <ChatInput 
              onSend={handleSendMessage}
              variant="arrow"
              isDarkMode={isDarkMode}
            />
          </>
        ) : (
          <>
            <div className={`flex-1 overflow-y-auto px-4 sm:px-6 py-8 ${
              isDarkMode ? 'bg-gray-900' : 'bg-gray-50'
            }`}>
              <div className="max-w-4xl mx-auto">
                {/* Chat Messages */}
                <ChatDisplay 
                  messages={messages}
                  isLoading={false}
                  isDarkMode={isDarkMode}
                />

                {/* Loading Indicator */}
                {isLoading && (
                  <LoadingIndicator 
                    message="Analyzing Finance Act 2024 Database..." 
                    isDarkMode={isDarkMode} 
                  />
                )}

                {/* Error Message */}
                {error && (
                  <ErrorMessage 
                    message={error} 
                    onRetry={retry} 
                    isDarkMode={isDarkMode} 
                  />
                )}

                {/* Source Citations */}
                {showSources && !isLoading && !error && messages.length > 0 && (
                  <SourceCitation 
                    sources={MOCK_SOURCES} 
                    isDarkMode={isDarkMode} 
                  />
                )}

                {/* Suggested Follow-up Actions */}
                {!isLoading && !error && messages.length > 0 && (
                  <div className="mt-6">
                    <h3 className={`text-sm font-semibold mb-3 ${
                      isDarkMode ? 'text-gray-300' : 'text-gray-700'
                    }`}>
                      Follow-up Questions:
                    </h3>
                    <SuggestedActions 
                      suggestions={FOLLOWUP_SUGGESTIONS}
                      onSelect={handleSuggestionSelect}
                      isDarkMode={isDarkMode}
                    />
                  </div>
                )}
              </div>
            </div>

            <ChatInput 
              onSend={handleSendMessage}
              disabled={isLoading}
              variant="advanced"
              isDarkMode={isDarkMode}
            />
          </>
        )}
      </div>
    </div>
  );
};

export default App;