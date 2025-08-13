'use client';

import React from 'react';
import { TaskPriority } from '../../types/Task';

interface TaskPriorityBadgeProps {
  priority: TaskPriority;
  className?: string;
}

export const TaskPriorityBadge: React.FC<TaskPriorityBadgeProps> = ({ priority, className = '' }) => {
  const getColorClasses = (priority: TaskPriority): string => {
    switch (priority) {
      case 'high':
        return 'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-400';
      case 'low':
        return 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400';
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-900/20 dark:text-gray-400';
    }
  };

  const getDisplayText = (priority: TaskPriority): string => {
    switch (priority) {
      case 'high': return 'High';
      case 'medium': return 'Medium';
      case 'low': return 'Low';
      default: return priority;
    }
  };

  return (
    <span
      className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getColorClasses(priority)} ${className}`}
      aria-label={`Priority: ${getDisplayText(priority)}`}
    >
      {getDisplayText(priority)}
    </span>
  );
};