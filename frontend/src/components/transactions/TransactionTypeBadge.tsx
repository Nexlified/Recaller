'use client';

import React from 'react';
import { TransactionType } from '../../types/Transaction';

interface TransactionTypeBadgeProps {
  type: TransactionType;
  className?: string;
}

export const TransactionTypeBadge: React.FC<TransactionTypeBadgeProps> = ({ type, className = '' }) => {
  const getColorClasses = (type: TransactionType): string => {
    switch (type) {
      case 'credit':
        return 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400';
      case 'debit':
        return 'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400';
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-900/20 dark:text-gray-400';
    }
  };

  const getDisplayText = (type: TransactionType): string => {
    switch (type) {
      case 'credit': return 'Credit';
      case 'debit': return 'Debit';
      default: return type;
    }
  };

  const getIcon = (type: TransactionType): string => {
    switch (type) {
      case 'credit': return '+';
      case 'debit': return '-';
      default: return '';
    }
  };

  return (
    <span
      className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getColorClasses(type)} ${className}`}
      aria-label={`Transaction type: ${getDisplayText(type)}`}
    >
      <span className="mr-1 font-bold" aria-hidden="true">{getIcon(type)}</span>
      {getDisplayText(type)}
    </span>
  );
};