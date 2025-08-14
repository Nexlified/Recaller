'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { Header } from '@/components/layout/Header';
import authService from '@/services/auth';
import tasksService from '@/services/tasks';
import { Task } from '@/types/Task';
import type { User } from '@/services/auth';

// Recurring Task Stats Component
const RecurringTaskStats = ({ tasks }: { tasks: Task[] }) => {
  const activeTasks = tasks.filter(t => t.status !== 'completed').length;
  const nextDueTasks = tasks.filter(t => 
    t.due_date && new Date(t.due_date) <= new Date(Date.now() + 7 * 24 * 60 * 60 * 1000)
  ).length;
  const overdueTasks = tasks.filter(t => 
    t.due_date && new Date(t.due_date) < new Date() && t.status !== 'completed'
  ).length;

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
      <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
        <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">Active Recurring</h3>
        <p className="text-2xl font-bold text-gray-900 dark:text-white">{activeTasks}</p>
      </div>
      <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
        <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">Due This Week</h3>
        <p className="text-2xl font-bold text-blue-600 dark:text-blue-400">{nextDueTasks}</p>
      </div>
      <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
        <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">Overdue</h3>
        <p className="text-2xl font-bold text-red-600 dark:text-red-400">{overdueTasks}</p>
      </div>
    </div>
  );
};

// Recurring Pattern Display Component
const RecurringPatternCard = ({ 
  pattern, 
  tasks 
}: { 
  pattern: string;
  tasks: Task[];
}) => {
  const patternTasks = tasks.filter(t => t.recurrence?.recurrence_type === pattern);
  const activeTasks = patternTasks.filter(t => t.status !== 'completed');

  const getPatternDisplay = (pattern: string) => {
    switch (pattern) {
      case 'daily': return { name: 'Daily Tasks', icon: '🌅', color: 'bg-blue-500' };
      case 'weekly': return { name: 'Weekly Tasks', icon: '📅', color: 'bg-green-500' };
      case 'monthly': return { name: 'Monthly Tasks', icon: '🗓️', color: 'bg-purple-500' };
      case 'yearly': return { name: 'Yearly Tasks', icon: '🎯', color: 'bg-orange-500' };
      default: return { name: 'Custom Pattern', icon: '⚙️', color: 'bg-gray-500' };
    }
  };

  const display = getPatternDisplay(pattern);

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-3">
          <div className={`w-10 h-10 ${display.color} rounded-lg flex items-center justify-center`}>
            <span className="text-lg">{display.icon}</span>
          </div>
          <div>
            <h3 className="font-medium text-gray-900 dark:text-white">{display.name}</h3>
            <p className="text-sm text-gray-500 dark:text-gray-400">
              {activeTasks.length} active task{activeTasks.length !== 1 ? 's' : ''}
            </p>
          </div>
        </div>
      </div>
      
      <div className="space-y-2">
        {activeTasks.slice(0, 3).map(task => (
          <div key={task.id} className="flex items-center justify-between p-2 bg-gray-50 dark:bg-gray-700 rounded">
            <Link 
              href={`/tasks/${task.id}`}
              className="font-medium text-gray-900 dark:text-white hover:text-indigo-600 dark:hover:text-indigo-400"
            >
              {task.title}
            </Link>
            {task.due_date && (
              <span className="text-xs text-gray-500 dark:text-gray-400">
                Due: {new Date(task.due_date).toLocaleDateString()}
              </span>
            )}
          </div>
        ))}
        
        {activeTasks.length > 3 && (
          <div className="text-center pt-2">
            <Link 
              href={`/tasks/list?recurring=true&pattern=${pattern}`}
              className="text-sm text-indigo-600 dark:text-indigo-400 hover:text-indigo-700 dark:hover:text-indigo-300"
            >
              View all {activeTasks.length} tasks
            </Link>
          </div>
        )}
        
        {activeTasks.length === 0 && (
          <p className="text-sm text-gray-500 dark:text-gray-400 text-center py-4">
            No active tasks
          </p>
        )}
      </div>
    </div>
  );
};

