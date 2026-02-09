/**
 * Authentication Wrapper Component
 *
 * Handles authentication flow and token management.
 */

import React, { useState, useEffect } from 'react';
import { getAuthToken, setAuthToken, removeAuthToken } from '../utils/auth';

interface AuthWrapperProps {
  children: (token: string, logout: () => void) => React.ReactNode;
}

export const AuthWrapper: React.FC<AuthWrapperProps> = ({ children }) => {
  const [token, setToken] = useState<string | null>(null);
  const [inputToken, setInputToken] = useState('');

  useEffect(() => {
    // Check for stored token on mount
    const storedToken = getAuthToken();
    if (storedToken) {
      setToken(storedToken);
    }
  }, []);

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    if (inputToken.trim()) {
      setAuthToken(inputToken);
      setToken(inputToken);
    }
  };

  const handleLogout = () => {
    removeAuthToken();
    setToken(null);
    setInputToken('');
  };

  if (!token) {
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
      }}>
        <div style={{
          background: 'white',
          padding: '40px',
          borderRadius: '12px',
          boxShadow: '0 10px 40px rgba(0,0,0,0.1)',
          maxWidth: '400px',
          width: '100%'
        }}>
          <h1 style={{
            margin: '0 0 10px 0',
            fontSize: '24px',
            fontWeight: '600',
            color: '#333'
          }}>
            Phase III AI Chatbot
          </h1>
          <p style={{
            margin: '0 0 30px 0',
            fontSize: '14px',
            color: '#666'
          }}>
            Enter your authentication token to continue
          </p>
          <form onSubmit={handleLogin}>
            <input
              type="text"
              value={inputToken}
              onChange={(e) => setInputToken(e.target.value)}
              placeholder="Enter your token"
              style={{
                width: '100%',
                padding: '12px',
                border: '1px solid #ddd',
                borderRadius: '8px',
                fontSize: '14px',
                marginBottom: '16px',
                boxSizing: 'border-box'
              }}
              required
            />
            <button
              type="submit"
              style={{
                width: '100%',
                padding: '12px',
                background: '#667eea',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                fontSize: '14px',
                fontWeight: '500',
                cursor: 'pointer',
                transition: 'background 0.3s ease'
              }}
            >
              Login
            </button>
          </form>
          <p style={{
            margin: '20px 0 0 0',
            fontSize: '12px',
            color: '#999',
            textAlign: 'center'
          }}>
            For demo: use "test-token"
          </p>
        </div>
      </div>
    );
  }

  return <>{children(token, handleLogout)}</>;
};
