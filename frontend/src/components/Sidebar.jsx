import React, { useState, useEffect } from 'react';
import ConversationList from './ConversationList';
import { getConversations, deleteConversation, createConversation } from '../services/conversationApi';

function Sidebar({ currentConversationId, onSelectConversation }) {
  const [conversations, setConversations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');

  const fetchConversations = async () => {
    try {
      setLoading(true);
      const data = await getConversations();
      setConversations(data);
      setError(null);
    } catch (err) {
      console.error('Failed to fetch conversations:', err);
      setError('Could not load chats');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchConversations();

    const handleConversationCreated = () => {
      fetchConversations();
    };

    window.addEventListener('conversationCreated', handleConversationCreated);
    return () => window.removeEventListener('conversationCreated', handleConversationCreated);
  }, []);

  const handleNewChat = () => {
    onSelectConversation(null);
  };

  const handleDelete = async (id) => {
    if (window.confirm('Delete this conversation?')) {
      try {
        await deleteConversation(id);
        setConversations(prev => prev.filter(c => c.id !== id));
        if (currentConversationId === id) {
          onSelectConversation(null);
        }
      } catch (err) {
        alert('Failed to delete conversation');
      }
    }
  };

  const filteredConversations = conversations.filter(conv =>
    conv.title?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="w-[280px] bg-gray-50 h-full flex flex-col border-r border-gray-200">
      {/* Header with New Chat */}
      <div className="p-4 border-b border-gray-200">
        <button
          onClick={handleNewChat}
          aria-label="Start new chat"
          className="w-full flex items-center justify-center gap-2 px-4 py-2.5 bg-brown-600 hover:bg-brown-700 text-white rounded-xl transition-smooth font-medium shadow-sm active:scale-[0.98]"
        >
          <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          New Chat
        </button>
      </div>

      {/* Search Bar */}
      <div className="px-4 pt-4 pb-2">
        <div className="relative">
          <input
            type="text"
            placeholder="Search chats..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full px-3 py-2 pl-9 text-sm bg-white border border-gray-200 rounded-lg focus:outline-none focus:border-brown-500 focus:ring-1 focus:ring-brown-500 transition-smooth"
          />
          <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </div>
      </div>

      {/* Conversations Section */}
      <div className="flex-1 flex flex-col min-h-0 overflow-hidden">
        <div className="px-4 py-2">
          <h2 className="text-xs font-semibold text-gray-500 uppercase tracking-wider">Recent</h2>
        </div>
        
        {loading && conversations.length === 0 ? (
          <div className="px-4 space-y-2">
            {[1, 2, 3].map((i) => (
              <div key={i} className="animate-pulse">
                <div className="h-12 bg-gray-200 rounded-xl"></div>
              </div>
            ))}
          </div>
        ) : error ? (
          <div className="px-4 py-4 text-xs text-red-500 text-center">{error}</div>
        ) : (
          <ConversationList
            conversations={filteredConversations}
            currentId={currentConversationId}
            onSelect={onSelectConversation}
            onDelete={handleDelete}
          />
        )}
      </div>

      {/* User Profile Footer */}
      <div className="p-4 border-t border-gray-200">
        <div className="flex items-center gap-3 px-2 py-2 rounded-xl hover:bg-gray-100 transition-smooth cursor-pointer">
          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-brown-500 to-brown-600 flex items-center justify-center text-white font-semibold text-sm shadow-sm">
            U
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-gray-900 truncate">User</p>
            <p className="text-xs text-gray-500">Free Plan</p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Sidebar;
