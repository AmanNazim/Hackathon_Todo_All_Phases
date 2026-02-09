/**
 * Chat Interface Component
 *
 * Main chat interface using OpenAI ChatKit.
 * Note: This is a placeholder as the actual ChatKit SDK integration
 * requires the @openai/chatkit package which may not be publicly available yet.
 */

import React from 'react';

interface ChatInterfaceProps {
  config: any;
  onLogout: () => void;
}

export const ChatInterface: React.FC<ChatInterfaceProps> = ({ config, onLogout }) => {
  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      height: '100vh',
      background: config.theme.colorScheme === 'dark' ? '#1a1a1a' : '#ffffff'
    }}>
      {/* Header */}
      <div style={{
        padding: '20px',
        borderBottom: `1px solid ${config.theme.colorScheme === 'dark' ? '#333' : '#e5e5e5'}`,
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center'
      }}>
        <h1 style={{
          margin: 0,
          fontSize: '20px',
          fontWeight: '600',
          color: config.theme.colorScheme === 'dark' ? '#fff' : '#000'
        }}>
          Task Management Chat
        </h1>
        <button
          onClick={onLogout}
          style={{
            padding: '8px 16px',
            borderRadius: '6px',
            border: 'none',
            background: '#ff4444',
            color: 'white',
            cursor: 'pointer',
            fontSize: '14px'
          }}
        >
          Logout
        </button>
      </div>

      {/* ChatKit Integration Placeholder */}
      <div style={{
        flex: 1,
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        padding: '40px',
        color: config.theme.colorScheme === 'dark' ? '#999' : '#666'
      }}>
        <div style={{ textAlign: 'center', maxWidth: '600px' }}>
          <h2 style={{ marginBottom: '20px' }}>ChatKit Integration Ready</h2>
          <p style={{ marginBottom: '30px', lineHeight: '1.6' }}>
            The backend is configured and ready for ChatKit integration.
            Install the @openai/chatkit package and replace this placeholder
            with the actual ChatKit component.
          </p>
          <div style={{
            background: config.theme.colorScheme === 'dark' ? '#2a2a2a' : '#f5f5f5',
            padding: '20px',
            borderRadius: '8px',
            textAlign: 'left',
            fontFamily: 'monospace',
            fontSize: '14px'
          }}>
            <div>npm install @openai/chatkit</div>
            <div style={{ marginTop: '10px' }}>
              import {'{'} ChatKit {'}'} from '@openai/chatkit';
            </div>
          </div>
          <div style={{ marginTop: '30px' }}>
            <h3 style={{ marginBottom: '15px' }}>Backend Endpoints Ready:</h3>
            <ul style={{ textAlign: 'left', lineHeight: '2' }}>
              <li>POST /api/chatkit/generate - Streaming responses</li>
              <li>POST /api/chatkit/action - Widget actions</li>
              <li>GET /api/chatkit/tasks - Task widgets</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};
