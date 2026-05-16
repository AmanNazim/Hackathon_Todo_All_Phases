import { AuthResponse, Task, User, LoginCredentials, RegisterCredentials, ApiResponse } from '../types';
import { authClient } from './auth-client';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

class ApiClient {
  private async getToken(): Promise<string | null> {
    // Get token from Better Auth session
    const session = await authClient.getSession();
    return session.data?.session?.token || null;
  }

  private async getUserId(): Promise<string | null> {
    // Get user ID from Better Auth session
    const session = await authClient.getSession();
    return session.data?.user?.id || null;
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<ApiResponse<T>> {
    const url = `${API_BASE_URL}${endpoint}`;
    const token = await this.getToken();

    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...(options.headers as Record<string, string>),
    };

    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    try {
      const response = await fetch(url, {
        ...options,
        headers,
      });

      // Check if response is JSON before parsing
      const contentType = response.headers.get('content-type');
      if (!contentType || !contentType.includes('application/json')) {
        // If not JSON, get the text to see what we got
        const text = await response.text();
        console.error('[API ERROR] Non-JSON response:', text.substring(0, 200));
        return {
          error: `Expected JSON response but received: ${text.substring(0, 100)}`,
          status: response.status,
        };
      }

      const data = await response.json();

      if (!response.ok) {
        return {
          error: data.message || 'An error occurred',
          status: response.status,
        };
      }

      return {
        data,
        status: response.status,
      };
    } catch (error) {
      console.error('[API ERROR]', error);
      return {
        error: error instanceof Error ? error.message : 'Network error occurred',
        status: 500,
      };
    }
  }

  // Task methods - include user ID in path for backend requirement
  async getTasks(): Promise<ApiResponse<Task[]>> {
    const userId = await this.getUserId();
    if (!userId) {
      return { error: 'User not authenticated', status: 401 };
    }
    return this.request<Task[]>(`/v1/users/${userId}/tasks`);
  }

  async createTask(task: Partial<Task>): Promise<ApiResponse<Task>> {
    const userId = await this.getUserId();
    if (!userId) {
      return { error: 'User not authenticated', status: 401 };
    }
    return this.request<Task>(`/v1/users/${userId}/tasks`, {
      method: 'POST',
      body: JSON.stringify(task),
    });
  }

  async getTaskById(id: string): Promise<ApiResponse<Task>> {
    const userId = await this.getUserId();
    if (!userId) {
      return { error: 'User not authenticated', status: 401 };
    }
    return this.request<Task>(`/v1/users/${userId}/tasks/${id}`);
  }

  async updateTask(id: string, task: Partial<Task>): Promise<ApiResponse<Task>> {
    const userId = await this.getUserId();
    if (!userId) {
      return { error: 'User not authenticated', status: 401 };
    }
    return this.request<Task>(`/v1/users/${userId}/tasks/${id}`, {
      method: 'PUT',
      body: JSON.stringify(task),
    });
  }

  async deleteTask(id: string): Promise<ApiResponse<void>> {
    const userId = await this.getUserId();
    if (!userId) {
      return { error: 'User not authenticated', status: 401 };
    }
    return this.request(`/v1/users/${userId}/tasks/${id}`, {
      method: 'DELETE',
    });
  }

  async updateTaskStatus(id: string, completed: boolean): Promise<ApiResponse<Task>> {
    const userId = await this.getUserId();
    if (!userId) {
      return { error: 'User not authenticated', status: 401 };
    }
    return this.request<Task>(`/v1/users/${userId}/tasks/${id}/complete`, {
      method: 'PATCH',
      body: JSON.stringify({ completed }),
    });
  }
}

export const apiClient = new ApiClient();