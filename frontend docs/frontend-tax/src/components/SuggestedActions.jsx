const SuggestedActions = ({ suggestions, onSelect, isDarkMode = false }) => {
  const defaultSuggestions = [
    {
      text: "What are the new VAT rates?"
    },
    {
      text: "Explain CIT compliance"
    },
    {
      text: "Small business exemptions"
    }
  ];

  const items = suggestions || defaultSuggestions;

  if (!items || items.length === 0) return null;

  return (
    <div className="flex flex-wrap gap-2">
      {items.map((item, index) => (
        <button
          key={index}
          onClick={() => onSelect && onSelect(item)}
          className={`px-4 py-2 rounded-full text-sm transition-colors flex items-center gap-2 group ${
            isDarkMode
              ? 'bg-gray-800 border border-gray-700 text-gray-300 hover:bg-gray-700 hover:border-gray-600'
              : 'bg-white border border-gray-300 text-gray-700 hover:bg-green-50 hover:border-green-400'
          }`}
        >
          {item.icon && <span className={`${
            isDarkMode 
              ? 'text-gray-500 group-hover:text-green-500' 
              : 'text-gray-500 group-hover:text-green-600'
          }`}>{item.icon}</span>}
          <span>{item.text}</span>
        </button>
      ))}
    </div>
  );
};

export default SuggestedActions;