// Location: frontend/app/components/TokenRenderer.tsx
'use client';

import React from 'react';

interface TokenRendererProps {
  text: string;
  onCitationClick: (index: number) => void;
}

export const TokenRenderer: React.FC<TokenRendererProps> = ({ text, onCitationClick }) => {
  if (!text) {
    return (
      <p className="text-sm text-slate-500 italic animate-pulse">
        Awaiting playbook generation stream...
      </p>
    );
  }

  // Regex to extract citation formats: [Doc-X] or [Doc X]
  const tokenRegex = /(\[Doc[- ]\d+\])/g;

  // 1. First split by the [BREAK] keyword streamed from backend/app/main.py
  const rawSegments = text.split('[BREAK]');

  // Helper function to convert raw text segments with citations into React elements
  const renderLineWithCitations = (lineText: string, segmentKey: number) => {
    const parts = lineText.split(tokenRegex);
    
    return (
      <span key={segmentKey}>
        {parts.map((part, index) => {
          if (tokenRegex.test(part)) {
            const match = part.match(/\d+/);
            const docIndex = match ? parseInt(match[0], 10) - 1 : 0;
            return (
              <button
                key={index}
                onClick={() => onCitationClick(docIndex)}
                className="inline-flex items-center px-2 py-0.5 mx-1 rounded text-[10px] font-bold bg-indigo-500/20 text-indigo-400 border border-indigo-500/30 hover:bg-indigo-500/40 hover:text-indigo-200 transition-all cursor-pointer"
              >
                📄 Ref-{docIndex + 1}
              </button>
            );
          }
          return <span key={index}>{part}</span>;
        })}
      </span>
    );
  };

  return (
    <div className="space-y-4">
      {rawSegments.map((segment, index) => {
        const trimmed = segment.trim();
        if (!trimmed) return null;

        // Check if the segment represents a numbered step
        const isListItem = /^\d+\.\s/.test(trimmed) || /^\d+\s/.test(trimmed);

        return (
          <div 
            key={index} 
            className={`text-sm leading-relaxed text-slate-200 transition-all duration-300 ${
              isListItem 
                ? 'pl-4 border-l-2 border-indigo-500/40 bg-indigo-500/5 p-4 rounded-r-lg shadow-sm' 
                : 'p-2'
            }`}
          >
            {renderLineWithCitations(trimmed, index)}
          </div>
        );
      })}
    </div>
  );
};