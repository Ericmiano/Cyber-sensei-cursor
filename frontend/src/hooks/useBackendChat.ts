import { useState, useEffect } from 'react';
import { apiClient } from '@/lib/apiClient';
import { ChatMessage } from '@/contexts/ChatHistoryContext';

export const useBackendChat = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);

  useEffect(() => {
    fetchMessages();
  }, []);

  const fetchMessages = async () => {
    try {
      const response = await apiClient.get('/chat/history');
      setMessages(response.data);
    } catch (error) {
      console.error('Failed to fetch chat history:', error);
    }
  };

  const addMessage = async (message: Omit<ChatMessage, 'id' | 'timestamp'>) => {
    try {
      const response = await apiClient.post('/chat/message', message);
      setMessages(prev => [...prev, response.data]);
    } catch (error) {
      console.error('Failed to add message:', error);
      // Add locally even if backend fails
      const newMessage: ChatMessage = {
        ...message,
        id: Date.now().toString(),
        timestamp: new Date().toISOString(),
      };
      setMessages(prev => [...prev, newMessage]);
    }
  };

  const clearHistory = async () => {
    try {
      await apiClient.delete('/chat/history');
      setMessages([]);
    } catch (error) {
      console.error('Failed to clear history:', error);
    }
  };

  return {
    messages,
    addMessage,
    clearHistory,
  };
};
