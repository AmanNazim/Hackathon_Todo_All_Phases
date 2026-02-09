'use client';

import React, { useState } from 'react';
import Button from '../ui/Button';

type RecurrenceFrequency = 'daily' | 'weekly' | 'monthly' | 'yearly';
type DayOfWeek = 'monday' | 'tuesday' | 'wednesday' | 'thursday' | 'friday' | 'saturday' | 'sunday';

interface RecurrencePattern {
  frequency: RecurrenceFrequency;
  interval: number; // e.g., every 2 weeks
  daysOfWeek?: DayOfWeek[]; // for weekly recurrence
  dayOfMonth?: number; // for monthly recurrence (1-31)
  monthOfYear?: number; // for yearly recurrence (1-12)
  endDate?: string;
  occurrences?: number; // number of times to repeat
}

interface RecurringTaskFormProps {
  onSubmit: (pattern: RecurrencePattern) => void;
  onCancel: () => void;
  initialPattern?: RecurrencePattern;
  className?: string;
}

export default function RecurringTaskForm({
  onSubmit,
  onCancel,
  initialPattern,
  className = '',
}: RecurringTaskFormProps) {
  const [frequency, setFrequency] = useState<RecurrenceFrequency>(
    initialPattern?.frequency || 'daily'
  );
  const [interval, setInterval] = useState(initialPattern?.interval || 1);
  const [daysOfWeek, setDaysOfWeek] = useState<DayOfWeek[]>(
    initialPattern?.daysOfWeek || []
  );
  const [dayOfMonth, setDayOfMonth] = useState(initialPattern?.dayOfMonth || 1);
  const [monthOfYear, setMonthOfYear] = useState(initialPattern?.monthOfYear || 1);
  const [endType, setEndType] = useState<'never' | 'date' | 'occurrences'>(
    initialPattern?.endDate ? 'date' : initialPattern?.occurrences ? 'occurrences' : 'never'
  );
  const [endDate, setEndDate] = useState(initialPattern?.endDate || '');
  const [occurrences, setOccurrences] = useState(initialPattern?.occurrences || 10);

  const daysOfWeekOptions: { value: DayOfWeek; label: string }[] = [
    { value: 'monday', label: 'Mon' },
    { value: 'tuesday', label: 'Tue' },
    { value: 'wednesday', label: 'Wed' },
    { value: 'thursday', label: 'Thu' },
    { value: 'friday', label: 'Fri' },
    { value: 'saturday', label: 'Sat' },
    { value: 'sunday', label: 'Sun' },
  ];

  const toggleDayOfWeek = (day: DayOfWeek) => {
    setDaysOfWeek((prev) =>
      prev.includes(day) ? prev.filter((d) => d !== day) : [...prev, day]
    );
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    const pattern: RecurrencePattern = {
      frequency,
      interval,
    };

    if (frequency === 'weekly') {
      if (daysOfWeek.length === 0) {
        alert('Please select at least one day of the week');
        return;
      }
      pattern.daysOfWeek = daysOfWeek;
    }

    if (frequency === 'monthly') {
      pattern.dayOfMonth = dayOfMonth;
    }

    if (frequency === 'yearly') {
      pattern.dayOfMonth = dayOfMonth;
      pattern.monthOfYear = monthOfYear;
    }

    if (endType === 'date') {
      if (!endDate) {
        alert('Please select an end date');
        return;
      }
      pattern.endDate = endDate;
    } else if (endType === 'occurrences') {
      pattern.occurrences = occurrences;
    }

    onSubmit(pattern);
  };

  const getRecurrenceSummary = (): string => {
    let summary = `Repeats every ${interval > 1 ? interval : ''} ${frequency}`;

    if (frequency === 'weekly' && daysOfWeek.length > 0) {
      summary += ` on ${daysOfWeek.map((d) => d.slice(0, 3)).join(', ')}`;
    }

    if (frequency === 'monthly') {
      summary += ` on day ${dayOfMonth}`;
    }

    if (frequency === 'yearly') {
      const monthNames = [
        'January',
        'February',
        'March',
        'April',
        'May',
        'June',
        'July',
        'August',
        'September',
        'October',
        'November',
        'December',
      ];
      summary += ` on ${monthNames[monthOfYear - 1]} ${dayOfMonth}`;
    }

    if (endType === 'date' && endDate) {
      summary += `, until ${new Date(endDate).toLocaleDateString()}`;
    } else if (endType === 'occurrences') {
      summary += `, ${occurrences} times`;
    }

    return summary;
  };

  return (
    <form onSubmit={handleSubmit} className={`space-y-6 ${className}`}>
      {/* Frequency Selection */}
      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Repeat Frequency
        </label>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
          {(['daily', 'weekly', 'monthly', 'yearly'] as RecurrenceFrequency[]).map((freq) => (
            <button
              key={freq}
              type="button"
              onClick={() => setFrequency(freq)}
              className={`
                px-4 py-2 rounded-lg border-2 transition-all
                ${
                  frequency === freq
                    ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300'
                    : 'border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:border-gray-400 dark:hover:border-gray-500'
                }
              `}
            >
              {freq.charAt(0).toUpperCase() + freq.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {/* Interval */}
      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Repeat Every
        </label>
        <div className="flex items-center gap-2">
          <input
            type="number"
            min="1"
            max="365"
            value={interval}
            onChange={(e) => setInterval(parseInt(e.target.value) || 1)}
            className="w-20 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
          />
          <span className="text-sm text-gray-700 dark:text-gray-300">
            {frequency}
            {interval > 1 ? 's' : ''}
          </span>
        </div>
      </div>

      {/* Weekly: Days of Week */}
      {frequency === 'weekly' && (
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Repeat On
          </label>
          <div className="flex flex-wrap gap-2">
            {daysOfWeekOptions.map((day) => (
              <button
                key={day.value}
                type="button"
                onClick={() => toggleDayOfWeek(day.value)}
                className={`
                  w-12 h-12 rounded-full border-2 transition-all
                  ${
                    daysOfWeek.includes(day.value)
                      ? 'border-blue-500 bg-blue-500 text-white'
                      : 'border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:border-gray-400 dark:hover:border-gray-500'
                  }
                `}
              >
                {day.label}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Monthly: Day of Month */}
      {frequency === 'monthly' && (
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Day of Month
          </label>
          <input
            type="number"
            min="1"
            max="31"
            value={dayOfMonth}
            onChange={(e) => setDayOfMonth(parseInt(e.target.value) || 1)}
            className="w-24 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
          />
        </div>
      )}

      {/* Yearly: Month and Day */}
      {frequency === 'yearly' && (
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Month
            </label>
            <select
              value={monthOfYear}
              onChange={(e) => setMonthOfYear(parseInt(e.target.value))}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
            >
              {[
                'January',
                'February',
                'March',
                'April',
                'May',
                'June',
                'July',
                'August',
                'September',
                'October',
                'November',
                'December',
              ].map((month, index) => (
                <option key={month} value={index + 1}>
                  {month}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Day
            </label>
            <input
              type="number"
              min="1"
              max="31"
              value={dayOfMonth}
              onChange={(e) => setDayOfMonth(parseInt(e.target.value) || 1)}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
            />
          </div>
        </div>
      )}

      {/* End Condition */}
      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Ends
        </label>
        <div className="space-y-3">
          <label className="flex items-center gap-2">
            <input
              type="radio"
              checked={endType === 'never'}
              onChange={() => setEndType('never')}
              className="w-4 h-4 text-blue-600"
            />
            <span className="text-sm text-gray-700 dark:text-gray-300">Never</span>
          </label>

          <label className="flex items-center gap-2">
            <input
              type="radio"
              checked={endType === 'date'}
              onChange={() => setEndType('date')}
              className="w-4 h-4 text-blue-600"
            />
            <span className="text-sm text-gray-700 dark:text-gray-300">On date</span>
            {endType === 'date' && (
              <input
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                className="ml-2 px-3 py-1 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
              />
            )}
          </label>

          <label className="flex items-center gap-2">
            <input
              type="radio"
              checked={endType === 'occurrences'}
              onChange={() => setEndType('occurrences')}
              className="w-4 h-4 text-blue-600"
            />
            <span className="text-sm text-gray-700 dark:text-gray-300">After</span>
            {endType === 'occurrences' && (
              <>
                <input
                  type="number"
                  min="1"
                  max="999"
                  value={occurrences}
                  onChange={(e) => setOccurrences(parseInt(e.target.value) || 1)}
                  className="ml-2 w-20 px-3 py-1 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                />
                <span className="text-sm text-gray-700 dark:text-gray-300">occurrences</span>
              </>
            )}
          </label>
        </div>
      </div>

      {/* Summary */}
      <div className="p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
        <h4 className="text-sm font-medium text-blue-900 dark:text-blue-200 mb-1">
          Recurrence Summary
        </h4>
        <p className="text-sm text-blue-800 dark:text-blue-300">{getRecurrenceSummary()}</p>
      </div>

      {/* Actions */}
      <div className="flex justify-end gap-3">
        <Button type="button" onClick={onCancel} variant="secondary">
          Cancel
        </Button>
        <Button type="submit">Save Recurrence</Button>
      </div>
    </form>
  );
}
