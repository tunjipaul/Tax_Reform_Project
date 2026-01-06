import React from 'react';
import Welcome from '../Welcome';
import ChatInput from '../ChatInput';
import SuggestedActions from '../SuggestedActions';
import { useChatContext } from '../../contexts/ChatContext';
import { INITIAL_SUGGESTIONS } from '../../constants';

const WelcomeView = ({ isDarkMode }) => {
  const { handleSendMessage, handleWelcomeCardClick, handleSuggestionSelect } = useChatContext();

  return (
    <>
      <div className="flex-1 overflow-y-auto">
        <Welcome 
          onCardClick={handleWelcomeCardClick} 
          isDarkMode={isDarkMode} 
        />
        
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
  );
};

export default WelcomeView;