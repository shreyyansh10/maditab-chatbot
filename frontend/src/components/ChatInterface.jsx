import React, { useState } from 'react';
import MessageList from './MessageList';
import MessageInput from './MessageInput';
import { sendMessage } from '../services/api';

function ChatInterface() {
  const [messages, setMessages] = useState([
    { role: 'assistant', content: 'Hello! How can I help you today?' },
  ]);
  const [loading, setLoading] = useState(false);

  const handleSend = async (content) => {
    const userMessage = { role: 'user', content };
    setMessages((prev) => [...prev, userMessage]);
    setLoading(true);

    try {
      const response = await sendMessage(content);
      setMessages((prev) => [...prev, { role: 'assistant', content: response }]);
    } catch (error) {
      let errorMessage = 'Sorry, there was an error processing your request.';
      if (error.response && error.response.data && error.response.data.detail) {
        errorMessage = `Error: ${error.response.data.detail}`;
      } else if (error.message) {
        errorMessage = `Error: ${error.message}`;
      }
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: errorMessage },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full bg-offwhite w-full">
      <div className="border-b border-brown-200 p-4 bg-white shadow-sm flex-shrink-0">
        <h1 className="text-xl font-bold text-brown-700 text-center">AI Chatbot</h1>
      </div>
      <div className="flex-1 overflow-hidden flex flex-col max-w-4xl mx-auto w-full">
        <MessageList messages={messages} />
        {loading && (
          <div className="px-4 pb-4 flex justify-start">
            <div className="bg-white border border-gray-200 rounded-lg p-3">
              <span className="text-sm text-brown-500 italic flex items-center">
                <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-brown-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Assistant is typing...
              </span>
            </div>
          </div>
        )}
      </div>
      <MessageInput onSend={handleSend} loading={loading} />
    </div>
  );
}

export default ChatInterface;
