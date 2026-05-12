import React, { useState, useEffect } from 'react';
import ConversationList from './ConversationList';
import { getConversations, deleteConversation, createConversation } from '../services/conversationApi';

function Sidebar({ currentConversationId, onSelectConversation }) {
  const [conversations, setConversations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

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

    // Listen for custom event when a new conversation is created by the backend
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
    if (window.confirm('Are you sure you want to delete this conversation?')) {
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

  return (
    <div className="w-64 bg-brown-900 h-full flex flex-col border-r border-brown-800 shadow-xl z-20">
      {/* New Chat Button */}
      <div className="p-4">
        <button
          onClick={handleNewChat}
          className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-brown-700 hover:bg-brown-600 text-white rounded-lg border border-brown-600 transition-all duration-200 font-medium shadow-sm active:scale-95"
        >
          <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          New Chat
        </button>
      </div>

      {/* Conversations Section */}
      <div className="flex-1 flex flex-col min-h-0">
        <div className="px-4 py-2">
          <h2 className="text-xs font-bold text-brown-400 uppercase tracking-widest px-2">Recent Chats</h2>
        </div>
        
        {loading && conversations.length === 0 ? (
          <div className="flex-1 flex items-center justify-center">
            <div className="animate-pulse flex flex-col items-center">
              <div className="h-2 w-24 bg-brown-700 rounded mb-2"></div>
              <div className="h-2 w-16 bg-brown-800 rounded"></div>
            </div>
          </div>
        ) : error ? (
          <div className="px-4 py-4 text-xs text-red-400 text-center italic">{error}</div>
        ) : (
          <ConversationList
            conversations={conversations}
            currentId={currentConversationId}
            onSelect={onSelectConversation}
            onDelete={handleDelete}
          />
        )}
      </div>

      {/* User / Settings Footer (Optional) */}
      <div className="p-4 border-t border-brown-800 bg-brown-900/50">
        <div className="flex items-center gap-3 px-2">
          <div className="w-8 h-8 rounded-full bg-brown-500 flex items-center justify-center text-white font-bold text-xs shadow-inner">
            U
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-white truncate">User Account</p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Sidebar;
