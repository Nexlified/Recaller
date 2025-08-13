'use client';

import React from 'react';

interface DueDateIndicatorProps {
  dueDate?: string;
  className?: string;
  showIcon?: boolean;
}

export const DueDateIndicator: React.FC<DueDateIndicatorProps> = ({ 
  dueDate, 
  className = '', 
  showIcon = true 
}) => {
  if (!dueDate) {
    return null;
  }

  const formatDueDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = date.getTime() - now.getTime();
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

    if (diffDays === 0) return { text: 'Due today', isOverdue: false, isUrgent: true };
    if (diffDays === 1) return { text: 'Due tomorrow', isOverdue: false, isUrgent: true };
    if (diffDays === -1) return { text: 'Due yesterday', isOverdue: true, isUrgent: true };
    if (diffDays < 0) return { text: `${Math.abs(diffDays)} days overdue`, isOverdue: true, isUrgent: true };
    if (diffDays < 7) return { text: `Due in ${diffDays} days`, isOverdue: false, isUrgent: diffDays <= 3 };
    
    return { 
      text: date.toLocaleDateString(), 
      isOverdue: false, 
      isUrgent: false 
    };
  };

  const { text, isOverdue, isUrgent } = formatDueDate(dueDate);

  const getColorClasses = () => {
    if (isOverdue) {
      return 'text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-900/20';
    }
    if (isUrgent) {
      return 'text-yellow-600 dark:text-yellow-400 bg-yellow-50 dark:bg-yellow-900/20';
    }
    return 'text-gray-600 dark:text-gray-400 bg-gray-50 dark:bg-gray-900/20';
  };

  const getIcon = () => {
    if (isOverdue) return '🔴';
    if (isUrgent) return '🟡';
    return '📅';
  };

  return (
    <span
      className={`inline-flex items-center px-2 py-1 rounded text-xs font-medium ${getColorClasses()} ${className}`}
      aria-label={`Due date: ${text}${isOverdue ? ' (overdue)' : ''}`}
      title={new Date(dueDate).toLocaleString()}
    >
      {showIcon && (
        <span className="mr-1" aria-hidden="true">
          {getIcon()}
        </span>
      )}
      {text}
    </span>
  );
};