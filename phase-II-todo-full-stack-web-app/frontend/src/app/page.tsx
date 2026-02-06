'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function Home() {
  const router = useRouter();

  useEffect(() => {
    // Check if user is authenticated
    const token = localStorage.getItem('auth-token');

    if (token) {
      // If authenticated, redirect to dashboard
      router.push('/dashboard');
    } else {
      // If not authenticated, redirect to auth page
      router.push('/auth');
    }
  }, [router]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="text-center">
        <p className="text-lg text-gray-600">Redirecting...</p>
      </div>
    </div>
  );
}
