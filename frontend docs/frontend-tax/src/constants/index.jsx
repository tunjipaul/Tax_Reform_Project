// API Configuration from environment variables
export const API_CONFIG = {
  BASE_URL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api',
  TIMEOUT: parseInt(import.meta.env.VITE_API_TIMEOUT) || 30000,
  ENABLE_MOCK: import.meta.env.VITE_ENABLE_MOCK_DATA === 'true',
  
  // Mock API settings (used when ENABLE_MOCK is true)
  MOCK_DELAY: 2000, // ms
  MOCK_ERROR_RATE: 0.2, // 20% chance for mock errors
};

// API Endpoints
export const API_ENDPOINTS = {
  CHAT: `${API_CONFIG.BASE_URL}/chat`,
  SOURCES: `${API_CONFIG.BASE_URL}/sources`,
  HISTORY: `${API_CONFIG.BASE_URL}/history`,
  PLACEHOLDER: `${API_CONFIG.BASE_URL}/placeholder`,
};

// UI Configuration
export const UI_CONFIG = {
  SIDEBAR_WIDTH: 256, // pixels
  MAX_MESSAGE_LENGTH: 2000,
  TYPING_INDICATOR_DELAY: 300,
  AUTO_SCROLL_DELAY: 100,
  APP_NAME: import.meta.env.VITE_APP_NAME || 'Nigeria Tax Reform Assistant',
  APP_VERSION: import.meta.env.VITE_APP_VERSION || '1.0.0',
};

// Sample Data
export const MOCK_RECENT_CHATS = [
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

export const MOCK_USER = {
  name: 'David Adewale',
  plan: 'Basic Plan',
  userId: 'user_123'
};

export const MOCK_SOURCES = [
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

export const INITIAL_SUGGESTIONS = [
  { text: "What are the new VAT rates?" },
  { text: "Explain CIT compliance" },
  { text: "Small business exemptions" }
];

export const FOLLOWUP_SUGGESTIONS = [
  { text: "How do I register for VAT exemption?" },
  { text: "What records do I need to maintain?" },
  { text: "When does this take effect?" }
];

// Tax Amounts
export const TAX_THRESHOLDS = {
  VAT_EXEMPTION: 25000000, // N25 million
  SMALL_BUSINESS: 25000000
};

// Messages
export const ERROR_MESSAGES = {
  NETWORK_ERROR: 'We encountered a network issue while retrieving the latest tax exemption data. Please check your connection and try again.',
  TIMEOUT_ERROR: 'Request timed out. Please try again.',
  GENERIC_ERROR: 'Something went wrong. Please try again.',
  NO_BACKEND: 'Backend server is not responding. Please try again later.'
};

export const SUCCESS_MESSAGES = {
  DEFAULT_RESPONSE: 'Under the 2024 reform, small businesses with a turnover of less than N25 million are exempt from charging VAT. This aims to reduce the compliance burden on SMEs while streamlining revenue collection.\n\nAdditionally, businesses in this category are no longer required to file monthly VAT returns, provided they maintain proper records of their transactions for audit purposes.'
};

// Default placeholder (fallback if API fails)
export const DEFAULT_PLACEHOLDER = 'Ask a question about the 2024 Tax Reform...';