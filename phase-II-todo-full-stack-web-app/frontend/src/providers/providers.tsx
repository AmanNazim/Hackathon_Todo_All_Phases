'use client';

import React from 'react';
import { AuthProvider } from "@/providers/better-auth-provider";
import { ThemeProvider } from "@/providers/theme-provider";
import { ToastProvider } from "@/providers/toast-provider";
import { ReactQueryProvider } from "@/lib/react-query";
import { CustomQueryClientProvider } from "@/providers/query-client-provider";
import ErrorBoundary from "@/components/ui/ErrorBoundary";

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <ReactQueryProvider>
      <CustomQueryClientProvider>
        <ThemeProvider>
          <AuthProvider>
            <ToastProvider>
              <ErrorBoundary>
                {children}
              </ErrorBoundary>
            </ToastProvider>
          </AuthProvider>
        </ThemeProvider>
      </CustomQueryClientProvider>
    </ReactQueryProvider>
  );
}
