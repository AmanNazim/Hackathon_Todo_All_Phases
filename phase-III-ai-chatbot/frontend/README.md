# Phase III AI Chatbot - ChatKit UI Frontend

## Overview

Modern chat interface for Phase III AI Chatbot using OpenAI's ChatKit framework (when available) with React, TypeScript, and Vite.

## Features

- 🎨 **Theme Switching**: Light and dark mode support
- 🔐 **Authentication**: Secure token-based authentication
- 💬 **Chat Interface**: Ready for ChatKit integration
- 📱 **Responsive Design**: Works on mobile and desktop
- ⚡ **Fast Development**: Vite for instant HMR

## Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Configuration

### Environment Variables

Create a `.env` file in the frontend directory:

```env
VITE_API_URL=http://localhost:8000/api/chatkit
```

### Backend Connection

The frontend connects to the Phase III backend at `http://localhost:8000` by default. Make sure the backend is running before starting the frontend.

## ChatKit Integration

**Note**: This implementation is ready for ChatKit integration but uses a placeholder component since the `@openai/chatkit` package may not be publicly available yet.

To integrate the actual ChatKit SDK:

1. Install the ChatKit package:
```bash
npm install @openai/chatkit
```

2. Replace the placeholder in `src/components/ChatInterface.tsx` with:
```typescript
import { ChatKit } from '@openai/chatkit';

export const ChatInterface: React.FC<ChatInterfaceProps> = ({ config, onLogout }) => {
  return (
    <div>
      <ChatKit config={config} />
    </div>
  );
};
```

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── AuthWrapper.tsx      # Authentication wrapper
│   │   ├── ChatInterface.tsx    # Main chat interface
│   │   └── ThemeToggle.tsx      # Theme toggle button
│   ├── config/
│   │   └── chatkit.ts           # ChatKit configuration
│   ├── utils/
│   │   └── auth.ts              # Authentication utilities
│   ├── styles/
│   │   └── global.css           # Global styles
│   ├── App.tsx                  # Main app component
│   └── index.tsx                # Entry point
├── package.json
├── tsconfig.json
├── vite.config.ts
└── README.md
```

## Usage

### Authentication

1. Start the application
2. Enter your authentication token (use "test-token" for demo)
3. Click "Login"

### Chat Interface

Once authenticated:
- Type messages in the chat input
- View streaming responses in real-time
- Interact with task widgets
- Toggle between light and dark themes
- Logout when done

## Backend Endpoints

The frontend connects to these backend endpoints:

- `POST /api/chatkit/generate` - Generate AI responses with streaming
- `POST /api/chatkit/action` - Handle widget actions
- `GET /api/chatkit/tasks` - Get task widgets

## Theme Customization

Themes are configured in `src/config/chatkit.ts`:

```typescript
export const lightTheme: ThemeConfig = {
  colorScheme: 'light',
  accent: { primary: '#1890ff' },
  fontFamily: "'Inter', sans-serif",
  fontSize: '16px',
  density: 'regular',
  radius: 'rounded'
};
```

## Development

### Hot Module Replacement

Vite provides instant HMR for fast development:

```bash
npm run dev
```

### Type Checking

TypeScript provides type safety:

```bash
npm run build  # Includes type checking
```

### Linting

```bash
npm run lint
```

## Production Build

```bash
# Build for production
npm run build

# Preview production build
npm run preview
```

The build output will be in the `dist/` directory.

## Deployment

### Static Hosting

Deploy the `dist/` directory to any static hosting service:

- Vercel
- Netlify
- AWS S3 + CloudFront
- GitHub Pages

### Environment Variables

Set the `VITE_API_URL` environment variable to your production backend URL.

## Troubleshooting

### Backend Connection Issues

- Ensure backend is running at `http://localhost:8000`
- Check CORS configuration in backend
- Verify authentication token is valid

### ChatKit Integration

- Install `@openai/chatkit` package when available
- Replace placeholder component with actual ChatKit component
- Configure ChatKit with backend endpoints

### Theme Not Persisting

- Check browser localStorage is enabled
- Clear browser cache and try again

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## License

MIT

## Support

For issues or questions:
- Check backend API documentation
- Review ChatKit documentation (when available)
- Check browser console for errors
