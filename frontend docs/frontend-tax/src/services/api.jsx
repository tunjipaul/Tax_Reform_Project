import { API_CONFIG, API_ENDPOINTS, ERROR_MESSAGES, DEFAULT_PLACEHOLDER } from '../constants';

/**
 * Fetch with timeout support
 * @param {string} url 
 * @param {object} options 
 * @returns {Promise}
 */
const fetchWithTimeout = async (url, options = {}) => {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), API_CONFIG.TIMEOUT);

  try {
    const response = await fetch(url, {
      ...options,
      signal: controller.signal,
    });

    clearTimeout(timeout);

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    clearTimeout(timeout);
    
    if (error.name === 'AbortError') {
      throw new Error(ERROR_MESSAGES.TIMEOUT_ERROR);
    }
    
    throw error;
  }
};

/**
 * Send chat message to backend
 * @param {string} message 
 * @returns {Promise}
 */
export const sendChatMessage = async (message) => {
  try {
    const response = await fetchWithTimeout(API_ENDPOINTS.CHAT, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message,
        timestamp: new Date().toISOString(),
      }),
    });

    return {
      success: true,
      data: response,
    };
  } catch (error) {
    return {
      success: false,
      error: error.message || ERROR_MESSAGES.GENERIC_ERROR,
    };
  }
};

/**
 * Fetch placeholder text from backend
 * @returns {Promise<string>}
 */
export const fetchPlaceholder = async () => {
  try {
    const response = await fetchWithTimeout(API_ENDPOINTS.PLACEHOLDER, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    return response.placeholder || DEFAULT_PLACEHOLDER;
  } catch (error) {
    console.error('Failed to fetch placeholder:', error);
    return DEFAULT_PLACEHOLDER;
  }
};

/**
 * Fetch sources/citations
 * @param {string} messageId 
 * @returns {Promise}
 */
export const fetchSources = async (messageId) => {
  try {
    const response = await fetchWithTimeout(
      `${API_ENDPOINTS.SOURCES}/${messageId}`,
      {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      }
    );

    return {
      success: true,
      data: response,
    };
  } catch (error) {
    return {
      success: false,
      error: error.message || ERROR_MESSAGES.GENERIC_ERROR,
    };
  }
};

/**
 * Fetch chat history
 * @param {string} userId 
 * @returns {Promise}
 */
export const fetchChatHistory = async (userId) => {
  try {
    const response = await fetchWithTimeout(
      `${API_ENDPOINTS.HISTORY}?userId=${userId}`,
      {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      }
    );

    return {
      success: true,
      data: response,
    };
  } catch (error) {
    return {
      success: false,
      error: error.message || ERROR_MESSAGES.GENERIC_ERROR,
    };
  }
};