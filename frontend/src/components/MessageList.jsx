import React, { useEffect, useRef } from 'react';
import PropTypes from 'prop-types';

function MessageList({ messages, isStreaming }) {
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  if (messages.length === 0) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <p className="text-gray-400 text-sm">Start a conversation</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {messages.map((msg, idx) => (
        <div
          key={msg.id || idx}
          className={`flex animate-fade-in ${
            msg.role === 'user' ? 'justify-end' : 'justify-start'
          }`}
        >
          <div
            className={`max-w-[80%] rounded-2xl px-5 py-3.5 ${
              msg.role === 'user'
                ? 'bg-brown-600 text-white shadow-sm'
                : msg.isError
                ? 'bg-red-50 text-red-900 border border-red-200'
                : 'bg-gray-50 text-gray-900 border border-gray-200'
            }`}
          >
            <div className="text-[15px] leading-relaxed whitespace-pre-wrap break-words">
              {msg.content}
              {msg.isStreaming && (
                <span className="inline-block w-1 h-5 ml-1 bg-gray-900 animate-pulse rounded-sm"></span>
              )}
            </div>
          </div>
        </div>
      ))}
      <div ref={messagesEndRef} />
    </div>
  );
}

MessageList.propTypes = {
  messages: PropTypes.arrayOf(
    PropTypes.shape({
      role: PropTypes.string.isRequired,
      content: PropTypes.string.isRequired,
      id: PropTypes.string,
      isStreaming: PropTypes.bool,
      isError: PropTypes.bool,
    })
  ).isRequired,
  isStreaming: PropTypes.bool,
};

export default MessageList;
