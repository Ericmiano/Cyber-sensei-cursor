import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

export interface ThemeSettings {
  mode: 'dark' | 'light';
  primaryColor: string;
  accentColor: string;
  animationIntensity: number;
}

export interface AgentPersonality {
  formality: number; // 0 = casual, 100 = professional
  teachingStyle: number; // 0 = encouraging, 100 = challenging
  humorLevel: number; // 0 = serious, 100 = playful
  responseLength: number; // 0 = concise, 100 = detailed
  technicalDepth: number; // 0 = beginner, 100 = expert
}

interface ThemeContextType {
  theme: ThemeSettings;
  setTheme: (theme: ThemeSettings) => void;
  personality: AgentPersonality;
  setPersonality: (personality: AgentPersonality) => void;
  toggleMode: () => void;
}

const defaultTheme: ThemeSettings = {
  mode: 'dark',
  primaryColor: 'cyan',
  accentColor: 'magenta',
  animationIntensity: 70,
};

const defaultPersonality: AgentPersonality = {
  formality: 50,
  teachingStyle: 50,
  humorLevel: 40,
  responseLength: 60,
  technicalDepth: 50,
};

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [theme, setThemeState] = useState<ThemeSettings>(() => {
    const saved = localStorage.getItem('cyber-sensei-theme');
    return saved ? JSON.parse(saved) : defaultTheme;
  });

  const [personality, setPersonalityState] = useState<AgentPersonality>(() => {
    const saved = localStorage.getItem('cyber-sensei-personality');
    return saved ? JSON.parse(saved) : defaultPersonality;
  });

  useEffect(() => {
    localStorage.setItem('cyber-sensei-theme', JSON.stringify(theme));
    
    // Apply theme mode to document
    if (theme.mode === 'dark') {
      document.documentElement.classList.remove('light');
    } else {
      document.documentElement.classList.add('light');
    }
  }, [theme]);

  useEffect(() => {
    localStorage.setItem('cyber-sensei-personality', JSON.stringify(personality));
  }, [personality]);

  const setTheme = (newTheme: ThemeSettings) => {
    setThemeState(newTheme);
  };

  const setPersonality = (newPersonality: AgentPersonality) => {
    setPersonalityState(newPersonality);
  };

  const toggleMode = () => {
    setThemeState(prev => ({
      ...prev,
      mode: prev.mode === 'dark' ? 'light' : 'dark',
    }));
  };

  return (
    <ThemeContext.Provider value={{ theme, setTheme, personality, setPersonality, toggleMode }}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  const context = useContext(ThemeContext);
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
}
