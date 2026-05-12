import React from 'react';

function ConversationList({ 
  conversations, 
  currentId, 
  onSelect, 
  onDelete 
}) {
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString(undefined, { 
      month: 'short', 
      day: 'numeric' 
    });
  };

  if (conversations.length === 0) {
    return (
      <div className="px-4 py-8 text-center text-brown-300 text-sm italic">
        No conversations yet. Start a new chat!
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-y-auto py-2 space-y-1">
      {conversations.map((conv) => (
        <div
          key={conv.id}
          onClick={() => onSelect(conv.id)}
          className={`
            group relative px-3 py-3 mx-2 rounded-lg cursor-pointer transition-all duration-200
            flex items-center justify-between
            ${currentId === conv.id 
              ? 'bg-brown-600 text-white shadow-md' 
              : 'text-brown-100 hover:bg-brown-700/50 hover:text-white'}
          `}
        >
          <div className="flex flex-col min-w-0 flex-1">
            <span className="text-sm font-medium truncate pr-6">
              {conv.title || "New Chat"}
            </span>
            <span className={`text-[10px] mt-0.5 ${currentId === conv.id ? 'text-brown-200' : 'text-brown-400'}`}>
              {formatDate(conv.updated_at)}
            </span>
          </div>
          
          <button
            onClick={(e) => {
              e.stopPropagation();
              onDelete(conv.id);
            }}
            className={`
              p-1.5 rounded-md opacity-0 group-hover:opacity-100 transition-opacity
              hover:bg-red-500/20 hover:text-red-300
              ${currentId === conv.id ? 'text-brown-200 hover:text-white' : 'text-brown-400'}
            `}
            title="Delete conversation"
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
