import React, { useState } from 'react';
import { FileText, ChevronDown, ChevronUp, ExternalLink, CheckCircle } from 'lucide-react';

const SourceCitation = ({ sources = [] }) => {
  const [expandedSource, setExpandedSource] = useState(null);

  const toggleSource = (index) => {
    setExpandedSource(expandedSource === index ? null : index);
  };

  if (!sources || sources.length === 0) return null;

  return (
    <div className="mt-6 pt-6 border-t border-gray-200">
      <div className="flex items-center gap-2 mb-4">
        <FileText className="w-5 h-5 text-green-600" />
        <h3 className="text-sm font-semibold text-gray-900 uppercase tracking-wide">
          Sources & Citations
        </h3>
      </div>

      <div className="space-y-3">
        {sources.map((source, index) => (
          <div 
            key={index}
            className="bg-white border-l-4 border-yellow-400 rounded-lg overflow-hidden"
          >
            {/* Source Header */}
            <div 
              className="p-4 cursor-pointer hover:bg-gray-50 transition-colors"
              onClick={() => toggleSource(index)}
            >
              <div className="flex items-start justify-between gap-3">
                <div className="flex items-start gap-3 flex-1">
                  <div className="w-10 h-10 bg-yellow-100 rounded-lg flex items-center justify-center flex-shrink-0">
                    <FileText className="w-5 h-5 text-yellow-600" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <h4 className="font-semibold text-gray-900">{source.title}</h4>
                      {source.verified && (
                        <span className="flex items-center gap-1 text-xs text-green-600">
                          <CheckCircle className="w-3 h-3" />
                          VERIFIED
                        </span>
                      )}
                    </div>
                    <p className="text-sm text-gray-600">{source.description}</p>
                  </div>
                </div>
                <button className="flex-shrink-0 p-1">
                  {expandedSource === index ? (
                    <ChevronUp className="w-5 h-5 text-gray-400" />
                  ) : (
                    <ChevronDown className="w-5 h-5 text-gray-400" />
                  )}
                </button>
              </div>
            </div>

            {/* Expanded Content */}
            {expandedSource === index && (
              <div className="px-4 pb-4 border-t border-gray-100">
                <div className="bg-gray-50 rounded-lg p-4 mt-3">
                  <p className="text-sm text-gray-700 font-mono leading-relaxed">
                    "{source.excerpt}"
                  </p>
                  {source.page && (
                    <p className="text-xs text-gray-500 mt-2">
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
        ))}
      </div>
    </div>
  );
};

export default SourceCitation;