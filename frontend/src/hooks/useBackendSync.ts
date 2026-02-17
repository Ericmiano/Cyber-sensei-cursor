import { useEffect } from 'react';
import { useBackendProgress } from './useBackendProgress';
import { useBackendAchievements } from './useBackendAchievements';
import { useBackendChat } from './useBackendChat';

/**
 * Auto-sync hook that periodically syncs data with backend
 */
export const useBackendSync = (intervalMs: number = 5 * 60 * 1000) => {
  const progress = useBackendProgress();
  const achievements = useBackendAchievements();
  const chat = useBackendChat();

  useEffect(() => {
    // Initial sync is handled by individual hooks
    
    // Set up periodic sync
    const interval = setInterval(() => {
      // Silently refetch data in background
      progress.updateStreak();
      achievements.refetch();
    }, intervalMs);

    return () => clearInterval(interval);
  }, [intervalMs]);

  return {
    progress,
    achievements,
    chat,
  };
};
