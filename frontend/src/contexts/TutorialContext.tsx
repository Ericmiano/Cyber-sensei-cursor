import React, { createContext, useContext, useState, useCallback, useEffect } from "react";

export interface TutorialStep {
  id: string;
  title: string;
  description: string;
  targetSelector?: string;
  placement?: "top" | "bottom" | "left" | "right" | "center";
  action?: string;
  highlight?: boolean;
}

const TUTORIAL_STEPS: TutorialStep[] = [
  {
    id: "welcome",
    title: "Welcome to Cyber Sensei! 🛡️",
    description: "Let's take a quick tour to help you get started on your cybersecurity journey. Swipe left/right or use arrows to navigate.",
    placement: "center",
  },
  {
    id: "sidebar",
    title: "Navigation Sidebar",
    description: "Use the sidebar to navigate between different sections. Tap the menu icon to toggle it on mobile.",
    targetSelector: "[data-tutorial='sidebar']",
    placement: "right",
    highlight: true,
  },
  {
    id: "dashboard",
    title: "Your Dashboard",
    description: "Track your progress, view achievements, and see daily challenges here.",
    targetSelector: "[data-tutorial='dashboard-link']",
    placement: "right",
    highlight: true,
  },
  {
    id: "chat",
    title: "AI Chat Interface",
    description: "Ask Cyber Sensei anything about cybersecurity. Get personalized guidance and answers.",
    targetSelector: "[data-tutorial='chat-link']",
    placement: "right",
    highlight: true,
  },
  {
    id: "training",
    title: "Training Modules",
    description: "Complete structured lessons and hands-on exercises to build your skills.",
    targetSelector: "[data-tutorial='training-link']",
    placement: "right",
    highlight: true,
  },
  {
    id: "xp-system",
    title: "XP & Leveling System",
    description: "Earn XP by completing lessons, quizzes, and exercises. Level up to unlock new content and achievements!",
    placement: "center",
  },
  {
    id: "streaks",
    title: "Daily Streaks 🔥",
    description: "Maintain your learning streak by training every day. Longer streaks earn bonus XP rewards!",
    placement: "center",
  },
  {
    id: "achievements",
    title: "Achievements & Badges",
    description: "Unlock badges as you progress. Complete challenges, maintain streaks, and master topics to earn them all.",
    placement: "center",
  },
  {
    id: "settings",
    title: "Customize Your Experience",
    description: "Visit Settings to personalize themes, notifications, and keyboard shortcuts.",
    placement: "center",
  },
  {
    id: "profile",
    title: "Your Profile",
    description: "Create an account to save your progress across devices and compete on leaderboards.",
    placement: "center",
  },
  {
    id: "complete",
    title: "You're All Set! 🎉",
    description: "Start your journey by exploring the training modules or chatting with your AI mentor. Good luck, cyber warrior!",
    placement: "center",
    action: "Start Learning",
  },
];

interface TutorialContextType {
  isActive: boolean;
  currentStep: number;
  steps: TutorialStep[];
  currentStepData: TutorialStep | null;
  startTutorial: () => void;
  endTutorial: () => void;
  nextStep: () => void;
  prevStep: () => void;
  skipTutorial: () => void;
  goToStep: (step: number) => void;
  hasCompletedTutorial: boolean;
  resetTutorial: () => void;
}

const TutorialContext = createContext<TutorialContextType | undefined>(undefined);

const TUTORIAL_STORAGE_KEY = "cyber-sensei-tutorial-completed";

export function TutorialProvider({ children }: { children: React.ReactNode }) {
  const [isActive, setIsActive] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);
  const [hasCompletedTutorial, setHasCompletedTutorial] = useState(() => {
    if (typeof window !== "undefined") {
      return localStorage.getItem(TUTORIAL_STORAGE_KEY) === "true";
    }
    return false;
  });

  const currentStepData = isActive ? TUTORIAL_STEPS[currentStep] : null;

  const startTutorial = useCallback(() => {
    setCurrentStep(0);
    setIsActive(true);
  }, []);

  const endTutorial = useCallback(() => {
    setIsActive(false);
    setHasCompletedTutorial(true);
    localStorage.setItem(TUTORIAL_STORAGE_KEY, "true");
  }, []);

  const skipTutorial = useCallback(() => {
    endTutorial();
  }, [endTutorial]);

  const nextStep = useCallback(() => {
    if (currentStep < TUTORIAL_STEPS.length - 1) {
      setCurrentStep((prev) => prev + 1);
    } else {
      endTutorial();
    }
  }, [currentStep, endTutorial]);

  const prevStep = useCallback(() => {
    if (currentStep > 0) {
      setCurrentStep((prev) => prev - 1);
    }
  }, [currentStep]);

  const goToStep = useCallback((step: number) => {
    if (step >= 0 && step < TUTORIAL_STEPS.length) {
      setCurrentStep(step);
    }
  }, []);

  const resetTutorial = useCallback(() => {
    localStorage.removeItem(TUTORIAL_STORAGE_KEY);
    setHasCompletedTutorial(false);
    setCurrentStep(0);
  }, []);

  // Auto-start tutorial for new users
  useEffect(() => {
    if (!hasCompletedTutorial) {
      const timer = setTimeout(() => {
        startTutorial();
      }, 1500);
      return () => clearTimeout(timer);
    }
  }, [hasCompletedTutorial, startTutorial]);

  return (
    <TutorialContext.Provider
      value={{
        isActive,
        currentStep,
        steps: TUTORIAL_STEPS,
        currentStepData,
        startTutorial,
        endTutorial,
        nextStep,
        prevStep,
        skipTutorial,
        goToStep,
        hasCompletedTutorial,
        resetTutorial,
      }}
    >
      {children}
    </TutorialContext.Provider>
  );
}

export function useTutorial() {
  const context = useContext(TutorialContext);
  if (context === undefined) {
    throw new Error("useTutorial must be used within a TutorialProvider");
  }
  return context;
}
