import Header from './Header';
import WelcomeView from './views/WelcomeView';
import ChatView from './views/ChatView';
import { useChatContext } from '../contexts/ChatContext';

const MainContent = ({ isDarkMode, onDarkModeToggle, onMenuToggle }) => {
  const { showWelcome, handleNewChat } = useChatContext();
  
  return (
    <>
      <Header 
        variant="default"
        onNewChat={handleNewChat}
        showNewChat={!showWelcome}
        onDarkModeToggle={onDarkModeToggle}
        onMenuToggle={onMenuToggle}
        isDarkMode={isDarkMode}
      />
      
      {showWelcome ? (
        <WelcomeView isDarkMode={isDarkMode} />
      ) : (
        <ChatView isDarkMode={isDarkMode} />
      )}
    </>
  );
};

export default MainContent;