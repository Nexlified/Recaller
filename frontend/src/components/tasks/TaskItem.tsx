'use client';

import React, { useState } from 'react';
import { Task } from '../../types/Task';
import { TaskStatusBadge } from './TaskStatusBadge';
import { TaskPriorityBadge } from './TaskPriorityBadge';
import { DueDateIndicator } from './DueDateIndicator';
import tasksService from '../../services/tasks';

interface TaskItemProps {
  task: Task;
  onUpdate: (task: Task) => void;
  onDelete: (taskId: number) => void;
  onComplete: (taskId: number) => void;
  compact?: boolean;
  className?: string;
}

export const TaskItem: React.FC<TaskItemProps> = ({
  task,
  onUpdate,
  onDelete,
  onComplete,
  compact = false,
  className = ''
}) => {
  const [isUpdating, setIsUpdating] = useState(false);
  const [showActions, setShowActions] = useState(false);

  // Removed unused handleComplete function as handleStatusToggle serves the same purpose

  const handleDelete = async () => {
    if (!window.confirm('Are you sure you want to delete this task?')) return;
    
    setIsUpdating(true);
    try {
      await tasksService.deleteTask(task.id);
      onDelete(task.id);
    } catch (error) {
      console.error('Failed to delete task:', error);
      setIsUpdating(false);
    }
  };

  const handleStatusToggle = async () => {
    const newStatus = task.status === 'completed' ? 'pending' : 'completed';
    setIsUpdating(true);
    try {
      const updatedTask = await tasksService.updateTaskStatus(task.id, newStatus);
      onUpdate(updatedTask);
      if (newStatus === 'completed') {
        onComplete(task.id);
      }
    } catch (error) {
      console.error('Failed to update task status:', error);
    } finally {
      setIsUpdating(false);
    }
  };

  const isOverdue = tasksService.isTaskOverdue(task);

  if (compact) {
    return (
      <div
        className={`flex items-center p-2 hover:bg-gray-50 dark:hover:bg-gray-800 rounded-lg transition-colors ${className}`}
        onMouseEnter={() => setShowActions(true)}
        onMouseLeave={() => setShowActions(false)}
      >
        {/* Checkbox */}
        <button
          onClick={handleStatusToggle}
          disabled={isUpdating}
          className="flex-shrink-0 mr-3 p-1 rounded-full hover:bg-gray-200 dark:hover:bg-gray-700 disabled:opacity-50"
          aria-label={task.status === 'completed' ? 'Mark as incomplete' : 'Mark as complete'}
        >
          <div className={`w-5 h-5 rounded-full border-2 flex items-center justify-center ${
            task.status === 'completed'
              ? 'bg-green-500 border-green-500 text-white'
              : 'border-gray-300 dark:border-gray-600 hover:border-green-500'
          }`}>
            {task.status === 'completed' && (
              <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
              </svg>
            )}
          </div>
        </button>

        {/* Task content */}
        <div className="flex-1 min-w-0">
          <h3 className={`text-sm font-medium truncate ${
            task.status === 'completed' ? 'line-through text-gray-500' : 'text-gray-900 dark:text-gray-100'
          }`}>
            {task.title}
          </h3>
        </div>

        {/* Badges */}
        <div className="flex-shrink-0 flex items-center space-x-2 ml-2">
          <TaskPriorityBadge priority={task.priority} />
          {task.due_date && <DueDateIndicator dueDate={task.due_date} />}
        </div>

        {/* Actions */}
        {showActions && (
          <div className="flex-shrink-0 flex items-center space-x-1 ml-2">
            <button
              onClick={handleDelete}
              disabled={isUpdating}
              className="p-1 text-red-600 hover:text-red-800 dark:text-red-400 dark:hover:text-red-200 disabled:opacity-50"
              aria-label="Delete task"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
            </button>
          </div>
        )}
      </div>
    );
  }

  return (
    <div
      className={`bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-4 hover:shadow-md transition-shadow ${
        isOverdue ? 'border-l-4 border-l-red-500' : ''
      } ${className}`}
      onMouseEnter={() => setShowActions(true)}
      onMouseLeave={() => setShowActions(false)}
    >
      <div className="flex items-start space-x-3">
        {/* Checkbox */}
        <button
          onClick={handleStatusToggle}
          disabled={isUpdating}
          className="flex-shrink-0 mt-1 p-1 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700 disabled:opacity-50"
          aria-label={task.status === 'completed' ? 'Mark as incomplete' : 'Mark as complete'}
        >
          <div className={`w-6 h-6 rounded-full border-2 flex items-center justify-center ${
            task.status === 'completed'
              ? 'bg-green-500 border-green-500 text-white'
              : 'border-gray-300 dark:border-gray-600 hover:border-green-500'
          }`}>
            {task.status === 'completed' && (
              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
              </svg>
            )}
          </div>
        </button>

        {/* Content */}
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between">
            <div className="flex-1 min-w-0">
              <h3 className={`text-lg font-medium ${
                task.status === 'completed' ? 'line-through text-gray-500' : 'text-gray-900 dark:text-gray-100'
              }`}>
                {task.title}
              </h3>
              {task.description && (
                <p className={`mt-1 text-sm ${
                  task.status === 'completed' ? 'text-gray-400' : 'text-gray-600 dark:text-gray-400'
                }`}>
                  {task.description}
                </p>
              )}
            </div>

            {/* Actions */}
            {showActions && (
              <div className="flex-shrink-0 flex items-center space-x-2 ml-4">
                <button
                  onClick={() => {/* TODO: Implement edit */}}
                  disabled={isUpdating}
                  className="p-2 text-gray-600 hover:text-gray-800 dark:text-gray-400 dark:hover:text-gray-200 disabled:opacity-50"
                  aria-label="Edit task"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                  </svg>
                </button>
                <button
                  onClick={handleDelete}
                  disabled={isUpdating}
                  className="p-2 text-red-600 hover:text-red-800 dark:text-red-400 dark:hover:text-red-200 disabled:opacity-50"
                  aria-label="Delete task"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                </button>
              </div>
            )}
          </div>

          {/* Metadata */}
          <div className="mt-3 flex items-center space-x-3">
            <TaskStatusBadge status={task.status} />
            <TaskPriorityBadge priority={task.priority} />
            {task.due_date && <DueDateIndicator dueDate={task.due_date} />}
            {task.is_recurring && (
              <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-purple-100 text-purple-800 dark:bg-purple-900/20 dark:text-purple-400">
                🔄 Recurring
              </span>
            )}
          </div>

          {/* Categories and Contacts */}
          {(task.categories.length > 0 || task.contacts.length > 0) && (
            <div className="mt-3 flex flex-wrap gap-2">
              {task.categories.map(category => (
                <span
                  key={category.id}
                  className="inline-flex items-center px-2 py-1 rounded text-xs font-medium"
                  style={{
                    backgroundColor: category.color ? `${category.color}20` : '#f3f4f6',
                    color: category.color || '#6b7280'
                  }}
                >
                  📂 {category.name}
                </span>
              ))}
              {task.contacts.map(contact => (
                <span
                  key={contact.id}
                  className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-400"
                >
                  👤 {contact.first_name} {contact.last_name}
                </span>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};