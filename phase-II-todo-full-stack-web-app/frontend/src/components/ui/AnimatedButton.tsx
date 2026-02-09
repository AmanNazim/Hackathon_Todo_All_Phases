/**
 * AnimatedButton Component
 *
 * Enhanced button with microinteractions and animations
 * Includes press effects, hover states, and loading animations
 */

'use client';

import React, { useState } from 'react';
import { useReducedMotion } from '@/hooks/useReducedMotion';
import { ANIMATION_TIMING } from '@/utils/animations';

interface AnimatedButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'ghost' | 'outline' | 'destructive';
  size?: 'sm' | 'md' | 'lg';
  isLoading?: boolean;
  children: React.ReactNode;
  icon?: React.ReactNode;
  iconPosition?: 'left' | 'right';
}

const AnimatedButton: React.FC<AnimatedButtonProps> = ({
  variant = 'primary',
  size = 'md',
  isLoading = false,
  children,
  icon,
  iconPosition = 'left',
  disabled,
  className = '',
  onClick,
  ...props
}) => {
  const [isPressed, setIsPressed] = useState(false);
  const [ripples, setRipples] = useState<Array<{ x: number; y: number; id: number }>>([]);
  const prefersReducedMotion = useReducedMotion();

  const baseClasses = 'relative inline-flex items-center justify-center rounded-lg font-medium transition-all duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none overflow-hidden';

  const variantClasses = {
    primary: 'bg-bubblegum-pink-600 text-white hover:bg-bubblegum-pink-700 focus-visible:ring-bubblegum-pink-500 active:bg-bubblegum-pink-800 shadow-md hover:shadow-lg',
    secondary: 'bg-lavender-blush-100 text-lavender-blush-900 hover:bg-lavender-blush-200 focus-visible:ring-lavender-blush-500 active:bg-lavender-blush-300 dark:bg-lavender-blush-900 dark:text-lavender-blush-100 dark:hover:bg-lavender-blush-800',
    ghost: 'hover:bg-gray-100 text-gray-700 focus-visible:ring-gray-500 active:bg-gray-200 dark:hover:bg-gray-800 dark:text-gray-300 dark:active:bg-gray-700',
    outline: 'border-2 border-gray-300 bg-transparent hover:bg-gray-50 text-gray-700 focus-visible:ring-gray-500 active:bg-gray-100 dark:border-gray-600 dark:hover:bg-gray-800 dark:text-gray-300 dark:active:bg-gray-700',
    destructive: 'bg-cinnabar-600 text-white hover:bg-cinnabar-700 focus-visible:ring-cinnabar-500 active:bg-cinnabar-800 shadow-md hover:shadow-lg',
  };

  const sizeClasses = {
    sm: 'h-9 px-3 text-xs gap-1.5',
    md: 'h-11 px-5 py-2.5 text-sm gap-2',
    lg: 'h-13 px-7 text-base gap-2.5',
  };

  const pressedScale = !prefersReducedMotion && isPressed ? 'scale-95' : 'scale-100';
  const classes = `${baseClasses} ${variantClasses[variant]} ${sizeClasses[size]} ${pressedScale} ${className}`;

  const handleMouseDown = (e: React.MouseEvent<HTMLButtonElement>) => {
    setIsPressed(true);

    // Create ripple effect
    if (!prefersReducedMotion) {
      const button = e.currentTarget;
      const rect = button.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      const id = Date.now();

      setRipples(prev => [...prev, { x, y, id }]);

      // Remove ripple after animation
      setTimeout(() => {
        setRipples(prev => prev.filter(ripple => ripple.id !== id));
      }, 600);
    }
  };

  const handleMouseUp = () => {
    setIsPressed(false);
  };

  const handleClick = (e: React.MouseEvent<HTMLButtonElement>) => {
    if (!disabled && !isLoading && onClick) {
      onClick(e);
    }
  };

  return (
    <button
      className={classes}
      disabled={disabled || isLoading}
      onMouseDown={handleMouseDown}
      onMouseUp={handleMouseUp}
      onMouseLeave={handleMouseUp}
      onClick={handleClick}
      {...props}
    >
      {/* Ripple effects */}
      {!prefersReducedMotion && ripples.map(ripple => (
        <span
          key={ripple.id}
          className="absolute rounded-full bg-white/30 animate-ping"
          style={{
            left: ripple.x,
            top: ripple.y,
            width: 20,
            height: 20,
            transform: 'translate(-50%, -50%)',
            animationDuration: '600ms',
          }}
        />
      ))}

      {/* Loading spinner */}
      {isLoading && (
        <svg
          className={`animate-spin h-4 w-4 text-current ${icon || children ? 'mr-2' : ''}`}
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
        >
          <circle
            className="opacity-25"
            cx="12"
            cy="12"
            r="10"
            stroke="currentColor"
            strokeWidth="4"
          />
          <path
            className="opacity-75"
            fill="currentColor"
            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
          />
        </svg>
      )}

      {/* Icon (left) */}
      {!isLoading && icon && iconPosition === 'left' && (
        <span className="flex-shrink-0">{icon}</span>
      )}

      {/* Content */}
      {!isLoading && <span className="flex-1">{children}</span>}

      {/* Icon (right) */}
      {!isLoading && icon && iconPosition === 'right' && (
        <span className="flex-shrink-0">{icon}</span>
      )}
    </button>
  );
};

export default AnimatedButton;
