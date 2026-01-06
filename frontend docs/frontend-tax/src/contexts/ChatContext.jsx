import { createContext, useState, useCallback, useContext } from "react";
import { useChat } from "../hooks/useChat";

const ChatContext = createContext(null);

export const ChatProvider = ({ children }) => {
  const chat = useChat();
  const [showWelcome, setShowWelcome] = useState(true);

  const handleSendMessage = useCallback(
    (text) => {
      setShowWelcome(false);
      chat.sendMessage(text);
    },
    [chat]
  );

  const handleNewChat = useCallback(() => {
    setShowWelcome(true);
    chat.clearMessages();
  }, [chat]);

  const handleWelcomeCardClick = useCallback(
    (card) => {
      handleSendMessage(card.title);
    },
    [handleSendMessage]
  );

  const handleSuggestionSelect = useCallback(
    (suggestion) => {
      handleSendMessage(suggestion.text);
    },
    [handleSendMessage]
  );

  const value = {
    messages: chat.messages,
    isLoading: chat.isLoading,
    error: chat.error,
    showSources: chat.showSources,
    showWelcome,
    sendMessage: chat.sendMessage,
    retry: chat.retry,
    clearMessages: chat.clearMessages,
    cancelRequest: chat.cancelRequest,
    handleSendMessage,
    handleNewChat,
    handleWelcomeCardClick,
    handleSuggestionSelect,
  };

  return <ChatContext.Provider value={value}>{children}</ChatContext.Provider>;
};

export const useChatContext = () => {
  const context = useContext(ChatContext);

  if (!context) {
    throw new Error("useChatContext must be used within ChatProvider");
  }

  return context;
};

export default ChatContext;
