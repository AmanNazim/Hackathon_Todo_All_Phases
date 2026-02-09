/**
 * TaskFilter Component
 *
 * Provides filtering and sorting options for task lists
 */

'use client';

import React from 'react';
import Dropdown from '../ui/Dropdown';
import Badge from '../ui/Badge';

export interface TaskFilterProps {
  onFilterChange?: (filters: TaskFilters) => void;
  onSortChange?: (sort: TaskSort) => void;
  activeFilters?: TaskFilters;
  activeSort?: TaskSort;
  className?: string;
}

export interface TaskFilters {
  status?: string[];
  priority?: string[];
  completed?: boolean;
}

export interface TaskSort {
  field: 'created_at' | 'updated_at' | 'due_date' | 'priority' | 'title';
  order: 'asc' | 'desc';
}

const TaskFilter: React.FC<TaskFilterProps> = ({
  onFilterChange,
  onSortChange,
  activeFilters = {},
  activeSort = { field: 'created_at', order: 'desc' },
  className = '',
}) => {
  const [filters, setFilters] = React.useState<TaskFilters>(activeFilters);
  const [sort, setSort] = React.useState<TaskSort>(activeSort);

  const statusOptions = [
    { value: 'todo', label: 'To Do' },
    { value: 'in_progress', label: 'In Progress' },
    { value: 'review', label: 'Review' },
    { value: 'done', label: 'Done' },
    { value: 'blocked', label: 'Blocked' },
  ];

  const priorityOptions = [
    { value: 'low', label: 'Low' },
    { value: 'medium', label: 'Medium' },
    { value: 'high', label: 'High' },
    { value: 'urgent', label: 'Urgent' },
  ];

  const sortOptions = [
    { value: 'created_at', label: 'Date Created' },
    { value: 'updated_at', label: 'Date Updated' },
    { value: 'due_date', label: 'Due Date' },
    { value: 'priority', label: 'Priority' },
    { value: 'title', label: 'Title' },
  ];

  const handleStatusToggle = (status: string) => {
    const newStatuses = filters.status?.includes(status)
      ? filters.status.filter((s) => s !== status)
      : [...(filters.status || []), status];

    const newFilters = { ...filters, status: newStatuses };
    setFilters(newFilters);
    onFilterChange?.(newFilters);
  };

  const handlePriorityToggle = (priority: string) => {
    const newPriorities = filters.priority?.includes(priority)
      ? filters.priority.filter((p) => p !== priority)
      : [...(filters.priority || []), priority];

    const newFilters = { ...filters, priority: newPriorities };
    setFilters(newFilters);
    onFilterChange?.(newFilters);
  };

  const handleCompletedToggle = () => {
    const newFilters = {
      ...filters,
      completed: filters.completed === undefined ? true : !filters.completed,
    };
    setFilters(newFilters);
    onFilterChange?.(newFilters);
  };

  const handleSortChange = (field: string) => {
    const newSort: TaskSort = {
      field: field as TaskSort['field'],
      order: sort.field === field && sort.order === 'asc' ? 'desc' : 'asc',
    };
    setSort(newSort);
    onSortChange?.(newSort);
  };

  const clearFilters = () => {
    const newFilters: TaskFilters = {};
    setFilters(newFilters);
    onFilterChange?.(newFilters);
  };

  const activeFilterCount =
    (filters.status?.length || 0) +
    (filters.priority?.length || 0) +
    (filters.completed !== undefined ? 1 : 0);

  return (
    <div className={`flex flex-wrap items-center gap-3 ${className}`}>
      {/* Status Filter */}
      <Dropdown
        trigger={
          <button className="inline-flex items-center px-4 py-2 border border-gray-300 dark:border-gray-700 rounded-lg text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-bubblegum-pink-500">
            Status
            {filters.status && filters.status.length > 0 && (
              <Badge variant="primary" className="ml-2">
                {filters.status.length}
              </Badge>
            )}
          </button>
        }
      >
        <div className="py-1">
          {statusOptions.map((option) => (
            <button
              key={option.value}
              onClick={() => handleStatusToggle(option.value)}
              className={`
                block w-full text-left px-4 py-2 text-sm
                ${
                  filters.status?.includes(option.value)
                    ? 'bg-bubblegum-pink-50 dark:bg-bubblegum-pink-900/20 text-bubblegum-pink-600 dark:text-bubblegum-pink-400'
                    : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800'
                }
              `}
            >
              {option.label}
            </button>
          ))}
        </div>
      </Dropdown>

      {/* Priority Filter */}
      <Dropdown
        trigger={
          <button className="inline-flex items-center px-4 py-2 border border-gray-300 dark:border-gray-700 rounded-lg text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-bubblegum-pink-500">
            Priority
            {filters.priority && filters.priority.length > 0 && (
              <Badge variant="primary" className="ml-2">
                {filters.priority.length}
              </Badge>
            )}
          </button>
        }
      >
        <div className="py-1">
          {priorityOptions.map((option) => (
            <button
              key={option.value}
              onClick={() => handlePriorityToggle(option.value)}
              className={`
                block w-full text-left px-4 py-2 text-sm
                ${
                  filters.priority?.includes(option.value)
                    ? 'bg-bubblegum-pink-50 dark:bg-bubblegum-pink-900/20 text-bubblegum-pink-600 dark:text-bubblegum-pink-400'
                    : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800'
                }
              `}
            >
              {option.label}
            </button>
          ))}
        </div>
      </Dropdown>

      {/* Sort */}
      <Dropdown
        trigger={
          <button className="inline-flex items-center px-4 py-2 border border-gray-300 dark:border-gray-700 rounded-lg text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-bubblegum-pink-500">
            Sort
            <svg
              className={`ml-2 w-4 h-4 transition-transform ${
                sort.order === 'desc' ? 'rotate-180' : ''
              }`}
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M5 15l7-7 7 7"
              />
            </svg>
          </button>
        }
      >
        <div className="py-1">
          {sortOptions.map((option) => (
            <button
              key={option.value}
              onClick={() => handleSortChange(option.value)}
              className={`
                block w-full text-left px-4 py-2 text-sm
                ${
                  sort.field === option.value
                    ? 'bg-bubblegum-pink-50 dark:bg-bubblegum-pink-900/20 text-bubblegum-pink-600 dark:text-bubblegum-pink-400'
                    : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800'
                }
              `}
            >
              {option.label}
            </button>
          ))}
        </div>
      </Dropdown>

      {/* Completed Toggle */}
      <button
        onClick={handleCompletedToggle}
        className={`
          inline-flex items-center px-4 py-2 border rounded-lg text-sm font-medium
          focus:outline-none focus:ring-2 focus:ring-bubblegum-pink-500
          ${
            filters.completed !== undefined
              ? 'border-bubblegum-pink-600 bg-bubblegum-pink-50 dark:bg-bubblegum-pink-900/20 text-bubblegum-pink-600 dark:text-bubblegum-pink-400'
              : 'border-gray-300 dark:border-gray-700 text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700'
          }
        `}
      >
        {filters.completed ? 'Completed' : 'All'}
      </button>

      {/* Clear Filters */}
      {activeFilterCount > 0 && (
        <button
          onClick={clearFilters}
          className="inline-flex items-center px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 hover:text-bubblegum-pink-600 dark:hover:text-bubblegum-pink-400"
        >
          Clear filters
          <Badge variant="secondary" className="ml-2">
            {activeFilterCount}
          </Badge>
        </button>
      )}
    </div>
  );
};

export default TaskFilter;
