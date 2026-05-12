import axios from 'axios';

export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 120000,
});

// Request interceptor for logging
apiClient.interceptors.request.use((request) => {
  console.log('API Request:', request.method?.toUpperCase(), request.url);
  return request;
});

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.message);
    return Promise.reject(error);
  }
);

export const sendMessage = async (message, conversationId = null) => {
  const payload = { message };
  if (conversationId) {
    payload.conversation_id = conversationId;
  }
  
  const response = await apiClient.post('/api/chat/message', payload);
  // The backend returns { response, conversation_id, user_message_id, assistant_message_id }
  return response.data;
};

export const sendMessageStream = async (message, conversationId = null, callbacks = {}) => {
  const { onToken, onDone, onError, onConversationId } = callbacks;
  
  const payload = { message };
  if (conversationId) {
    payload.conversation_id = conversationId;
  }
  
  const baseURL = import.meta.env.VITE_API_BASE_URL || '';
  const url = `${baseURL}/api/chat/stream`;
  
  console.log('Starting SSE stream:', url);
  
  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';
    
    while (true) {
      const { done, value } = await reader.read();
      
      if (done) {
        console.log('Stream complete');
        break;
      }
      
      // Decode chunk and add to buffer
      buffer += decoder.decode(value, { stream: true });
      
      // Process complete SSE messages
      const lines = buffer.split('\n');
      buffer = lines.pop() || ''; // Keep incomplete line in buffer
      
      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.slice(6); // Remove 'data: ' prefix
          
          try {
            const event = JSON.parse(data);
            
            switch (event.type) {
              case 'conversation_id':
                console.log('Received conversation_id:', event.conversation_id);
                if (onConversationId) {
                  onConversationId(event.conversation_id);
                }
                break;
                
              case 'token':
                if (onToken) {
                  onToken(event.content);
                }
                break;
                
              case 'done':
                console.log('Stream done:', event);
                if (onDone) {
                  onDone({
                    conversation_id: event.conversation_id,
                    message_id: event.message_id
                  });
                }
                break;
                
              case 'error':
                console.error('Stream error:', event.content);
                if (onError) {
                  onError(new Error(event.content));
                }
                break;
            }
          } catch (e) {
            console.error('Failed to parse SSE event:', e, data);
          }
        }
      }
    }
  } catch (error) {
    console.error('Stream error:', error);
    if (onError) {
      onError(error);
    }
    throw error;
  }
};
