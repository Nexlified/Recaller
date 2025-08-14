'use client';

import React from 'react';

interface TransactionStatusIndicatorProps {
  isRecurring: boolean;
  hasAttachments?: boolean;
  isOverdue?: boolean;
  className?: string;
}

export const TransactionStatusIndicator: React.FC<TransactionStatusIndicatorProps> = ({ 
  isRecurring, 
  hasAttachments = false,
  isOverdue = false,
  className = '' 
}) => {
  const indicators = [];

  if (isRecurring) {
    indicators.push({
      icon: '🔄',
      label: 'Recurring transaction',
      className: 'text-blue-600 dark:text-blue-400'
    });
  }

  if (hasAttachments) {
    indicators.push({
      icon: '📎',
      label: 'Has attachments',
      className: 'text-gray-600 dark:text-gray-400'
    });
  }

  if (isOverdue) {
    indicators.push({
      icon: '⚠️',
      label: 'Overdue',
      className: 'text-red-600 dark:text-red-400'
    });
  }

  if (indicators.length === 0) {
    return null;
  }

  return (
    <div className={`flex items-center space-x-1 ${className}`}>
      {indicators.map((indicator, index) => (
        <span
          key={index}
          className={`text-sm ${indicator.className}`}
          title={indicator.label}
          aria-label={indicator.label}
        >
          {indicator.icon}
        </span>
      ))}
    </div>
  );
};