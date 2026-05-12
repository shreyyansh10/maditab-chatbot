import { apiClient } from './api';

export const getConversations = async (limit = 50) => {
  try {
    const response = await apiClient.get(`/api/conversations?limit=${limit}`);
    return response.data;
  } catch (error) {
    console.error('Error fetching conversations:', error);
    throw error;
  }
};

export const getConversation = async (id) => {
  try {
    const response = await apiClient.get(`/api/conversations/${id}`);
    return response.data;
  } catch (error) {
    console.error(`Error fetching conversation ${id}:`, error);
    throw error;
  }
};

export const createConversation = async (title = "New Conversation") => {
  try {
    const response = await apiClient.post('/api/conversations', { title });
    return response.data;
  } catch (error) {
    console.error('Error creating conversation:', error);
    throw error;
  }
};

export const deleteConversation = async (id) => {
  try {
    await apiClient.delete(`/api/conversations/${id}`);
    return true;
  } catch (error) {
    console.error(`Error deleting conversation ${id}:`, error);
    throw error;
  }
};
