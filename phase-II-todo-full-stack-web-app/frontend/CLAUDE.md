# Claude Code Instructions for Phase II Frontend

This document provides specific instructions for Claude Code when generating code for the Phase II Frontend (Next.js, TypeScript, Tailwind CSS).

## Project Context

- **Project Name**: Phase II Full-Stack Web Todo Application - Frontend
- **Technology Stack**: Next.js 16+, TypeScript, Tailwind CSS, React Hooks
- **Architecture**: Client-side application consuming REST API with JWT authentication
- **User Interface**: Responsive web interface with modern UX patterns
- **Development Methodology**: Spec-Driven Development (Specification → Plan → Tasks → Implementation)

## Core Principles

- **Responsive Design**: Interface must work seamlessly across mobile, tablet, and desktop
- **User Experience**: Intuitive, accessible, and performant user interactions
- **API Integration**: Secure communication with backend API using JWT authentication
- **Clean Component Architecture**: Proper separation of concerns with reusable components
- **Accessibility**: Follow WCAG 2.1 AA standards for inclusive design

## Code Generation Guidelines

### Frontend Architecture (Next.js 16+)

1. **Project Structure**:
   - Use App Router (`/app` directory) with proper layout and page organization
   - Component organization: `/components`, `/lib`, `/hooks`, `/types`, `/styles`
   - Page organization with proper loading states and error boundaries
   - Environment configuration for API endpoints

2. **Authentication Integration**:
   - JWT token management in browser storage
   - Protected route components and authentication context
   - User session handling and persistence
   - Secure token storage and cleanup

3. **UI Components**:
   - Responsive design with Tailwind CSS utility classes
   - Reusable components for task management operations
   - Loading and error states with appropriate feedback
   - Form validation and user input handling

4. **API Integration**:
   - Client-side API calls to FastAPI backend
   - Error handling with user-friendly messages
   - Loading states during API operations
   - Proper TypeScript typing for all API interactions

### Component Architecture

1. **Component Design**:
   - Use functional components with TypeScript interfaces
   - Implement proper prop validation and typing
   - Create reusable UI components with consistent styling
   - Follow React best practices for state management

2. **State Management**:
   - Use React hooks (useState, useEffect, useContext) appropriately
   - Implement proper state synchronization with backend
   - Handle loading and error states consistently
   - Manage form state effectively

3. **Styling Approach**:
   - Use Tailwind CSS utility classes for styling
   - Implement consistent design system and color palette
   - Create responsive layouts with mobile-first approach
   - Use proper typography and spacing

### API Communication Layer

1. **Client Implementation**:
   - Create centralized API client utility functions
   - Implement proper error handling for API failures
   - Add request interceptors for JWT token attachment
   - Handle network errors gracefully

2. **Authentication Flow**:
   - Store JWT tokens securely in browser storage
   - Attach tokens to API requests automatically
   - Handle token expiration and refresh
   - Implement secure logout functionality

3. **Data Management**:
   - Handle CRUD operations for tasks with proper feedback
   - Implement optimistic updates where appropriate
   - Show loading states during operations
   - Provide clear error messages for failed operations

### User Experience (UX) Standards

1. **Navigation and Interaction**:
   - Intuitive navigation with clear user pathways
   - Consistent interaction patterns across the application
   - Accessible design following WCAG 2.1 AA standards
   - Keyboard navigation support

2. **Feedback and States**:
   - Clear loading indicators during operations
   - Meaningful error messages and recovery options
   - Success feedback for completed operations
   - Empty states for lists and data displays

3. **Performance Optimization**:
   - Optimize component rendering and re-renders
   - Implement proper memoization where needed
   - Lazy load components when appropriate
   - Optimize bundle size and asset loading

### Technology Constraints

- **Framework**: Next.js 16+ with App Router architecture
- **Language**: TypeScript with strict typing
- **Styling**: Tailwind CSS for all styling needs
- **API Communication**: Fetch API or Axios with proper error handling
- **Authentication**: JWT token-based authentication with secure storage
- **Components**: React functional components with TypeScript interfaces

### Responsive Design Requirements

- **Mobile-First Approach**: Design for mobile first, then enhance for larger screens
- **Breakpoints**: Use Tailwind CSS responsive utility classes
- **Touch Targets**: Ensure minimum 44px touch targets for mobile
- **Viewport Adaptation**: Proper viewport meta tag and responsive units

### Accessibility Implementation

1. **Semantic HTML**:
   - Use proper semantic elements (nav, main, header, etc.)
   - Implement proper heading hierarchy
   - Use ARIA attributes where necessary
   - Ensure proper focus management

2. **Keyboard Navigation**:
   - Full keyboard operability
   - Visible focus indicators
   - Logical tab order
   - Skip links for main content

3. **Screen Reader Support**:
   - Proper labels and descriptions
   - Live regions for dynamic content
   - Alternative text for images
   - Semantic structure

## Forbidden Implementation Details

- **No Direct DOM Manipulation**: Use React state and refs appropriately
- **No Insecure Token Storage**: Use secure methods for JWT storage
- **No Poor Accessibility**: Follow accessibility best practices
- **No Blocking Operations**: Use asynchronous operations appropriately
- **No Inconsistent Styling**: Follow design system and Tailwind conventions

## File Structure Expectations

```
frontend/
├── app/
│   ├── layout.tsx
│   ├── page.tsx
│   ├── dashboard/
│   └── auth/
├── components/
│   ├── ui/           # Reusable UI components
│   ├── tasks/        # Task-specific components
│   └── auth/         # Authentication components
├── lib/
│   ├── api.ts        # API client utilities
│   └── types.ts      # Type definitions
├── types/
│   └── index.ts      # TypeScript type definitions
├── hooks/
├── styles/
│   └── globals.css
├── public/
├── package.json
├── next.config.ts
├── tailwind.config.ts
└── tsconfig.json
```

## Quality Standards

- All components must have proper TypeScript interfaces
- Strict type checking throughout the application
- Follow Next.js and React best practices
- Implement proper error boundaries and fallbacks
- Include comprehensive accessibility features
- Follow security best practices for authentication and data handling

## Common Patterns to Use

- Next.js App Router with proper layout and loading states
- React Server Components and Client Components appropriately
- Next.js data fetching patterns (client-side API calls)
- React hooks for state management and side effects
- Context providers for global state management
- Custom hooks for reusable logic
- Tailwind CSS for responsive, consistent styling
- TypeScript interfaces for all props and data structures