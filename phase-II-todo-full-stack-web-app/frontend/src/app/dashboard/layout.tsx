'use client';

import React, { useState } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { useSession, signOut } from '@/lib/auth-client';
import Button from '@/components/ui/Button';
import Link from 'next/link';
import { Card, CardContent } from '@/components/ui/Card';
import LoadingSpinner from '@/components/ui/LoadingSpinner';
import MobileMenu from '@/components/ui/MobileMenu';
import Breadcrumbs from '@/components/ui/Breadcrumbs';

// Force dynamic rendering for all dashboard routes
export const dynamic = 'force-dynamic';
export const runtime = 'nodejs';

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const router = useRouter();
  const pathname = usePathname();
  const { data: session, isPending } = useSession();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  // Show loading while checking session
  if (isPending) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  // Redirect to login if not authenticated
  if (!session) {
    router.push('/auth/login');
    return null;
  }

  const handleLogout = async () => {
    await signOut();
    router.push('/auth/login');
    router.refresh();
  };

  // Helper function to check if link is active
  const isActive = (path: string) => {
    if (path === '/dashboard') {
      return pathname === '/dashboard';
    }
    return pathname.startsWith(path);
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <header className="bg-white dark:bg-gray-800 shadow sticky top-0 z-30">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex">
              <div className="flex-shrink-0 flex items-center">
                <h1 className="text-xl font-bold text-gray-900 dark:text-white">Todo App</h1>
              </div>
              {/* Desktop Navigation */}
              <nav className="hidden md:ml-6 md:flex md:space-x-8">
                <Link
                  href="/dashboard"
                  className={`${
                    isActive('/dashboard')
                      ? 'border-blue-500 text-gray-900 dark:text-white'
                      : 'border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300'
                  } hover:border-gray-300 border-b-2 inline-flex items-center px-1 pt-1 text-sm font-medium transition-colors`}
                >
                  Dashboard
                </Link>
                <Link
                  href="/dashboard/tasks"
                  className={`${
                    isActive('/dashboard/tasks')
                      ? 'border-blue-500 text-gray-900 dark:text-white'
                      : 'border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300'
                  } hover:border-gray-300 border-b-2 inline-flex items-center px-1 pt-1 text-sm font-medium transition-colors`}
                >
                  Tasks
                </Link>
                <Link
                  href="/dashboard/statistics"
                  className={`${
                    isActive('/dashboard/statistics')
                      ? 'border-blue-500 text-gray-900 dark:text-white'
                      : 'border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300'
                  } hover:border-gray-300 border-b-2 inline-flex items-center px-1 pt-1 text-sm font-medium transition-colors`}
                >
                  Statistics
                </Link>
              </nav>
            </div>
            <div className="flex items-center">
              {/* Desktop User Menu */}
              <div className="hidden md:flex md:items-center md:space-x-4">
                <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  Welcome, {session.user?.name || session.user?.email}
                </span>
                <Button onClick={handleLogout} variant="outline" size="sm">
                  Logout
                </Button>
              </div>
              {/* Mobile Menu Button */}
              <button
                onClick={() => setIsMobileMenuOpen(true)}
                className="md:hidden p-2 rounded-md text-gray-500 hover:text-gray-700 hover:bg-gray-100 dark:text-gray-400 dark:hover:text-gray-200 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
                aria-label="Open menu"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                </svg>
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Mobile Menu */}
      <MobileMenu
        isOpen={isMobileMenuOpen}
        onClose={() => setIsMobileMenuOpen(false)}
        onLogout={handleLogout}
        userName={session.user?.name || session.user?.email}
      />

      <div className="py-6">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col md:flex-row gap-6">
            {/* Desktop Sidebar */}
            <div className="hidden md:block w-64">
              <Card>
                <CardContent className="pt-6">
                  <nav className="space-y-1">
                    <Link
                      href="/dashboard"
                      className={`${
                        isActive('/dashboard')
                          ? 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-100'
                          : 'text-gray-700 hover:bg-gray-50 hover:text-gray-900 dark:text-gray-300 dark:hover:bg-gray-700 dark:hover:text-white'
                      } group flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors`}
                    >
                      Overview
                    </Link>
                    <Link
                      href="/dashboard/tasks"
                      className={`${
                        isActive('/dashboard/tasks')
                          ? 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-100'
                          : 'text-gray-700 hover:bg-gray-50 hover:text-gray-900 dark:text-gray-300 dark:hover:bg-gray-700 dark:hover:text-white'
                      } group flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors`}
                    >
                      My Tasks
                    </Link>
                    <Link
                      href="/dashboard/statistics"
                      className={`${
                        isActive('/dashboard/statistics')
                          ? 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-100'
                          : 'text-gray-700 hover:bg-gray-50 hover:text-gray-900 dark:text-gray-300 dark:hover:bg-gray-700 dark:hover:text-white'
                      } group flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors`}
                    >
                      Statistics
                    </Link>
                    <Link
                      href="/dashboard/settings"
                      className={`${
                        isActive('/dashboard/settings')
                          ? 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-100'
                          : 'text-gray-700 hover:bg-gray-50 hover:text-gray-900 dark:text-gray-300 dark:hover:bg-gray-700 dark:hover:text-white'
                      } group flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors`}
                    >
                      Settings
                    </Link>
                  </nav>
                </CardContent>
              </Card>
            </div>

            {/* Main content */}
            <div className="flex-1">
              <Breadcrumbs />
              {children}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
