'use client';

import React from 'react';
import {
  useQuery,
  useMutation,
  useQueryClient,
  QueryClient,
  QueryClientProvider,
} from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';

// Create a client
export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      gcTime: 10 * 60 * 1000, // 10 minutes (formerly cacheTime)
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

// Provider component
export function ReactQueryProvider({ children }: { children: React.ReactNode }) {
  return (
    <QueryClientProvider client={queryClient}>
      {children}
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  );
}

// API base URL
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Helper function to get auth token
const getAuthToken = () => {
  if (typeof window !== 'undefined') {
    return localStorage.getItem('auth-token');
  }
  return null;
};

// Helper function for API calls
async function fetchAPI(endpoint: string, options: RequestInit = {}) {
  const token = getAuthToken();
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...(token && { Authorization: `Bearer ${token}` }),
    ...options.headers,
  };

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ message: 'Request failed' }));
    throw new Error(error.message || `HTTP ${response.status}`);
  }

  return response.json();
}

// Task-related hooks
export function useTasks(filters?: {
  status?: string;
  priority?: string;
  search?: string;
}) {
  const queryKey = ['tasks', filters];

  return useQuery({
    queryKey,
    queryFn: () => {
      const params = new URLSearchParams();
      if (filters?.status) params.append('status', filters.status);
      if (filters?.priority) params.append('priority', filters.priority);
      if (filters?.search) params.append('search', filters.search);

      const queryString = params.toString();
      return fetchAPI(`/api/tasks${queryString ? `?${queryString}` : ''}`);
    },
  });
}

export function useTask(taskId: string) {
  return useQuery({
    queryKey: ['tasks', taskId],
    queryFn: () => fetchAPI(`/api/tasks/${taskId}`),
    enabled: !!taskId,
  });
}

export function useCreateTask() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (newTask: any) =>
      fetchAPI('/api/tasks', {
        method: 'POST',
        body: JSON.stringify(newTask),
      }),
    onMutate: async (newTask) => {
      // Cancel outgoing refetches
      await queryClient.cancelQueries({ queryKey: ['tasks'] });

      // Snapshot previous value
      const previousTasks = queryClient.getQueryData(['tasks']);

      // Optimistically update
      queryClient.setQueryData(['tasks'], (old: any) => {
        return {
          ...old,
          tasks: [...(old?.tasks || []), { ...newTask, id: 'temp-' + Date.now() }],
        };
      });

      return { previousTasks };
    },
    onError: (err, newTask, context) => {
      // Rollback on error
      if (context?.previousTasks) {
        queryClient.setQueryData(['tasks'], context.previousTasks);
      }
    },
    onSuccess: () => {
      // Invalidate and refetch
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
    },
  });
}

export function useUpdateTask() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, updates }: { id: string; updates: any }) =>
      fetchAPI(`/api/tasks/${id}`, {
        method: 'PUT',
        body: JSON.stringify(updates),
      }),
    onMutate: async ({ id, updates }) => {
      await queryClient.cancelQueries({ queryKey: ['tasks', id] });

      const previousTask = queryClient.getQueryData(['tasks', id]);

      queryClient.setQueryData(['tasks', id], (old: any) => ({
        ...old,
        ...updates,
      }));

      return { previousTask };
    },
    onError: (err, { id }, context) => {
      if (context?.previousTask) {
        queryClient.setQueryData(['tasks', id], context.previousTask);
      }
    },
    onSuccess: (data, { id }) => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
      queryClient.setQueryData(['tasks', id], data);
    },
  });
}

export function useDeleteTask() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (taskId: string) =>
      fetchAPI(`/api/tasks/${taskId}`, {
        method: 'DELETE',
      }),
    onMutate: async (taskId) => {
      await queryClient.cancelQueries({ queryKey: ['tasks'] });

      const previousTasks = queryClient.getQueryData(['tasks']);

      queryClient.setQueryData(['tasks'], (old: any) => ({
        ...old,
        tasks: old?.tasks?.filter((task: any) => task.id !== taskId) || [],
      }));

      return { previousTasks };
    },
    onError: (err, taskId, context) => {
      if (context?.previousTasks) {
        queryClient.setQueryData(['tasks'], context.previousTasks);
      }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
    },
  });
}

export function useToggleTaskStatus() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, status }: { id: string; status: string }) =>
      fetchAPI(`/api/tasks/${id}/status`, {
        method: 'PATCH',
        body: JSON.stringify({ status }),
      }),
    onMutate: async ({ id, status }) => {
      await queryClient.cancelQueries({ queryKey: ['tasks', id] });

      const previousTask = queryClient.getQueryData(['tasks', id]);

      queryClient.setQueryData(['tasks', id], (old: any) => ({
        ...old,
        status,
      }));

      // Also update in the list
      queryClient.setQueryData(['tasks'], (old: any) => ({
        ...old,
        tasks: old?.tasks?.map((task: any) =>
          task.id === id ? { ...task, status } : task
        ),
      }));

      return { previousTask };
    },
    onError: (err, { id }, context) => {
      if (context?.previousTask) {
        queryClient.setQueryData(['tasks', id], context.previousTask);
      }
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
    },
    onSuccess: (data, { id }) => {
      queryClient.setQueryData(['tasks', id], data);
    },
  });
}

// Statistics hooks
export function useTaskStatistics(timeRange?: string) {
  return useQuery({
    queryKey: ['statistics', timeRange],
    queryFn: () => {
      const params = timeRange ? `?range=${timeRange}` : '';
      return fetchAPI(`/api/tasks/statistics${params}`);
    },
    staleTime: 2 * 60 * 1000, // 2 minutes for statistics
  });
}

// Goal hooks
export function useGoals() {
  return useQuery({
    queryKey: ['goals'],
    queryFn: () => fetchAPI('/api/goals'),
  });
}

export function useCreateGoal() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (newGoal: any) =>
      fetchAPI('/api/goals', {
        method: 'POST',
        body: JSON.stringify(newGoal),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['goals'] });
    },
  });
}

export function useUpdateGoal() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, updates }: { id: string; updates: any }) =>
      fetchAPI(`/api/goals/${id}`, {
        method: 'PUT',
        body: JSON.stringify(updates),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['goals'] });
    },
  });
}

// Template hooks
export function useTemplates() {
  return useQuery({
    queryKey: ['templates'],
    queryFn: () => fetchAPI('/api/templates'),
  });
}

export function useCreateTemplate() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (newTemplate: any) =>
      fetchAPI('/api/templates', {
        method: 'POST',
        body: JSON.stringify(newTemplate),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['templates'] });
    },
  });
}

// Prefetch utilities
export function prefetchTasks(filters?: any) {
  return queryClient.prefetchQuery({
    queryKey: ['tasks', filters],
    queryFn: () => {
      const params = new URLSearchParams(filters);
      const queryString = params.toString();
      return fetchAPI(`/api/tasks${queryString ? `?${queryString}` : ''}`);
    },
  });
}

export function prefetchTask(taskId: string) {
  return queryClient.prefetchQuery({
    queryKey: ['tasks', taskId],
    queryFn: () => fetchAPI(`/api/tasks/${taskId}`),
  });
}
