'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { Header } from '@/components/layout/Header';
import { TaskList } from '@/components/tasks/TaskList';
import { TaskFiltersComponent } from '@/components/tasks/TaskFilters';
import authService from '@/services/auth';
import tasksService from '@/services/tasks';
import { Task, TaskCategory, TaskFilters as ITaskFilters } from '@/types/Task';
import type { User } from '@/services/auth';

// Task Page Header Component
const TaskPageHeader = ({ 
  viewMode, 
  onViewModeChange,
  onCreateNew 
}: { 
  viewMode: 'list' | 'board' | 'calendar';
  onViewModeChange: (mode: 'list' | 'board' | 'calendar') => void;
  onCreateNew: () => void;
}) => {
  return (
    <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">All Tasks</h1>
        <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
          Manage and organize your tasks
        </p>
      </div>
      
      <div className="mt-4 sm:mt-0 flex items-center space-x-3">
        {/* View Mode Toggle */}
        <div className="flex bg-gray-100 dark:bg-gray-700 rounded-lg p-1">
          <button
            onClick={() => onViewModeChange('list')}
            className={`px-3 py-1 rounded text-sm font-medium transition-colors ${
              viewMode === 'list'
                ? 'bg-white dark:bg-gray-600 text-gray-900 dark:text-white shadow'
                : 'text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white'
            }`}
          >
            List
          </button>
          <button
            onClick={() => onViewModeChange('board')}
            className={`px-3 py-1 rounded text-sm font-medium transition-colors ${
              viewMode === 'board'
                ? 'bg-white dark:bg-gray-600 text-gray-900 dark:text-white shadow'
                : 'text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white'
            }`}
          >
            Board
          </button>
          <button
            onClick={() => onViewModeChange('calendar')}
            className={`px-3 py-1 rounded text-sm font-medium transition-colors ${
              viewMode === 'calendar'
                ? 'bg-white dark:bg-gray-600 text-gray-900 dark:text-white shadow'
                : 'text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white'
            }`}
          >
            Calendar
          </button>
        </div>

        {/* Create New Task Button */}
        <Link 
          href="/tasks/create"
          onClick={onCreateNew}
          className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
        >
          <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          New Task
        </Link>
      </div>
    </div>
  );
};

// Task Pagination Component
const TaskPagination = ({ 
  currentPage,
  totalPages,
  onPageChange 
}: { 
  currentPage: number;
  totalPages: number;
  onPageChange: (page: number) => void;
}) => {
  if (totalPages <= 1) return null;

  return (
    <div className="flex items-center justify-between mt-6">
      <div className="text-sm text-gray-700 dark:text-gray-300">
        Page {currentPage} of {totalPages}
      </div>
      <div className="flex space-x-2">
        <button
          onClick={() => onPageChange(currentPage - 1)}
          disabled={currentPage === 1}
          className="px-3 py-2 text-sm bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-md hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Previous
        </button>
        <button
          onClick={() => onPageChange(currentPage + 1)}
          disabled={currentPage === totalPages}
          className="px-3 py-2 text-sm bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-md hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Next
        </button>
      </div>
    </div>
  );
};

