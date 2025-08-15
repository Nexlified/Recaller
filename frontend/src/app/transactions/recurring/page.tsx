'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import transactionsService from '@/services/transactions';
import { 
  RecurringTransaction, 
  RecurringTransactionWithNext,
  TransactionCategory, 
  FinancialAccount 
} from '@/types/Transaction';

export default function RecurringTransactionsPage() {
  const [recurringTransactions, setRecurringTransactions] = useState<RecurringTransaction[]>([]);
  const [recurringWithNext, setRecurringWithNext] = useState<RecurringTransactionWithNext[]>([]);
  const [categories, setCategories] = useState<TransactionCategory[]>([]);
  const [accounts, setAccounts] = useState<FinancialAccount[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [processingRecurring, setProcessingRecurring] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [recurringData, recurringWithNextData, categoriesData, accountsData] = await Promise.all([
        transactionsService.getRecurringTransactions(),
        transactionsService.getRecurringTransactionsWithNext(),
        transactionsService.getTransactionCategories(),
        transactionsService.getFinancialAccounts()
      ]);
      setRecurringTransactions(recurringData);
      setRecurringWithNext(recurringWithNextData);
      setCategories(categoriesData);
      setAccounts(accountsData);
    } catch (err) {
      console.error('Error loading recurring transactions:', err);
      setError('Failed to load recurring transactions');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (recurringId: number) => {
    if (!window.confirm('Are you sure you want to delete this recurring transaction? This action cannot be undone.')) {
      return;
    }

    try {
      await transactionsService.deleteRecurringTransaction(recurringId);
      setRecurringTransactions(prev => prev.filter(rt => rt.id !== recurringId));
      setRecurringWithNext(prev => prev.filter(rt => rt.id !== recurringId));
    } catch (err) {
      console.error('Error deleting recurring transaction:', err);
      setError('Failed to delete recurring transaction');
    }
  };

  const handleProcessRecurring = async (dryRun: boolean = false) => {
    try {
      setProcessingRecurring(true);
      setError(null);
      const processedTransactions = await transactionsService.processRecurringTransactions(dryRun);
      
      if (dryRun) {
        alert(`Dry run complete. ${processedTransactions.length} transactions would be created.`);
      } else {
        alert(`${processedTransactions.length} recurring transactions processed successfully.`);
        await loadData(); // Reload data to get updated next execution dates
      }
    } catch (err) {
      console.error('Error processing recurring transactions:', err);
      setError('Failed to process recurring transactions');
    } finally {
      setProcessingRecurring(false);
    }
  };

  const getCategoryName = (categoryId?: number) => {
    if (!categoryId) return 'No Category';
    const category = categories.find(c => c.id === categoryId);
    return category ? category.name : 'Unknown Category';
  };

  const getAccountName = (accountId?: number) => {
    if (!accountId) return 'No Account';
    const account = accounts.find(a => a.id === accountId);
    return account ? account.account_name : 'Unknown Account';
  };

  const formatCurrency = (amount: number, currency: string) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency,
    }).format(amount);
  };

  const formatDate = (dateString?: string) => {
    if (!dateString) return 'Not set';
    return new Date(dateString).toLocaleDateString();
  };

  const getFrequencyLabel = (frequency: string) => {
    const labels: Record<string, string> = {
      daily: 'Daily',
      weekly: 'Weekly',
      monthly: 'Monthly',
      quarterly: 'Quarterly',
      yearly: 'Yearly',
    };
    return labels[frequency] || frequency;
  };

  const getStatusColor = (isActive: boolean) => {
    return isActive 
      ? 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400'
      : 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300';
  };

  const isOverdue = (nextOccurrenceDate?: string) => {
    if (!nextOccurrenceDate) return false;
    return new Date(nextOccurrenceDate) < new Date();
  };

  return (
    <div className="px-4 py-6 sm:px-0">
      {/* Breadcrumb Navigation */}
      <nav className="flex mb-6" aria-label="Breadcrumb">
        <ol className="inline-flex items-center space-x-1 md:space-x-3">
          <li className="inline-flex items-center">
            <Link
              href="/transactions"
              className="text-gray-700 hover:text-gray-900 dark:text-gray-300 dark:hover:text-white"
            >
              Transactions
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
              <span className="ml-1 text-gray-500 dark:text-gray-400">Recurring Transactions</span>
            </div>
          </li>
        </ol>
      </nav>

      {/* Page Header */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Recurring Transactions</h1>
          <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
            Manage your automatic recurring transactions and payments
          </p>
        </div>
        <div className="flex space-x-3">
          <button
            onClick={() => handleProcessRecurring(true)}
            disabled={processingRecurring}
            className="inline-flex items-center px-4 py-2 border border-gray-300 dark:border-gray-600 text-sm font-medium rounded-md text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
          >
            {processingRecurring ? 'Processing...' : 'Dry Run'}
          </button>
          <button
            onClick={() => handleProcessRecurring(false)}
            disabled={processingRecurring}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
          >
            {processingRecurring ? 'Processing...' : 'Process Due'}
          </button>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="mb-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-md">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-red-400" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <p className="text-sm text-red-800 dark:text-red-200">{error}</p>
            </div>
          </div>
        </div>
      )}

      {/* Stats Cards */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-3 mb-6">
        <div className="bg-white dark:bg-gray-800 overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <svg className="h-6 w-6 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 dark:text-gray-400 truncate">
                    Total Recurring
                  </dt>
                  <dd className="text-lg font-medium text-gray-900 dark:text-gray-100">
                    {recurringTransactions.length}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <svg className="h-6 w-6 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 dark:text-gray-400 truncate">
                    Active
                  </dt>
                  <dd className="text-lg font-medium text-gray-900 dark:text-gray-100">
                    {recurringTransactions.filter(rt => rt.is_active).length}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <svg className="h-6 w-6 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 dark:text-gray-400 truncate">
                    Overdue
                  </dt>
                  <dd className="text-lg font-medium text-gray-900 dark:text-gray-100">
                    {recurringWithNext.filter(rt => isOverdue(rt.next_occurrence_date)).length}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Recurring Transactions List */}
      <div className="bg-white dark:bg-gray-800 shadow rounded-lg">
        {loading ? (
          <div className="p-6">
            <div className="animate-pulse space-y-4">
              {[...Array(3)].map((_, i) => (
                <div key={i} className="flex items-center justify-between py-4 border-b border-gray-200 dark:border-gray-700">
                  <div className="flex items-center space-x-4">
                    <div className="space-y-2">
                      <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-48"></div>
                      <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-32"></div>
                    </div>
                  </div>
                  <div className="flex items-center space-x-4">
                    <div className="text-right space-y-2">
                      <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-20"></div>
                      <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-16"></div>
                    </div>
                    <div className="flex space-x-2">
                      <div className="h-6 bg-gray-200 dark:bg-gray-700 rounded w-12"></div>
                      <div className="h-6 bg-gray-200 dark:bg-gray-700 rounded w-12"></div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ) : recurringTransactions.length === 0 ? (
          <div className="text-center py-12">
            <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 48 48">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            <h3 className="mt-2 text-sm font-medium text-gray-900 dark:text-gray-100">No recurring transactions</h3>
            <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
              Set up recurring transactions when creating a new transaction.
            </p>
            <div className="mt-6">
              <Link
                href="/transactions/create"
                className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                Create Transaction
              </Link>
            </div>
          </div>
        ) : (
          <div className="divide-y divide-gray-200 dark:divide-gray-700">
            {recurringWithNext.map((recurring) => {
              const isOverdueItem = isOverdue(recurring.next_occurrence_date);
              return (
                <div key={recurring.id} className="p-6 hover:bg-gray-50 dark:hover:bg-gray-700/50">
                  <div className="flex items-center justify-between">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center space-x-3">
                        <h3 className="text-sm font-medium text-gray-900 dark:text-gray-100 truncate">
                          {recurring.template_name}
                        </h3>
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(recurring.is_active)}`}>
                          {recurring.is_active ? 'Active' : 'Inactive'}
                        </span>
                        {isOverdueItem && (
                          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400">
                            Overdue
                          </span>
                        )}
                      </div>
                      <div className="mt-1 flex items-center space-x-4 text-sm text-gray-500 dark:text-gray-400">
                        <span>{formatCurrency(Number(recurring.amount), recurring.currency)}</span>
                        <span>•</span>
                        <span className={recurring.type === 'credit' ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'}>
                          {recurring.type === 'credit' ? 'Income' : 'Expense'}
                        </span>
                        <span>•</span>
                        <span>{getFrequencyLabel(recurring.frequency)}</span>
                        <span>•</span>
                        <span>{getCategoryName(recurring.category_id)}</span>
                      </div>
                      <div className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                        Account: {getAccountName(recurring.account_id)}
                      </div>
                    </div>
                    <div className="flex items-center space-x-6">
                      <div className="text-right">
                        <div className="text-sm font-medium text-gray-900 dark:text-gray-100">
                          Next: {formatDate(recurring.next_occurrence_date)}
                        </div>
                        <div className="text-sm text-gray-500 dark:text-gray-400">
                          Last: {formatDate(recurring.updated_at)}
                        </div>
                      </div>
                      <div className="flex space-x-2">
                        <Link
                          href={`/transactions/create?template=${recurring.id}`}
                          className="text-blue-600 hover:text-blue-900 dark:text-blue-400 dark:hover:text-blue-300 text-sm font-medium"
                        >
                          Use Template
                        </Link>
                        <button
                          onClick={() => handleDelete(recurring.id)}
                          className="text-red-600 hover:text-red-900 dark:text-red-400 dark:hover:text-red-300 text-sm font-medium"
                        >
                          Delete
                        </button>
                      </div>
                    </div>
                  </div>
                  {recurring.description && (
                    <div className="mt-2 text-sm text-gray-600 dark:text-gray-400">
                      {recurring.description}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Help Text */}
      <div className="mt-6 p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-md">
        <div className="flex">
          <div className="flex-shrink-0">
            <svg
              className="h-5 w-5 text-blue-400"
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 20 20"
              fill="currentColor"
            >
              <path
                fillRule="evenodd"
                d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z"
                clipRule="evenodd"
              />
            </svg>
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-blue-800 dark:text-blue-200">About Recurring Transactions</h3>
            <div className="mt-2 text-sm text-blue-700 dark:text-blue-300">
              <ul className="list-disc list-inside space-y-1">
                <li>Recurring transactions are automatically created based on their frequency schedule</li>
                <li>Use &quot;Dry Run&quot; to preview what transactions would be created without actually creating them</li>
                <li>&quot;Process Due&quot; creates actual transactions for all overdue recurring items</li>
                <li>Inactive recurring transactions won&apos;t generate new transactions</li>
                <li>You can use existing recurring transactions as templates for new transactions</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}