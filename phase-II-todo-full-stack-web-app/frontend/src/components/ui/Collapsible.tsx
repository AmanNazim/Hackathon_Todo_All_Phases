'use client';

import React, { useState, useRef, useEffect } from 'react';

interface CollapsibleProps {
  title: string;
  children: React.ReactNode;
  defaultOpen?: boolean;
  disabled?: boolean;
  className?: string;
  icon?: React.ReactNode;
  badge?: string | number;
  onToggle?: (isOpen: boolean) => void;
}

export default function Collapsible({
  title,
  children,
  defaultOpen = false,
  disabled = false,
  className = '',
  icon,
  badge,
  onToggle,
}: CollapsibleProps) {
  const [isOpen, setIsOpen] = useState(defaultOpen);
  const [height, setHeight] = useState<number | undefined>(defaultOpen ? undefined : 0);
  const contentRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!contentRef.current) return;

    if (isOpen) {
      const contentHeight = contentRef.current.scrollHeight;
      setHeight(contentHeight);
    } else {
      setHeight(0);
    }
  }, [isOpen, children]);

  const handleToggle = () => {
    if (disabled) return;
    const newState = !isOpen;
    setIsOpen(newState);
    if (onToggle) {
      onToggle(newState);
    }
  };

  return (
    <div className={`border border-gray-200 dark:border-gray-700 rounded-lg ${className}`}>
      <button
        type="button"
        onClick={handleToggle}
        disabled={disabled}
        className={`
          w-full flex items-center justify-between p-4 text-left
          transition-colors duration-200
          ${
            disabled
              ? 'cursor-not-allowed opacity-50'
              : 'hover:bg-gray-50 dark:hover:bg-gray-800 cursor-pointer'
          }
          focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-inset
        `}
        aria-expanded={isOpen}
        aria-controls={`collapsible-content-${title}`}
      >
        <div className="flex items-center gap-3 flex-1">
          {icon && (
            <div className="flex-shrink-0 text-gray-500 dark:text-gray-400">
              {icon}
            </div>
          )}
          <span className="font-medium text-gray-900 dark:text-white">
            {title}
          </span>
          {badge !== undefined && (
            <span className="px-2 py-0.5 text-xs font-medium bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 rounded-full">
              {badge}
            </span>
          )}
        </div>
        <svg
          className={`w-5 h-5 text-gray-500 dark:text-gray-400 transition-transform duration-200 ${
            isOpen ? 'transform rotate-180' : ''
          }`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M19 9l-7 7-7-7"
          />
        </svg>
      </button>

      <div
        ref={contentRef}
        id={`collapsible-content-${title}`}
        style={{ height }}
        className="overflow-hidden transition-all duration-300 ease-in-out"
      >
        <div className="p-4 pt-0 border-t border-gray-200 dark:border-gray-700">
          {children}
        </div>
      </div>
    </div>
  );
}

// Accordion component for managing multiple collapsibles
interface AccordionProps {
  children: React.ReactElement<CollapsibleProps>[];
  allowMultiple?: boolean;
  className?: string;
}

export function Accordion({
  children,
  allowMultiple = false,
  className = '',
}: AccordionProps) {
  const [openIndexes, setOpenIndexes] = useState<number[]>([]);

  const handleToggle = (index: number, isOpen: boolean) => {
    if (allowMultiple) {
      setOpenIndexes((prev) =>
        isOpen ? [...prev, index] : prev.filter((i) => i !== index)
      );
    } else {
      setOpenIndexes(isOpen ? [index] : []);
    }
  };

  return (
    <div className={`space-y-2 ${className}`}>
      {React.Children.map(children, (child, index) => {
        if (!React.isValidElement(child)) return null;

        return React.cloneElement(child, {
          defaultOpen: openIndexes.includes(index),
          onToggle: (isOpen: boolean) => {
            handleToggle(index, isOpen);
            if (child.props.onToggle) {
              child.props.onToggle(isOpen);
            }
          },
        });
      })}
    </div>
  );
}

// Preset collapsible sections for common use cases
interface FormSectionProps {
  title: string;
  children: React.ReactNode;
  required?: boolean;
  defaultOpen?: boolean;
  className?: string;
}

export function FormSection({
  title,
  children,
  required = false,
  defaultOpen = true,
  className = '',
}: FormSectionProps) {
  return (
    <Collapsible
      title={title}
      defaultOpen={defaultOpen}
      className={className}
      badge={required ? 'Required' : undefined}
      icon={
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
          />
        </svg>
      }
    >
      {children}
    </Collapsible>
  );
}

export function SettingsSection({
  title,
  children,
  defaultOpen = false,
  className = '',
}: Omit<FormSectionProps, 'required'>) {
  return (
    <Collapsible
      title={title}
      defaultOpen={defaultOpen}
      className={className}
      icon={
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
          />
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
          />
        </svg>
      }
    >
      {children}
    </Collapsible>
  );
}

export function InfoSection({
  title,
  children,
  defaultOpen = false,
  className = '',
}: Omit<FormSectionProps, 'required'>) {
  return (
    <Collapsible
      title={title}
      defaultOpen={defaultOpen}
      className={className}
      icon={
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        </svg>
      }
    >
      {children}
    </Collapsible>
  );
}
