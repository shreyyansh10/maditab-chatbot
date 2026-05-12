import { apiClient } from './api';

export const getSuggestions = async (conversationId) => {
  if (!conversationId) {
    console.warn('getSuggestions called without conversationId');
    return { suggestions: [] };
  }
  
  console.log(`API: Fetching suggestions for conversation: ${conversationId}`);
  const response = await apiClient.get(`/api/chat/suggestions/${conversationId}`);
  console.log(`API: Received suggestions for conversation: ${conversationId}`, response.data);
  return response.data;
};
