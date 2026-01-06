import React from 'react';
import { DollarSign, BookOpen, Building, TrendingUp } from 'lucide-react';

const Welcome = ({ onCardClick, isDarkMode = false }) => {
  const cards = [
    {
      icon: <DollarSign className="w-6 h-6" />,
      title: "Will I pay more income tax?",
      description: "Under the new personal income tax law and adjustments."
    },
    {
      icon: <BookOpen className="w-6 h-6" />,
      title: "VAT & State Derivation",
      description: "How does the new derivation formula affect my state?"
    },
    {
      icon: <Building className="w-6 h-6" />,
      title: "Company Income Tax",
      description: "Summary of rate changes for small businesses."
    },
    {
      icon: <TrendingUp className="w-6 h-6" />,
      title: "Development Levy",
      description: "Explain the purpose of the new development levy."
    }
  ];

  return (
    <div className="flex-1 flex flex-col items-center justify-center px-6 py-12">
      <h2 className={`text-4xl font-bold mb-4 ${
        isDarkMode ? 'text-white' : 'text-gray-900'
      }`}>
        Nigeria Tax Reform Q&A
      </h2>
      <p className={`text-center max-w-2xl mb-12 ${
        isDarkMode ? 'text-gray-400' : 'text-gray-600'
      }`}>
        Your intelligent assistant for understanding the 2024 tax reform bills. Ask about
        exemptions, new levies, VAT changes, or personal income tax implications.
      </p>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-4xl w-full">
        {cards.map((card, index) => (
          <div
            key={index}
            onClick={() => onCardClick && onCardClick(card)}
            className={`rounded-xl p-6 hover:shadow-md transition-shadow cursor-pointer group ${
              isDarkMode 
                ? 'bg-gray-800 border border-gray-700 hover:border-gray-600' 
                : 'bg-white border border-gray-200'
            }`}
          >
            <div className={`w-12 h-12 rounded-lg flex items-center justify-center mb-4 transition-colors ${
              isDarkMode
                ? 'bg-gray-700 group-hover:bg-green-900/30'
                : 'bg-gray-100 group-hover:bg-green-50'
            }`}>
              <div className={`transition-colors ${
                isDarkMode
                  ? 'text-gray-400 group-hover:text-green-500'
                  : 'text-gray-600 group-hover:text-green-600'
              }`}>
                {card.icon}
              </div>
            </div>
            <h3 className={`text-lg font-semibold mb-2 ${
              isDarkMode ? 'text-white' : 'text-gray-900'
            }`}>
              {card.title}
            </h3>
            <p className={`text-sm ${
              isDarkMode ? 'text-gray-400' : 'text-gray-600'
            }`}>
              {card.description}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Welcome;