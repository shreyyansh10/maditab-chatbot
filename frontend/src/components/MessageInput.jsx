import React, { useState, useRef, useEffect } from 'react';
import PropTypes from 'prop-types';

function MessageInput({ onSend, loading, isStreaming }) {
  const [input, setInput] = useState('');
  const textareaRef = useRef(null);

  const handleSend = () => {
    if (input.trim() && !loading && !isStreaming) {
      onSend(input.trim());
      setInput('');
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 200)}px`;
    }
  }, [input]);

  const isDisabled = !input.trim() || loading || isStreaming;

  return (
    <div className="bg-white border border-gray-200 rounded-2xl shadow-sm p-2 transition-smooth focus-within:border-brown-500 focus-within:shadow-md">
      <div className="flex gap-2 items-end">
        <textarea
          ref={textareaRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Message..."
          disabled={loading || isStreaming}
          rows={1}
          aria-label="Message input"
          className="flex-1 px-3 py-2.5 text-[15px] focus:outline-none bg-transparent resize-none min-h-[44px] max-h-[200px] disabled:opacity-50"
        />
        <button
          onClick={handleSend}
          disabled={isDisabled}
          aria-label="Send message"
          className={`px-4 py-2.5 rounded-xl font-medium transition-smooth flex items-center justify-center min-w-[70px] ${
            isDisabled
              ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
              : 'bg-brown-600 hover:bg-brown-700 text-white shadow-sm active:scale-[0.98]'
          }`}
        >
          {isStreaming ? (
            <span className="text-sm">...</span>
          ) : (
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
            </svg>
          )}
        </button>
      </div>
    </div>
  );
}

MessageInput.propTypes = {
  onSend: PropTypes.func.isRequired,
  loading: PropTypes.bool,
  isStreaming: PropTypes.bool,
};

export default MessageInput;
