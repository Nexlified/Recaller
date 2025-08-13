'use client';

import React, { useState, useEffect } from 'react';
import { Header } from '@/components/layout/Header';
import authService from '@/services/auth';
import tasksService from '@/services/tasks';
import { Task, TaskCategory } from '@/types/Task';
import type { User } from '@/services/auth';

// Dashboard Components (will be created next)
const TaskSummaryCards = ({ tasks }: { tasks: Task[] }) => {
  const totalTasks = tasks.length;
  const pendingTasks = tasks.filter(t => t.status === 'pending').length;
  const completedToday = tasks.filter(t => {
    if (t.status !== 'completed') return false;
    const today = new Date().toDateString();
    return new Date(t.created_at).toDateString() === today;
  }).length;
  const overdueTasks = tasks.filter(t => 
    t.due_date && new Date(t.due_date) < new Date() && t.status !== 'completed'
  ).length;

  return (
    <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
      <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
        <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">Total Tasks</h3>
        <p className="text-2xl font-bold text-gray-900 dark:text-white">{totalTasks}</p>
      </div>
      <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
        <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">Pending</h3>
        <p className="text-2xl font-bold text-gray-900 dark:text-white">{pendingTasks}</p>
      </div>
      <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
        <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">Completed Today</h3>
        <p className="text-2xl font-bold text-green-600 dark:text-green-400">{completedToday}</p>
      </div>
      <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
        <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">Overdue</h3>
        <p className="text-2xl font-bold text-red-600 dark:text-red-400">{overdueTasks}</p>
      </div>
    </div>
  );
};

const UpcomingTasksList = ({ tasks }: { tasks: Task[] }) => {
  const upcomingTasks = tasks
    .filter(t => t.due_date && t.status !== 'completed')
    .sort((a, b) => new Date(a.due_date!).getTime() - new Date(b.due_date!).getTime())
    .slice(0, 5);

  return (
    <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
      <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">Upcoming Tasks</h3>
      {upcomingTasks.length === 0 ? (
        <p className="text-gray-500 dark:text-gray-400">No upcoming tasks</p>
      ) : (
        <div className="space-y-3">
          {upcomingTasks.map(task => (
            <div key={task.id} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded">
              <div>
                <p className="font-medium text-gray-900 dark:text-white">{task.title}</p>
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  Due: {new Date(task.due_date!).toLocaleDateString()}
                </p>
              </div>
              <div className={`px-2 py-1 rounded text-xs font-medium ${
                task.priority === 'high' ? 'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400' :
                task.priority === 'medium' ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-400' :
                'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400'
              }`}>
                {task.priority}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

const OverdueTasksAlert = ({ tasks }: { tasks: Task[] }) => {
  const overdueTasks = tasks.filter(t => 
    t.due_date && new Date(t.due_date) < new Date() && t.status !== 'completed'
  );

  if (overdueTasks.length === 0) return null;

  return (
    <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 p-4 rounded-lg">
      <div className="flex items-center">
        <svg className="w-5 h-5 text-red-400 mr-2" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
        </svg>
        <h3 className="text-sm font-medium text-red-800 dark:text-red-200">
          You have {overdueTasks.length} overdue task{overdueTasks.length > 1 ? 's' : ''}
        </h3>
      </div>
    </div>
  );
};

const QuickTaskCreate = ({ onTaskCreate }: { onTaskCreate: (title: string) => void }) => {
  const [title, setTitle] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (title.trim()) {
      onTaskCreate(title.trim());
      setTitle('');
    }
  };

  return (
    <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
      <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">Quick Add Task</h3>
      <form onSubmit={handleSubmit} className="space-y-3">
        <input
          type="text"
          placeholder="What needs to be done?"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:text-white"
        />
        <button
          type="submit"
          disabled={!title.trim()}
          className="w-full px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Add Task
        </button>
      </form>
    </div>
  );
};

const TaskAnalyticsWidget = ({ tasks, categories }: { tasks: Task[]; categories: TaskCategory[] }) => {
  const completionRate = tasks.length > 0 ? 
    (tasks.filter(t => t.status === 'completed').length / tasks.length * 100).toFixed(1) : '0';

  return (
    <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
      <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">Analytics</h3>
      <div className="space-y-4">
        <div>
          <div className="flex justify-between text-sm">
            <span className="text-gray-600 dark:text-gray-400">Completion Rate</span>
            <span className="font-medium text-gray-900 dark:text-white">{completionRate}%</span>
          </div>
          <div className="mt-1 bg-gray-200 dark:bg-gray-700 rounded-full h-2">
            <div 
              className="bg-green-500 h-2 rounded-full" 
              style={{ width: `${completionRate}%` }}
            ></div>
          </div>
        </div>
        <div className="text-sm text-gray-600 dark:text-gray-400">
          <p>Categories: {categories.length}</p>
          <p>Active Tasks: {tasks.filter(t => t.status !== 'completed').length}</p>
        </div>
      </div>
    </div>
  );
};

export default function TaskDashboard() {
  const [user, setUser] = useState<User | null>(null);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [categories, setCategories] = useState<TaskCategory[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const currentUser = authService.getCurrentUser();
    if (!currentUser) {
      window.location.href = '/login';
      return;
    }
    setUser(currentUser);
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Load recent tasks and categories
      const [tasksData, categoriesData] = await Promise.all([
        tasksService.getTasks(0, 50), // Get recent 50 tasks
        tasksService.getCategories()
      ]);
      
      setTasks(tasksData);
      setCategories(categoriesData);
    } catch (err) {
      console.error('Error loading dashboard data:', err);
      setError('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    await authService.logout();
    setUser(null);
    window.location.href = '/login';
  };

  const handleQuickTaskCreate = async (title: string) => {
    try {
      const newTask = await tasksService.createTask({
        title,
        description: '',
        status: 'pending',
        priority: 'medium'
      });
      setTasks(prev => [newTask, ...prev]);
    } catch (err) {
      console.error('Error creating quick task:', err);
      setError('Failed to create task');
    }
  };

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
        <div className="text-lg text-gray-600 dark:text-gray-400">Redirecting to login...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <Header user={user} title="Task Dashboard" onLogout={handleLogout} />

      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          {/* Page Header */}
          <div className="mb-6">
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Task Dashboard</h1>
            <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
              Overview of your tasks and productivity
            </p>
          </div>

          {error && (
            <div className="mb-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-md">
              <p className="text-red-800 dark:text-red-200">{error}</p>
            </div>
          )}

          {loading ? (
            <div className="space-y-6">
              <div className="animate-pulse">
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                  {[...Array(4)].map((_, i) => (
                    <div key={i} className="h-24 bg-gray-200 dark:bg-gray-700 rounded-lg"></div>
                  ))}
                </div>
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  <div className="h-64 bg-gray-200 dark:bg-gray-700 rounded-lg"></div>
                  <div className="h-64 bg-gray-200 dark:bg-gray-700 rounded-lg"></div>
                </div>
              </div>
            </div>
          ) : (
            <div className="space-y-6">
              {/* Task Summary Cards */}
              <TaskSummaryCards tasks={tasks} />

              {/* Main Dashboard Content */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Left Column */}
                <div className="space-y-6">
                  <UpcomingTasksList tasks={tasks} />
                  <OverdueTasksAlert tasks={tasks} />
                </div>

                {/* Right Column */}
                <div className="space-y-6">
                  <QuickTaskCreate onTaskCreate={handleQuickTaskCreate} />
                  <TaskAnalyticsWidget tasks={tasks} categories={categories} />
                </div>
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}