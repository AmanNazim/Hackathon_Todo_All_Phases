'use client';

import React, { useState, useEffect } from 'react';
import Button from '../ui/Button';

interface TimeEntry {
  id: string;
  taskId: string;
  startTime: string;
  endTime?: string;
  duration: number; // in seconds
  description?: string;
}

interface TimeTrackerProps {
  taskId: string;
  taskTitle: string;
  timeEntries: TimeEntry[];
  onStartTimer: () => Promise<TimeEntry>;
  onStopTimer: (entryId: string) => Promise<TimeEntry>;
  onDeleteEntry: (entryId: string) => Promise<void>;
  onUpdateEntry: (entryId: string, updates: Partial<TimeEntry>) => Promise<void>;
  className?: string;
}

export default function TimeTracker({
  taskId,
  taskTitle,
  timeEntries,
  onStartTimer,
  onStopTimer,
  onDeleteEntry,
  onUpdateEntry,
  className = '',
}: TimeTrackerProps) {
  const [activeEntry, setActiveEntry] = useState<TimeEntry | null>(null);
  const [elapsedTime, setElapsedTime] = useState(0);
  const [isProcessing, setIsProcessing] = useState(false);

  // Find active timer
  useEffect(() => {
    const active = timeEntries.find((entry) => !entry.endTime);
    setActiveEntry(active || null);
  }, [timeEntries]);

  // Update elapsed time for active timer
  useEffect(() => {
    if (!activeEntry) {
      setElapsedTime(0);
      return;
    }

    const startTime = new Date(activeEntry.startTime).getTime();
    const updateElapsed = () => {
      const now = Date.now();
      setElapsedTime(Math.floor((now - startTime) / 1000));
    };

    updateElapsed();
    const interval = setInterval(updateElapsed, 1000);

    return () => clearInterval(interval);
  }, [activeEntry]);

  const formatDuration = (seconds: number): string => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;

    if (hours > 0) {
      return `${hours}h ${minutes}m ${secs}s`;
    }
    if (minutes > 0) {
      return `${minutes}m ${secs}s`;
    }
    return `${secs}s`;
  };

  const formatTime = (dateString: string): string => {
    return new Date(dateString).toLocaleTimeString([], {
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const formatDate = (dateString: string): string => {
    return new Date(dateString).toLocaleDateString();
  };

  const getTotalTime = (): number => {
    return timeEntries.reduce((total, entry) => total + entry.duration, 0);
  };

  const handleStartTimer = async () => {
    if (activeEntry) return;

    setIsProcessing(true);
    try {
      const entry = await onStartTimer();
      setActiveEntry(entry);
    } catch (error) {
      console.error('Failed to start timer:', error);
      alert('Failed to start timer');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleStopTimer = async () => {
    if (!activeEntry) return;

    setIsProcessing(true);
    try {
      await onStopTimer(activeEntry.id);
      setActiveEntry(null);
      setElapsedTime(0);
    } catch (error) {
      console.error('Failed to stop timer:', error);
      alert('Failed to stop timer');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleDeleteEntry = async (entryId: string) => {
    if (!confirm('Are you sure you want to delete this time entry?')) return;

    try {
      await onDeleteEntry(entryId);
    } catch (error) {
      console.error('Failed to delete entry:', error);
      alert('Failed to delete time entry');
    }
  };

  const totalTime = getTotalTime();
  const totalHours = (totalTime / 3600).toFixed(1);

  return (
    <div className={`bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700 ${className}`}>
      {/* Header */}
      <div className="p-4 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between">
          <h4 className="text-sm font-medium text-gray-900 dark:text-white flex items-center gap-2">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            Time Tracking
          </h4>
          <div className="text-sm text-gray-600 dark:text-gray-400">
            Total: <span className="font-medium text-gray-900 dark:text-white">{totalHours}h</span>
          </div>
        </div>
      </div>

      <div className="p-4">
        {/* Active Timer */}
        {activeEntry ? (
          <div className="mb-4 p-4 bg-blue-50 dark:bg-blue-900/20 border-2 border-blue-500 dark:border-blue-400 rounded-lg">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse" />
                <span className="text-sm font-medium text-gray-900 dark:text-white">
                  Timer Running
                </span>
              </div>
              <span className="text-xs text-gray-600 dark:text-gray-400">
                Started at {formatTime(activeEntry.startTime)}
              </span>
            </div>

            <div className="text-center mb-4">
              <div className="text-4xl font-bold text-blue-600 dark:text-blue-400 font-mono">
                {formatDuration(elapsedTime)}
              </div>
            </div>

            <Button
              onClick={handleStopTimer}
              disabled={isProcessing}
              variant="destructive"
              className="w-full"
            >
              <svg className="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path
                  fillRule="evenodd"
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zM8 7a1 1 0 00-1 1v4a1 1 0 001 1h4a1 1 0 001-1V8a1 1 0 00-1-1H8z"
                  clipRule="evenodd"
                />
              </svg>
              Stop Timer
            </Button>
          </div>
        ) : (
          <div className="mb-4">
            <Button
              onClick={handleStartTimer}
              disabled={isProcessing}
              variant="primary"
              className="w-full"
            >
              <svg className="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path
                  fillRule="evenodd"
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z"
                  clipRule="evenodd"
                />
              </svg>
              Start Timer
            </Button>
          </div>
        )}

        {/* Time Entries List */}
        <div>
          <h5 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
            Time Entries ({timeEntries.length})
          </h5>

          {timeEntries.length === 0 ? (
            <p className="text-sm text-gray-500 dark:text-gray-400 text-center py-8">
              No time entries yet. Start the timer to track your work.
            </p>
          ) : (
            <div className="space-y-2">
              {timeEntries
                .filter((entry) => entry.endTime) // Only show completed entries
                .sort((a, b) => new Date(b.startTime).getTime() - new Date(a.startTime).getTime())
                .map((entry) => (
                  <div
                    key={entry.id}
                    className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-750 transition-colors"
                  >
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-sm font-medium text-gray-900 dark:text-white">
                          {formatDuration(entry.duration)}
                        </span>
                        <span className="text-xs text-gray-500 dark:text-gray-400">
                          {formatDate(entry.startTime)}
                        </span>
                      </div>
                      <div className="text-xs text-gray-600 dark:text-gray-400">
                        {formatTime(entry.startTime)} - {entry.endTime && formatTime(entry.endTime)}
                      </div>
                      {entry.description && (
                        <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                          {entry.description}
                        </p>
                      )}
                    </div>

                    <button
                      onClick={() => handleDeleteEntry(entry.id)}
                      className="p-1 text-gray-400 hover:text-red-600 dark:hover:text-red-400 transition-colors"
                      aria-label="Delete entry"
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

        {/* Summary Statistics */}
        {timeEntries.length > 0 && (
          <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
            <div className="grid grid-cols-3 gap-4 text-center">
              <div>
                <p className="text-xs text-gray-600 dark:text-gray-400 mb-1">Total Time</p>
                <p className="text-lg font-bold text-gray-900 dark:text-white">
                  {totalHours}h
                </p>
              </div>
              <div>
                <p className="text-xs text-gray-600 dark:text-gray-400 mb-1">Sessions</p>
                <p className="text-lg font-bold text-gray-900 dark:text-white">
                  {timeEntries.filter((e) => e.endTime).length}
                </p>
              </div>
              <div>
                <p className="text-xs text-gray-600 dark:text-gray-400 mb-1">Avg Session</p>
                <p className="text-lg font-bold text-gray-900 dark:text-white">
                  {timeEntries.filter((e) => e.endTime).length > 0
                    ? (
                        totalTime /
                        3600 /
                        timeEntries.filter((e) => e.endTime).length
                      ).toFixed(1)
                    : '0'}
                  h
                </p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
