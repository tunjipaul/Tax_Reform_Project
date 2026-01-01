import { useState, useEffect } from 'react';

/**
 * Custom hook for managing dark mode state
 * Handles localStorage persistence and DOM class manipulation
 * @returns {[boolean, function]} [isDarkMode, toggleDarkMode]
 */
export const useDarkMode = () => {
  const [isDarkMode, setIsDarkMode] = useState(() => {
    // Initialize from localStorage with validation
    try {
      const saved = localStorage.getItem('darkMode');
      return saved === 'true';
    } catch (error) {
      console.error('Error reading dark mode preference:', error);
      return false;
    }
  });

  // Apply dark mode class when state changes
  useEffect(() => {
    const html = document.documentElement;
    
    if (isDarkMode) {
      html.classList.add('dark');
      html.style.colorScheme = 'dark';
    } else {
      html.classList.remove('dark');
      html.style.colorScheme = 'light';
    }

    // Save to localStorage
    try {
      localStorage.setItem('darkMode', isDarkMode.toString());
    } catch (error) {
      console.error('Error saving dark mode preference:', error);
    }
  }, [isDarkMode]);

  const toggleDarkMode = () => {
    setIsDarkMode(prev => !prev);
  };

  return [isDarkMode, toggleDarkMode];
};

export default useDarkMode;