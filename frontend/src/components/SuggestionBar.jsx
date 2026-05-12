import React from 'react';

function SuggestionBar({ suggestions, onSuggestionClick, loading, conversationId }) {
  if (loading) {
    return (
      <div className="flex gap-2 flex-wrap animate-pulse">
        <div className="h-9 w-32 bg-gray-100 rounded-full"></div>
        <div className="h-9 w-40 bg-gray-100 rounded-full"></div>
        <div className="h-9 w-36 bg-gray-100 rounded-full"></div>
      </div>
    );
  }

  if (!suggestions || suggestions.length === 0) {
    return null;
  }

  return (
    <div className="flex gap-2 flex-wrap animate-fade-in">
      {suggestions.map((suggestion, index) => (
        <button
          key={`${conversationId}-${index}-${suggestion}`}
          onClick={() => onSuggestionClick(suggestion)}
          aria-label={`Suggestion: ${suggestion}`}
          className="px-4 py-2 bg-white hover:bg-gray-50 text-gray-700 text-sm rounded-full border border-gray-200 transition-smooth hover:border-gray-300 active:scale-[0.98] shadow-sm"
        >
          {suggestion}
        </button>
      ))}
    </div>
  );
}

export default SuggestionBar;
