'use client';

import React, { ReactNode } from 'react';
import { useSession } from '@/lib/auth-client';

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  return <>{children}</>;
};

// Export Better Auth hooks for convenience
export { useSession } from '@/lib/auth-client';

export const useUser = () => {
  const session = useSession();
  return {
    data: session.data?.user || null,
    isLoading: session.isPending
  };
};
