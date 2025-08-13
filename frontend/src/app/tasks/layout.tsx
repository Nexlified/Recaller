'use client';

import React, { useState, useEffect } from 'react';
import { TaskSidebar } from '@/components/tasks/TaskSidebar';
import tasksService from '@/services/tasks';

interface TasksLayoutProps {
  children: React.ReactNode;
}

export default function TasksLayout({ children }: TasksLayoutProps) {
  const [taskCounts, setTaskCounts] = useState({
    total: 0,
    pending: 0,
    inProgress: 0,
    completed: 0,
    overdue: 0,
    recurring: 0,
  });
  const [categoryCounts, setCategoryCounts] = useState<Array<{
    id: number;
    name: string;
    count: number;
    color?: string;
  }>>([]);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  useEffect(() => {
    loadTaskStatistics();
  }, []);

  const loadTaskStatistics = async () => {
    try {
      const [tasks, categories] = await Promise.all([
        tasksService.getTasks(0, 1000), // Get all tasks for statistics
        tasksService.getCategories()
      ]);

      // Calculate task counts
      const now = new Date();
      const counts = {
        total: tasks.length,
        pending: tasks.filter(t => t.status === 'pending').length,
        inProgress: tasks.filter(t => t.status === 'in_progress').length,
        completed: tasks.filter(t => t.status === 'completed').length,
        overdue: tasks.filter(t => 
          t.due_date && new Date(t.due_date) < now && t.status !== 'completed'
        ).length,
        recurring: tasks.filter(t => t.is_recurring).length,
      };

      // Calculate category counts
      const categoryCountsMap = new Map<number, number>();
      tasks.forEach(task => {
        task.categories?.forEach(category => {
          const current = categoryCountsMap.get(category.id) || 0;
          categoryCountsMap.set(category.id, current + 1);
        });
      });

      const categoriesWithCounts = categories
        .map(category => ({
          id: category.id,
          name: category.name,
          count: categoryCountsMap.get(category.id) || 0,
          color: category.color,
        }))
        .filter(category => category.count > 0)
        .sort((a, b) => b.count - a.count);

      setTaskCounts(counts);
      setCategoryCounts(categoriesWithCounts);
    } catch (error) {
      console.error('Error loading task statistics:', error);
    }
  };

  return (
    <div className="flex h-screen bg-gray-50 dark:bg-gray-900">
      {/* Mobile sidebar backdrop */}
      {isSidebarOpen && (
        <div 
          className="fixed inset-0 z-40 bg-black bg-opacity-50 lg:hidden"
          onClick={() => setIsSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <div className={`
        fixed inset-y-0 left-0 z-50 w-64 transition-transform duration-300 ease-in-out lg:static lg:translate-x-0
        ${isSidebarOpen ? 'translate-x-0' : '-translate-x-full'}
      `}>
        <TaskSidebar 
          taskCounts={taskCounts}
          categoryCounts={categoryCounts}
          className="h-full"
        />
      </div>

      {/* Main content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Mobile header */}
        <div className="lg:hidden bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-4 py-3">
          <button
            onClick={() => setIsSidebarOpen(true)}
            className="text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
        </div>

        {/* Main content area */}
        <main className="flex-1 overflow-auto">
          {children}
        </main>
      </div>
    </div>
  );
}