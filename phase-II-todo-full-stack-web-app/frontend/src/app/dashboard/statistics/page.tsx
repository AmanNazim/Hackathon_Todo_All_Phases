'use client';

import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import Chart from '@/components/ui/Chart';
import { Task } from '@/types';
import { apiClient } from '@/lib/api';
import LoadingSpinner from '@/components/ui/LoadingSpinner';

export default function StatisticsPage() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [chartData, setChartData] = useState<any>(null);

  useEffect(() => {
    const fetchTasks = async () => {
      try {
        const response = await apiClient.getTasks();
        if (response.data) {
          setTasks(response.data);
          generateChartData(response.data);
        }
      } catch (error) {
        console.error('Error fetching tasks for statistics:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchTasks();
  }, []);

  const generateChartData = (tasks: Task[]) => {
    // Count tasks by priority
    const priorities = ['low', 'medium', 'high', 'urgent'];
    const priorityCounts = priorities.map(priority =>
      tasks.filter(task => task.priority === priority).length
    );

    // Count tasks by status
    const completedCount = tasks.filter(task => task.completed).length;
    const pendingCount = tasks.filter(task => !task.completed).length;

    // Prepare chart data
    const priorityData = {
      labels: priorities,
      datasets: [
        {
          label: 'Tasks by Priority',
          data: priorityCounts,
          backgroundColor: ['#10B981', '#3B82F6', '#F59E0B', '#EF4444'],
        }
      ]
    };

    const statusData = {
      labels: ['Completed', 'Pending'],
      datasets: [
        {
          label: 'Tasks by Status',
          data: [completedCount, pendingCount],
          backgroundColor: ['#10B981', '#3B82F6'],
        }
      ]
    };

    setChartData({ priorityData, statusData });
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-[50vh]">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Statistics</h1>
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
          Visualize your task completion and productivity metrics.
        </p>
      </div>

      {chartData ? (
        <>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Tasks by Priority</CardTitle>
              </CardHeader>
              <CardContent>
                <Chart type="pie" data={chartData.priorityData} />
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Tasks by Status</CardTitle>
              </CardHeader>
              <CardContent>
                <Chart type="pie" data={chartData.statusData} />
              </CardContent>
            </Card>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Task Completion Trend</CardTitle>
            </CardHeader>
            <CardContent>
              <Chart
                type="line"
                data={{
                  labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                  datasets: [
                    {
                      label: 'Tasks Completed',
                      data: [12, 19, 3, 5, 2, 3],
                      backgroundColor: ['#3B82F6'],
                    }
                  ]
                }}
              />
            </CardContent>
          </Card>
        </>
      ) : (
        <Card>
          <CardContent className="py-12 text-center">
            <p className="text-gray-500 dark:text-gray-400">
              No data available. Complete some tasks to see statistics.
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}