import { useState, useEffect } from 'react';

const STORAGE_KEY = 'darkMode';

export const useDarkMode = () => {
  const [isDarkMode, setIsDarkMode] = useState(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      return saved === 'true';
    } catch (error) {
      console.error('Error reading dark mode preference:', error);
      return false;
    }
  });

  useEffect(() => {
    const html = document.documentElement;
    
    if (isDarkMode) {
      html.classList.add('dark');
      html.style.colorScheme = 'dark';
    } else {
      html.classList.remove('dark');
      html.style.colorScheme = 'light';
    }

    try {
      localStorage.setItem(STORAGE_KEY, isDarkMode.toString());
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