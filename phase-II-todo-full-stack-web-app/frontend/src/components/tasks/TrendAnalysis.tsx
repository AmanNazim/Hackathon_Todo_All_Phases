'use client';

import React, { useMemo, useState } from 'react';

interface Task {
  id: string;
  title: string;
  status: 'pending' | 'in_progress' | 'completed';
  priority: 'low' | 'medium' | 'high' | 'urgent';
  created_at: string;
  completed_at?: string;
  due_date?: string;
}

interface TrendAnalysisProps {
  tasks: Task[];
  className?: string;
}

type TimeRange = '7days' | '30days' | '90days' | 'all';

export default function TrendAnalysis({ tasks, className = '' }: TrendAnalysisProps) {
  const [timeRange, setTimeRange] = useState<TimeRange>('30days');

  const getDateRange = (range: TimeRange): { start: Date; end: Date } => {
    const end = new Date();
    let start = new Date();

    switch (range) {
      case '7days':
        start.setDate(end.getDate() - 7);
        break;
      case '30days':
        start.setDate(end.getDate() - 30);
        break;
      case '90days':
        start.setDate(end.getDate() - 90);
        break;
      case 'all':
        start = new Date(Math.min(...tasks.map((t) => new Date(t.created_at).getTime())));
        break;
    }

    return { start, end };
  };

  const dateRange = getDateRange(timeRange);

  const filteredTasks = useMemo(() => {
    return tasks.filter((task) => {
      const createdDate = new Date(task.created_at);
      return createdDate >= dateRange.start && createdDate <= dateRange.end;
    });
  }, [tasks, dateRange]);

  const completionTrend = useMemo(() => {
    const completedTasks = filteredTasks.filter((t) => t.status === 'completed');
    const totalTasks = filteredTasks.length;
    const completionRate = totalTasks > 0 ? (completedTasks.length / totalTasks) * 100 : 0;

    // Calculate daily completion data
    const dailyData: { [key: string]: { completed: number; created: number } } = {};

    filteredTasks.forEach((task) => {
      const createdDate = new Date(task.created_at).toISOString().split('T')[0];
      if (!dailyData[createdDate]) {
        dailyData[createdDate] = { completed: 0, created: 0 };
      }
      dailyData[createdDate].created++;

      if (task.completed_at) {
        const completedDate = new Date(task.completed_at).toISOString().split('T')[0];
        if (!dailyData[completedDate]) {
          dailyData[completedDate] = { completed: 0, created: 0 };
        }
        dailyData[completedDate].completed++;
      }
    });

    return {
      completionRate,
      totalCompleted: completedTasks.length,
      totalCreated: totalTasks,
      dailyData,
    };
  }, [filteredTasks]);

  const priorityTrend = useMemo(() => {
    const byPriority = {
      urgent: { total: 0, completed: 0 },
      high: { total: 0, completed: 0 },
      medium: { total: 0, completed: 0 },
      low: { total: 0, completed: 0 },
    };

    filteredTasks.forEach((task) => {
      byPriority[task.priority].total++;
      if (task.status === 'completed') {
        byPriority[task.priority].completed++;
      }
    });

    return byPriority;
  }, [filteredTasks]);

  const averageCompletionTime = useMemo(() => {
    const completedWithTime = filteredTasks.filter(
      (t) => t.status === 'completed' && t.completed_at
    );

    if (completedWithTime.length === 0) return 0;

    const totalTime = completedWithTime.reduce((sum, task) => {
      const created = new Date(task.created_at).getTime();
      const completed = new Date(task.completed_at!).getTime();
      return sum + (completed - created);
    }, 0);

    const avgMilliseconds = totalTime / completedWithTime.length;
    return Math.round(avgMilliseconds / (1000 * 60 * 60 * 24)); // Convert to days
  }, [filteredTasks]);

  const overdueRate = useMemo(() => {
    const tasksWithDueDate = filteredTasks.filter((t) => t.due_date && t.status !== 'completed');
    if (tasksWithDueDate.length === 0) return 0;

    const overdue = tasksWithDueDate.filter((t) => new Date(t.due_date!) < new Date());
    return Math.round((overdue.length / tasksWithDueDate.length) * 100);
  }, [filteredTasks]);

  const productivityScore = useMemo(() => {
    // Calculate a productivity score based on multiple factors
    const completionWeight = 0.4;
    const speedWeight = 0.3;
    const priorityWeight = 0.3;

    // Completion rate score (0-100)
    const completionScore = completionTrend.completionRate;

    // Speed score (inverse of average completion time, normalized)
    const speedScore = averageCompletionTime > 0 ? Math.max(0, 100 - averageCompletionTime * 2) : 50;

    // Priority score (higher priority tasks completed = higher score)
    const priorityScore =
      ((priorityTrend.urgent.completed * 4 +
        priorityTrend.high.completed * 3 +
        priorityTrend.medium.completed * 2 +
        priorityTrend.low.completed * 1) /
        Math.max(
          1,
          priorityTrend.urgent.total * 4 +
            priorityTrend.high.total * 3 +
            priorityTrend.medium.total * 2 +
            priorityTrend.low.total * 1
        )) *
      100;

    const score =
      completionScore * completionWeight +
      speedScore * speedWeight +
      priorityScore * priorityWeight;

    return Math.round(score);
  }, [completionTrend, averageCompletionTime, priorityTrend]);

  const getScoreColor = (score: number): string => {
    if (score >= 80) return 'text-green-600 dark:text-green-400';
    if (score >= 60) return 'text-blue-600 dark:text-blue-400';
    if (score >= 40) return 'text-yellow-600 dark:text-yellow-400';
    return 'text-red-600 dark:text-red-400';
  };

  const getScoreLabel = (score: number): string => {
    if (score >= 80) return 'Excellent';
    if (score >= 60) return 'Good';
    if (score >= 40) return 'Fair';
    return 'Needs Improvement';
  };

  return (
    <div className={`bg-white dark:bg-gray-900 rounded-lg shadow ${className}`}>
      <div className="p-6 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Trend Analysis</h3>
          <div className="flex bg-gray-100 dark:bg-gray-800 rounded-lg p-1">
            {(['7days', '30days', '90days', 'all'] as TimeRange[]).map((range) => (
              <button
                key={range}
                onClick={() => setTimeRange(range)}
                className={`px-3 py-1 text-sm font-medium rounded-md transition-colors ${
                  timeRange === range
                    ? 'bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow-sm'
                    : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
                }`}
              >
                {range === '7days'
                  ? '7 Days'
                  : range === '30days'
                  ? '30 Days'
                  : range === '90days'
                  ? '90 Days'
                  : 'All Time'}
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="p-6">
        {/* Productivity Score */}
        <div className="mb-6 p-6 bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20 rounded-lg">
          <div className="text-center">
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">Productivity Score</p>
            <div className={`text-5xl font-bold ${getScoreColor(productivityScore)} mb-2`}>
              {productivityScore}
            </div>
            <p className={`text-sm font-medium ${getScoreColor(productivityScore)}`}>
              {getScoreLabel(productivityScore)}
            </p>
          </div>
        </div>

        {/* Key Metrics Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4">
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Completion Rate</p>
            <p className="text-2xl font-bold text-gray-900 dark:text-white">
              {Math.round(completionTrend.completionRate)}%
            </p>
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
              {completionTrend.totalCompleted} of {completionTrend.totalCreated} tasks
            </p>
          </div>

          <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4">
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Avg. Completion Time</p>
            <p className="text-2xl font-bold text-gray-900 dark:text-white">
              {averageCompletionTime}
            </p>
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">days</p>
          </div>

          <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4">
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Overdue Rate</p>
            <p className="text-2xl font-bold text-red-600 dark:text-red-400">{overdueRate}%</p>
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">of tasks with due dates</p>
          </div>

          <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4">
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Total Tasks</p>
            <p className="text-2xl font-bold text-gray-900 dark:text-white">
              {filteredTasks.length}
            </p>
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">in selected period</p>
          </div>
        </div>

        {/* Priority Completion Breakdown */}
        <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4 mb-6">
          <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
            Completion by Priority
          </h4>
          <div className="space-y-3">
            {Object.entries(priorityTrend).map(([priority, data]) => {
              const percentage = data.total > 0 ? (data.completed / data.total) * 100 : 0;
              const priorityColors = {
                urgent: 'bg-red-500',
                high: 'bg-orange-500',
                medium: 'bg-yellow-500',
                low: 'bg-green-500',
              };

              return (
                <div key={priority}>
                  <div className="flex items-center justify-between text-sm mb-1">
                    <span className="text-gray-700 dark:text-gray-300 capitalize">{priority}</span>
                    <span className="text-gray-600 dark:text-gray-400">
                      {data.completed}/{data.total} ({Math.round(percentage)}%)
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full transition-all duration-300 ${
                        priorityColors[priority as keyof typeof priorityColors]
                      }`}
                      style={{ width: `${percentage}%` }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Insights */}
        <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
          <h4 className="text-sm font-medium text-blue-900 dark:text-blue-200 mb-2">
            Insights & Recommendations
          </h4>
          <ul className="text-sm text-blue-800 dark:text-blue-300 space-y-1">
            {completionTrend.completionRate < 50 && (
              <li>• Consider breaking down tasks into smaller, more manageable pieces</li>
            )}
            {averageCompletionTime > 7 && (
              <li>• Tasks are taking longer than a week on average - review task complexity</li>
            )}
            {overdueRate > 30 && (
              <li>• High overdue rate detected - review your task prioritization and deadlines</li>
            )}
            {priorityTrend.urgent.total > priorityTrend.low.total * 2 && (
              <li>• Too many urgent tasks - consider better planning to reduce urgency</li>
            )}
            {completionTrend.completionRate >= 80 && (
              <li>• Excellent completion rate! Keep up the great work</li>
            )}
            {averageCompletionTime <= 3 && completionTrend.completionRate >= 70 && (
              <li>• Great productivity! You're completing tasks quickly and consistently</li>
            )}
          </ul>
        </div>
      </div>
    </div>
  );
}
