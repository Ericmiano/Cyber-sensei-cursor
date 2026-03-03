import { useState, useEffect, useCallback } from 'react';
import { apiClient } from '@/lib/apiClient';
import { ChatMessage } from '@/contexts/ChatHistoryContext';

function toChatMessage(msg: { id: string; role: string; content: string; created_at: string }): ChatMessage {
  return {
    id: msg.id,
    role: msg.role as 'user' | 'assistant',
    content: msg.content,
    timestamp: msg.created_at,
  };
}

export const useBackendChat = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const fetchMessages = useCallback(async () => {
    try {
      const response = await apiClient.get('/chat/history');
      const list = Array.isArray(response.data) ? response.data : [];
      setMessages(list.map(toChatMessage));
    } catch (error) {
      console.error('Failed to fetch chat history:', error);
    }
  }, []);

  useEffect(() => {
    fetchMessages();
  }, [fetchMessages]);

  const addMessage = async (message: Omit<ChatMessage, 'id' | 'timestamp'>) => {
    if (message.role !== 'user') return;

    const userMsg: ChatMessage = {
      ...message,
      id: `temp-${Date.now()}`,
      timestamp: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, userMsg]);
    setIsLoading(true);

    try {
      const response = await apiClient.post('/chat/send', { message: message.content });
      const { user_message, assistant_message } = response.data;

      setMessages((prev) =>
        prev
          .filter((m) => m.id !== userMsg.id)
          .concat([toChatMessage(user_message), toChatMessage(assistant_message)])
      );
    } catch (error) {
      console.error('Failed to send message:', error);
      setMessages((prev) => prev.filter((m) => m.id !== userMsg.id));
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const clearHistory = async () => {
    try {
      await apiClient.delete('/chat/history');
      setMessages([]);
    } catch (error) {
      console.error('Failed to clear history:', error);
      setMessages([]);
    }
  };

  return {
    messages,
    addMessage,
    clearHistory,
    isLoading,
  };
};
