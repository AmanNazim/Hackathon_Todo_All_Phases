'use client';

import React, { useState } from 'react';
import Button from '../ui/Button';

interface Task {
  id: string;
  title: string;
  status: 'pending' | 'in_progress' | 'completed';
  priority: 'low' | 'medium' | 'high' | 'urgent';
}

interface BulkOperationsProps {
  selectedTasks: Task[];
  onBulkStatusChange?: (taskIds: string[], status: Task['status']) => Promise<void>;
  onBulkPriorityChange?: (taskIds: string[], priority: Task['priority']) => Promise<void>;
  onBulkDelete?: (taskIds: string[]) => Promise<void>;
  onBulkTagAdd?: (taskIds: string[], tags: string[]) => Promise<void>;
  onClearSelection?: () => void;
  className?: string;
}

export default function BulkOperations({
  selectedTasks,
  onBulkStatusChange,
  onBulkPriorityChange,
  onBulkDelete,
  onBulkTagAdd,
  onClearSelection,
  className = '',
}: BulkOperationsProps) {
  const [isProcessing, setIsProcessing] = useState(false);
  const [showStatusMenu, setShowStatusMenu] = useState(false);
  const [showPriorityMenu, setShowPriorityMenu] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  const selectedCount = selectedTasks.length;
  const selectedIds = selectedTasks.map((t) => t.id);

  if (selectedCount === 0) {
    return null;
  }

  const handleStatusChange = async (status: Task['status']) => {
    if (!onBulkStatusChange) return;
    setIsProcessing(true);
    try {
      await onBulkStatusChange(selectedIds, status);
      setShowStatusMenu(false);
    } catch (error) {
      console.error('Failed to update status:', error);
    } finally {
      setIsProcessing(false);
    }
  };

  const handlePriorityChange = async (priority: Task['priority']) => {
    if (!onBulkPriorityChange) return;
    setIsProcessing(true);
    try {
      await onBulkPriorityChange(selectedIds, priority);
      setShowPriorityMenu(false);
    } catch (error) {
      console.error('Failed to update priority:', error);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleDelete = async () => {
    if (!onBulkDelete) return;
    setIsProcessing(true);
    try {
      await onBulkDelete(selectedIds);
      setShowDeleteConfirm(false);
      onClearSelection?.();
    } catch (error) {
      console.error('Failed to delete tasks:', error);
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <>
      <div
        className={`
          fixed bottom-6 left-1/2 transform -translate-x-1/2 z-50
          bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700
          px-6 py-4 flex items-center gap-4 animate-fade-in-up
          ${className}
        `}
      >
        {/* Selection Count */}
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-blue-100 dark:bg-blue-900 rounded-full flex items-center justify-center">
            <span className="text-sm font-bold text-blue-600 dark:text-blue-400">
              {selectedCount}
            </span>
          </div>
          <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
            {selectedCount === 1 ? 'task selected' : 'tasks selected'}
          </span>
        </div>

        <div className="h-6 w-px bg-gray-300 dark:bg-gray-600" />

        {/* Action Buttons */}
        <div className="flex items-center gap-2">
          {/* Change Status */}
          {onBulkStatusChange && (
            <div className="relative">
              <Button
                onClick={() => setShowStatusMenu(!showStatusMenu)}
                disabled={isProcessing}
                variant="secondary"
                size="sm"
              >
                <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
                Status
              </Button>

              {showStatusMenu && (
                <div className="absolute bottom-full mb-2 left-0 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 py-1 min-w-[150px] animate-fade-in-down">
                  <button
                    onClick={() => handleStatusChange('pending')}
                    className="w-full px-4 py-2 text-left text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
                  >
                    Pending
                  </button>
                  <button
                    onClick={() => handleStatusChange('in_progress')}
                    className="w-full px-4 py-2 text-left text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
                  >
                    In Progress
                  </button>
                  <button
                    onClick={() => handleStatusChange('completed')}
                    className="w-full px-4 py-2 text-left text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
                  >
                    Completed
                  </button>
                </div>
              )}
            </div>
          )}

          {/* Change Priority */}
          {onBulkPriorityChange && (
            <div className="relative">
              <Button
                onClick={() => setShowPriorityMenu(!showPriorityMenu)}
                disabled={isProcessing}
                variant="secondary"
                size="sm"
              >
                <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M7 11.5V14m0-2.5v-6a1.5 1.5 0 113 0m-3 6a1.5 1.5 0 00-3 0v2a7.5 7.5 0 0015 0v-5a1.5 1.5 0 00-3 0m-6-3V11m0-5.5v-1a1.5 1.5 0 013 0v1m0 0V11m0-5.5a1.5 1.5 0 013 0v3m0 0V11"
                  />
                </svg>
                Priority
              </Button>

              {showPriorityMenu && (
                <div className="absolute bottom-full mb-2 left-0 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 py-1 min-w-[150px] animate-fade-in-down">
                  <button
                    onClick={() => handlePriorityChange('urgent')}
                    className="w-full px-4 py-2 text-left text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center gap-2"
                  >
                    <span className="w-2 h-2 rounded-full bg-red-500" />
                    Urgent
                  </button>
                  <button
                    onClick={() => handlePriorityChange('high')}
                    className="w-full px-4 py-2 text-left text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center gap-2"
                  >
                    <span className="w-2 h-2 rounded-full bg-orange-500" />
                    High
                  </button>
                  <button
                    onClick={() => handlePriorityChange('medium')}
                    className="w-full px-4 py-2 text-left text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center gap-2"
                  >
                    <span className="w-2 h-2 rounded-full bg-yellow-500" />
                    Medium
                  </button>
                  <button
                    onClick={() => handlePriorityChange('low')}
                    className="w-full px-4 py-2 text-left text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center gap-2"
                  >
                    <span className="w-2 h-2 rounded-full bg-green-500" />
                    Low
                  </button>
                </div>
              )}
            </div>
          )}

          {/* Delete */}
          {onBulkDelete && (
            <Button
              onClick={() => setShowDeleteConfirm(true)}
              disabled={isProcessing}
              variant="danger"
              size="sm"
            >
              <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                />
              </svg>
              Delete
            </Button>
          )}
        </div>

        <div className="h-6 w-px bg-gray-300 dark:bg-gray-600" />

        {/* Clear Selection */}
        <button
          onClick={onClearSelection}
          disabled={isProcessing}
          className="text-sm text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white disabled:opacity-50"
        >
          Clear
        </button>
      </div>

      {/* Delete Confirmation Modal */}
      {showDeleteConfirm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 animate-fade-in">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl p-6 max-w-md w-full mx-4 animate-scale-in">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
              Delete {selectedCount} {selectedCount === 1 ? 'task' : 'tasks'}?
            </h3>
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-6">
              This action cannot be undone. The selected tasks will be permanently deleted.
            </p>
            <div className="flex justify-end gap-3">
              <Button
                onClick={() => setShowDeleteConfirm(false)}
                variant="secondary"
                disabled={isProcessing}
              >
                Cancel
              </Button>
              <Button onClick={handleDelete} variant="danger" disabled={isProcessing}>
                {isProcessing ? 'Deleting...' : 'Delete'}
              </Button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
