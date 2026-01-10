import { useState } from 'react';
import { FileText, ChevronDown, ChevronUp, ExternalLink, CheckCircle, Book } from 'lucide-react';

const SourceCitation = ({ sources = [], isDarkMode = false }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [expandedSource, setExpandedSource] = useState(null);

  const toggleSection = () => {
    setIsOpen(!isOpen);
  };

  const toggleSource = (index) => {
    setExpandedSource(expandedSource === index ? null : index);
  };

  if (!sources || sources.length === 0) return null;

  // Helper to format source type for display
  const formatType = (type) => {
    if (!type) return 'Document';
    return type.toUpperCase();
  };

  // Helper to format relevance score
  const formatScore = (score) => {
    if (!score && score !== 0) return null;
    return `${Math.round(score * 100)}% relevant`;
  };

  // Generate a link to the document (served from backend/public)
  const getDocumentLink = (documentName) => {
    if (!documentName) return null;
    // Clean the document name and create a link
    // Documents are in ai_engine/documents/ folder
    const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
    const encodedName = encodeURIComponent(documentName);
    return `${baseUrl}/documents/${encodedName}`;
  };

  return (
    <div className={`mt-6 pt-6 border-t ${isDarkMode ? 'border-gray-700' : 'border-gray-200'}`}>
      {/* Collapsible Header */}
      <button 
        onClick={toggleSection}
        className={`w-full flex items-center justify-between gap-2 p-3 rounded-lg transition-colors ${
          isDarkMode 
            ? 'bg-gray-800 hover:bg-gray-750 border border-gray-700' 
            : 'bg-white hover:bg-gray-50 border border-gray-200'
        }`}
      >
        <div className="flex items-center gap-3">
          <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${
            isDarkMode ? 'bg-green-900/30' : 'bg-green-100'
          }`}>
            <Book className="w-4 h-4 text-green-600" />
          </div>
          <div className="text-left">
            <h3 className={`text-sm font-semibold ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>
              Sources and Citations
            </h3>
            <p className={`text-xs ${isDarkMode ? 'text-gray-400' : 'text-gray-500'}`}>
              {sources.length} document{sources.length !== 1 ? 's' : ''} referenced
            </p>
          </div>
        </div>
        <div className={`p-1 rounded ${isDarkMode ? 'text-gray-400' : 'text-gray-500'}`}>
          {isOpen ? (
            <ChevronUp className="w-5 h-5" />
          ) : (
            <ChevronDown className="w-5 h-5" />
          )}
        </div>
      </button>

      {/* Expandable Content */}
      {isOpen && (
        <div className="mt-3 space-y-3">
          {sources.map((source, index) => {
            const isExpanded = expandedSource === index;
            // Support both new format (document) and old format (title)
            const documentName = source.document || source.title || 'Unknown Document';
            const description = source.description || formatType(source.type);
            const relevanceScore = formatScore(source.score);
            const documentLink = source.link || getDocumentLink(documentName);
            
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
                      <div className={`w-10 h-10 rounded-lg flex items-center justify-center shrink-0 ${isDarkMode ? 'bg-yellow-900/30' : 'bg-yellow-100'}`}>
                        <FileText className="w-5 h-5 text-yellow-600" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                          <h4 className={`font-semibold ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>
                            {documentName}
                          </h4>
                          {(source.verified !== false) && (
                            <span className="flex items-center gap-1 text-xs text-green-600">
                              <CheckCircle className="w-3 h-3" />
                              VERIFIED
                            </span>
                          )}
                        </div>
                        <p className={`text-sm ${isDarkMode ? 'text-gray-400' : 'text-gray-600'}`}>
                          {description}
                          {relevanceScore && (
                            <span className="ml-2 text-xs text-green-600 font-medium">
                              • {relevanceScore}
                            </span>
                          )}
                        </p>
                      </div>
                    </div>
                    <button className="shrink-0 p-1" type="button">
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
                        {source.excerpt || 'No excerpt available'}
                      </p>
                      {source.page && (
                        <p className={`text-xs mt-2 ${isDarkMode ? 'text-gray-500' : 'text-gray-500'}`}>
                          Page {source.page}{source.section ? `, ${source.section}` : ''}
                        </p>
                      )}
                    </div>

                    {documentLink && (
                      <a
                        href={documentLink}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center gap-2 mt-3 px-4 py-2 text-sm text-white bg-green-600 hover:bg-green-700 rounded-lg font-medium transition-colors"
                      >
                        <ExternalLink className="w-4 h-4" />
                        Read Full Document
                      </a>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default SourceCitation;
