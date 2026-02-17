import { useState, useEffect } from 'react';
import { apiClient } from '@/lib/apiClient';

interface Module {
  id: string;
  title: string;
  description: string;
  icon: string;
  category: string;
  difficulty: string;
  estimatedHours: number;
  totalLessons: number;
  completedLessons: number;
  orderIndex: number;
}

interface Lesson {
  id: string;
  moduleId: string;
  title: string;
  description: string;
  content: string;
  estimatedMinutes: number;
  orderIndex: number;
  completed: boolean;
}

export const useBackendTraining = () => {
  const [modules, setModules] = useState<Module[]>([]);
  const [lessons, setLessons] = useState<Lesson[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchModules();
    fetchLessons();
  }, []);

  const fetchModules = async () => {
    try {
      const response = await apiClient.get('/training/modules');
      setModules(response.data);
    } catch (error) {
      console.error('Failed to fetch modules:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchLessons = async () => {
    try {
      const response = await apiClient.get('/training/lessons');
      setLessons(response.data);
    } catch (error) {
      console.error('Failed to fetch lessons:', error);
    }
  };

  const completeLesson = async (lessonId: string) => {
    try {
      await apiClient.post(`/training/lessons/${lessonId}/complete`);
      // Refresh data
      fetchModules();
      fetchLessons();
    } catch (error) {
      console.error('Failed to complete lesson:', error);
    }
  };

  return {
    modules,
    lessons,
    loading,
    completeLesson,
  };
};
