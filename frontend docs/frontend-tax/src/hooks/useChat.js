import { useState, useCallback, useRef, useEffect } from 'react';
import { API_CONFIG, ERROR_MESSAGES, SUCCESS_MESSAGES } from '../constants';
import { sendChatMessage, generateSessionId } from '../services/api';

export const useChat = () => {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showSources, setShowSources] = useState(false);
  
  const sessionIdRef = useRef(generateSessionId());
  
  const pendingTimeoutRef = useRef(null);
  const abortControllerRef = useRef(null);

  useEffect(() => {
    return () => {
      if (pendingTimeoutRef.current) {
        clearTimeout(pendingTimeoutRef.current);
      }
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, []);

  const buildHistory = useCallback(() => {
    return messages.map(msg => ({
      role: msg.isUser ? 'user' : 'assistant',
      content: msg.text
    }));
  }, [messages]);

  const sendMessage = useCallback(async (text) => {
    if (!text.trim()) return;

    setError(null);
    setShowSources(false);

    const userMessage = {
      text,
      isUser: true,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      id: Date.now()
    };
    setMessages(prev => [...prev, userMessage]);

    setIsLoading(true);

    try {
      if (API_CONFIG.ENABLE_MOCK) {
        await new Promise((resolve, reject) => {
          pendingTimeoutRef.current = setTimeout(() => {
            const shouldError = Math.random() < 0.2;
            
            if (shouldError) {
              reject(new Error(ERROR_MESSAGES.NETWORK_ERROR));
            } else {
              resolve();
            }
          }, API_CONFIG.MOCK_DELAY);
        });

        const botMessage = {
          text: SUCCESS_MESSAGES.DEFAULT_RESPONSE,
          isUser: false,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          showActions: true,
          source: 'Finance Act 2024, Section 15 (VAT Modifications)',
          sources: [],
          id: Date.now() + 1
        };
        
        setMessages(prev => [...prev, botMessage]);
        setShowSources(true);

      } else {
        abortControllerRef.current = new AbortController();

        const history = buildHistory();

        const result = await sendChatMessage(
          text, 
          sessionIdRef.current, 
          history,
          abortControllerRef.current.signal
        );

        if (result.success) {
          const botMessage = {
            text: result.data.response || result.data.message,
            isUser: false,
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
            showActions: true,
            sources: result.data.sources || [],
            retrieved: result.data.retrieved || false,
            messageId: result.data.session_id || `msg_${Date.now()}`,
            id: Date.now() + 1
          };
          
          setMessages(prev => [...prev, botMessage]);
          
          if (result.data.sources && result.data.sources.length > 0) {
            setShowSources(true);
          }
        } else {
          throw new Error(result.error || ERROR_MESSAGES.GENERIC_ERROR);
        }
      }

    } catch (err) {
      if (err.message !== 'Request cancelled') {
        setError(err.message || ERROR_MESSAGES.GENERIC_ERROR);
        console.error('Chat error:', err);
      }
    } finally {
      setIsLoading(false);
      pendingTimeoutRef.current = null;
    }
  }, [buildHistory]);

  const retry = useCallback(() => {
    setError(null);
    const lastUserMessage = messages.filter(m => m.isUser).pop();
    if (lastUserMessage) {
      sendMessage(lastUserMessage.text);
    }
  }, [messages, sendMessage]);

  const clearMessages = useCallback(() => {
    setMessages([]);
    setError(null);
    setShowSources(false);
    sessionIdRef.current = generateSessionId();
  }, []);

  const cancelRequest = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    if (pendingTimeoutRef.current) {
      clearTimeout(pendingTimeoutRef.current);
    }
    setIsLoading(false);
  }, []);

  const loadMessages = useCallback((newMessages) => {
    setMessages(newMessages);
    setError(null);
    if (newMessages.some(m => m.sources && m.sources.length > 0)) {
      setShowSources(true);
    }
  }, []);

  return {
    messages,
    isLoading,
    error,
    showSources,
    sendMessage,
    retry,
    clearMessages,
    cancelRequest,
    loadMessages
  };
};

export default useChat;