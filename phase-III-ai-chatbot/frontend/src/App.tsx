/**
 * Phase III AI Chatbot - ChatKit UI Frontend
 *
 * Main application component with authentication, theme switching, and ChatKit integration.
 */

import React, { useState, useEffect } from 'react';
import { AuthWrapper } from './components/AuthWrapper';
import { ThemeToggle } from './components/ThemeToggle';
import { ChatInterface } from './components/ChatInterface';
import { getChatKitConfig } from './config/chatkit';
import './styles/global.css';

function App() {
  const [theme, setTheme] = useState<'light' | 'dark'>('light');

  // Load theme preference from localStorage
  useEffect(() => {
    const savedTheme = localStorage.getItem('theme') as 'light' | 'dark' | null;
    if (savedTheme) {
      setTheme(savedTheme);
    }
  }, []);

  // Toggle theme and save preference
  const toggleTheme = () => {
    const newTheme = theme === 'light' ? 'dark' : 'light';
    setTheme(newTheme);
    localStorage.setItem('theme', newTheme);
  };

  return (
    <AuthWrapper>
      {(token, logout) => {
        const config = getChatKitConfig(token, theme);

        return (
          <div className="app" data-theme={theme}>
            <ThemeToggle theme={theme} onToggle={toggleTheme} />
            <ChatInterface config={config} onLogout={logout} />
          </div>
        );
      }}
    </AuthWrapper>
  );
}

export default App;
