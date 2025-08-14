'use client';

import React, { useState } from 'react';
import { Transaction } from '../../types/Transaction';
import { TransactionTypeBadge } from './TransactionTypeBadge';
import { AmountDisplay } from './AmountDisplay';
import { TransactionStatusIndicator } from './TransactionStatusIndicator';
import transactionsService from '../../services/transactions';

interface TransactionItemProps {
  transaction: Transaction;
  onUpdate: (transaction: Transaction) => void;
  onDelete: (transactionId: number) => void;
  compact?: boolean;
  className?: string;
  showAccount?: boolean;
  showCategory?: boolean;
}

export const TransactionItem: React.FC<TransactionItemProps> = ({
  transaction,
  onUpdate,
  onDelete,
  compact = false,
  className = '',
  showAccount = true,
  showCategory = true
}) => {
  const [isUpdating, setIsUpdating] = useState(false);
  const [showActions, setShowActions] = useState(false);

  const handleDelete = async () => {
    if (!window.confirm('Are you sure you want to delete this transaction?')) return;
    
    setIsUpdating(true);
    try {
      await transactionsService.deleteTransaction(transaction.id);
      onDelete(transaction.id);
    } catch (error) {
      console.error('Failed to delete transaction:', error);
      setIsUpdating(false);
    }
  };

  const formatDate = (dateString: string): string => {
    try {
      return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      });
    } catch {
      return dateString;
    }
  };

  const hasAttachments = transaction.attachments && Object.keys(transaction.attachments).length > 0;

  if (compact) {
    return (
      <div 
        className={`flex items-center justify-between p-3 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg hover:shadow-md transition-shadow ${className}`}
        onMouseEnter={() => setShowActions(true)}
        onMouseLeave={() => setShowActions(false)}
      >
        <div className="flex items-center space-x-3 flex-grow min-w-0">
          <TransactionTypeBadge type={transaction.type} />
          
          <div className="flex-grow min-w-0">
            <div className="flex items-center justify-between">
              <p className="text-sm font-medium text-gray-900 dark:text-gray-100 truncate">
                {transaction.description || 'No description'}
              </p>
              <AmountDisplay 
                amount={transaction.amount}
                currency={transaction.currency}
                type={transaction.type}
                className="ml-2"
              />
            </div>
            <p className="text-xs text-gray-500 dark:text-gray-400">
              {formatDate(transaction.transaction_date)}
            </p>
          </div>

          <TransactionStatusIndicator 
            isRecurring={transaction.is_recurring}
            hasAttachments={hasAttachments}
          />
        </div>

        {showActions && (
          <div className="flex items-center space-x-2 ml-3">
            <button
              onClick={handleDelete}
              disabled={isUpdating}
              className="p-1 text-red-600 hover:text-red-800 dark:text-red-400 dark:hover:text-red-300 disabled:opacity-50"
              aria-label="Delete transaction"
            >
              🗑️
            </button>
          </div>
        )}
      </div>
    );
  }

  return (
    <div 
      className={`p-4 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg hover:shadow-md transition-shadow ${className}`}
      onMouseEnter={() => setShowActions(true)}
      onMouseLeave={() => setShowActions(false)}
    >
      <div className="flex items-start justify-between">
        <div className="flex-grow min-w-0">
          <div className="flex items-center space-x-3 mb-2">
            <TransactionTypeBadge type={transaction.type} />
            
            <TransactionStatusIndicator 
              isRecurring={transaction.is_recurring}
              hasAttachments={hasAttachments}
            />
          </div>

          <div className="mb-2">
            <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-1">
              {transaction.description || 'No description'}
            </h3>
            
            <div className="flex items-center justify-between">
              <AmountDisplay 
                amount={transaction.amount}
                currency={transaction.currency}
                type={transaction.type}
                className="text-lg"
              />
              
              <span className="text-sm text-gray-500 dark:text-gray-400">
                {formatDate(transaction.transaction_date)}
              </span>
            </div>
          </div>

          <div className="flex flex-wrap gap-2 text-sm text-gray-600 dark:text-gray-400">
            {transaction.reference_number && (
              <span className="inline-flex items-center px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded-md">
                Ref: {transaction.reference_number}
              </span>
            )}
            
            {showCategory && transaction.category_id && (
              <span className="inline-flex items-center px-2 py-1 bg-blue-100 dark:bg-blue-900/20 text-blue-800 dark:text-blue-400 rounded-md">
                Category ID: {transaction.category_id}
              </span>
            )}
            
            {showAccount && transaction.account_id && (
              <span className="inline-flex items-center px-2 py-1 bg-green-100 dark:bg-green-900/20 text-green-800 dark:text-green-400 rounded-md">
                Account ID: {transaction.account_id}
              </span>
            )}
          </div>
        </div>

        {showActions && (
          <div className="flex items-center space-x-2 ml-4">
            <button
              onClick={() => {/* TODO: Edit functionality */}}
              disabled={isUpdating}
              className="p-2 text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300 disabled:opacity-50"
              aria-label="Edit transaction"
            >
              ✏️
            </button>
            <button
              onClick={handleDelete}
              disabled={isUpdating}
              className="p-2 text-red-600 hover:text-red-800 dark:text-red-400 dark:hover:text-red-300 disabled:opacity-50"
              aria-label="Delete transaction"
            >
              🗑️
            </button>
          </div>
        )}
      </div>
    </div>
  );
};