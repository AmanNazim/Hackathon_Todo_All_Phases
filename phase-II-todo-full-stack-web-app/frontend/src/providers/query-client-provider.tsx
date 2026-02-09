'use client';

import React, { createContext, useContext, useState, ReactNode } from 'react';

interface CacheItem<T> {
  data: T;
  timestamp: number;
  ttl: number; // Time to live in milliseconds
}

interface QueryClientContextType {
  get: <T>(key: string) => T | undefined;
  set: <T>(key: string, data: T, ttl?: number) => void;
  invalidate: (key: string) => void;
  clear: () => void;
}

const QueryClientContext = createContext<QueryClientContextType | undefined>(undefined);

export const QueryClientProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [cache, setCache] = useState<Record<string, CacheItem<any>>>({});

  const get = <T,>(key: string): T | undefined => {
    const item = cache[key];
    if (!item) return undefined;

    // Check if the item has expired
    const now = Date.now();
    if (now - item.timestamp > item.ttl) {
      // Item has expired, remove it
      setCache(prev => {
        const newCache = { ...prev };
        delete newCache[key];
        return newCache;
      });
      return undefined;
    }

    return item.data as T;
  };

  const set = <T,>(key: string, data: T, ttl: number = 5 * 60 * 1000): void => {
    // Default TTL is 5 minutes
    setCache(prev => ({
      ...prev,
      [key]: {
        data,
        timestamp: Date.now(),
        ttl,
      },
    }));
  };

  const invalidate = (key: string): void => {
    setCache(prev => {
      const newCache = { ...prev };
      delete newCache[key];
      return newCache;
    });
  };

  const clear = (): void => {
    setCache({});
  };

  const value: QueryClientContextType = {
    get,
    set,
    invalidate,
    clear,
  };

  return <QueryClientContext.Provider value={value}>{children}</QueryClientContext.Provider>;
};

export const useQueryClient = (): QueryClientContextType => {
  const context = useContext(QueryClientContext);
  if (context === undefined) {
    throw new Error('useQueryClient must be used within a QueryClientProvider');
  }
  return context;
};