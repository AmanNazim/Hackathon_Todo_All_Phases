'use client';

import React, { ReactNode, createContext, useContext, useState, useEffect } from 'react';

interface AuthProviderProps {
  children: ReactNode;
}

interface AuthContextType {
  user: any | null;
  session: any | null;
  isLoading: boolean;
}

const AuthContext = createContext<AuthContextType>({
  user: null,
  session: null,
  isLoading: true,
});

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<any | null>(null);
  const [session, setSession] = useState<any | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Check for stored auth token
    const token = localStorage.getItem('auth_token');
    if (token) {
      // Token exists, user is authenticated
      setSession({ token });
      // You can fetch user data here if needed
    }
    setIsLoading(false);
  }, []);

  return (
    <AuthContext.Provider value={{ user, session, isLoading }}>
      {children}
    </AuthContext.Provider>
  );
};

// Export hooks for convenience
export const useSession = () => {
  const context = useContext(AuthContext);
  return { data: context.session, isLoading: context.isLoading };
};

export const useUser = () => {
  const context = useContext(AuthContext);
  return { data: context.user, isLoading: context.isLoading };
};
