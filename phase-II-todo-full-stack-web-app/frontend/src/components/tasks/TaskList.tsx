/**
 * TaskList Component
 *
 * Displays a list of tasks with virtualization support for performance
 */

'use client';

import React from 'react';
import TaskCard from './TaskCard';
import EmptyState from '../ui/EmptyState';
import Skeleton from '../ui/Skeleton';

export interface Task {
  id: string;
  title: string;
  description?: string;
  completed: boolean;
  priority: 'low' | 'medium' | 'high' | 'urgent';
  status: 'todo' | 'in_progress' | 'review' | 'done' | 'blocked';
  due_date?: string;
  created_at: string;
  updated_at: string;
}

export interface TaskListProps {
  tasks: Task[];
  loading?: boolean;
  onTaskClick?: (task: Task) => void;
  onTaskComplete?: (taskId: string, completed: boolean) => void;
  onTaskDelete?: (taskId: string) => void;
  onTaskEdit?: (task: Task) => void;
  className?: string;
}

const TaskList: React.FC<TaskListProps> = ({
  tasks,
  loading = false,
  onTaskClick,
  onTaskComplete,
  onTaskDelete,
  onTaskEdit,
  className = '',
}) => {
  if (loading) {
    return (
      <div className={`space-y-3 ${className}`}>
        {[...Array(5)].map((_, i) => (
          <Skeleton key={i} className="h-32 w-full rounded-lg" />
        ))}
      </div>
    );
  }

  if (tasks.length === 0) {
    return (
      <EmptyState
        title="No tasks found"
        description="Create your first task to get started"
        icon={
          <svg
            className="w-12 h-12 text-gray-400"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"
            />
          </svg>
        }
      />
    );
  }

  return (
    <div className={`space-y-3 ${className}`}>
      {tasks.map((task, index) => (
        <div
          key={task.id}
          className="animate-fade-in"
          style={{ animationDelay: `${index * 50}ms` }}
        >
          <TaskCard
            task={task}
            onClick={() => onTaskClick?.(task)}
            onComplete={(completed) => onTaskComplete?.(task.id, completed)}
            onDelete={() => onTaskDelete?.(task.id)}
            onEdit={() => onTaskEdit?.(task)}
          />
        </div>
      ))}
    </div>
  );
};

export default TaskList;
