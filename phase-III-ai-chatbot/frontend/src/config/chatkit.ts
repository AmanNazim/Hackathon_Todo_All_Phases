/**
 * ChatKit Configuration
 *
 * Configuration for OpenAI ChatKit integration with Phase III AI Chatbot backend.
 */

export interface ChatKitConfig {
  apiUrl: string;
  headers: Record<string, string>;
  theme: ThemeConfig;
  starterPrompts?: StarterPrompt[];
}

export interface ThemeConfig {
  colorScheme: 'light' | 'dark';
  accent?: {
    primary?: string;
  };
  fontFamily?: string;
  fontSize?: string;
  density?: 'compact' | 'regular' | 'comfortable';
  radius?: 'sharp' | 'rounded' | 'round';
}

export interface StarterPrompt {
  text: string;
  icon?: string;
}

/**
 * Get ChatKit configuration
 */
export function getChatKitConfig(
  token: string,
  theme: 'light' | 'dark' = 'light'
): ChatKitConfig {
  return {
    apiUrl: import.meta.env.VITE_API_URL || 'http://localhost:8000/api/chatkit',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    theme: {
      colorScheme: theme,
      accent: {
        primary: theme === 'dark' ? '#2D8CFF' : '#1890ff'
      },
      fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
      fontSize: '16px',
      density: 'regular',
      radius: 'rounded'
    },
    starterPrompts: [
      {
        text: 'Add a task to buy groceries',
        icon: 'plus'
      },
      {
        text: 'Show me all my tasks',
        icon: 'list'
      },
      {
        text: 'What tasks are pending?',
        icon: 'clock'
      },
      {
        text: 'Mark my first task as complete',
        icon: 'check'
      }
    ]
  };
}

/**
 * Light theme configuration
 */
export const lightTheme: ThemeConfig = {
  colorScheme: 'light',
  accent: {
    primary: '#1890ff'
  },
  fontFamily: "'Inter', sans-serif",
  fontSize: '16px',
  density: 'regular',
  radius: 'rounded'
};

/**
 * Dark theme configuration
 */
export const darkTheme: ThemeConfig = {
  colorScheme: 'dark',
  accent: {
    primary: '#2D8CFF'
  },
  fontFamily: "'Inter', sans-serif",
  fontSize: '16px',
  density: 'regular',
  radius: 'rounded'
};
