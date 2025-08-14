'use client';

import React, { useState } from 'react';
import { Transaction } from '../../types/Transaction';
import { TransactionItem } from './TransactionItem';

interface TransactionListProps {
  transactions: Transaction[];
  onTransactionUpdate: (transaction: Transaction) => void;
  onTransactionDelete: (transactionId: number) => void;
  loading?: boolean;
  emptyState?: React.ReactNode;
  compact?: boolean;
  className?: string;
  showAccount?: boolean;
  showCategory?: boolean;
}

export const TransactionList: React.FC<TransactionListProps> = ({
  transactions,
  onTransactionUpdate,
  onTransactionDelete,
  loading = false,
  emptyState,
  compact = false,
  className = '',
  showAccount = true,
  showCategory = true
}) => {
  const [sortBy, setSortBy] = useState<'date' | 'amount' | 'type' | 'created_at'>('date');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');

  const sortedTransactions = [...transactions].sort((a, b) => {
    let aValue: number | string;
    let bValue: number | string;

    switch (sortBy) {
      case 'date':
        aValue = new Date(a.transaction_date).getTime();
        bValue = new Date(b.transaction_date).getTime();
        break;
      case 'amount':
        aValue = a.amount;
        bValue = b.amount;
        break;
      case 'type':
        aValue = a.type;
        bValue = b.type;
        break;
      case 'created_at':
        aValue = new Date(a.created_at).getTime();
        bValue = new Date(b.created_at).getTime();
        break;
      default:
        aValue = new Date(a.transaction_date).getTime();
        bValue = new Date(b.transaction_date).getTime();
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
      setSortOrder('desc'); // Default to desc for transactions (most recent first)
    }
  };

  if (loading) {
    return (
      <div className={`space-y-4 ${className}`}>
        {[...Array(5)].map((_, index) => (
          <div
            key={index}
            className="animate-pulse p-4 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg"
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <div className="h-6 w-16 bg-gray-200 dark:bg-gray-700 rounded-full"></div>
                <div className="h-4 w-32 bg-gray-200 dark:bg-gray-700 rounded"></div>
              </div>
              <div className="h-6 w-20 bg-gray-200 dark:bg-gray-700 rounded"></div>
            </div>
            <div className="mt-3 space-y-2">
              <div className="h-3 w-3/4 bg-gray-200 dark:bg-gray-700 rounded"></div>
              <div className="h-3 w-1/2 bg-gray-200 dark:bg-gray-700 rounded"></div>
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (transactions.length === 0) {
    return (
      <div className={`text-center py-12 ${className}`}>
        {emptyState || (
          <div>
            <div className="text-6xl mb-4">💰</div>
            <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">
              No transactions found
            </h3>
            <p className="text-gray-500 dark:text-gray-400">
              Get started by creating your first transaction.
            </p>
          </div>
        )}
      </div>
    );
  }

  return (
    <div className={className}>
      {/* Sort Controls */}
      <div className="flex items-center justify-between mb-4 p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
        <div className="flex items-center space-x-4">
          <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Sort by:</span>
          
          <button
            onClick={() => handleSort('date')}
            className={`text-sm px-3 py-1 rounded-md transition-colors ${
              sortBy === 'date'
                ? 'bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-400'
                : 'text-gray-600 hover:text-gray-800 dark:text-gray-400 dark:hover:text-gray-200'
            }`}
          >
            Date {sortBy === 'date' && (sortOrder === 'asc' ? '↑' : '↓')}
          </button>
          
          <button
            onClick={() => handleSort('amount')}
            className={`text-sm px-3 py-1 rounded-md transition-colors ${
              sortBy === 'amount'
                ? 'bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-400'
                : 'text-gray-600 hover:text-gray-800 dark:text-gray-400 dark:hover:text-gray-200'
            }`}
          >
            Amount {sortBy === 'amount' && (sortOrder === 'asc' ? '↑' : '↓')}
          </button>
          
          <button
            onClick={() => handleSort('type')}
            className={`text-sm px-3 py-1 rounded-md transition-colors ${
              sortBy === 'type'
                ? 'bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-400'
                : 'text-gray-600 hover:text-gray-800 dark:text-gray-400 dark:hover:text-gray-200'
            }`}
          >
            Type {sortBy === 'type' && (sortOrder === 'asc' ? '↑' : '↓')}
          </button>
        </div>
        
        <span className="text-sm text-gray-500 dark:text-gray-400">
          {transactions.length} transaction{transactions.length !== 1 ? 's' : ''}
        </span>
      </div>

      {/* Transaction List */}
      <div className={compact ? 'space-y-2' : 'space-y-4'}>
        {sortedTransactions.map((transaction) => (
          <TransactionItem
            key={transaction.id}
            transaction={transaction}
            onUpdate={onTransactionUpdate}
            onDelete={onTransactionDelete}
            compact={compact}
            showAccount={showAccount}
            showCategory={showCategory}
          />
        ))}
      </div>
    </div>
  );
};