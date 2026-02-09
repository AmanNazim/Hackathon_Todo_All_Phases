'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useSession } from '@/lib/auth-client';
import LoadingSpinner from '@/components/ui/LoadingSpinner';

interface ProtectedRouteProps {
  children: React.ReactNode;
  fallback?: React.ReactNode;
}

export default function ProtectedRoute({ children, fallback }: ProtectedRouteProps) {
  const router = useRouter();
  const { data: session, isPending } = useSession();

  useEffect(() => {
    if (!isPending && !session) {
      // Not authenticated, redirect to login
      router.push('/auth/login');
    }
  }, [session, isPending, router]);

  // Show loading spinner while checking authentication
  if (isPending) {
    return fallback || (
      <div className="flex justify-center items-center min-h-screen">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  // Not authenticated, don't render children
  if (!session) {
    return null;
  }

  // Authenticated, render children
  return <>{children}</>;
}
