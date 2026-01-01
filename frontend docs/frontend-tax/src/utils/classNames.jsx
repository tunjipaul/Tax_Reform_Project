/**
 * Utility function to conditionally join classNames
 * @param  {...any} classes - Class names to join
 * @returns {string} Combined class names
 */
export const cn = (...classes) => {
  return classes.filter(Boolean).join(' ');
};

/**
 * Get background color based on dark mode
 * @param {boolean} isDarkMode 
 * @param {string} lightColor 
 * @param {string} darkColor 
 * @returns {string}
 */
export const getBgColor = (isDarkMode, lightColor = 'bg-white', darkColor = 'bg-gray-900') => {
  return isDarkMode ? darkColor : lightColor;
};

/**
 * Get text color based on dark mode
 * @param {boolean} isDarkMode 
 * @param {string} lightColor 
 * @param {string} darkColor 
 * @returns {string}
 */
export const getTextColor = (isDarkMode, lightColor = 'text-gray-900', darkColor = 'text-white') => {
  return isDarkMode ? darkColor : lightColor;
};

/**
 * Get border color based on dark mode
 * @param {boolean} isDarkMode 
 * @returns {string}
 */
export const getBorderColor = (isDarkMode) => {
  return isDarkMode ? 'border-gray-700' : 'border-gray-200';
};

/**
 * Get hover background color based on dark mode
 * @param {boolean} isDarkMode 
 * @returns {string}
 */
export const getHoverBg = (isDarkMode) => {
  return isDarkMode ? 'hover:bg-gray-700' : 'hover:bg-gray-100';
};

/**
 * Combine all theme-aware classes for a container
 * @param {boolean} isDarkMode 
 * @returns {string}
 */
export const getContainerClasses = (isDarkMode) => {
  return cn(
    getBgColor(isDarkMode, 'bg-gray-50', 'bg-gray-900'),
    getTextColor(isDarkMode),
    'transition-colors duration-200'
  );
};

/**
 * Get card classes with dark mode support
 * @param {boolean} isDarkMode 
 * @returns {string}
 */
export const getCardClasses = (isDarkMode) => {
  return cn(
    getBgColor(isDarkMode, 'bg-white', 'bg-gray-800'),
    getBorderColor(isDarkMode),
    'border rounded-xl'
  );
};

export default cn;