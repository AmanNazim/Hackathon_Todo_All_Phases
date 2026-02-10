'use client';

import React, { createContext, useContext, useState, ReactNode } from 'react';

interface CacheItem<T> {
  data: T;
  timestamp: number;
  ttl: number; // Time to live in milliseconds
}

interface CustomQueryClientContextType {
  get: <T>(key: string) => T | undefined;
  set: <T>(key: string, data: T, ttl?: number) => void;
  invalidate: (key: string) => void;
  clear: () => void;
}

const CustomQueryClientContext = createContext<CustomQueryClientContextType | undefined>(undefined);

export const CustomQueryClientProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
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

  const value: CustomQueryClientContextType = {
    get,
    set,
    invalidate,
    clear,
  };

  return <CustomQueryClientContext.Provider value={value}>{children}</CustomQueryClientContext.Provider>;
};

export const useQueryClient = (): CustomQueryClientContextType => {
  const context = useContext(CustomQueryClientContext);

  // During SSR/build time, return a no-op implementation
  if (context === undefined) {
    if (typeof window === 'undefined') {
      // Server-side: return no-op functions
      return {
        get: () => undefined,
        set: () => {},
        invalidate: () => {},
        clear: () => {},
      };
    }
    // Client-side: this is an actual error
    throw new Error('useQueryClient must be used within a CustomQueryClientProvider');
  }

  return context;
};

// Keep old export for backward compatibility
export const QueryClientProvider = CustomQueryClientProvider;