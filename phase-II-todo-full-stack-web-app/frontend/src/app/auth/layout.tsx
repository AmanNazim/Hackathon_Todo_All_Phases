'use client';

import React from 'react';
import { useUser } from '@/providers/better-auth-provider';
import { useRouter } from 'next/navigation';

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { data: user } = useUser();
  const router = useRouter();

  // If user is already authenticated, redirect to dashboard
  if (user) {
    router.push('/dashboard');
    return null;
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900 p-4">
      {children}
    </div>
  );
}