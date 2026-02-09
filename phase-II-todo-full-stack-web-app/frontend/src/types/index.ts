// User types
export interface User {
  id: string;
  email: string;
  name?: string;
  createdAt: string;
  updatedAt: string;
}

// Task types
export interface Task {
  id: string;
  title: string;
  description?: string;
  completed: boolean;
  priority: 'low' | 'medium' | 'high' | 'urgent';
  dueDate?: string;
  userId: string;
  createdAt: string;
  updatedAt: string;
  tags?: string[];
}

// Authentication types
export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterCredentials {
  email: string;
  password: string;
  name?: string;
}

export interface AuthResponse {
  token: string;
  user: User;
}

// API Response types
export interface ApiResponse<T> {
  data?: T;
  error?: string;
  message?: string;
  status: number;
}

// Form validation types
export interface ValidationError {
  field: string;
  message: string;
}

// Priority type for UI
export type PriorityLevel = 'low' | 'medium' | 'high' | 'urgent';

// Filter types
export interface TaskFilters {
  status?: 'all' | 'active' | 'completed';
  priority?: PriorityLevel | 'all';
  search?: string;
  startDate?: string;
  endDate?: string;
}