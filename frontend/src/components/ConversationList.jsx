import React from 'react';

function ConversationList({ 
  conversations, 
  currentId, 
  onSelect, 
  onDelete 
}) {
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffDays = Math.floor((now - date) / (1000 * 60 * 60 * 24));
    
    if (diffDays === 0) return 'Today';
    if (diffDays === 1) return 'Yesterday';
    if (diffDays < 7) return `${diffDays}d ago`;
    
    return date.toLocaleDateString(undefined, { 
      month: 'short', 
      day: 'numeric' 
    });
  };

  if (conversations.length === 0) {
    return (
      <div className="px-4 py-8 text-center text-gray-400 text-sm">
        No conversations yet
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-y-auto scrollbar-minimal px-3 space-y-1">
      {conversations.map((conv) => (
        <div
          key={conv.id}
          onClick={() => onSelect(conv.id)}
          className={`
            group relative px-3 py-3 rounded-xl cursor-pointer transition-smooth
            flex items-center justify-between
            ${currentId === conv.id 
              ? 'bg-brown-50 border border-brown-200' 
              : 'hover:bg-gray-100 border border-transparent'}
          `}
        >
          <div className="flex flex-col min-w-0 flex-1">
            <span className={`text-sm font-medium truncate pr-6 ${
              currentId === conv.id ? 'text-brown-900' : 'text-gray-900'
            }`}>
              {conv.title || "New Chat"}
            </span>
            <span className={`text-xs mt-0.5 ${
              currentId === conv.id ? 'text-brown-600' : 'text-gray-500'
            }`}>
              {formatDate(conv.updated_at)}
            </span>
          </div>
          
          <button
            onClick={(e) => {
              e.stopPropagation();
              onDelete(conv.id);
            }}
            aria-label="Delete conversation"
            className="p-1.5 rounded-lg opacity-0 group-hover:opacity-100 transition-smooth hover:bg-red-50 text-gray-400 hover:text-red-500"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
          </button>
        </div>
      ))}
    </div>
  );
}

export default ConversationList;
