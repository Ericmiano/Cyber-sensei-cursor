import React, { createContext, useContext, ReactNode } from "react";
import { useBackendProgress } from "@/hooks/useBackendProgress";
import { useBackendAchievements } from "@/hooks/useBackendAchievements";

// Types
export interface Achievement {
  id: string;
  title: string;
  description: string;
  icon: string;
  earnedAt?: Date;
  requirement: {
    type: "lessons" | "xp" | "streak" | "quizzes" | "exercises" | "modules";
    value: number;
  };
}

export interface LessonProgress {
  lessonId: string;
  moduleId: string;
  completed: boolean;
  completedAt?: string;
  quizScore?: number;
  exerciseCompleted?: boolean;
}

export interface ActivityLog {
  id: string;
  type: "lesson" | "quiz" | "exercise" | "achievement" | "chat" | "xp";
  title: string;
  description?: string;
  xpEarned?: number;
  timestamp: string;
}

export interface UserProgress {
  xp: number;
  level: number;
  currentStreak: number;
  longestStreak: number;
  lastActiveDate: string;
  lessonsCompleted: LessonProgress[];
  achievementsEarned: string[];
  totalQuizzesPassed: number;
  totalExercisesCompleted: number;
  totalChatMessages: number;
  activityLog: ActivityLog[];
}

// Achievement definitions
export const ACHIEVEMENTS: Achievement[] = [
  { id: "first_steps", title: "First Steps", description: "Complete your first lesson", icon: "🎯", requirement: { type: "lessons", value: 1 } },
  { id: "quick_learner", title: "Quick Learner", description: "Complete 5 lessons", icon: "⚡", requirement: { type: "lessons", value: 5 } },
  { id: "dedicated", title: "Dedicated", description: "Complete 10 lessons", icon: "📚", requirement: { type: "lessons", value: 10 } },
  { id: "streak_starter", title: "Streak Starter", description: "Maintain a 3-day streak", icon: "🔥", requirement: { type: "streak", value: 3 } },
  { id: "streak_master", title: "Streak Master", description: "Maintain a 7-day streak", icon: "🔥", requirement: { type: "streak", value: 7 } },
  { id: "streak_legend", title: "Streak Legend", description: "Maintain a 30-day streak", icon: "⭐", requirement: { type: "streak", value: 30 } },
  { id: "quiz_novice", title: "Quiz Novice", description: "Pass 5 quizzes", icon: "✅", requirement: { type: "quizzes", value: 5 } },
  { id: "quiz_master", title: "Quiz Master", description: "Pass 25 quizzes", icon: "🏆", requirement: { type: "quizzes", value: 25 } },
  { id: "hands_on", title: "Hands-On", description: "Complete 5 exercises", icon: "🛠️", requirement: { type: "exercises", value: 5 } },
  { id: "practitioner", title: "Practitioner", description: "Complete 15 exercises", icon: "💪", requirement: { type: "exercises", value: 15 } },
  { id: "xp_hunter", title: "XP Hunter", description: "Earn 1000 XP", icon: "💎", requirement: { type: "xp", value: 1000 } },
  { id: "xp_legend", title: "XP Legend", description: "Earn 5000 XP", icon: "👑", requirement: { type: "xp", value: 5000 } },
  { id: "module_complete", title: "Module Master", description: "Complete a full module", icon: "🎓", requirement: { type: "modules", value: 1 } },
  { id: "curious_mind", title: "Curious Mind", description: "Send 50 chat messages", icon: "🧠", requirement: { type: "lessons", value: 50 } },
];

interface UserProgressContextType {
  progress: UserProgress;
  addXP: (amount: number, reason: string) => void;
  completeLesson: (lessonId: string, moduleId: string) => void;
  passQuiz: (lessonId: string, score: number) => void;
  completeExercise: (lessonId: string) => void;
  incrementChatMessages: () => void;
  getLevel: () => number;
  getXPForNextLevel: () => number;
  getCurrentLevelXP: () => number;
  getAchievements: () => (Achievement & { earned: boolean })[];
  updateStreak: () => void;
  resetProgress: () => void;
}

const UserProgressContext = createContext<UserProgressContextType | undefined>(undefined);

export function UserProgressProvider({ children }: { children: ReactNode }) {
  const backendProgress = useBackendProgress();
  const { achievements: backendAchievements } = useBackendAchievements();

  const getAchievements = () => {
    return ACHIEVEMENTS.map(a => ({
      ...a,
      earned: backendProgress.progress.achievementsEarned.includes(a.id) || 
              backendAchievements.some(ba => ba.id === a.id),
    }));
  };

  return (
    <UserProgressContext.Provider value={{
      ...backendProgress,
      getAchievements,
    }}>
      {children}
    </UserProgressContext.Provider>
  );
}

export function useUserProgress() {
  const context = useContext(UserProgressContext);
  if (!context) {
    throw new Error("useUserProgress must be used within UserProgressProvider");
  }
  return context;
}
