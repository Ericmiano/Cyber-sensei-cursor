import { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { UserPreferences } from '../types';
import { supabase } from '../lib/supabase';
import { useAuth } from './AuthContext';

interface ThemeContextType {
  preferences: UserPreferences | null;
  loading: boolean;
  updatePreferences: (updates: Partial<UserPreferences>) => Promise<void>;
  isDark: boolean;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

const defaultPreferences: Omit<UserPreferences, 'id' | 'user_id' | 'created_at' | 'updated_at'> = {
  theme_mode: 'dark',
  primary_color: '#3b82f6',
  accent_color: '#8b5cf6',
  agent_personality: 'professional',
  agent_name: 'Cyber Sensei',
  font_size: 'medium',
  animations_enabled: true,
};

export function ThemeProvider({ children }: { children: ReactNode }) {
  const { user } = useAuth();
  const [preferences, setPreferences] = useState<UserPreferences | null>(null);
  const [loading, setLoading] = useState(true);
  const [isDark, setIsDark] = useState(true);

  useEffect(() => {
    if (user) {
      loadPreferences();
    } else {
      setPreferences(null);
      setLoading(false);
      applySystemTheme();
    }
  }, [user]);

  useEffect(() => {
    if (preferences) {
      applyTheme(preferences);
    }
  }, [preferences]);

  const applySystemTheme = () => {
    const systemDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    setIsDark(systemDark);
    document.documentElement.classList.toggle('dark', systemDark);
  };

  const loadPreferences = async () => {
    if (!user) return;

    try {
      const { data, error } = await supabase
        .from('user_preferences')
        .select('*')
        .eq('user_id', user.id)
        .single();

      if (error && error.code !== 'PGRST116') { // PGRST116 = no rows returned
        throw error;
      }

      if (data) {
        setPreferences(data);
      } else {
        // Create default preferences
        const newPrefs = {
          ...defaultPreferences,
          user_id: user.id,
        };

        const { data: createdPrefs, error: createError } = await supabase
          .from('user_preferences')
          .insert(newPrefs)
          .select()
          .single();

        if (createError) throw createError;
        setPreferences(createdPrefs);
      }
    } catch (error) {
      console.error('Error loading preferences:', error);
      applySystemTheme();
    } finally {
      setLoading(false);
    }
  };

  const applyTheme = (prefs: UserPreferences) => {
    const root = document.documentElement;

    // Apply theme mode
    if (prefs.theme_mode === 'dark') {
      setIsDark(true);
      root.classList.add('dark');
    } else if (prefs.theme_mode === 'light') {
      setIsDark(false);
      root.classList.remove('dark');
    } else {
      // Auto mode
      applySystemTheme();
    }

    // Apply custom colors
    root.style.setProperty('--primary-color', prefs.primary_color);
    root.style.setProperty('--accent-color', prefs.accent_color);

    // Apply font size
    root.classList.remove('font-small', 'font-medium', 'font-large');
    root.classList.add(`font-${prefs.font_size}`);
  };

  const updatePreferences = async (updates: Partial<UserPreferences>) => {
    if (!user || !preferences) return;

    try {
      const { data, error } = await supabase
        .from('user_preferences')
        .update(updates)
        .eq('user_id', user.id)
        .select()
        .single();

      if (error) throw error;
      setPreferences(data);
    } catch (error) {
      console.error('Error updating preferences:', error);
      throw error;
    }
  };

  return (
    <ThemeContext.Provider value={{ preferences, loading, updatePreferences, isDark }}>
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
