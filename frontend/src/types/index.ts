export interface UserPreferences {
  id?: string;
  user_id?: string;
  theme_mode: 'light' | 'dark' | 'system';
  primary_color: string;
  accent_color: string;
  agent_personality: string;
  agent_name: string;
  font_size: 'small' | 'medium' | 'large';
  animations_enabled: boolean;
  created_at?: string;
  updated_at?: string;
}