// Upcoming Recurring Tasks Component
const UpcomingRecurringTasks = ({ tasks }: { tasks: Task[] }) => {
  const upcomingTasks = tasks
    .filter(t => t.due_date && t.status !== 'completed')
    .sort((a, b) => new Date(a.due_date!).getTime() - new Date(b.due_date!).getTime())
    .slice(0, 10);

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
      <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">Upcoming Recurring Tasks</h3>
      {upcomingTasks.length === 0 ? (
        <p className="text-gray-500 dark:text-gray-400">No upcoming recurring tasks</p>
      ) : (
        <div className="space-y-3">
          {upcomingTasks.map(task => (
            <div key={task.id} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded">
              <div className="flex-1">
                <Link 
                  href={`/tasks/${task.id}`}
                  className="font-medium text-gray-900 dark:text-white hover:text-indigo-600 dark:hover:text-indigo-400"
                >
                  {task.title}
                </Link>
                <div className="flex items-center space-x-2 mt-1">
                  <span className="text-xs text-gray-500 dark:text-gray-400">
                    {task.recurrence?.recurrence_type || 'unknown'}
                  </span>
                  {task.due_date && (
                    <span className="text-xs text-gray-500 dark:text-gray-400">
                      Due: {new Date(task.due_date).toLocaleDateString()}
                    </span>
                  )}
                </div>
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

export default function RecurringTasksPage() {
  const [user, setUser] = useState<User | null>(null);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const currentUser = authService.getCurrentUser();
    if (!currentUser) {
      window.location.href = '/login';
      return;
    }
    setUser(currentUser);
    loadTaskData();
  }, []);

  const loadTaskData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const [tasksData] = await Promise.all([
        tasksService.getTasks(0, 100), // Get all tasks
        tasksService.getCategories()
      ]);
      
      // Filter for recurring tasks only
      const recurringTasks = tasksData.filter(task => task.is_recurring);
      
      setTasks(recurringTasks);
    } catch (err) {
      console.error('Error loading recurring tasks:', err);
      setError('Failed to load recurring tasks');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    await authService.logout();
    setUser(null);
    window.location.href = '/login';
  };

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
        <div className="text-lg text-gray-600 dark:text-gray-400">Redirecting to login...</div>
      </div>
    );
  }

  // Group tasks by recurrence pattern
  const tasksByPattern = tasks.reduce((acc, task) => {
    const pattern = task.recurrence?.recurrence_type || 'custom';
    if (!acc[pattern]) acc[pattern] = [];
    acc[pattern].push(task);
    return acc;
  }, {} as Record<string, Task[]>);

  const patterns = Object.keys(tasksByPattern);

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <Header user={user} title="Recurring Tasks" onLogout={handleLogout} />

      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          {/* Breadcrumb Navigation */}
          <nav className="flex mb-6" aria-label="Breadcrumb">
            <ol className="inline-flex items-center space-x-1 md:space-x-3">
              <li className="inline-flex items-center">
                <Link
                  href="/tasks"
                  className="text-gray-700 hover:text-gray-900 dark:text-gray-300 dark:hover:text-white"
                >
                  Tasks
                </Link>
              </li>
              <li>
                <div className="flex items-center">
                  <svg
                    className="w-6 h-6 text-gray-400"
                    fill="currentColor"
                    viewBox="0 0 20 20"
                    xmlns="http://www.w3.org/2000/svg"
                  >
                    <path
                      fillRule="evenodd"
                      d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z"
                      clipRule="evenodd"
                    />
                  </svg>
                  <span className="ml-1 text-gray-500 dark:text-gray-400">Recurring Tasks</span>
                </div>
              </li>
            </ol>
          </nav>

          {/* Page Header */}
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-6">
            <div>
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Recurring Tasks</h1>
              <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
                Manage your recurring and repeating tasks
              </p>
            </div>
            
            <div className="mt-4 sm:mt-0 flex items-center space-x-3">
              <Link 
                href="/tasks/create?recurring=true"
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
              >
                <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                </svg>
                New Recurring Task
              </Link>
            </div>
          </div>

          {error && (
            <div className="mb-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-md">
              <p className="text-red-800 dark:text-red-200">{error}</p>
            </div>
          )}

          {loading ? (
            <div className="animate-pulse space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {[...Array(3)].map((_, i) => (
                  <div key={i} className="h-24 bg-gray-200 dark:bg-gray-700 rounded-lg"></div>
                ))}
              </div>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="h-64 bg-gray-200 dark:bg-gray-700 rounded-lg"></div>
                <div className="h-64 bg-gray-200 dark:bg-gray-700 rounded-lg"></div>
              </div>
            </div>
          ) : (
            <div className="space-y-6">
              {/* Recurring Task Stats */}
              <RecurringTaskStats tasks={tasks} />

              {tasks.length === 0 ? (
                <div className="text-center py-12">
                  <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                  </svg>
                  <h3 className="mt-2 text-sm font-medium text-gray-900 dark:text-white">No recurring tasks</h3>
                  <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">Get started by creating your first recurring task.</p>
                  <div className="mt-6">
                    <Link
                      href="/tasks/create?recurring=true"
                      className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700"
                    >
                      Create Recurring Task
                    </Link>
                  </div>
                </div>
              ) : (
                <div className="space-y-6">
                  {/* Recurring Patterns Grid */}
                  {patterns.length > 0 && (
                    <div>
                      <h2 className="text-lg font-medium text-gray-900 dark:text-white mb-4">By Pattern</h2>
                      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {patterns.map(pattern => (
                          <RecurringPatternCard
                            key={pattern}
                            pattern={pattern}
                            tasks={tasksByPattern[pattern]}
                          />
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Upcoming Tasks */}
                  <UpcomingRecurringTasks tasks={tasks} />
                </div>
              )}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

// Metadata handled by document head