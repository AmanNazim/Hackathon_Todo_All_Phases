/**
 * MainLayout Component
 *
 * Main application layout with navbar, sidebar, and content area
 */

'use client';

import React from 'react';
import Navbar from './Navbar';
import Sidebar from './Sidebar';

export interface MainLayoutProps {
  children: React.ReactNode;
  user?: {
    name: string;
    email: string;
    avatar?: string;
  };
  onLogout?: () => void;
  showSidebar?: boolean;
  className?: string;
}

const MainLayout: React.FC<MainLayoutProps> = ({
  children,
  user,
  onLogout,
  showSidebar = true,
  className = '',
}) => {
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-950 flex flex-col">
      {/* Navbar */}
      <Navbar user={user} onLogout={onLogout} />

      {/* Main content area */}
      <div className="flex-1 flex overflow-hidden">
        {/* Sidebar */}
        {showSidebar && (
          <div className="hidden lg:block">
            <Sidebar user={user} />
          </div>
        )}

        {/* Content */}
        <main
          className={`
            flex-1 overflow-y-auto
            ${className}
          `}
        >
          {children}
        </main>
      </div>
    </div>
  );
};

export default MainLayout;
