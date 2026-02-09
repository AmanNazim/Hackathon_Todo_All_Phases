/**
 * ProgressBar Component
 *
 * Accessible progress indicator with smooth animations
 * Supports determinate and indeterminate states
 */

'use client';

import React from 'react';
import { useReducedMotion } from '@/hooks/useReducedMotion';

export interface ProgressBarProps {
  value?: number; // 0-100, undefined for indeterminate
  label?: string;
  showLabel?: boolean;
  size?: 'sm' | 'md' | 'lg';
  color?: 'primary' | 'secondary' | 'success' | 'warning' | 'error';
  className?: string;
}

const ProgressBar: React.FC<ProgressBarProps> = ({
  value,
  label,
  showLabel = false,
  size = 'md',
  color = 'primary',
  className = '',
}) => {
  const prefersReducedMotion = useReducedMotion();
  const isIndeterminate = value === undefined;
  const clampedValue = value !== undefined ? Math.min(Math.max(value, 0), 100) : 0;

  const sizeClasses = {
    sm: 'h-1',
    md: 'h-2',
    lg: 'h-3',
  };

  const colorClasses = {
    primary: 'bg-bubblegum-pink-600',
    secondary: 'bg-lavender-blush-600',
    success: 'bg-green-600',
    warning: 'bg-yellow-600',
    error: 'bg-cinnabar-600',
  };

  return (
    <div className={`w-full ${className}`}>
      {showLabel && label && (
        <div className="flex justify-between items-center mb-2">
          <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
            {label}
          </span>
          {!isIndeterminate && (
            <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
              {clampedValue}%
            </span>
          )}
        </div>
      )}
      <div
        className={`
          w-full bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden
          ${sizeClasses[size]}
        `}
        role="progressbar"
        aria-valuenow={isIndeterminate ? undefined : clampedValue}
        aria-valuemin={0}
        aria-valuemax={100}
        aria-label={label || 'Progress'}
      >
        <div
          className={`
            ${sizeClasses[size]}
            ${colorClasses[color]}
            ${!prefersReducedMotion ? 'transition-all duration-300 ease-out' : ''}
            ${isIndeterminate && !prefersReducedMotion ? 'animate-pulse' : ''}
          `}
          style={{
            width: isIndeterminate ? '100%' : `${clampedValue}%`,
          }}
        />
      </div>
    </div>
  );
};

export default ProgressBar;
