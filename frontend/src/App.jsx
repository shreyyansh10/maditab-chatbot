import React, { useState, useEffect } from 'react';
import ChatInterface from './components/ChatInterface';
import Sidebar from './components/Sidebar';

function App() {
  const [currentConversationId, setCurrentConversationId] = useState(null);

  useEffect(() => {
    const handleConversationCreated = (event) => {
      if (event.detail && event.detail.conversationId) {
        setCurrentConversationId(event.detail.conversationId);
      }
    };

    window.addEventListener('conversationCreated', handleConversationCreated);
    return () => window.removeEventListener('conversationCreated', handleConversationCreated);
  }, []);

  return (
    <div className="flex h-screen w-full bg-offwhite overflow-hidden font-sans">
      <Sidebar 
        currentConversationId={currentConversationId} 
        onSelectConversation={setCurrentConversationId} 
      />
      <main className="flex-1 relative flex flex-col min-w-0">
        <ChatInterface conversationId={currentConversationId} />
      </main>
    </div>
  );
}

export default App;