// Board View Component (Kanban)
const TaskBoard = ({ 
  tasks, 
  onTaskDelete, 
  onTaskComplete 
}: { 
  tasks: Task[];
  onTaskDelete: (taskId: number) => void;
  onTaskComplete: (taskId: number) => void;
}) => {
  const columns = [
    { status: 'pending', title: 'Pending', color: 'gray' },
    { status: 'in_progress', title: 'In Progress', color: 'blue' },
    { status: 'completed', title: 'Completed', color: 'green' },
  ];

  const tasksByStatus = tasks.reduce((acc, task) => {
    if (!acc[task.status]) acc[task.status] = [];
    acc[task.status].push(task);
    return acc;
  }, {} as Record<string, Task[]>);

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      {columns.map(column => (
        <div key={column.status} className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4">
          <h3 className="font-medium text-gray-900 dark:text-white mb-4">
            {column.title} ({tasksByStatus[column.status]?.length || 0})
          </h3>
          <div className="space-y-3">
            {(tasksByStatus[column.status] || []).map(task => (
              <div key={task.id} className="bg-white dark:bg-gray-700 p-4 rounded-lg shadow-sm">
                <h4 className="font-medium text-gray-900 dark:text-white">{task.title}</h4>
                {task.description && (
                  <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">{task.description}</p>
                )}
                {task.due_date && (
                  <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">
                    Due: {new Date(task.due_date).toLocaleDateString()}
                  </p>
                )}
                <div className="flex items-center justify-between mt-3">
                  <span className={`px-2 py-1 rounded text-xs font-medium ${
                    task.priority === 'high' ? 'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400' :
                    task.priority === 'medium' ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-400' :
                    'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400'
                  }`}>
                    {task.priority}
                  </span>
                  <div className="flex space-x-1">
                    <button 
                      onClick={() => onTaskComplete(task.id)}
                      className="text-green-600 hover:text-green-700 dark:text-green-400"
                    >
                      ✓
                    </button>
                    <button 
                      onClick={() => onTaskDelete(task.id)}
                      className="text-red-600 hover:text-red-700 dark:text-red-400"
                    >
                      ×
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
};

// Calendar View Component
const TaskCalendar = ({ tasks }: { tasks: Task[] }) => {
  const today = new Date();
  
  // Get tasks with due dates
  const tasksWithDueDates = tasks.filter(task => task.due_date);
  
  // Group tasks by date
  const tasksByDate = tasksWithDueDates.reduce((acc, task) => {
    const date = new Date(task.due_date!).toDateString();
    if (!acc[date]) acc[date] = [];
    acc[date].push(task);
    return acc;
  }, {} as Record<string, Task[]>);

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
      <div className="mb-4">
        <h3 className="text-lg font-medium text-gray-900 dark:text-white">
          Tasks Calendar - {today.toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}
        </h3>
      </div>
      
      <div className="space-y-4">
        {Object.entries(tasksByDate)
          .sort(([a], [b]) => new Date(a).getTime() - new Date(b).getTime())
          .slice(0, 10) // Show next 10 dates with tasks
          .map(([date, dateTasks]) => (
            <div key={date} className="border-l-4 border-indigo-500 pl-4">
              <h4 className="font-medium text-gray-900 dark:text-white">
                {new Date(date).toLocaleDateString('en-US', { 
                  weekday: 'long', 
                  month: 'short', 
                  day: 'numeric' 
                })}
              </h4>
              <div className="mt-2 space-y-2">
                {dateTasks.map(task => (
                  <div key={task.id} className="text-sm">
                    <span className="font-medium text-gray-900 dark:text-white">{task.title}</span>
                    <span className={`ml-2 px-2 py-1 rounded text-xs ${
                      task.priority === 'high' ? 'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400' :
                      task.priority === 'medium' ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-400' :
                      'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400'
                    }`}>
                      {task.priority}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          ))}
        
        {Object.keys(tasksByDate).length === 0 && (
          <p className="text-gray-500 dark:text-gray-400 text-center py-8">
            No tasks with due dates
          </p>
        )}
      </div>
    </div>
  );
};

export default function TaskListPage() {
  const [user, setUser] = useState<User | null>(null);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [categories, setCategories] = useState<TaskCategory[]>([]);
  const [filteredTasks, setFilteredTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<'list' | 'board' | 'calendar'>('list');
  const [currentPage, setCurrentPage] = useState(1);
  const [activeFilters, setActiveFilters] = useState<ITaskFilters>({});
  
  const tasksPerPage = 20;
  const totalPages = Math.ceil(filteredTasks.length / tasksPerPage);
  const paginatedTasks = filteredTasks.slice(
    (currentPage - 1) * tasksPerPage,
    currentPage * tasksPerPage
  );

  useEffect(() => {
    const currentUser = authService.getCurrentUser();
    if (!currentUser) {
      window.location.href = '/login';
      return;
    }
    setUser(currentUser);
    loadTaskData();
  }, []);

  useEffect(() => {
    // Apply filters to tasks
    let filtered = tasks;
    
    if (activeFilters.status && activeFilters.status.length > 0) {
      filtered = filtered.filter(task => activeFilters.status!.includes(task.status));
    }
    if (activeFilters.priority && activeFilters.priority.length > 0) {
      filtered = filtered.filter(task => activeFilters.priority!.includes(task.priority));
    }
    if (activeFilters.category_ids && activeFilters.category_ids.length > 0) {
      filtered = filtered.filter(task => 
        task.categories.some(cat => activeFilters.category_ids!.includes(cat.id))
      );
    }
    if (activeFilters.is_overdue) {
      filtered = filtered.filter(task => 
        task.due_date && new Date(task.due_date) < new Date() && task.status !== 'completed'
      );
    }
    
    setFilteredTasks(filtered);
    setCurrentPage(1); // Reset to first page when filters change
  }, [tasks, activeFilters]);

  // Handle pagination when filteredTasks changes due to deletions
  useEffect(() => {
    const newTotalPages = Math.ceil(filteredTasks.length / tasksPerPage);
    if (currentPage > newTotalPages && newTotalPages > 0) {
      setCurrentPage(newTotalPages);
    }
  }, [filteredTasks.length, currentPage, tasksPerPage]);

  const loadTaskData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const [tasksData, categoriesData] = await Promise.all([
        tasksService.getTasks(0, 100), // Get all tasks for filtering
        tasksService.getCategories()
      ]);
      
      setTasks(tasksData);
      setCategories(categoriesData);
    } catch (err) {
      console.error('Error loading task data:', err);
      setError('Failed to load tasks');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    await authService.logout();
    setUser(null);
    window.location.href = '/login';
  };

  const handleTaskUpdate = async (updatedTask: Task) => {
    try {
      const updated = await tasksService.updateTask(updatedTask.id, updatedTask);
      setTasks(prev => prev.map(task => task.id === updated.id ? updated : task));
    } catch (err) {
      console.error('Error updating task:', err);
      setError('Failed to update task');
    }
  };

  const handleTaskDelete = async (taskId: number) => {
    if (!confirm('Are you sure you want to delete this task?')) return;
    
    // Optimistic update: remove from UI immediately
    const originalTasks = tasks;
    setTasks(prev => prev.filter(task => task.id !== taskId));
    
    try {
      await tasksService.deleteTask(taskId);
      // Success - task already removed from UI
    } catch (err) {
      console.error('Error deleting task:', err);
      setError('Failed to delete task');
      // Revert optimistic update on error
      setTasks(originalTasks);
    }
  };

  const handleTaskComplete = async (taskId: number) => {
    try {
      const updated = await tasksService.markTaskComplete(taskId);
      setTasks(prev => prev.map(task => task.id === updated.id ? updated : task));
    } catch (err) {
      console.error('Error completing task:', err);
      setError('Failed to complete task');
    }
  };

  const handleFiltersChange = (filters: ITaskFilters) => {
    setActiveFilters(filters);
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
      <Header user={user} title="Tasks" onLogout={handleLogout} />

      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          {/* Page Header */}
          <TaskPageHeader 
            viewMode={viewMode}
            onViewModeChange={setViewMode}
            onCreateNew={() => {}} // Will navigate to create page
          />

          {error && (
            <div className="mb-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-md">
              <p className="text-red-800 dark:text-red-200">{error}</p>
            </div>
          )}

          {/* Filters */}
          <div className="mb-6">
            <TaskFiltersComponent
              filters={activeFilters}
              categories={categories}
              contacts={[]} // Will be loaded from contacts service
              onFiltersChange={handleFiltersChange}
              className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow"
            />
          </div>

          {loading ? (
            <div className="animate-pulse">
              <div className="space-y-4">
                {[...Array(5)].map((_, i) => (
                  <div key={i} className="h-20 bg-gray-200 dark:bg-gray-700 rounded-lg"></div>
                ))}
              </div>
            </div>
          ) : (
            <>
              {/* Task Content based on view mode */}
              {viewMode === 'list' && (
                <>
                  <TaskList
                    tasks={paginatedTasks}
                    onTaskUpdate={handleTaskUpdate}
                    onTaskDelete={handleTaskDelete}
                    onTaskComplete={handleTaskComplete}
                    loading={loading}
                    emptyState={
                      <div className="text-center py-12">
                        <p className="text-gray-500 dark:text-gray-400 mb-4">No tasks found</p>
                        <Link 
                          href="/tasks/create"
                          className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700"
                        >
                          Create your first task
                        </Link>
                      </div>
                    }
                  />
                  <TaskPagination
                    currentPage={currentPage}
                    totalPages={totalPages}
                    onPageChange={setCurrentPage}
                  />
                </>
              )}

              {viewMode === 'board' && (
                <TaskBoard
                  tasks={filteredTasks}
                  onTaskDelete={handleTaskDelete}
                  onTaskComplete={handleTaskComplete}
                />
              )}

              {viewMode === 'calendar' && (
                <TaskCalendar tasks={filteredTasks} />
              )}
            </>
          )}
        </div>
      </main>
    </div>
  );
}