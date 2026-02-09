/**
 * SkipLink Component
 *
 * Accessibility component for keyboard navigation
 * Allows users to skip to main content
 */

'use client';

import React from 'react';

export interface SkipLinkProps {
  href?: string;
  children?: React.ReactNode;
  className?: string;
}

const SkipLink: React.FC<SkipLinkProps> = ({
  href = '#main-content',
  children = 'Skip to main content',
  className = '',
}) => {
  return (
    <a
      href={href}
      className={`
        sr-only focus:not-sr-only
        fixed top-4 left-4 z-50
        bg-bubblegum-pink-600 text-white
        px-4 py-2 rounded-lg
        font-medium text-sm
        focus:outline-none focus:ring-2 focus:ring-bubblegum-pink-500 focus:ring-offset-2
        transition-all duration-200
        ${className}
      `}
    >
      {children}
    </a>
  );
};

export default SkipLink;
