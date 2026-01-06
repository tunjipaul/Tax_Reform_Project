import { useState } from 'react';
import { FileText, ChevronDown, ChevronUp, ExternalLink, CheckCircle } from 'lucide-react';

const SourceCitation = ({ sources = [], isDarkMode = false }) => {
  const [expandedSource, setExpandedSource] = useState(null);

  const toggleSource = (index) => {
    setExpandedSource(expandedSource === index ? null : index);
  };

  if (!sources || sources.length === 0) return null;

  return (
    <div className={`mt-6 pt-6 border-t ${isDarkMode ? 'border-gray-700' : 'border-gray-200'}`}>
      <div className="flex items-center gap-2 mb-4">
        <FileText className="w-5 h-5 text-green-600" />
        <h3 className={`text-sm font-semibold uppercase tracking-wide ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>
          Sources and Citations
        </h3>
      </div>

      <div className="space-y-3">
        {sources.map((source, index) => {
          const isExpanded = expandedSource === index;
          
          return (
            <div 
              key={index}
              className={`border-l-4 border-yellow-400 rounded-lg overflow-hidden ${isDarkMode ? 'bg-gray-800' : 'bg-white'}`}
            >
              <div 
                className={`p-4 cursor-pointer transition-colors ${isDarkMode ? 'hover:bg-gray-700' : 'hover:bg-gray-50'}`}
                onClick={() => toggleSource(index)}
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="flex items-start gap-3 flex-1">
                    <div className={`w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0 ${isDarkMode ? 'bg-yellow-900/30' : 'bg-yellow-100'}`}>
                      <FileText className="w-5 h-5 text-yellow-600" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <h4 className={`font-semibold ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>
                          {source.title}
                        </h4>
                        {source.verified && (
                          <span className="flex items-center gap-1 text-xs text-green-600">
                            <CheckCircle className="w-3 h-3" />
                            VERIFIED
                          </span>
                        )}
                      </div>
                      <p className={`text-sm ${isDarkMode ? 'text-gray-400' : 'text-gray-600'}`}>
                        {source.description}
                      </p>
                    </div>
                  </div>
                  <button className="flex-shrink-0 p-1" type="button">
                    {isExpanded ? (
                      <ChevronUp className={`w-5 h-5 ${isDarkMode ? 'text-gray-500' : 'text-gray-400'}`} />
                    ) : (
                      <ChevronDown className={`w-5 h-5 ${isDarkMode ? 'text-gray-500' : 'text-gray-400'}`} />
                    )}
                  </button>
                </div>
              </div>

              {isExpanded && (
                <div className={`px-4 pb-4 border-t ${isDarkMode ? 'border-gray-700' : 'border-gray-100'}`}>
                  <div className={`rounded-lg p-4 mt-3 ${isDarkMode ? 'bg-gray-900' : 'bg-gray-50'}`}>
                    <p className={`text-sm font-mono leading-relaxed ${isDarkMode ? 'text-gray-300' : 'text-gray-700'}`}>
                      {source.excerpt}
                    </p>
                    {source.page && (
                      <p className={`text-xs mt-2 ${isDarkMode ? 'text-gray-500' : 'text-gray-500'}`}>
                        Page {source.page}, {source.section}
                      </p>
                    )}
                  </div>

                  {source.link && (
                    <a
                      href={source.link}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-2 mt-3 text-sm text-green-600 hover:text-green-700 font-medium"
                    >
                      Read Full Document
                      <ExternalLink className="w-4 h-4" />
                    </a>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default SourceCitation;