'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Task, TaskFilters } from '@/types';
import { useTasks } from '@/hooks/useTasks';
import Button from '@/components/ui/Button';
import LoadingSpinner from '@/components/ui/LoadingSpinner';
import { TaskCard } from '@/components/tasks/TaskCard';
import { TaskForm } from '@/components/tasks/TaskForm';

// Force dynamic rendering
export const dynamic = 'force-dynamic';
export const runtime = 'nodejs';

export default function TasksPage() {
  const { tasks, loading, error, fetchTasks } = useTasks();
  const [filteredTasks, setFilteredTasks] = useState<Task[]>([]);
  const [filters, setFilters] = useState<TaskFilters>({
    status: 'all',
    priority: 'all',
    search: ''
  });
  const [showForm, setShowForm] = useState(false);

  useEffect(() => {
    fetchTasks();
  }, [fetchTasks]);

  // Apply filters whenever tasks or filters change
  useEffect(() => {
    let result = [...tasks];

    // Apply status filter
    if (filters.status && filters.status !== 'all') {
      if (filters.status === 'active') {
        result = result.filter(task => !task.completed);
      } else if (filters.status === 'completed') {
        result = result.filter(task => task.completed);
      }
    }

    // Apply priority filter
    if (filters.priority && filters.priority !== 'all') {
      result = result.filter(task => task.priority === filters.priority);
    }

    // Apply search filter
    if (filters.search) {
      const searchTerm = filters.search.toLowerCase();
      result = result.filter(task =>
        task.title.toLowerCase().includes(searchTerm) ||
        (task.description && task.description.toLowerCase().includes(searchTerm))
      );
    }

    setFilteredTasks(result);
  }, [tasks, filters]);

  const handleFilterChange = (filterType: keyof TaskFilters, value: any) => {
    setFilters(prev => ({
      ...prev,
      [filterType]: value
    }));
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-[50vh]">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">My Tasks</h1>
        <Button onClick={() => setShowForm(!showForm)}>
          {showForm ? 'Cancel' : 'Add Task'}
        </Button>
      </div>

      {/* Filters */}
      <Card>
        <CardHeader>
          <CardTitle>Filters</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Status
              </label>
              <select
                value={filters.status || 'all'}
                onChange={(e) => handleFilterChange('status', e.target.value as any)}
                className="w-full rounded-md border border-gray-300 bg-white py-2 px-3 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-700 dark:text-white"
              >
                <option value="all">All</option>
                <option value="active">Active</option>
                <option value="completed">Completed</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Priority
              </label>
              <select
                value={filters.priority || 'all'}
                onChange={(e) => handleFilterChange('priority', e.target.value as any)}
                className="w-full rounded-md border border-gray-300 bg-white py-2 px-3 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-700 dark:text-white"
              >
                <option value="all">All</option>
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
                <option value="urgent">Urgent</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Search
              </label>
              <input
                type="text"
                placeholder="Search tasks..."
                value={filters.search || ''}
                onChange={(e) => handleFilterChange('search', e.target.value)}
                className="w-full rounded-md border border-gray-300 bg-white py-2 px-3 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-700 dark:text-white"
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Task Form */}
      {showForm && (
        <TaskForm
          onSuccess={() => {
            setShowForm(false);
            // Refresh tasks after creating a new one
            window.location.reload();
          }}
          onCancel={() => setShowForm(false)}
        />
      )}

      {/* Task List */}
      <div className="space-y-4">
        {filteredTasks.length === 0 ? (
          <Card>
            <CardContent className="py-12 text-center">
              <p className="text-gray-500 dark:text-gray-400">
                {tasks.length === 0 ? 'No tasks yet. Create your first task!' : 'No tasks match your filters.'}
              </p>
            </CardContent>
          </Card>
        ) : (
          <div className="grid grid-cols-1 gap-4">
            {filteredTasks.map(task => (
              <TaskCard key={task.id} task={task} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}