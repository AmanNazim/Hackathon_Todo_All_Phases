'use client';

import React, { useState, useEffect } from 'react';
import Button from '../ui/Button';

interface Reminder {
  id: string;
  taskId: string;
  taskTitle: string;
  reminderTime: string;
  type: 'notification' | 'email' | 'both';
  isRecurring?: boolean;
  recurringInterval?: number; // in minutes
}

interface ReminderManagerProps {
  taskId: string;
  taskTitle: string;
  reminders: Reminder[];
  onAddReminder: (reminder: Omit<Reminder, 'id'>) => Promise<void>;
  onDeleteReminder: (id: string) => Promise<void>;
  className?: string;
}

export default function ReminderManager({
  taskId,
  taskTitle,
  reminders,
  onAddReminder,
  onDeleteReminder,
  className = '',
}: ReminderManagerProps) {
  const [notificationPermission, setNotificationPermission] = useState<NotificationPermission>('default');
  const [isAddingReminder, setIsAddingReminder] = useState(false);
  const [reminderTime, setReminderTime] = useState('');
  const [reminderType, setReminderType] = useState<'notification' | 'email' | 'both'>('notification');
  const [isRecurring, setIsRecurring] = useState(false);
  const [recurringInterval, setRecurringInterval] = useState(60);

  useEffect(() => {
    if ('Notification' in window) {
      setNotificationPermission(Notification.permission);
    }
  }, []);

  const requestNotificationPermission = async () => {
    if ('Notification' in window) {
      const permission = await Notification.requestPermission();
      setNotificationPermission(permission);
      return permission === 'granted';
    }
    return false;
  };

  const scheduleNotification = (reminder: Reminder) => {
    const reminderDate = new Date(reminder.reminderTime);
    const now = new Date();
    const timeUntilReminder = reminderDate.getTime() - now.getTime();

    if (timeUntilReminder > 0) {
      setTimeout(() => {
        if ('Notification' in window && Notification.permission === 'granted') {
          new Notification('Task Reminder', {
            body: `Reminder: ${reminder.taskTitle}`,
            icon: '/favicon.ico',
            badge: '/favicon.ico',
            tag: reminder.id,
            requireInteraction: true,
          });
        }

        // If recurring, schedule next reminder
        if (reminder.isRecurring && reminder.recurringInterval) {
          const nextReminderTime = new Date(reminderDate.getTime() + reminder.recurringInterval * 60 * 1000);
          scheduleNotification({
            ...reminder,
            reminderTime: nextReminderTime.toISOString(),
          });
        }
      }, timeUntilReminder);
    }
  };

  const handleAddReminder = async () => {
    if (!reminderTime) {
      alert('Please select a reminder time');
      return;
    }

    const reminderDate = new Date(reminderTime);
    if (reminderDate <= new Date()) {
      alert('Reminder time must be in the future');
      return;
    }

    if (reminderType === 'notification' || reminderType === 'both') {
      const hasPermission = notificationPermission === 'granted' || (await requestNotificationPermission());
      if (!hasPermission) {
        alert('Notification permission is required for browser notifications');
        return;
      }
    }

    const newReminder: Omit<Reminder, 'id'> = {
      taskId,
      taskTitle,
      reminderTime,
      type: reminderType,
      isRecurring,
      recurringInterval: isRecurring ? recurringInterval : undefined,
    };

    try {
      await onAddReminder(newReminder);

      // Schedule the notification
      if (reminderType === 'notification' || reminderType === 'both') {
        scheduleNotification({
          ...newReminder,
          id: Date.now().toString(), // Temporary ID for scheduling
        });
      }

      // Reset form
      setReminderTime('');
      setReminderType('notification');
      setIsRecurring(false);
      setRecurringInterval(60);
      setIsAddingReminder(false);
    } catch (error) {
      console.error('Failed to add reminder:', error);
      alert('Failed to add reminder');
    }
  };

  const handleDeleteReminder = async (id: string) => {
    if (!confirm('Are you sure you want to delete this reminder?')) return;

    try {
      await onDeleteReminder(id);
    } catch (error) {
      console.error('Failed to delete reminder:', error);
      alert('Failed to delete reminder');
    }
  };

  const formatReminderTime = (time: string): string => {
    const date = new Date(time);
    const now = new Date();
    const diff = date.getTime() - now.getTime();

    if (diff < 0) return 'Past';

    const minutes = Math.floor(diff / (1000 * 60));
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);

    if (days > 0) return `in ${days} day${days > 1 ? 's' : ''}`;
    if (hours > 0) return `in ${hours} hour${hours > 1 ? 's' : ''}`;
    if (minutes > 0) return `in ${minutes} minute${minutes > 1 ? 's' : ''}`;
    return 'Soon';
  };

  const getQuickReminderOptions = () => {
    const now = new Date();
    return [
      { label: '15 minutes', value: new Date(now.getTime() + 15 * 60 * 1000).toISOString().slice(0, 16) },
      { label: '1 hour', value: new Date(now.getTime() + 60 * 60 * 1000).toISOString().slice(0, 16) },
      { label: '3 hours', value: new Date(now.getTime() + 3 * 60 * 60 * 1000).toISOString().slice(0, 16) },
      { label: 'Tomorrow', value: new Date(now.getTime() + 24 * 60 * 60 * 1000).toISOString().slice(0, 16) },
    ];
  };

  return (
    <div className={`bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700 ${className}`}>
      <div className="p-4 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between">
          <h4 className="text-sm font-medium text-gray-900 dark:text-white flex items-center gap-2">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"
              />
            </svg>
            Reminders
          </h4>
          {!isAddingReminder && (
            <Button onClick={() => setIsAddingReminder(true)} size="sm" variant="secondary">
              <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
              Add
            </Button>
          )}
        </div>
      </div>

      <div className="p-4">
        {/* Notification Permission Warning */}
        {notificationPermission !== 'granted' && (
          <div className="mb-4 p-3 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg">
            <div className="flex items-start gap-2">
              <svg className="w-5 h-5 text-yellow-600 dark:text-yellow-400 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                <path
                  fillRule="evenodd"
                  d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
                  clipRule="evenodd"
                />
              </svg>
              <div className="flex-1">
                <p className="text-sm text-yellow-800 dark:text-yellow-200">
                  Browser notifications are {notificationPermission === 'denied' ? 'blocked' : 'not enabled'}.
                </p>
                {notificationPermission === 'default' && (
                  <button
                    onClick={requestNotificationPermission}
                    className="text-sm text-yellow-700 dark:text-yellow-300 underline hover:no-underline mt-1"
                  >
                    Enable notifications
                  </button>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Add Reminder Form */}
        {isAddingReminder && (
          <div className="mb-4 p-4 bg-gray-50 dark:bg-gray-800 rounded-lg space-y-3">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Reminder Time
              </label>
              <input
                type="datetime-local"
                value={reminderTime}
                onChange={(e) => setReminderTime(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-900 text-gray-900 dark:text-white"
              />

              {/* Quick Options */}
              <div className="flex flex-wrap gap-2 mt-2">
                {getQuickReminderOptions().map((option) => (
                  <button
                    key={option.label}
                    onClick={() => setReminderTime(option.value)}
                    className="px-2 py-1 text-xs bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded hover:bg-gray-50 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-300"
                  >
                    {option.label}
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Reminder Type
              </label>
              <div className="flex gap-2">
                {(['notification', 'email', 'both'] as const).map((type) => (
                  <button
                    key={type}
                    onClick={() => setReminderType(type)}
                    className={`flex-1 px-3 py-2 rounded-lg border-2 transition-all text-sm ${
                      reminderType === type
                        ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300'
                        : 'border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:border-gray-400 dark:hover:border-gray-500'
                    }`}
                  >
                    {type.charAt(0).toUpperCase() + type.slice(1)}
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={isRecurring}
                  onChange={(e) => setIsRecurring(e.target.checked)}
                  className="w-4 h-4 text-blue-600 rounded"
                />
                <span className="text-sm text-gray-700 dark:text-gray-300">Recurring reminder</span>
              </label>

              {isRecurring && (
                <div className="mt-2 flex items-center gap-2">
                  <span className="text-sm text-gray-700 dark:text-gray-300">Repeat every</span>
                  <input
                    type="number"
                    min="1"
                    value={recurringInterval}
                    onChange={(e) => setRecurringInterval(parseInt(e.target.value) || 1)}
                    className="w-20 px-2 py-1 border border-gray-300 dark:border-gray-600 rounded focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-900 text-gray-900 dark:text-white"
                  />
                  <span className="text-sm text-gray-700 dark:text-gray-300">minutes</span>
                </div>
              )}
            </div>

            <div className="flex justify-end gap-2">
              <Button
                onClick={() => {
                  setIsAddingReminder(false);
                  setReminderTime('');
                  setReminderType('notification');
                  setIsRecurring(false);
                }}
                variant="secondary"
                size="sm"
              >
                Cancel
              </Button>
              <Button onClick={handleAddReminder} size="sm">
                Add Reminder
              </Button>
            </div>
          </div>
        )}

        {/* Reminders List */}
        {reminders.length === 0 ? (
          <p className="text-sm text-gray-500 dark:text-gray-400 text-center py-4">
            No reminders set
          </p>
        ) : (
          <div className="space-y-2">
            {reminders.map((reminder) => (
              <div
                key={reminder.id}
                className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800 rounded-lg"
              >
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-sm font-medium text-gray-900 dark:text-white">
                      {new Date(reminder.reminderTime).toLocaleString()}
                    </span>
                    <span className="text-xs text-gray-500 dark:text-gray-400">
                      ({formatReminderTime(reminder.reminderTime)})
                    </span>
                  </div>
                  <div className="flex items-center gap-2 text-xs text-gray-600 dark:text-gray-400">
                    <span className="px-2 py-0.5 bg-gray-200 dark:bg-gray-700 rounded">
                      {reminder.type}
                    </span>
                    {reminder.isRecurring && (
                      <span className="px-2 py-0.5 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 rounded">
                        Recurring ({reminder.recurringInterval}min)
                      </span>
                    )}
                  </div>
                </div>
                <button
                  onClick={() => handleDeleteReminder(reminder.id)}
                  className="p-1 text-gray-400 hover:text-red-600 dark:hover:text-red-400"
                  aria-label="Delete reminder"
                >
                  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                    <path
                      fillRule="evenodd"
                      d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                      clipRule="evenodd"
                    />
                  </svg>
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
