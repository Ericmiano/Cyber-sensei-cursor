import { useState, useEffect } from 'react';
import { apiClient } from '@/lib/apiClient';
import { UserProgress } from '@/contexts/UserProgressContext';

const defaultProgress: UserProgress = {
  xp: 0,
  level: 1,
  currentStreak: 0,
  longestStreak: 0,
  lastActiveDate: '',
  lessonsCompleted: [],
  achievementsEarned: [],
  totalQuizzesPassed: 0,
  totalExercisesCompleted: 0,
  totalChatMessages: 0,
  activityLog: [],
};

export const useBackendProgress = () => {
  const [progress, setProgress] = useState<UserProgress>(defaultProgress);

  useEffect(() => {
    fetchProgress();
  }, []);

  const fetchProgress = async () => {
    try {
      const response = await apiClient.get('/progress');
      setProgress(response.data);
    } catch (error) {
      console.error('Failed to fetch progress:', error);
    }
  };

  const addXP = async (amount: number, reason: string) => {
    try {
      await apiClient.post('/progress/xp', { amount, reason });
      fetchProgress();
    } catch (error) {
      console.error('Failed to add XP:', error);
    }
  };

  const completeLesson = async (lessonId: string, moduleId: string) => {
    try {
      await apiClient.post('/progress/lesson', { lessonId, moduleId });
      fetchProgress();
    } catch (error) {
      console.error('Failed to complete lesson:', error);
    }
  };

  const passQuiz = async (lessonId: string, score: number) => {
    try {
      await apiClient.post('/progress/quiz', { lessonId, score });
      fetchProgress();
    } catch (error) {
      console.error('Failed to record quiz:', error);
    }
  };

  const completeExercise = async (lessonId: string) => {
    try {
      await apiClient.post('/progress/exercise', { lessonId });
      fetchProgress();
    } catch (error) {
      console.error('Failed to complete exercise:', error);
    }
  };

  const incrementChatMessages = async () => {
    try {
      await apiClient.post('/progress/chat');
      fetchProgress();
    } catch (error) {
      console.error('Failed to increment chat:', error);
    }
  };

  const updateStreak = async () => {
    try {
      await apiClient.post('/progress/streak');
      fetchProgress();
    } catch (error) {
      console.error('Failed to update streak:', error);
    }
  };

  const resetProgress = async () => {
    try {
      await apiClient.delete('/progress');
      setProgress(defaultProgress);
    } catch (error) {
      console.error('Failed to reset progress:', error);
    }
  };

  const getLevel = () => progress.level;
  const getXPForNextLevel = () => 500;
  const getCurrentLevelXP = () => progress.xp % 500;

  return {
    progress,
    addXP,
    completeLesson,
    passQuiz,
    completeExercise,
    incrementChatMessages,
    getLevel,
    getXPForNextLevel,
    getCurrentLevelXP,
    updateStreak,
    resetProgress,
  };
};
