'use client';

import React, { useState, useRef, DragEvent } from 'react';

interface DraggableTask {
  id: string;
  title: string;
  description?: string;
  status: 'pending' | 'in_progress' | 'completed';
  priority: 'low' | 'medium' | 'high' | 'urgent';
  order?: number;
}

interface DragDropTaskListProps {
  tasks: DraggableTask[];
  onReorder: (reorderedTasks: DraggableTask[]) => void;
  onTaskClick?: (task: DraggableTask) => void;
  className?: string;
}

export default function DragDropTaskList({
  tasks,
  onReorder,
  onTaskClick,
  className = '',
}: DragDropTaskListProps) {
  const [draggedIndex, setDraggedIndex] = useState<number | null>(null);
  const [dragOverIndex, setDragOverIndex] = useState<number | null>(null);
  const dragCounter = useRef(0);

  const handleDragStart = (e: DragEvent<HTMLDivElement>, index: number) => {
    setDraggedIndex(index);
    e.dataTransfer.effectAllowed = 'move';
    e.dataTransfer.setData('text/html', e.currentTarget.innerHTML);

    // Add a slight opacity to the dragged element
    if (e.currentTarget instanceof HTMLElement) {
      e.currentTarget.style.opacity = '0.5';
    }
  };

  const handleDragEnd = (e: DragEvent<HTMLDivElement>) => {
    if (e.currentTarget instanceof HTMLElement) {
      e.currentTarget.style.opacity = '1';
    }
    setDraggedIndex(null);
    setDragOverIndex(null);
    dragCounter.current = 0;
  };

  const handleDragOver = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
  };

  const handleDragEnter = (e: DragEvent<HTMLDivElement>, index: number) => {
    dragCounter.current++;
    if (draggedIndex !== null && draggedIndex !== index) {
      setDragOverIndex(index);
    }
  };

  const handleDragLeave = () => {
    dragCounter.current--;
    if (dragCounter.current === 0) {
      setDragOverIndex(null);
    }
  };

  const handleDrop = (e: DragEvent<HTMLDivElement>, dropIndex: number) => {
    e.preventDefault();
    e.stopPropagation();

    if (draggedIndex === null || draggedIndex === dropIndex) {
      setDragOverIndex(null);
      return;
    }

    const reorderedTasks = [...tasks];
    const [draggedTask] = reorderedTasks.splice(draggedIndex, 1);
    reorderedTasks.splice(dropIndex, 0, draggedTask);

    // Update order property
    const tasksWithOrder = reorderedTasks.map((task, index) => ({
      ...task,
      order: index,
    }));

    onReorder(tasksWithOrder);
    setDragOverIndex(null);
    dragCounter.current = 0;
  };

  const getPriorityColor = (priority: string): string => {
    switch (priority) {
      case 'urgent':
        return 'border-red-500';
      case 'high':
        return 'border-orange-500';
      case 'medium':
        return 'border-yellow-500';
      case 'low':
        return 'border-green-500';
      default:
        return 'border-gray-300 dark:border-gray-600';
    }
  };

  const getPriorityBadgeColor = (priority: string): string => {
    switch (priority) {
      case 'urgent':
        return 'bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-200';
      case 'high':
        return 'bg-orange-100 dark:bg-orange-900 text-orange-800 dark:text-orange-200';
      case 'medium':
        return 'bg-yellow-100 dark:bg-yellow-900 text-yellow-800 dark:text-yellow-200';
      case 'low':
        return 'bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200';
      default:
        return 'bg-gray-100 dark:bg-gray-800 text-gray-800 dark:text-gray-200';
    }
  };

  if (tasks.length === 0) {
    return (
      <div className={`text-center py-12 ${className}`}>
        <p className="text-gray-500 dark:text-gray-400">No tasks to display</p>
      </div>
    );
  }

  return (
    <div className={`space-y-2 ${className}`}>
      <div className="flex items-center gap-2 mb-4 text-sm text-gray-600 dark:text-gray-400">
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M7 16V4m0 0L3 8m4-4l4 4m6 0v12m0 0l4-4m-4 4l-4-4"
          />
        </svg>
        <span>Drag and drop to reorder tasks</span>
      </div>

      {tasks.map((task, index) => {
        const isDragging = draggedIndex === index;
        const isDragOver = dragOverIndex === index;
        const isCompleted = task.status === 'completed';

        return (
          <div
            key={task.id}
            draggable
            onDragStart={(e) => handleDragStart(e, index)}
            onDragEnd={handleDragEnd}
            onDragOver={handleDragOver}
            onDragEnter={(e) => handleDragEnter(e, index)}
            onDragLeave={handleDragLeave}
            onDrop={(e) => handleDrop(e, index)}
            onClick={() => onTaskClick?.(task)}
            className={`
              relative p-4 bg-white dark:bg-gray-800 rounded-lg border-l-4
              cursor-move transition-all duration-200
              ${getPriorityColor(task.priority)}
              ${isDragging ? 'opacity-50 scale-95' : 'opacity-100 scale-100'}
              ${isDragOver ? 'border-t-4 border-t-blue-500' : ''}
              ${isCompleted ? 'opacity-60' : ''}
              hover:shadow-md
            `}
          >
            {/* Drag Handle */}
            <div className="absolute left-2 top-1/2 transform -translate-y-1/2">
              <svg
                className="w-5 h-5 text-gray-400 dark:text-gray-500"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M4 8h16M4 16h16"
                />
              </svg>
            </div>

            {/* Task Content */}
            <div className="ml-6">
              <div className="flex items-start justify-between gap-2 mb-1">
                <h3
                  className={`font-medium text-gray-900 dark:text-white ${
                    isCompleted ? 'line-through' : ''
                  }`}
                >
                  {task.title}
                </h3>
                <span
                  className={`px-2 py-0.5 text-xs font-medium rounded-full whitespace-nowrap ${getPriorityBadgeColor(
                    task.priority
                  )}`}
                >
                  {task.priority}
                </span>
              </div>

              {task.description && (
                <p className="text-sm text-gray-600 dark:text-gray-400 line-clamp-2">
                  {task.description}
                </p>
              )}

              <div className="mt-2 flex items-center gap-2">
                <span
                  className={`px-2 py-0.5 text-xs rounded ${
                    task.status === 'completed'
                      ? 'bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200'
                      : task.status === 'in_progress'
                      ? 'bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200'
                      : 'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200'
                  }`}
                >
                  {task.status.replace('_', ' ')}
                </span>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}

// Kanban-style drag and drop between columns
interface KanbanColumn {
  id: string;
  title: string;
  status: 'pending' | 'in_progress' | 'completed';
  tasks: DraggableTask[];
}

interface KanbanBoardProps {
  columns: KanbanColumn[];
  onTaskMove: (taskId: string, fromStatus: string, toStatus: string, newIndex: number) => void;
  onTaskClick?: (task: DraggableTask) => void;
  className?: string;
}

export function KanbanBoard({
  columns,
  onTaskMove,
  onTaskClick,
  className = '',
}: KanbanBoardProps) {
  const [draggedTask, setDraggedTask] = useState<{
    task: DraggableTask;
    fromColumn: string;
  } | null>(null);
  const [dragOverColumn, setDragOverColumn] = useState<string | null>(null);

  const handleDragStart = (task: DraggableTask, columnId: string) => {
    setDraggedTask({ task, fromColumn: columnId });
  };

  const handleDragEnd = () => {
    setDraggedTask(null);
    setDragOverColumn(null);
  };

  const handleDragOver = (e: DragEvent<HTMLDivElement>, columnId: string) => {
    e.preventDefault();
    setDragOverColumn(columnId);
  };

  const handleDrop = (e: DragEvent<HTMLDivElement>, toColumnId: string) => {
    e.preventDefault();

    if (!draggedTask) return;

    const toColumn = columns.find((col) => col.id === toColumnId);
    if (!toColumn) return;

    onTaskMove(
      draggedTask.task.id,
      draggedTask.fromColumn,
      toColumn.status,
      toColumn.tasks.length
    );

    setDraggedTask(null);
    setDragOverColumn(null);
  };

  return (
    <div className={`grid grid-cols-1 md:grid-cols-3 gap-4 ${className}`}>
      {columns.map((column) => (
        <div
          key={column.id}
          onDragOver={(e) => handleDragOver(e, column.id)}
          onDrop={(e) => handleDrop(e, column.id)}
          className={`
            bg-gray-50 dark:bg-gray-900 rounded-lg p-4
            ${dragOverColumn === column.id ? 'ring-2 ring-blue-500' : ''}
          `}
        >
          <h3 className="font-semibold text-gray-900 dark:text-white mb-4 flex items-center justify-between">
            {column.title}
            <span className="text-sm font-normal text-gray-500 dark:text-gray-400">
              {column.tasks.length}
            </span>
          </h3>

          <div className="space-y-2">
            {column.tasks.map((task) => (
              <div
                key={task.id}
                draggable
                onDragStart={() => handleDragStart(task, column.id)}
                onDragEnd={handleDragEnd}
                onClick={() => onTaskClick?.(task)}
                className="p-3 bg-white dark:bg-gray-800 rounded-lg shadow-sm cursor-move hover:shadow-md transition-shadow"
              >
                <h4 className="font-medium text-gray-900 dark:text-white text-sm mb-1">
                  {task.title}
                </h4>
                {task.description && (
                  <p className="text-xs text-gray-600 dark:text-gray-400 line-clamp-2">
                    {task.description}
                  </p>
                )}
              </div>
            ))}

            {column.tasks.length === 0 && (
              <p className="text-sm text-gray-400 dark:text-gray-500 text-center py-8">
                Drop tasks here
              </p>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}
