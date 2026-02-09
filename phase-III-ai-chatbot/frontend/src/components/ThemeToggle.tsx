/**
 * Theme Toggle Component
 *
 * Button to toggle between light and dark themes.
 */

import React from 'react';

interface ThemeToggleProps {
  theme: 'light' | 'dark';
  onToggle: () => void;
}

export const ThemeToggle: React.FC<ThemeToggleProps> = ({ theme, onToggle }) => {
  return (
    <button
      onClick={onToggle}
      style={{
        position: 'fixed',
        top: '20px',
        right: '20px',
        padding: '10px 20px',
        borderRadius: '8px',
        border: 'none',
        background: theme === 'dark' ? '#333' : '#f0f0f0',
        color: theme === 'dark' ? '#fff' : '#000',
        cursor: 'pointer',
        fontSize: '14px',
        fontWeight: '500',
        zIndex: 1000,
        transition: 'all 0.3s ease'
      }}
      aria-label="Toggle theme"
    >
      {theme === 'dark' ? '☀️ Light' : '🌙 Dark'}
    </button>
  );
};
