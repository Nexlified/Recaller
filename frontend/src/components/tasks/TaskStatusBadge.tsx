'use client';

import React from 'react';
import { TaskStatus } from '../../types/Task';

interface TaskStatusBadgeProps {
  status: TaskStatus;
  className?: string;
}

export const TaskStatusBadge: React.FC<TaskStatusBadgeProps> = ({ status, className = '' }) => {
  const getColorClasses = (status: TaskStatus): string => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400';
      case 'in_progress':
        return 'bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-400';
      case 'pending':
        return 'bg-gray-100 text-gray-800 dark:bg-gray-900/20 dark:text-gray-400';
      case 'cancelled':
        return 'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400';
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-900/20 dark:text-gray-400';
    }
  };

  const getDisplayText = (status: TaskStatus): string => {
    switch (status) {
      case 'completed': return 'Completed';
      case 'in_progress': return 'In Progress';
      case 'pending': return 'Pending';
      case 'cancelled': return 'Cancelled';
      default: return status;
    }
  };

  const getIcon = (status: TaskStatus): string => {
    switch (status) {
      case 'completed': return '✓';
      case 'in_progress': return '▶';
      case 'pending': return '⏸';
      case 'cancelled': return '✕';
      default: return '';
    }
  };

  return (
    <span
      className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getColorClasses(status)} ${className}`}
      aria-label={`Status: ${getDisplayText(status)}`}
    >
      <span className="mr-1" aria-hidden="true">{getIcon(status)}</span>
      {getDisplayText(status)}
    </span>
  );
};