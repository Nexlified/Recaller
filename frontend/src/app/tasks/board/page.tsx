'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { Header } from '@/components/layout/Header';
import { TaskFiltersComponent } from '@/components/tasks/TaskFilters';
import authService from '@/services/auth';
import tasksService from '@/services/tasks';
import { Task, TaskCategory, TaskFilters as ITaskFilters } from '@/types/Task';
import type { User } from '@/services/auth';

// Task Card Component for Board View
const TaskCard = ({ 
  task, 
  onTaskClick, 
  onDelete 
}: {
  task: Task;
  onTaskClick: (task: Task) => void;
  onDelete: (taskId: number) => void;
}) => {
  const [isHovered, setIsHovered] = useState(false);

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric'
    });
  };

  const isOverdue = task.due_date && new Date(task.due_date) < new Date() && task.status !== 'completed';

  return (
    <div 
      className={`bg-white dark:bg-gray-700 rounded-lg shadow-sm border border-gray-200 dark:border-gray-600 p-4 cursor-pointer transition-all hover:shadow-md ${
        isOverdue ? 'border-red-300 dark:border-red-600' : ''
      }`}
      onClick={() => onTaskClick(task)}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {/* Card Header */}
      <div className="flex items-start justify-between mb-3">
        <h4 className="font-medium text-gray-900 dark:text-white text-sm leading-5 line-clamp-2">
          {task.title}
        </h4>
        {isHovered && (
          <div className="flex items-center space-x-1 ml-2">
            <button
              onClick={(e) => {
                e.stopPropagation();
                onDelete(task.id);
              }}
              className="text-gray-400 hover:text-red-600 dark:hover:text-red-400 p-1"
              title="Delete task"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
            </button>
          </div>
        )}
      </div>

      {/* Task Description */}
      {task.description && (
        <p className="text-xs text-gray-600 dark:text-gray-400 mb-3 line-clamp-2">
          {task.description}
        </p>
      )}

      {/* Task Meta Information */}
      <div className="space-y-2">
        {/* Priority and Due Date */}
        <div className="flex items-center justify-between">
          <span className={`px-2 py-1 rounded text-xs font-medium ${
            task.priority === 'high' ? 'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400' :
            task.priority === 'medium' ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-400' :
            'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400'
          }`}>
            {task.priority}
          </span>
          
          {task.due_date && (
            <span className={`text-xs ${
              isOverdue ? 'text-red-600 dark:text-red-400 font-medium' : 'text-gray-500 dark:text-gray-400'
            }`}>
              {formatDate(task.due_date)}
            </span>
          )}
        </div>

        {/* Categories */}
        {task.categories && task.categories.length > 0 && (
          <div className="flex flex-wrap gap-1">
            {task.categories.slice(0, 2).map(category => (
              <span
                key={category.id}
                className="inline-flex items-center px-2 py-1 rounded text-xs"
                style={{
                  backgroundColor: category.color ? `${category.color}20` : '#6B728020',
                  color: category.color || '#6B7280'
                }}
              >
                {category.name}
              </span>
            ))}
            {task.categories.length > 2 && (
              <span className="text-xs text-gray-500 dark:text-gray-400">
                +{task.categories.length - 2}
              </span>
            )}
          </div>
        )}

        {/* Contacts */}
        {task.contacts && task.contacts.length > 0 && (
          <div className="flex items-center space-x-1">
            <svg className="w-3 h-3 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
            <span className="text-xs text-gray-500 dark:text-gray-400">
              {task.contacts.length} contact{task.contacts.length !== 1 ? 's' : ''}
            </span>
          </div>
        )}

        {/* Recurring Indicator */}
        {task.is_recurring && (
          <div className="flex items-center space-x-1">
            <svg className="w-3 h-3 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            <span className="text-xs text-blue-500">Recurring</span>
          </div>
        )}
      </div>
    </div>
  );
};

