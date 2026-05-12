import React, { useState, useEffect, useRef } from 'react';
import MessageList from './MessageList';
import MessageInput from './MessageInput';
import SuggestionBar from './SuggestionBar';
import { sendMessage, sendMessageStream } from '../services/api';
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
  const [isStreaming, setIsStreaming] = useState(false);
  const messagesEndRef = useRef(null);
  
  // Track current conversation to prevent stale suggestions
  const currentConversationRef = useRef(conversationId);
  const suggestionRequestIdRef = useRef(0);
  const streamingMessageIdRef = useRef(null);

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
          
          // Load suggestions after messages load (only if conversation has messages)
          setTimeout(() => {
            if (currentConversationRef.current === conversationId) {
              fetchSuggestions(conversationId);
            }
          }, 100);
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
    if (!content.trim() || isStreaming) return;

    // Clear suggestions immediately before sending
    console.log('Clearing suggestions before sending message');
    setSuggestions([]);
    setSuggestionsLoading(false);

    // 1. Optimistic Update - Add user message
    const userMessage = { role: 'user', content, id: Date.now().toString() };
    setMessages((prev) => [...prev, userMessage]);
    
    // 2. Add temporary streaming assistant message
    const streamingId = `streaming-${Date.now()}`;
    streamingMessageIdRef.current = streamingId;
    setMessages((prev) => [
      ...prev,
      { role: 'assistant', content: '', id: streamingId, isStreaming: true }
    ]);
    
    setIsStreaming(true);
    setLoading(true);

    try {
      let streamedContent = '';
      let finalConversationId = conversationId;
      
      // 3. Try streaming first
      await sendMessageStream(content, conversationId, {
        onConversationId: (convId) => {
          console.log('Stream: New conversation created:', convId);
          finalConversationId = convId;
          currentConversationRef.current = convId;
          
          if (!conversationId) {
            window.dispatchEvent(new CustomEvent('conversationCreated', {
              detail: { conversationId: convId }
            }));
          }
        },
        
        onToken: (token) => {
          streamedContent += token;
          
          // Update streaming message
          setMessages((prev) =>
            prev.map((msg) =>
              msg.id === streamingId
                ? { ...msg, content: streamedContent }
                : msg
            )
          );
        },
        
        onDone: (data) => {
          console.log('Stream complete:', data);
          
          // Finalize message
          setMessages((prev) =>
            prev.map((msg) =>
              msg.id === streamingId
                ? { ...msg, id: data.message_id, isStreaming: false }
                : msg
            )
          );
          
          // Fetch suggestions
          setTimeout(() => {
            if (finalConversationId) {
              fetchSuggestions(finalConversationId);
            }
          }, 100);
        },
        
        onError: (error) => {
          console.error('Stream error, falling back to normal API:', error);
          throw error; // Trigger fallback
        }
      });
      
    } catch (error) {
      console.error('Streaming failed, using fallback:', error);
      
      // Remove streaming message
      setMessages((prev) => prev.filter((msg) => msg.id !== streamingId));
      
      // Fallback to normal API
      try {
        const result = await sendMessage(content, conversationId);
        
        setMessages((prev) => [
          ...prev,
          { role: 'assistant', content: result.response, id: result.assistant_message_id }
        ]);
        
        if (!conversationId && result.conversation_id) {
          currentConversationRef.current = result.conversation_id;
          window.dispatchEvent(new CustomEvent('conversationCreated', {
            detail: { conversationId: result.conversation_id }
          }));
        }
        
        setTimeout(() => {
          const targetConversationId = result.conversation_id || conversationId;
          if (targetConversationId) {
            fetchSuggestions(targetConversationId);
          }
        }, 100);
        
      } catch (fallbackError) {
        console.error('Fallback also failed:', fallbackError);
        
        let errorMessage = 'Sorry, there was an error processing your request.';
        if (fallbackError.response?.data?.detail) {
          errorMessage = `Error: ${fallbackError.response.data.detail}`;
        }
        
        setMessages((prev) => [
          ...prev,
          { role: 'assistant', content: errorMessage, isError: true }
        ]);
        
        alert('Failed to send message. Please try again.');
      }
    } finally {
      setIsStreaming(false);
      setLoading(false);
      streamingMessageIdRef.current = null;
    }
  };

  const fetchSuggestions = async (convId) => {
    // Don't fetch for empty conversations or while streaming
    if (!convId || isStreaming || initialLoading) {
      return;
    }
    
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
    <div className="flex flex-col h-full bg-white w-full">
      {/* Minimal Header */}
      <div className="border-b border-gray-200 px-6 py-4 bg-white flex-shrink-0">
        <div className="max-w-[850px] mx-auto">
          <h1 className="text-base font-semibold text-gray-900">Chat</h1>
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 overflow-hidden flex flex-col relative">
        {initialLoading ? (
          <div className="flex-1 flex items-center justify-center">
            <div className="flex flex-col items-center gap-3">
              <div className="w-6 h-6 border-2 border-gray-200 border-t-brown-600 rounded-full animate-spin"></div>
              <p className="text-sm text-gray-500">Loading...</p>
            </div>
          </div>
        ) : null}

        <div className="flex-1 overflow-y-auto scrollbar-minimal">
          <div className="max-w-[850px] mx-auto px-6 py-8">
            <MessageList messages={messages} isStreaming={isStreaming} />
            <div ref={messagesEndRef} />
          </div>
        </div>
      </div>

      {/* Input Area */}
      <div className="border-t border-gray-200 bg-white">
        <div className="max-w-[850px] mx-auto px-6 py-6">
          {/* Suggestions */}
          {!loading && !initialLoading && (suggestions.length > 0 || suggestionsLoading) && (
            <div className="mb-4">
              <SuggestionBar 
                suggestions={suggestions} 
                onSuggestionClick={handleSuggestionClick}
                loading={suggestionsLoading}
                conversationId={conversationId}
              />
            </div>
          )}
          
          <MessageInput onSend={handleSend} loading={loading || initialLoading} isStreaming={isStreaming} />
          
          <p className="text-xs text-center text-gray-400 mt-4">
            AI can make mistakes. Verify important information.
          </p>
        </div>
      </div>
    </div>
  );
}

export default ChatInterface;
