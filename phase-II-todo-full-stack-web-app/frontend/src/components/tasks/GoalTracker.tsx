'use client';

import React, { useState } from 'react';
import Button from '../ui/Button';
import Modal from '../ui/Modal';

interface Goal {
  id: string;
  title: string;
  description?: string;
  targetValue: number;
  currentValue: number;
  unit: string; // e.g., "tasks", "hours", "points"
  startDate: string;
  endDate: string;
  category?: string;
  color?: string;
}

interface GoalTrackerProps {
  goals: Goal[];
  onCreateGoal: (goal: Omit<Goal, 'id' | 'currentValue'>) => Promise<void>;
  onUpdateGoal: (id: string, updates: Partial<Goal>) => Promise<void>;
  onDeleteGoal: (id: string) => Promise<void>;
  onUpdateProgress: (id: string, value: number) => Promise<void>;
  className?: string;
}

export default function GoalTracker({
  goals,
  onCreateGoal,
  onUpdateGoal,
  onDeleteGoal,
  onUpdateProgress,
  className = '',
}: GoalTrackerProps) {
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [selectedGoal, setSelectedGoal] = useState<Goal | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);

  const [formData, setFormData] = useState({
    title: '',
    description: '',
    targetValue: 10,
    unit: 'tasks',
    startDate: new Date().toISOString().split('T')[0],
    endDate: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    category: '',
    color: '#3b82f6',
  });

  const resetForm = () => {
    setFormData({
      title: '',
      description: '',
      targetValue: 10,
      unit: 'tasks',
      startDate: new Date().toISOString().split('T')[0],
      endDate: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
      category: '',
      color: '#3b82f6',
    });
  };

  const handleCreateGoal = async () => {
    if (!formData.title || formData.targetValue <= 0) {
      alert('Please provide a title and valid target value');
      return;
    }

    setIsProcessing(true);
    try {
      await onCreateGoal(formData);
      setIsCreateModalOpen(false);
      resetForm();
    } catch (error) {
      console.error('Failed to create goal:', error);
      alert('Failed to create goal');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleUpdateGoal = async () => {
    if (!selectedGoal) return;

    setIsProcessing(true);
    try {
      await onUpdateGoal(selectedGoal.id, formData);
      setIsEditModalOpen(false);
      setSelectedGoal(null);
      resetForm();
    } catch (error) {
      console.error('Failed to update goal:', error);
      alert('Failed to update goal');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleDeleteGoal = async (id: string) => {
    if (!confirm('Are you sure you want to delete this goal?')) return;

    setIsProcessing(true);
    try {
      await onDeleteGoal(id);
    } catch (error) {
      console.error('Failed to delete goal:', error);
      alert('Failed to delete goal');
    } finally {
      setIsProcessing(false);
    }
  };

  const openEditModal = (goal: Goal) => {
    setSelectedGoal(goal);
    setFormData({
      title: goal.title,
      description: goal.description || '',
      targetValue: goal.targetValue,
      unit: goal.unit,
      startDate: goal.startDate,
      endDate: goal.endDate,
      category: goal.category || '',
      color: goal.color || '#3b82f6',
    });
    setIsEditModalOpen(true);
  };

  const getProgressPercentage = (goal: Goal): number => {
    return Math.min(Math.round((goal.currentValue / goal.targetValue) * 100), 100);
  };

  const getDaysRemaining = (endDate: string): number => {
    const end = new Date(endDate);
    const now = new Date();
    const diff = end.getTime() - now.getTime();
    return Math.ceil(diff / (1000 * 60 * 60 * 24));
  };

  const getStatusColor = (goal: Goal): string => {
    const percentage = getProgressPercentage(goal);
    const daysRemaining = getDaysRemaining(goal.endDate);

    if (percentage >= 100) return 'text-green-600 dark:text-green-400';
    if (daysRemaining < 0) return 'text-red-600 dark:text-red-400';
    if (percentage >= 75) return 'text-blue-600 dark:text-blue-400';
    if (percentage >= 50) return 'text-yellow-600 dark:text-yellow-400';
    return 'text-orange-600 dark:text-orange-400';
  };

  const getStatusLabel = (goal: Goal): string => {
    const percentage = getProgressPercentage(goal);
    const daysRemaining = getDaysRemaining(goal.endDate);

    if (percentage >= 100) return 'Completed';
    if (daysRemaining < 0) return 'Overdue';
    if (daysRemaining === 0) return 'Due today';
    if (daysRemaining === 1) return '1 day left';
    return `${daysRemaining} days left`;
  };

  const GoalForm = () => (
    <div className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
          Goal Title *
        </label>
        <input
          type="text"
          value={formData.title}
          onChange={(e) => setFormData({ ...formData, title: e.target.value })}
          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
          placeholder="e.g., Complete 50 tasks this month"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
          Description
        </label>
        <textarea
          value={formData.description}
          onChange={(e) => setFormData({ ...formData, description: e.target.value })}
          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
          rows={2}
          placeholder="What do you want to achieve?"
        />
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Target Value *
          </label>
          <input
            type="number"
            min="1"
            value={formData.targetValue}
            onChange={(e) => setFormData({ ...formData, targetValue: parseInt(e.target.value) || 0 })}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Unit
          </label>
          <input
            type="text"
            value={formData.unit}
            onChange={(e) => setFormData({ ...formData, unit: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
            placeholder="e.g., tasks, hours"
          />
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Start Date
          </label>
          <input
            type="date"
            value={formData.startDate}
            onChange={(e) => setFormData({ ...formData, startDate: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            End Date
          </label>
          <input
            type="date"
            value={formData.endDate}
            onChange={(e) => setFormData({ ...formData, endDate: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
          />
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
          Category
        </label>
        <input
          type="text"
          value={formData.category}
          onChange={(e) => setFormData({ ...formData, category: e.target.value })}
          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
          placeholder="e.g., Work, Personal, Health"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
          Color
        </label>
        <div className="flex gap-2">
          <input
            type="color"
            value={formData.color}
            onChange={(e) => setFormData({ ...formData, color: e.target.value })}
            className="w-16 h-10 border border-gray-300 dark:border-gray-600 rounded-lg cursor-pointer"
          />
          <input
            type="text"
            value={formData.color}
            onChange={(e) => setFormData({ ...formData, color: e.target.value })}
            className="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
            placeholder="#3b82f6"
          />
        </div>
      </div>
    </div>
  );

  return (
    <div className={`bg-white dark:bg-gray-900 rounded-lg shadow ${className}`}>
      <div className="p-6 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Goal Tracker</h3>
          <Button onClick={() => setIsCreateModalOpen(true)}>
            <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            New Goal
          </Button>
        </div>
      </div>

      <div className="p-6">
        {goals.length === 0 ? (
          <div className="text-center py-12">
            <svg
              className="w-16 h-16 mx-auto text-gray-400 dark:text-gray-500 mb-4"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z"
              />
            </svg>
            <p className="text-gray-600 dark:text-gray-400 mb-4">No goals yet</p>
            <Button onClick={() => setIsCreateModalOpen(true)}>Create your first goal</Button>
          </div>
        ) : (
          <div className="space-y-4">
            {goals.map((goal) => {
              const percentage = getProgressPercentage(goal);
              const statusColor = getStatusColor(goal);
              const statusLabel = getStatusLabel(goal);

              return (
                <div
                  key={goal.id}
                  className="border border-gray-200 dark:border-gray-700 rounded-lg p-4 hover:shadow-md transition-shadow"
                  style={{ borderLeftWidth: '4px', borderLeftColor: goal.color }}
                >
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1">
                      <h4 className="font-medium text-gray-900 dark:text-white mb-1">
                        {goal.title}
                      </h4>
                      {goal.description && (
                        <p className="text-sm text-gray-600 dark:text-gray-400">
                          {goal.description}
                        </p>
                      )}
                    </div>
                    <div className="flex gap-2 ml-4">
                      <button
                        onClick={() => openEditModal(goal)}
                        className="p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                        aria-label="Edit goal"
                      >
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
                          />
                        </svg>
                      </button>
                      <button
                        onClick={() => handleDeleteGoal(goal.id)}
                        className="p-1 text-gray-400 hover:text-red-600 dark:hover:text-red-400"
                        aria-label="Delete goal"
                        disabled={isProcessing}
                      >
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                          />
                        </svg>
                      </button>
                    </div>
                  </div>

                  <div className="mb-3">
                    <div className="flex items-center justify-between text-sm mb-1">
                      <span className="text-gray-700 dark:text-gray-300">
                        {goal.currentValue} / {goal.targetValue} {goal.unit}
                      </span>
                      <span className={`font-medium ${statusColor}`}>{percentage}%</span>
                    </div>
                    <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                      <div
                        className="h-2 rounded-full transition-all duration-300"
                        style={{
                          width: `${percentage}%`,
                          backgroundColor: goal.color,
                        }}
                      />
                    </div>
                  </div>

                  <div className="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
                    <span>{statusLabel}</span>
                    {goal.category && (
                      <span className="px-2 py-0.5 bg-gray-100 dark:bg-gray-800 rounded">
                        {goal.category}
                      </span>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Create Goal Modal */}
      <Modal
        isOpen={isCreateModalOpen}
        onClose={() => {
          setIsCreateModalOpen(false);
          resetForm();
        }}
        title="Create New Goal"
      >
        <GoalForm />
        <div className="flex justify-end gap-3 mt-6">
          <Button
            onClick={() => {
              setIsCreateModalOpen(false);
              resetForm();
            }}
            variant="secondary"
            disabled={isProcessing}
          >
            Cancel
          </Button>
          <Button onClick={handleCreateGoal} disabled={isProcessing}>
            {isProcessing ? 'Creating...' : 'Create Goal'}
          </Button>
        </div>
      </Modal>

      {/* Edit Goal Modal */}
      <Modal
        isOpen={isEditModalOpen}
        onClose={() => {
          setIsEditModalOpen(false);
          setSelectedGoal(null);
          resetForm();
        }}
        title="Edit Goal"
      >
        <GoalForm />
        <div className="flex justify-end gap-3 mt-6">
          <Button
            onClick={() => {
              setIsEditModalOpen(false);
              setSelectedGoal(null);
              resetForm();
            }}
            variant="secondary"
            disabled={isProcessing}
          >
            Cancel
          </Button>
          <Button onClick={handleUpdateGoal} disabled={isProcessing}>
            {isProcessing ? 'Saving...' : 'Save Changes'}
          </Button>
        </div>
      </Modal>
    </div>
  );
}