// Board Column Component
const BoardColumn = ({ 
  title, 
  status, 
  tasks, 
  onTaskClick, 
  onStatusChange, 
  onDelete, 
  color = 'gray' 
}: {
  title: string;
  status: string;
  tasks: Task[];
  onTaskClick: (task: Task) => void;
  onStatusChange: (taskId: number, newStatus: string) => void;
  onDelete: (taskId: number) => void;
  color?: string;
}) => {
  const [isDragOver, setIsDragOver] = useState(false);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = () => {
    setIsDragOver(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    
    const taskId = e.dataTransfer.getData('text/plain');
    if (taskId && taskId !== status) {
      onStatusChange(parseInt(taskId), status);
    }
  };

  const colorClasses = {
    gray: 'bg-gray-100 dark:bg-gray-800 border-gray-300 dark:border-gray-600',
    blue: 'bg-blue-50 dark:bg-blue-900/20 border-blue-300 dark:border-blue-600',
    green: 'bg-green-50 dark:bg-green-900/20 border-green-300 dark:border-green-600',
    yellow: 'bg-yellow-50 dark:bg-yellow-900/20 border-yellow-300 dark:border-yellow-600'
  };

  return (
    <div 
      className={`flex flex-col h-full min-h-[600px] rounded-lg border-2 ${
        isDragOver ? 'border-indigo-400' : colorClasses[color as keyof typeof colorClasses] || colorClasses.gray
      } transition-colors`}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
    >
      {/* Column Header */}
      <div className="p-4 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between">
          <h3 className="font-medium text-gray-900 dark:text-white">{title}</h3>
          <span className="bg-gray-200 dark:bg-gray-600 text-gray-700 dark:text-gray-300 text-xs font-medium px-2 py-1 rounded">
            {tasks.length}
          </span>
        </div>
      </div>

      {/* Column Content */}
      <div className="flex-1 p-4 space-y-3 overflow-y-auto">
        {tasks.map(task => (
          <div
            key={task.id}
            draggable
            onDragStart={(e) => e.dataTransfer.setData('text/plain', task.id.toString())}
          >
            <TaskCard
              task={task}
              onTaskClick={onTaskClick}
              onDelete={onDelete}
            />
          </div>
        ))}
        
        {tasks.length === 0 && (
          <div className="text-center py-8">
            <svg className="mx-auto h-8 w-8 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-2">No tasks</p>
          </div>
        )}
      </div>
    </div>
  );
};

// Board View Component
const TaskBoard = ({ 
  tasks, 
  onTaskClick, 
  onStatusChange, 
  onDelete 
}: {
  tasks: Task[];
  onTaskClick: (task: Task) => void;
  onStatusChange: (taskId: number, newStatus: string) => void;
  onDelete: (taskId: number) => void;
}) => {
  const columns = [
    { status: 'pending', title: 'To Do', color: 'gray' },
    { status: 'in_progress', title: 'In Progress', color: 'blue' },
    { status: 'completed', title: 'Completed', color: 'green' },
  ];

  const tasksByStatus = tasks.reduce((acc, task) => {
    if (!acc[task.status]) acc[task.status] = [];
    acc[task.status].push(task);
    return acc;
  }, {} as Record<string, Task[]>);

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-full">
      {columns.map(column => (
        <BoardColumn
          key={column.status}
          title={column.title}
          status={column.status}
          tasks={tasksByStatus[column.status] || []}
          onTaskClick={onTaskClick}
          onStatusChange={onStatusChange}
          onDelete={onDelete}
          color={column.color}
        />
      ))}
    </div>
  );
};

