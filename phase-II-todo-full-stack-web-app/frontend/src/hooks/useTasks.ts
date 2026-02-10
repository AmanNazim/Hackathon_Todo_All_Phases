import { useState, useEffect } from 'react';
import { Task, TaskFilters } from '@/types';
import { apiClient } from '@/lib/api';
import { useToast } from '@/providers/toast-provider';

export const useTasks = () => {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const { addToast } = useToast();

  // Fetch all tasks
  const fetchTasks = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await apiClient.getTasks();
      if (response.data) {
        setTasks(response.data);
      } else {
        const errorMsg = response.error || 'Failed to fetch tasks';
        setError(errorMsg);
        addToast(errorMsg, 'error');
      }
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'An unknown error occurred';
      setError(errorMsg);
      addToast(errorMsg, 'error');
    } finally {
      setLoading(false);
    }
  };

  // Create a new task
  const createTask = async (taskData: Partial<Task>): Promise<Task | null> => {
    try {
      setLoading(true);
      setError(null);

      const response = await apiClient.createTask(taskData);
      if (response.data) {
        const newTask = response.data;
        setTasks(prev => [...prev, newTask]);
        addToast('Task created successfully!', 'success');
        return newTask;
      } else {
        const errorMsg = response.error || 'Failed to create task';
        setError(errorMsg);
        addToast(errorMsg, 'error');
        return null;
      }
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'An unknown error occurred';
      setError(errorMsg);
      addToast(errorMsg, 'error');
      return null;
    } finally {
      setLoading(false);
    }
  };

  // Update a task
  const updateTask = async (id: string, taskData: Partial<Task>): Promise<Task | null> => {
    try {
      setLoading(true);
      setError(null);

      const response = await apiClient.updateTask(id, taskData);
      if (response.data) {
        const updatedTask = response.data;
        const updatedTasks = tasks.map(task =>
          task.id === id ? updatedTask : task
        );
        setTasks(updatedTasks);
        addToast('Task updated successfully!', 'success');
        return updatedTask;
      } else {
        const errorMsg = response.error || 'Failed to update task';
        setError(errorMsg);
        addToast(errorMsg, 'error');
        return null;
      }
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'An unknown error occurred';
      setError(errorMsg);
      addToast(errorMsg, 'error');
      return null;
    } finally {
      setLoading(false);
    }
  };

  // Toggle task completion status
  const toggleTaskStatus = async (id: string): Promise<Task | null> => {
    try {
      setLoading(true);
      setError(null);

      const currentTask = tasks.find(task => task.id === id);
      if (!currentTask) {
        const errorMsg = 'Task not found';
        setError(errorMsg);
        addToast(errorMsg, 'error');
        return null;
      }

      const response = await apiClient.updateTaskStatus(id, !currentTask.completed);
      if (response.data) {
        const updatedTask = response.data;
        const updatedTasks = tasks.map(task =>
          task.id === id ? updatedTask : task
        );
        setTasks(updatedTasks);
        addToast(`Task marked as ${!currentTask.completed ? 'completed' : 'incomplete'}!`, 'success');
        return updatedTask;
      } else {
        const errorMsg = response.error || 'Failed to update task status';
        setError(errorMsg);
        addToast(errorMsg, 'error');
        return null;
      }
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'An unknown error occurred';
      setError(errorMsg);
      addToast(errorMsg, 'error');
      return null;
    } finally {
      setLoading(false);
    }
  };

  // Delete a task
  const deleteTask = async (id: string): Promise<boolean> => {
    try {
      setLoading(true);
      setError(null);

      const response = await apiClient.deleteTask(id);
      if (response.status === 200) {
        const updatedTasks = tasks.filter(task => task.id !== id);
        setTasks(updatedTasks);
        addToast('Task deleted successfully!', 'success');
        return true;
      } else {
        const errorMsg = response.error || 'Failed to delete task';
        setError(errorMsg);
        addToast(errorMsg, 'error');
        return false;
      }
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'An unknown error occurred';
      setError(errorMsg);
      addToast(errorMsg, 'error');
      return false;
    } finally {
      setLoading(false);
    }
  };

  // Filter tasks based on criteria
  const filterTasks = (filters: TaskFilters): Task[] => {
    return tasks.filter(task => {
      // Apply status filter
      if (filters.status && filters.status !== 'all') {
        if (filters.status === 'active' && task.completed) return false;
        if (filters.status === 'completed' && !task.completed) return false;
      }

      // Apply priority filter
      if (filters.priority && filters.priority !== 'all') {
        if (task.priority !== filters.priority) return false;
      }

      // Apply search filter
      if (filters.search) {
        const searchTerm = filters.search.toLowerCase();
        if (
          !task.title.toLowerCase().includes(searchTerm) &&
          !(task.description && task.description.toLowerCase().includes(searchTerm))
        ) {
          return false;
        }
      }

      return true;
    });
  };

  // Get task by ID
  const getTaskById = (id: string): Task | undefined => {
    return tasks.find(task => task.id === id);
  };

  // Get task statistics
  const getTaskStats = () => {
    const total = tasks.length;
    const completed = tasks.filter(task => task.completed).length;
    const pending = tasks.filter(task => !task.completed).length;

    // For overdue, we consider tasks that are not completed and past their due date
    const overdue = tasks.filter(task =>
      !task.completed &&
      task.dueDate &&
      new Date(task.dueDate) < new Date()
    ).length;

    return { total, completed, pending, overdue };
  };

  return {
    tasks,
    loading,
    error,
    fetchTasks,
    createTask,
    updateTask,
    toggleTaskStatus,
    deleteTask,
    filterTasks,
    getTaskById,
    getTaskStats,
  };
};