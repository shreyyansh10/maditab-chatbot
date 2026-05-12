import React, { useState, useEffect, useRef } from 'react';
import MessageList from './MessageList';
import MessageInput from './MessageInput';
import SuggestionBar from './SuggestionBar';
import { sendMessage } from '../services/api';
import { getConversation } from '../services/conversationApi';
import { getSuggestions } from '../services/suggestionApi';

const DEFAULT_MESSAGES = [
  { role: 'assistant', content: 'Hello! How can I help you today?' },
];

function ChatInterface({ conversationId }) {
  const [messages, setMessages] = useState(DEFAULT_MESSAGES);
  const [loading, setLoading] = useState(false);
  const [initialLoading, setInitialLoading] = useState(false);
  const [suggestions, setSuggestions] = useState([]);
  const [suggestionsLoading, setSuggestionsLoading] = useState(false);
  const messagesEndRef = useRef(null);
  
  // Track current conversation to prevent stale suggestions
  const currentConversationRef = useRef(conversationId);
  const suggestionRequestIdRef = useRef(0);

  // Auto-scroll to bottom whenever messages change
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  // Load conversation messages when ID changes
  useEffect(() => {
    // Clear suggestions immediately when conversation changes
    console.log('Conversation changed to:', conversationId);
    setSuggestions([]);
    setSuggestionsLoading(false);
    currentConversationRef.current = conversationId;
    
    const loadConversation = async () => {
      if (!conversationId) {
        setMessages(DEFAULT_MESSAGES);
        return;
      }

      try {
        setInitialLoading(true);
        const data = await getConversation(conversationId);
        if (data.messages && data.messages.length > 0) {
          setMessages(data.messages);
        } else {
          setMessages(DEFAULT_MESSAGES);
        }
      } catch (error) {
        console.error('Failed to load conversation history:', error);
        setMessages(DEFAULT_MESSAGES);
      } finally {
        setInitialLoading(false);
      }
    };

    loadConversation();
  }, [conversationId]);

  const handleSend = async (content) => {
    if (!content.trim()) return;

    // Clear suggestions immediately before sending
    console.log('Clearing suggestions before sending message');
    setSuggestions([]);
    setSuggestionsLoading(false);

    // 1. Optimistic Update
    const userMessage = { role: 'user', content, id: Date.now().toString() };
    setMessages((prev) => [...prev, userMessage]);
    setLoading(true);

    try {
      // 2. Send to API
      const result = await sendMessage(content, conversationId);
      
      // 3. Update messages with actual AI response
      setMessages((prev) => [
        ...prev, 
        { role: 'assistant', content: result.response, id: result.assistant_message_id }
      ]);

      // 4. Handle new conversation creation by backend
      if (!conversationId && result.conversation_id) {
        currentConversationRef.current = result.conversation_id;
        window.dispatchEvent(new CustomEvent('conversationCreated', { 
          detail: { conversationId: result.conversation_id } 
        }));
      }

      // 5. Fetch suggestions after assistant response completes
      // Wait a tick to ensure messages are fully updated
      setTimeout(() => {
        const targetConversationId = result.conversation_id || conversationId;
        if (targetConversationId) {
          fetchSuggestions(targetConversationId);
        }
      }, 100);
    } catch (error) {
      console.error('Error sending message:', error);
      
      // 5. Remove optimistic message if it failed and show error (or keep it and mark as failed)
      // For simplicity, we'll just show an error message and keep the history
      let errorMessage = 'Sorry, there was an error processing your request.';
      if (error.response?.data?.detail) {
        errorMessage = `Error: ${error.response.data.detail}`;
      }
      
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: errorMessage, isError: true },
      ]);
      
      alert('Failed to send message. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const fetchSuggestions = async (convId) => {
    // Generate unique request ID
    const requestId = ++suggestionRequestIdRef.current;
    
    console.log(`Loading suggestions for: ${convId} (request #${requestId})`);
    
    try {
      setSuggestionsLoading(true);
      const data = await getSuggestions(convId);
      
      // Only update if this is still the current conversation
      if (currentConversationRef.current === convId && suggestionRequestIdRef.current === requestId) {
        console.log(`Suggestions loaded for: ${convId}`, data.suggestions);
        setSuggestions(data.suggestions || []);
      } else {
        console.log(`Ignoring stale suggestions for: ${convId} (current: ${currentConversationRef.current})`);
      }
    } catch (error) {
      console.error('Failed to fetch suggestions:', error);
      // Only clear if still current conversation
      if (currentConversationRef.current === convId && suggestionRequestIdRef.current === requestId) {
        setSuggestions([]);
      }
    } finally {
      // Only update loading state if still current
      if (currentConversationRef.current === convId && suggestionRequestIdRef.current === requestId) {
        setSuggestionsLoading(false);
      }
    }
  };

  const handleSuggestionClick = (suggestion) => {
    handleSend(suggestion);
  };

  return (
    <div className="flex flex-col h-full bg-offwhite w-full">
      {/* Header */}
      <div className="border-b border-brown-200 p-4 bg-white shadow-sm flex-shrink-0 z-10">
        <h1 className="text-xl font-bold text-brown-700 text-center flex items-center justify-center gap-2">
          <span className="w-2 h-2 bg-green-500 rounded-full"></span>
          AI Chat Assistant
        </h1>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 overflow-hidden flex flex-col relative">
        {initialLoading ? (
          <div className="flex-1 flex items-center justify-center bg-offwhite/50 backdrop-blur-sm z-10">
            <div className="flex flex-col items-center gap-3">
              <div className="w-10 h-10 border-4 border-brown-200 border-t-brown-600 rounded-full animate-spin"></div>
              <p className="text-brown-500 font-medium">Loading conversation...</p>
            </div>
          </div>
        ) : null}

        <div className="flex-1 overflow-y-auto px-4 py-6 scrollbar-thin scrollbar-thumb-brown-200">
          <div className="max-w-4xl mx-auto space-y-6">
            <MessageList messages={messages} />
            
            {loading && (
              <div className="flex justify-start animate-fade-in">
                <div className="bg-white border border-brown-100 rounded-2xl rounded-tl-none p-4 shadow-sm max-w-[80%]">
                  <div className="flex items-center gap-3">
                    <div className="flex gap-1">
                      <div className="w-2 h-2 bg-brown-400 rounded-full animate-bounce [animation-delay:-0.3s]"></div>
                      <div className="w-2 h-2 bg-brown-400 rounded-full animate-bounce [animation-delay:-0.15s]"></div>
                      <div className="w-2 h-2 bg-brown-400 rounded-full animate-bounce"></div>
                    </div>
                    <span className="text-sm text-brown-500 font-medium italic">Assistant is thinking...</span>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        </div>
      </div>

      {/* Input Area */}
      <div className="bg-white border-t border-brown-100 p-4 shadow-[0_-4px_12px_rgba(0,0,0,0.03)]">
        <div className="max-w-4xl mx-auto space-y-3">
          {/* Suggestions */}
          {!loading && suggestions.length > 0 && (
            <SuggestionBar 
              suggestions={suggestions} 
              onSuggestionClick={handleSuggestionClick}
              loading={suggestionsLoading}
              conversationId={conversationId}
            />
          )}
          
          <MessageInput onSend={handleSend} loading={loading || initialLoading} />
          <p className="text-[10px] text-center text-brown-400 mt-2">
            AI can make mistakes. Verify important information.
          </p>
        </div>
      </div>
    </div>
  );
}

export default ChatInterface;
