'use client';

import React, { useState } from 'react';
import { Task } from '../../types/Task';
import { TaskItem } from './TaskItem';

interface TaskListProps {
  tasks: Task[];
  onTaskUpdate: (task: Task) => void;
  onTaskDelete: (taskId: number) => void;
  onTaskComplete: (taskId: number) => void;
  loading?: boolean;
  emptyState?: React.ReactNode;
  compact?: boolean;
  className?: string;
}

export const TaskList: React.FC<TaskListProps> = ({
  tasks,
  onTaskUpdate,
  onTaskDelete,
  onTaskComplete,
  loading = false,
  emptyState,
  compact = false,
  className = ''
}) => {
  const [sortBy, setSortBy] = useState<'due_date' | 'priority' | 'created_at' | 'status'>('due_date');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc');

  const sortedTasks = [...tasks].sort((a, b) => {
    let aValue: number | string;
    let bValue: number | string;

    switch (sortBy) {
      case 'due_date':
        aValue = a.due_date ? new Date(a.due_date).getTime() : Infinity;
        bValue = b.due_date ? new Date(b.due_date).getTime() : Infinity;
        break;
      case 'priority':
        const priorityOrder = { high: 3, medium: 2, low: 1 };
        aValue = priorityOrder[a.priority];
        bValue = priorityOrder[b.priority];
        break;
      case 'created_at':
        aValue = new Date(a.created_at).getTime();
        bValue = new Date(b.created_at).getTime();
        break;
      case 'status':
        const statusOrder = { pending: 1, in_progress: 2, completed: 3, cancelled: 4 };
        aValue = statusOrder[a.status];
        bValue = statusOrder[b.status];
        break;
      default:
        aValue = a.created_at;
        bValue = b.created_at;
    }

    if (sortOrder === 'asc') {
      return aValue < bValue ? -1 : aValue > bValue ? 1 : 0;
    } else {
      return aValue > bValue ? -1 : aValue < bValue ? 1 : 0;
    }
  });

  const handleSort = (field: typeof sortBy) => {
    if (sortBy === field) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(field);
      setSortOrder('asc');
    }
  };

  if (loading) {
    return (
      <div className={`space-y-4 ${className}`}>
        {[...Array(5)].map((_, index) => (
          <div
            key={index}
            className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-4 animate-pulse"
          >
            <div className="flex items-start space-x-3">
              <div className="w-6 h-6 bg-gray-200 dark:bg-gray-600 rounded-full"></div>
              <div className="flex-1 space-y-2">
                <div className="h-4 bg-gray-200 dark:bg-gray-600 rounded w-3/4"></div>
                <div className="h-3 bg-gray-200 dark:bg-gray-600 rounded w-1/2"></div>
                <div className="flex space-x-2">
                  <div className="h-5 bg-gray-200 dark:bg-gray-600 rounded w-16"></div>
                  <div className="h-5 bg-gray-200 dark:bg-gray-600 rounded w-20"></div>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (tasks.length === 0) {
    return (
      <div className={`text-center py-12 ${className}`}>
        {emptyState || (
          <div>
            <svg
              className="mx-auto h-12 w-12 text-gray-400"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              aria-hidden="true"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01"
              />
            </svg>
            <h3 className="mt-2 text-sm font-medium text-gray-900 dark:text-gray-100">No tasks found</h3>
            <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
              Create a new task to get started.
            </p>
          </div>
        )}
      </div>
    );
  }

  return (
    <div className={className}>
      {/* Sort Controls */}
      {!compact && (
        <div className="mb-4 flex flex-wrap gap-2">
          <span className="text-sm text-gray-600 dark:text-gray-400 self-center">Sort by:</span>
          <button
            onClick={() => handleSort('due_date')}
            className={`px-3 py-1 rounded text-sm font-medium transition-colors ${
              sortBy === 'due_date'
                ? 'bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-400'
                : 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
            }`}
          >
            Due Date {sortBy === 'due_date' && (sortOrder === 'asc' ? '↑' : '↓')}
          </button>
          <button
            onClick={() => handleSort('priority')}
            className={`px-3 py-1 rounded text-sm font-medium transition-colors ${
              sortBy === 'priority'
                ? 'bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-400'
                : 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
            }`}
          >
            Priority {sortBy === 'priority' && (sortOrder === 'asc' ? '↑' : '↓')}
          </button>
          <button
            onClick={() => handleSort('status')}
            className={`px-3 py-1 rounded text-sm font-medium transition-colors ${
              sortBy === 'status'
                ? 'bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-400'
                : 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
            }`}
          >
            Status {sortBy === 'status' && (sortOrder === 'asc' ? '↑' : '↓')}
          </button>
          <button
            onClick={() => handleSort('created_at')}
            className={`px-3 py-1 rounded text-sm font-medium transition-colors ${
              sortBy === 'created_at'
                ? 'bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-400'
                : 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
            }`}
          >
            Created {sortBy === 'created_at' && (sortOrder === 'asc' ? '↑' : '↓')}
          </button>
        </div>
      )}

      {/* Task List */}
      <div className={compact ? 'space-y-1' : 'space-y-4'}>
        {sortedTasks.map(task => (
          <TaskItem
            key={task.id}
            task={task}
            onUpdate={onTaskUpdate}
            onDelete={onTaskDelete}
            onComplete={onTaskComplete}
            compact={compact}
          />
        ))}
      </div>

      {/* Summary */}
      {!compact && tasks.length > 0 && (
        <div className="mt-6 p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
          <div className="flex flex-wrap gap-4 text-sm text-gray-600 dark:text-gray-400">
            <span>Total: {tasks.length}</span>
            <span>Pending: {tasks.filter(t => t.status === 'pending').length}</span>
            <span>In Progress: {tasks.filter(t => t.status === 'in_progress').length}</span>
            <span>Completed: {tasks.filter(t => t.status === 'completed').length}</span>
            <span className="text-red-600 dark:text-red-400">
              Overdue: {tasks.filter(t => t.due_date && new Date(t.due_date) < new Date() && t.status !== 'completed').length}
            </span>
          </div>
        </div>
      )}
    </div>
  );
};