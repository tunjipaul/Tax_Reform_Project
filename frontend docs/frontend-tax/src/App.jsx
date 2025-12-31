import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import Sidebar from './components/Sidebar';
import Welcome from './components/Welcome';
import ChatDisplay from './components/ChatDisplay';
import ChatInput from './components/ChatInput';
import LoadingIndicator from './components/LoadingIndicator';
import ErrorMessage from './components/ErrorMessage';
import SourceCitation from './components/SourceCitation';
import SuggestedActions from './components/SuggestedActions';

const App = () => {
  const [showWelcome, setShowWelcome] = useState(true);
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showSources, setShowSources] = useState(false);
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [forceUpdate, setForceUpdate] = useState(0);

  useEffect(() => {
    const savedDarkMode = localStorage.getItem('darkMode') === 'false';
    setIsDarkMode(savedDarkMode);
    if (savedDarkMode) {
      document.documentElement.classList.add('dark');
    }
  }, []);
  useEffect(() => {
    if (isDarkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
    setForceUpdate(prev => prev + 1);
  }, [isDarkMode]);

  const recentChats = [
    { 
      title: 'VAT Implications...', 
      active: true,
      
    },
    { 
      title: 'Company Tax 2024',
      
    },
    { 
      title: 'PAYE Reforms',
      
    }
  ];

  const currentUser = {
    name: 'Paul Ogor',
    plan: 'Basic Plan'
  };
  const sampleSources = [
    {
      title: 'Nigeria Tax Bill 2024',
      description: 'Section 45 • Value Added Tax Adjustments',
      excerpt: '45. (1) Subject to the provisions of subsection (2), a taxable person who has made a taxable supply to a person ... where the taxable person is a small company with a turnover of less than N25,000,000.00, shall be exempt from the requirements of registration and charging of tax...',
      page: 112,
      section: 'Paragraph 3',
      verified: true,
      link: '#'
    },
    {
      title: 'FIRS Circular 2023/04',
      description: 'Implementation Guidelines',
      excerpt: 'All registered businesses must comply with the new VAT threshold requirements by Q1 2024...',
      page: 5,
      section: 'Section 2.3',
      verified: true,
      link: '#'
    }
  ];


  const suggestions = [
    {
      text: "What are the new VAT rates?"
    },
    {
      text: "Explain CIT compliance"
    },
    {
      text: "Small business exemptions"
    }
  ];

  const handleSendMessage = (text) => {
    setShowWelcome(false);
    setError(null);

    const userMessage = {
      text,
      isUser: true,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };
    setMessages(prev => [...prev, userMessage]);

    setIsLoading(true);
    setShowSources(false);

    const shouldError = Math.random() < 0.2;

    setTimeout(() => {
      if (shouldError) {
        setError('We encountered a network issue while retrieving the latest tax exemption data. Please check your connection and try again.');
        setIsLoading(false);
      } else {
        const botMessage = {
          text: 'Under the 2024 reform, small businesses with a turnover of less than N25 million are exempt from charging VAT. This aims to reduce the compliance burden on SMEs while streamlining revenue collection.\n\nAdditionally, businesses in this category are no longer required to file monthly VAT returns, provided they maintain proper records of their transactions for audit purposes.',
          isUser: false,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          showActions: true,
          source: 'Finance Act 2024, Section 15 (VAT Modifications)'
        };
        setMessages(prev => [...prev, botMessage]);
        setIsLoading(false);
        setShowSources(true);
      }
    }, 2000);
  };

  const handleRetry = () => {
    setError(null);
    const lastUserMessage = messages.filter(m => m.isUser).pop();
    if (lastUserMessage) {
      handleSendMessage(lastUserMessage.text);
    }
  };

  const handleNewChat = () => {
    setShowWelcome(true);
    setMessages([]);
    setError(null);
    setShowSources(false);
  };

  const handleWelcomeCardClick = (card) => {
    handleSendMessage(card.title);
  };

  const handleSuggestionSelect = (suggestion) => {
    handleSendMessage(suggestion.text);
  };

  const handleDarkModeToggle = (darkMode) => {
    setIsDarkMode(darkMode);
  };

  return (
    <div key={forceUpdate} className={`flex h-screen ${isDarkMode ? 'bg-gray-900' : 'bg-gray-50'}`}>
      
      <Sidebar 
        variant="light"
        recentChats={recentChats}
        currentUser={currentUser}
        onNewChat={handleNewChat}
        isDarkMode={isDarkMode}
      />

      <div className="flex-1 flex flex-col">
        <Header 
          variant="default"
          onNewChat={handleNewChat}
          showNewChat={!showWelcome}
          onDarkModeToggle={handleDarkModeToggle}
          isDarkMode={isDarkMode}
        />
        {showWelcome ? (
          <>
            <div className="flex-1 overflow-y-auto">
              <Welcome onCardClick={handleWelcomeCardClick} isDarkMode={isDarkMode} />

              <div className="max-w-4xl mx-auto px-6 pb-8">
                <h3 className={`text-sm font-semibold mb-3 ${isDarkMode ? 'text-gray-300' : 'text-gray-700'}`}>
                  Quick Questions:
                </h3>
                <SuggestedActions 
                  suggestions={suggestions}
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
            <div className={`flex-1 overflow-y-auto px-6 py-8 ${isDarkMode ? 'bg-gray-900' : 'bg-gray-50'}`}>
              <div className="max-w-4xl mx-auto">
                
                <ChatDisplay 
                  messages={messages}
                  isLoading={false}
                  isDarkMode={isDarkMode}
                />

                
                {isLoading && <LoadingIndicator message="Analyzing Finance Act 2024 Database..." isDarkMode={isDarkMode} />}

                {error && <ErrorMessage message={error} onRetry={handleRetry} isDarkMode={isDarkMode} />}

                {showSources && !isLoading && !error && messages.length > 0 && (
                  <SourceCitation sources={sampleSources} isDarkMode={isDarkMode} />
                )}

                {!isLoading && !error && messages.length > 0 && (
                  <div className="mt-6">
                    <h3 className={`text-sm font-semibold mb-3 ${isDarkMode ? 'text-gray-300' : 'text-gray-700'}`}>
                      Follow-up Questions:
                    </h3>
                    <SuggestedActions 
                      suggestions={[
                        { text: "How do I register for VAT exemption?" },
                        { text: "What records do I need to maintain?" },
                        { text: "When does this take effect?" }
                      ]}
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