import React from 'react';

function SuggestionBar({ suggestions, onSuggestionClick, loading, conversationId }) {
  if (loading) {
    return (
      <div className="flex gap-2 flex-wrap animate-pulse">
        <div className="h-9 w-32 bg-brown-100 rounded-full"></div>
        <div className="h-9 w-40 bg-brown-100 rounded-full"></div>
        <div className="h-9 w-36 bg-brown-100 rounded-full"></div>
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
          className="px-4 py-2 bg-brown-50 hover:bg-brown-100 text-brown-700 text-sm rounded-full border border-brown-200 transition-all duration-200 hover:shadow-md hover:scale-105 active:scale-95"
        >
          {suggestion}
        </button>
      ))}
    </div>
  );
}

export default SuggestionBar;
