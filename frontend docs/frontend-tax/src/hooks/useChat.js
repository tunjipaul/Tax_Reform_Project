import { useState, useCallback, useRef, useEffect } from 'react';
import { API_CONFIG, ERROR_MESSAGES, SUCCESS_MESSAGES } from '../constants';
import { sendChatMessage } from '../services/api';

/**
 * Custom hook for managing chat state and operations
 * Handles messages, loading states, errors, and async operations
 * @returns {object} Chat state and methods
 */
export const useChat = () => {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showSources, setShowSources] = useState(false);
  
  // Track pending requests for cleanup
  const pendingTimeoutRef = useRef(null);
  const abortControllerRef = useRef(null);

  // Cleanup on unmount
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

  /**
   * Send a message and get response from backend
   * @param {string} text - Message text
   */
  const sendMessage = useCallback(async (text) => {
    if (!text.trim()) return;

    // Clear any previous errors
    setError(null);
    setShowSources(false);

    // Add user message immediately
    const userMessage = {
      text,
      isUser: true,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      id: Date.now()
    };
    setMessages(prev => [...prev, userMessage]);

    // Set loading state
    setIsLoading(true);

    try {
      // Check if we should use mock data or real backend
      if (API_CONFIG.ENABLE_MOCK) {
        // ===== MOCK MODE (for development without backend) =====
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

        // Add mock bot message
        const botMessage = {
          text: SUCCESS_MESSAGES.DEFAULT_RESPONSE,
          isUser: false,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          showActions: true,
          source: 'Finance Act 2024, Section 15 (VAT Modifications)',
          id: Date.now() + 1
        };
        
        setMessages(prev => [...prev, botMessage]);
        setShowSources(true);

      } else {
        // ===== REAL BACKEND MODE =====
        
        // Create abort controller for cancellation
        abortControllerRef.current = new AbortController();

        // Call real backend API
        const result = await sendChatMessage(text);

        // Check if request was successful
        if (result.success) {
          // Extract response from backend
          const botMessage = {
            text: result.data.message || result.data.response,
            isUser: false,
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
            showActions: true,
            source: result.data.source || null,
            messageId: result.data.messageId || `msg_${Date.now()}`,
            id: Date.now() + 1
          };
          
          setMessages(prev => [...prev, botMessage]);
          
          // Show sources if available
          if (result.data.sources || result.data.source) {
            setShowSources(true);
          }
        } else {
          // Backend returned error
          throw new Error(result.error || ERROR_MESSAGES.GENERIC_ERROR);
        }
      }

    } catch (err) {
      // Handle errors
      if (err.message !== 'Request cancelled') {
        setError(err.message || ERROR_MESSAGES.GENERIC_ERROR);
        console.error('Chat error:', err);
      }
    } finally {
      setIsLoading(false);
      pendingTimeoutRef.current = null;
    }
  }, []);

  /**
   * Retry last failed message
   */
  const retry = useCallback(() => {
    setError(null);
    const lastUserMessage = messages.filter(m => m.isUser).pop();
    if (lastUserMessage) {
      sendMessage(lastUserMessage.text);
    }
  }, [messages, sendMessage]);

  /**
   * Clear all messages
   */
  const clearMessages = useCallback(() => {
    setMessages([]);
    setError(null);
    setShowSources(false);
  }, []);

  /**
   * Cancel pending request
   */
  const cancelRequest = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    if (pendingTimeoutRef.current) {
      clearTimeout(pendingTimeoutRef.current);
    }
    setIsLoading(false);
  }, []);

  return {
    messages,
    isLoading,
    error,
    showSources,
    sendMessage,
    retry,
    clearMessages,
    cancelRequest
  };
};

export default useChat;