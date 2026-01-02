import React from 'react';
import ChatDisplay from '../ChatDisplay';
import ChatInput from '../ChatInput';
import LoadingIndicator from '../LoadingIndicator';
import ErrorMessage from '../ErrorMessage';
import SourceCitation from '../SourceCitation';
import SuggestedActions from '../SuggestedActions';
import { useChatContext } from '../../contexts/ChatContext';
import { MOCK_SOURCES, FOLLOWUP_SUGGESTIONS } from '../../constants';

const ChatView = ({ isDarkMode }) => {
  const { 
    messages, 
    isLoading, 
    error, 
    showSources, 
    handleSendMessage,
    handleSuggestionSelect,
    retry 
  } = useChatContext();

  const hasMessages = messages.length > 0;

  return (
    <>
      <div className={`flex-1 overflow-y-auto px-4 sm:px-6 py-8 ${
        isDarkMode ? 'bg-gray-900' : 'bg-gray-50'
      }`}>
        <div className="max-w-4xl mx-auto">
          <ChatDisplay 
            messages={messages}
            isLoading={false}
            isDarkMode={isDarkMode}
          />

          {isLoading && (
            <LoadingIndicator 
              message="Analyzing Finance Act 2024 Database..." 
              isDarkMode={isDarkMode} 
            />
          )}

          {error && (
            <ErrorMessage 
              message={error} 
              onRetry={retry} 
              isDarkMode={isDarkMode} 
            />
          )}

          {showSources && !isLoading && !error && hasMessages && (
            <SourceCitation 
              sources={MOCK_SOURCES} 
              isDarkMode={isDarkMode} 
            />
          )}

          {!isLoading && !error && hasMessages && (
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
  );
};

export default ChatView;