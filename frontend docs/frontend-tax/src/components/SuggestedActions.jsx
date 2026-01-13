import { cn, getBgColor, getTextColor, getBorderColor } from '../utils/classNames';

const SuggestedActions = ({ suggestions, onSelect, isDarkMode = false }) => {
  const defaultSuggestions = [
    { text: "What are the new VAT rates?" },
    { text: "Explain CIT compliance" },
    { text: "Small business exemptions" }
  ];

  const items = suggestions || defaultSuggestions;

  if (!items || items.length === 0) return null;

  return (
    <div className="flex flex-wrap gap-2">
      {items.map((item, index) => (
        <button
          key={index}
          onClick={() => onSelect && onSelect(item)}
          className={cn(
            'px-4 py-2 rounded-full text-sm transition-colors flex items-center gap-2 group border',
            getBgColor(isDarkMode, 'bg-white', 'bg-gray-800'),
            getBorderColor(isDarkMode),
            getTextColor(isDarkMode, 'text-gray-700', 'text-gray-300'),
            isDarkMode ? 'hover:bg-gray-700 hover:border-gray-600' : 'hover:bg-green-50 hover:border-green-400'
          )}
        >
          {item.icon && (
            <span className={cn(
              'text-gray-500',
              isDarkMode ? 'group-hover:text-green-500' : 'group-hover:text-green-600'
            )}>
              {item.icon}
            </span>
          )}
          <span>{item.text}</span>
        </button>
      ))}
    </div>
  );
};

export default SuggestedActions;