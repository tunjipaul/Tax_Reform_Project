export const cn = (...classes) => {
  return classes.filter(Boolean).join(' ');
};

export const getBgColor = (isDarkMode, lightColor = 'bg-white', darkColor = 'bg-gray-900') => {
  return isDarkMode ? darkColor : lightColor;
};

export const getTextColor = (isDarkMode, lightColor = 'text-gray-900', darkColor = 'text-white') => {
  return isDarkMode ? darkColor : lightColor;
};

export const getBorderColor = (isDarkMode) => {
  return isDarkMode ? 'border-gray-700' : 'border-gray-200';
};

export const getHoverBg = (isDarkMode) => {
  return isDarkMode ? 'hover:bg-gray-700' : 'hover:bg-gray-100';
};

export const getContainerClasses = (isDarkMode) => {
  return cn(
    getBgColor(isDarkMode, 'bg-gray-50', 'bg-gray-900'),
    getTextColor(isDarkMode),
    'transition-colors duration-200'
  );
};

export const getCardClasses = (isDarkMode) => {
  return cn(
    getBgColor(isDarkMode, 'bg-white', 'bg-gray-800'),
    getBorderColor(isDarkMode),
    'border rounded-xl'
  );
};

export default cn;