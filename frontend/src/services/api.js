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
