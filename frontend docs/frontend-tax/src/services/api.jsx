import {
  API_CONFIG,
  API_ENDPOINTS,
  ERROR_MESSAGES,
  DEFAULT_PLACEHOLDER,
} from "../constants";

export const generateSessionId = () => {
  return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
};

const fetchWithTimeout = async (url, options = {}) => {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), API_CONFIG.TIMEOUT);

  try {
    const response = await fetch(url, {
      ...options,
      signal: options.signal || controller.signal,
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    clearTimeout(timeoutId);

    if (error.name === "AbortError") {
      throw new Error(ERROR_MESSAGES.TIMEOUT_ERROR);
    }

    throw error;
  }
};

export const sendChatMessage = async (message, sessionId, history = [], signal = null) => {
  try {
    const response = await fetchWithTimeout(API_ENDPOINTS.CHAT, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        session_id: sessionId,
        message,
        history,
      }),
      signal,
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

export const fetchPlaceholder = async () => {
  try {
    const response = await fetchWithTimeout(API_ENDPOINTS.PLACEHOLDER, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    });

    return response.placeholder || DEFAULT_PLACEHOLDER;
  } catch (error) {
    console.error("Failed to fetch placeholder:", error);
    return DEFAULT_PLACEHOLDER;
  }
};

export const fetchSources = async (messageId) => {
  try {
    const response = await fetchWithTimeout(
      `${API_ENDPOINTS.SOURCES}/${messageId}`,
      {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
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

export const fetchChatHistory = async (userId) => {
  try {
    const response = await fetchWithTimeout(
      `${API_ENDPOINTS.HISTORY}?userId=${userId}`,
      {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
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

export const fetchSessions = async () => {
  try {
    const response = await fetchWithTimeout(
      `${API_CONFIG.BASE_URL}/api/sessions`,
      {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
      }
    );

    return {
      success: true,
      data: response.sessions || [],
    };
  } catch (error) {
    console.error("Failed to fetch sessions:", error);
    return {
      success: false,
      data: [],
      error: error.message || ERROR_MESSAGES.GENERIC_ERROR,
    };
  }
};

export const loadSession = async (sessionId) => {
  try {
    const response = await fetchWithTimeout(
      `${API_CONFIG.BASE_URL}/api/sessions/${sessionId}`,
      {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
      }
    );

    return {
      success: true,
      data: response,
    };
  } catch (error) {
    console.error("Failed to load session:", error);
    return {
      success: false,
      error: error.message || ERROR_MESSAGES.GENERIC_ERROR,
    };
  }
};
