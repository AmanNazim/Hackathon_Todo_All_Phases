'use client';

import React, { lazy, Suspense, ComponentType } from 'react';

interface LazyLoadOptions {
  fallback?: React.ReactNode;
  delay?: number;
}

/**
 * Utility function to create lazy-loaded components with custom loading states
 */
export function createLazyComponent<T extends ComponentType<any>>(
  importFunc: () => Promise<{ default: T }>,
  options: LazyLoadOptions = {}
): React.FC<React.ComponentProps<T>> {
  const LazyComponent = lazy(importFunc);

  const defaultFallback = (
    <div className="flex items-center justify-center p-8">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 dark:border-blue-400" />
    </div>
  );

  return (props) => (
    <Suspense fallback={options.fallback || defaultFallback}>
      <LazyComponent {...props} />
    </Suspense>
  );
}

/**
 * Lazy-loaded task components for code splitting
 */

// Calendar View - Large component with date calculations
export const LazyCalendarView = createLazyComponent(
  () => import('../tasks/CalendarView'),
  {
    fallback: (
      <div className="bg-white dark:bg-gray-900 rounded-lg shadow p-8">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-gray-200 dark:bg-gray-700 rounded w-1/3" />
          <div className="grid grid-cols-7 gap-2">
            {Array.from({ length: 35 }).map((_, i) => (
              <div key={i} className="aspect-square bg-gray-200 dark:bg-gray-700 rounded" />
            ))}
          </div>
        </div>
      </div>
    ),
  }
);

// Summary View - Complex statistics calculations
export const LazySummaryView = createLazyComponent(
  () => import('../tasks/SummaryView'),
  {
    fallback: (
      <div className="bg-white dark:bg-gray-900 rounded-lg shadow p-8">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-gray-200 dark:bg-gray-700 rounded w-1/4" />
          <div className="grid grid-cols-4 gap-4">
            {Array.from({ length: 4 }).map((_, i) => (
              <div key={i} className="h-24 bg-gray-200 dark:bg-gray-700 rounded" />
            ))}
          </div>
        </div>
      </div>
    ),
  }
);

// Trend Analysis - Heavy data processing
export const LazyTrendAnalysis = createLazyComponent(
  () => import('../tasks/TrendAnalysis'),
  {
    fallback: (
      <div className="bg-white dark:bg-gray-900 rounded-lg shadow p-8">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-gray-200 dark:bg-gray-700 rounded w-1/3" />
          <div className="h-32 bg-gray-200 dark:bg-gray-700 rounded" />
          <div className="grid grid-cols-4 gap-4">
            {Array.from({ length: 4 }).map((_, i) => (
              <div key={i} className="h-20 bg-gray-200 dark:bg-gray-700 rounded" />
            ))}
          </div>
        </div>
      </div>
    ),
  }
);

// Goal Tracker - Complex form and visualization
export const LazyGoalTracker = createLazyComponent(
  () => import('../tasks/GoalTracker'),
  {
    fallback: (
      <div className="bg-white dark:bg-gray-900 rounded-lg shadow p-8">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-gray-200 dark:bg-gray-700 rounded w-1/4" />
          <div className="grid grid-cols-3 gap-4">
            {Array.from({ length: 3 }).map((_, i) => (
              <div key={i} className="h-40 bg-gray-200 dark:bg-gray-700 rounded" />
            ))}
          </div>
        </div>
      </div>
    ),
  }
);

// Task Template Manager - Complex form with multiple fields
export const LazyTaskTemplateManager = createLazyComponent(
  () => import('../tasks/TaskTemplateManager'),
  {
    fallback: (
      <div className="bg-white dark:bg-gray-900 rounded-lg shadow p-8">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-gray-200 dark:bg-gray-700 rounded w-1/3" />
          <div className="grid grid-cols-3 gap-4">
            {Array.from({ length: 6 }).map((_, i) => (
              <div key={i} className="h-32 bg-gray-200 dark:bg-gray-700 rounded" />
            ))}
          </div>
        </div>
      </div>
    ),
  }
);

// Import/Export - File processing
export const LazyImportExport = createLazyComponent(
  () => import('../tasks/ImportExport'),
  {
    fallback: (
      <div className="bg-white dark:bg-gray-900 rounded-lg shadow p-8">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-gray-200 dark:bg-gray-700 rounded w-1/3" />
          <div className="space-y-3">
            <div className="h-24 bg-gray-200 dark:bg-gray-700 rounded" />
            <div className="h-24 bg-gray-200 dark:bg-gray-700 rounded" />
          </div>
        </div>
      </div>
    ),
  }
);

// Drag and Drop Task List - Complex interaction
export const LazyDragDropTaskList = createLazyComponent(
  () => import('../tasks/DragDropTaskList'),
  {
    fallback: (
      <div className="space-y-2">
        {Array.from({ length: 5 }).map((_, i) => (
          <div key={i} className="animate-pulse h-24 bg-gray-200 dark:bg-gray-700 rounded" />
        ))}
      </div>
    ),
  }
);

// Rich Text Editor - Large dependency
export const LazyRichTextEditor = createLazyComponent(
  () => import('../ui/RichTextEditor'),
  {
    fallback: (
      <div className="animate-pulse">
        <div className="h-10 bg-gray-200 dark:bg-gray-700 rounded mb-2" />
        <div className="h-40 bg-gray-200 dark:bg-gray-700 rounded" />
      </div>
    ),
  }
);

/**
 * Preload function for critical components
 * Call this when you know a component will be needed soon
 */
export const preloadComponent = (componentName: string) => {
  switch (componentName) {
    case 'CalendarView':
      import('../tasks/CalendarView');
      break;
    case 'SummaryView':
      import('../tasks/SummaryView');
      break;
    case 'TrendAnalysis':
      import('../tasks/TrendAnalysis');
      break;
    case 'GoalTracker':
      import('../tasks/GoalTracker');
      break;
    case 'TaskTemplateManager':
      import('../tasks/TaskTemplateManager');
      break;
    case 'ImportExport':
      import('../tasks/ImportExport');
      break;
    case 'DragDropTaskList':
      import('../tasks/DragDropTaskList');
      break;
    case 'RichTextEditor':
      import('../ui/RichTextEditor');
      break;
  }
};

/**
 * Hook to preload components on hover or focus
 */
export const usePreloadOnInteraction = (componentName: string) => {
  const handleInteraction = () => {
    preloadComponent(componentName);
  };

  return {
    onMouseEnter: handleInteraction,
    onFocus: handleInteraction,
  };
};
