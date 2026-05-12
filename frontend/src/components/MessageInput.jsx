import React, { useState, useRef, useEffect } from 'react';
import PropTypes from 'prop-types';

function MessageInput({ onSend, loading }) {
  const [input, setInput] = useState('');
  const textareaRef = useRef(null);

  const handleSend = () => {
    if (input.trim() && !loading) {
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
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 150)}px`;
    }
  }, [input]);

  return (
    <div className="border-t border-brown-200 bg-white p-4">
      <div className="flex gap-2 items-end max-w-4xl mx-auto">
        <textarea
          ref={textareaRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Type your message..."
          disabled={loading}
          rows={1}
          className="flex-1 border border-brown-300 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-brown-500 bg-white resize-none min-h-[48px] max-h-[150px]"
        />
        <button
          onClick={handleSend}
          disabled={!input.trim() || loading}
          className={`font-bold py-3 px-6 rounded-lg transition-colors h-[48px] flex items-center justify-center ${
            !input.trim() || loading
              ? 'bg-brown-300 text-brown-100 cursor-not-allowed'
              : 'bg-brown-600 hover:bg-brown-700 text-white'
          }`}
        >
          Send
        </button>
      </div>
    </div>
  );
}

MessageInput.propTypes = {
  onSend: PropTypes.func.isRequired,
  loading: PropTypes.bool,
};

export default MessageInput;
