'use client';

import React from 'react';
import { AuthProvider } from "@/providers/better-auth-provider";
import { ThemeProvider } from "@/providers/theme-provider";
import { ToastProvider } from "@/providers/toast-provider";
import { ReactQueryProvider } from "@/lib/react-query";
import { QueryClientProvider } from "@/providers/query-client-provider";
import ErrorBoundary from "@/components/ui/ErrorBoundary";

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <ReactQueryProvider>
      <QueryClientProvider>
        <ThemeProvider>
          <AuthProvider>
            <ToastProvider>
              <ErrorBoundary>
                {children}
              </ErrorBoundary>
            </ToastProvider>
          </AuthProvider>
        </ThemeProvider>
      </QueryClientProvider>
    </ReactQueryProvider>
  );
}
