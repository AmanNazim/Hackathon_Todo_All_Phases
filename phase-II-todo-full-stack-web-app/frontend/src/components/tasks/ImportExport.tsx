'use client';

import React, { useState, useRef } from 'react';
import Button from '../ui/Button';

interface Task {
  id?: string;
  title: string;
  description?: string;
  status: 'pending' | 'in_progress' | 'completed';
  priority: 'low' | 'medium' | 'high' | 'urgent';
  due_date?: string;
  tags?: string[];
  created_at?: string;
  completed_at?: string;
}

interface ImportExportProps {
  tasks?: Task[];
  onImport?: (tasks: Omit<Task, 'id'>[]) => Promise<void>;
  className?: string;
}

type ExportFormat = 'json' | 'csv';

export default function ImportExport({
  tasks = [],
  onImport,
  className = '',
}: ImportExportProps) {
  const [isImporting, setIsImporting] = useState(false);
  const [importError, setImportError] = useState<string | null>(null);
  const [importSuccess, setImportSuccess] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const exportToJSON = () => {
    const dataStr = JSON.stringify(tasks, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `tasks-export-${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  const exportToCSV = () => {
    if (tasks.length === 0) {
      alert('No tasks to export');
      return;
    }

    // CSV headers
    const headers = [
      'Title',
      'Description',
      'Status',
      'Priority',
      'Due Date',
      'Tags',
      'Created At',
      'Completed At',
    ];

    // Convert tasks to CSV rows
    const rows = tasks.map((task) => [
      `"${(task.title || '').replace(/"/g, '""')}"`,
      `"${(task.description || '').replace(/"/g, '""')}"`,
      task.status,
      task.priority,
      task.due_date || '',
      `"${(task.tags || []).join(', ')}"`,
      task.created_at || '',
      task.completed_at || '',
    ]);

    // Combine headers and rows
    const csvContent = [headers.join(','), ...rows.map((row) => row.join(','))].join('\n');

    // Create and download file
    const dataBlob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `tasks-export-${new Date().toISOString().split('T')[0]}.csv`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  const handleExport = (format: ExportFormat) => {
    if (tasks.length === 0) {
      alert('No tasks to export');
      return;
    }

    if (format === 'json') {
      exportToJSON();
    } else if (format === 'csv') {
      exportToCSV();
    }
  };

  const parseCSV = (csvText: string): Omit<Task, 'id'>[] => {
    const lines = csvText.split('\n').filter((line) => line.trim());
    if (lines.length < 2) {
      throw new Error('CSV file is empty or invalid');
    }

    // Skip header row
    const dataLines = lines.slice(1);
    const tasks: Omit<Task, 'id'>[] = [];

    for (let i = 0; i < dataLines.length; i++) {
      const line = dataLines[i];
      // Simple CSV parsing (handles quoted fields)
      const matches = line.match(/(".*?"|[^,]+)(?=\s*,|\s*$)/g);
      if (!matches || matches.length < 4) continue;

      const [title, description, status, priority, dueDate, tags] = matches.map((field) =>
        field.replace(/^"|"$/g, '').replace(/""/g, '"')
      );

      if (!title || !status || !priority) continue;

      tasks.push({
        title,
        description: description || undefined,
        status: status as Task['status'],
        priority: priority as Task['priority'],
        due_date: dueDate || undefined,
        tags: tags ? tags.split(',').map((t) => t.trim()).filter(Boolean) : undefined,
      });
    }

    return tasks;
  };

  const handleFileSelect = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file || !onImport) return;

    setIsImporting(true);
    setImportError(null);
    setImportSuccess(null);

    try {
      const text = await file.text();
      let parsedTasks: Omit<Task, 'id'>[];

      if (file.name.endsWith('.json')) {
        const data = JSON.parse(text);
        parsedTasks = Array.isArray(data) ? data : [data];
      } else if (file.name.endsWith('.csv')) {
        parsedTasks = parseCSV(text);
      } else {
        throw new Error('Unsupported file format. Please use JSON or CSV.');
      }

      // Validate tasks
      if (parsedTasks.length === 0) {
        throw new Error('No valid tasks found in file');
      }

      // Import tasks
      await onImport(parsedTasks);
      setImportSuccess(`Successfully imported ${parsedTasks.length} tasks`);

      // Clear file input
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    } catch (error) {
      setImportError(
        error instanceof Error ? error.message : 'Failed to import tasks'
      );
    } finally {
      setIsImporting(false);
    }
  };

  const handleImportClick = () => {
    fileInputRef.current?.click();
  };

  return (
    <div className={`bg-white dark:bg-gray-900 rounded-lg shadow p-6 ${className}`}>
      <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
        Import / Export Tasks
      </h3>

      {/* Export Section */}
      <div className="mb-6">
        <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
          Export Tasks
        </h4>
        <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">
          Download your tasks in JSON or CSV format for backup or transfer.
        </p>
        <div className="flex gap-3">
          <Button
            onClick={() => handleExport('json')}
            variant="secondary"
            disabled={tasks.length === 0}
          >
            <svg
              className="w-4 h-4 mr-2"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
              />
            </svg>
            Export as JSON
          </Button>
          <Button
            onClick={() => handleExport('csv')}
            variant="secondary"
            disabled={tasks.length === 0}
          >
            <svg
              className="w-4 h-4 mr-2"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
              />
            </svg>
            Export as CSV
          </Button>
        </div>
        {tasks.length === 0 && (
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">
            No tasks available to export
          </p>
        )}
      </div>

      {/* Import Section */}
      <div>
        <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
          Import Tasks
        </h4>
        <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">
          Upload a JSON or CSV file to import tasks. Existing tasks will not be affected.
        </p>
        <input
          ref={fileInputRef}
          type="file"
          accept=".json,.csv"
          onChange={handleFileSelect}
          className="hidden"
          disabled={!onImport || isImporting}
        />
        <Button
          onClick={handleImportClick}
          disabled={!onImport || isImporting}
          variant="primary"
        >
          <svg
            className="w-4 h-4 mr-2"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
            />
          </svg>
          {isImporting ? 'Importing...' : 'Import from File'}
        </Button>

        {/* Import Feedback */}
        {importError && (
          <div className="mt-3 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
            <div className="flex items-start gap-2">
              <svg
                className="w-5 h-5 text-red-600 dark:text-red-400 flex-shrink-0 mt-0.5"
                fill="currentColor"
                viewBox="0 0 20 20"
              >
                <path
                  fillRule="evenodd"
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                  clipRule="evenodd"
                />
              </svg>
              <p className="text-sm text-red-800 dark:text-red-200">{importError}</p>
            </div>
          </div>
        )}

        {importSuccess && (
          <div className="mt-3 p-3 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg">
            <div className="flex items-start gap-2">
              <svg
                className="w-5 h-5 text-green-600 dark:text-green-400 flex-shrink-0 mt-0.5"
                fill="currentColor"
                viewBox="0 0 20 20"
              >
                <path
                  fillRule="evenodd"
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                  clipRule="evenodd"
                />
              </svg>
              <p className="text-sm text-green-800 dark:text-green-200">{importSuccess}</p>
            </div>
          </div>
        )}

        {/* Format Information */}
        <div className="mt-4 p-3 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
          <h5 className="text-xs font-medium text-blue-900 dark:text-blue-200 mb-2">
            Supported Formats
          </h5>
          <ul className="text-xs text-blue-800 dark:text-blue-300 space-y-1">
            <li>• JSON: Array of task objects with standard fields</li>
            <li>• CSV: Comma-separated values with headers</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