export default function TaskBoardPage() {
  const [user, setUser] = useState<User | null>(null);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [filteredTasks, setFilteredTasks] = useState<Task[]>([]);
  const [categories, setCategories] = useState<TaskCategory[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeFilters, setActiveFilters] = useState<ITaskFilters>({});

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
    
    if (activeFilters.priority && activeFilters.priority.length > 0) {
      filtered = filtered.filter(task => activeFilters.priority!.includes(task.priority));
    }
    if (activeFilters.category_ids && activeFilters.category_ids.length > 0) {
      filtered = filtered.filter(task => 
        task.categories?.some(cat => activeFilters.category_ids!.includes(cat.id))
      );
    }
    if (activeFilters.is_overdue) {
      filtered = filtered.filter(task => 
        task.due_date && new Date(task.due_date) < new Date() && task.status !== 'completed'
      );
    }
    
    setFilteredTasks(filtered);
  }, [tasks, activeFilters]);

  const loadTaskData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const [tasksData, categoriesData] = await Promise.all([
        tasksService.getTasks(0, 1000), // Get all tasks
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

  const handleTaskClick = (task: Task) => {
    window.location.href = `/tasks/${task.id}`;
  };

  const handleStatusChange = async (taskId: number, newStatus: string) => {
    try {
      const task = tasks.find(t => t.id === taskId);
      if (!task) return;

      const updatedTask = await tasksService.updateTask(taskId, {
        ...task,
        status: newStatus as 'pending' | 'in_progress' | 'completed'
      });
      
      setTasks(prev => prev.map(t => t.id === taskId ? updatedTask : t));
    } catch (err) {
      console.error('Error updating task status:', err);
      setError('Failed to update task status');
    }
  };

  const handleTaskDelete = async (taskId: number) => {
    if (!confirm('Are you sure you want to delete this task?')) return;
    
    try {
      await tasksService.deleteTask(taskId);
      setTasks(prev => prev.filter(task => task.id !== taskId));
    } catch (err) {
      console.error('Error deleting task:', err);
      setError('Failed to delete task');
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
      <Header user={user} title="Task Board" onLogout={handleLogout} />

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
                  <span className="ml-1 text-gray-500 dark:text-gray-400">Board</span>
                </div>
              </li>
            </ol>
          </nav>

          {/* Page Header */}
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-6">
            <div>
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Task Board</h1>
              <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
                Manage your tasks in a Kanban board view
              </p>
            </div>
            
            <div className="mt-4 sm:mt-0 flex items-center space-x-3">
              <Link 
                href="/tasks/list"
                className="inline-flex items-center px-4 py-2 border border-gray-300 dark:border-gray-600 text-sm font-medium rounded-md text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700"
              >
                <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 10h16M4 14h16M4 18h16" />
                </svg>
                List View
              </Link>
              <Link 
                href="/tasks/create"
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700"
              >
                <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                </svg>
                New Task
              </Link>
            </div>
          </div>

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
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {[...Array(3)].map((_, i) => (
                  <div key={i} className="h-96 bg-gray-200 dark:bg-gray-700 rounded-lg"></div>
                ))}
              </div>
            </div>
          ) : (
            <>
              {/* Board Statistics */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow">
                  <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">Total Tasks</h3>
                  <p className="text-2xl font-bold text-gray-900 dark:text-white">{filteredTasks.length}</p>
                </div>
                <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow">
                  <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">To Do</h3>
                  <p className="text-2xl font-bold text-gray-900 dark:text-white">
                    {filteredTasks.filter(t => t.status === 'pending').length}
                  </p>
                </div>
                <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow">
                  <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">In Progress</h3>
                  <p className="text-2xl font-bold text-blue-600 dark:text-blue-400">
                    {filteredTasks.filter(t => t.status === 'in_progress').length}
                  </p>
                </div>
                <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow">
                  <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">Completed</h3>
                  <p className="text-2xl font-bold text-green-600 dark:text-green-400">
                    {filteredTasks.filter(t => t.status === 'completed').length}
                  </p>
                </div>
              </div>

              {/* Task Board */}
              {filteredTasks.length === 0 ? (
                <div className="text-center py-12">
                  <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 17V7m0 10a2 2 0 01-2 2H5a2 2 0 01-2-2V7a2 2 0 012-2h2a2 2 0 012 2m0 10a2 2 0 002 2h2a2 2 0 002-2M9 7a2 2 0 012-2h2a2 2 0 012 2m0 10V7m0 10a2 2 0 002 2h2a2 2 0 002-2V7a2 2 0 00-2-2H9a2 2 0 00-2 2v10z" />
                  </svg>
                  <h3 className="mt-2 text-sm font-medium text-gray-900 dark:text-white">No tasks found</h3>
                  <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                    {tasks.length === 0 ? 'Get started by creating your first task.' : 'Try adjusting your filters.'}
                  </p>
                  <div className="mt-6">
                    <Link
                      href="/tasks/create"
                      className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700"
                    >
                      Create Task
                    </Link>
                  </div>
                </div>
              ) : (
                <TaskBoard
                  tasks={filteredTasks}
                  onTaskClick={handleTaskClick}
                  onStatusChange={handleStatusChange}
                  onDelete={handleTaskDelete}
                />
              )}

              {/* Help Text */}
              {filteredTasks.length > 0 && (
                <div className="mt-6 p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-md">
                  <div className="flex">
                    <div className="flex-shrink-0">
                      <svg className="h-5 w-5 text-blue-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                        <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                      </svg>
                    </div>
                    <div className="ml-3">
                      <h3 className="text-sm font-medium text-blue-800 dark:text-blue-200">Drag & Drop</h3>
                      <div className="mt-2 text-sm text-blue-700 dark:text-blue-300">
                        <p>Drag tasks between columns to change their status. Click on a task to view details.</p>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      </main>
    </div>
  );
}

// Metadata handled by document head