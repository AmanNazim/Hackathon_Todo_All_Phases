/**
 * Header Component
 *
 * Page header with title, description, and action buttons
 */

import React from 'react';

export interface HeaderProps {
  title: string;
  description?: string;
  actions?: React.ReactNode;
  className?: string;
}

const Header: React.FC<HeaderProps> = ({
  title,
  description,
  actions,
  className = '',
}) => {
  return (
    <header
      className={`
        bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-800
        px-4 sm:px-6 lg:px-8 py-6
        ${className}
      `}
    >
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between space-y-4 sm:space-y-0">
        <div className="flex-1 min-w-0">
          <h1 className="text-2xl sm:text-3xl font-bold text-gray-900 dark:text-white">
            {title}
          </h1>
          {description && (
            <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
              {description}
            </p>
          )}
        </div>
        {actions && (
          <div className="flex-shrink-0 flex items-center space-x-3">
            {actions}
          </div>
        )}
      </div>
    </header>
  );
};

export default Header;
