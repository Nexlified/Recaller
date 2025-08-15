'use client';

import React, { useState, useEffect } from 'react';
import { useRouter, useParams } from 'next/navigation';
import Link from 'next/link';
import { TransactionForm } from '@/components/transactions/TransactionForm';
import transactionsService from '@/services/transactions';
import { 
  Transaction,
  TransactionWithDetails,
  TransactionCreate, 
  TransactionUpdate, 
  TransactionCategory, 
  FinancialAccount,
  RecurringTransaction
} from '@/types/Transaction';

export default function TransactionDetailPage() {
  const router = useRouter();
  const params = useParams();
  const transactionId = parseInt(params.id as string);

  const [transaction, setTransaction] = useState<TransactionWithDetails | null>(null);
  const [categories, setCategories] = useState<TransactionCategory[]>([]);
  const [accounts, setAccounts] = useState<FinancialAccount[]>([]);
  const [recurringTemplates, setRecurringTemplates] = useState<RecurringTransaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isEditing, setIsEditing] = useState(false);

  useEffect(() => {
    if (transactionId) {
      loadData();
    }
  }, [transactionId]);

  const loadData = async () => {
    try {
      setLoading(true);
      const [transactionData, categoriesData, accountsData, recurringData] = await Promise.all([
        transactionsService.getTransaction(transactionId),
        transactionsService.getTransactionCategories(),
        transactionsService.getFinancialAccounts(),
        transactionsService.getRecurringTransactions()
      ]);
      setTransaction(transactionData);
      setCategories(categoriesData);
      setAccounts(accountsData);
      setRecurringTemplates(recurringData);
    } catch (err) {
      console.error('Error loading transaction data:', err);
      setError('Failed to load transaction data');
    } finally {
      setLoading(false);
    }
  };

  const handleTransactionUpdate = async (transactionData: TransactionCreate | TransactionUpdate) => {
    try {
      setError(null);
      
      const updatedTransaction = await transactionsService.updateTransaction(
        transactionId,
        transactionData as TransactionUpdate
      );
      
      // Reload the transaction data to get the latest version
      await loadData();
      setIsEditing(false);
    } catch (err) {
      console.error('Error updating transaction:', err);
      setError('Failed to update transaction. Please try again.');
      throw err; // Re-throw to be handled by the form component
    }
  };

  const handleDelete = async () => {
    if (!window.confirm('Are you sure you want to delete this transaction? This action cannot be undone.')) {
      return;
    }

    try {
      await transactionsService.deleteTransaction(transactionId);
      router.push('/transactions');
    } catch (err) {
      console.error('Error deleting transaction:', err);
      setError('Failed to delete transaction');
    }
  };

  const handleCancel = () => {
    setIsEditing(false);
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

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  const formatDateTime = (dateString: string) => {
    return new Date(dateString).toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  if (loading) {
    return (
      <div className="px-4 py-6 sm:px-0">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 dark:bg-gray-700 rounded w-1/4 mb-6"></div>
          <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
            <div className="space-y-4">
              <div className="h-6 bg-gray-200 dark:bg-gray-700 rounded w-1/2"></div>
              <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-3/4"></div>
              <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-1/2"></div>
              <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-2/3"></div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!transaction) {
    return (
      <div className="px-4 py-6 sm:px-0">
        <div className="text-center py-12">
          <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 48 48">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5l7-7 7 7M9 5l7-7 7 7M9 35l7-7 7 7" />
          </svg>
          <h3 className="mt-2 text-sm font-medium text-gray-900 dark:text-gray-100">Transaction not found</h3>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
            The transaction you&apos;re looking for doesn&apos;t exist or you don&apos;t have permission to view it.
          </p>
          <div className="mt-6">
            <Link
              href="/transactions"
              className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              Back to Transactions
            </Link>
          </div>
        </div>
      </div>
    );
  }

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
              <span className="ml-1 text-gray-500 dark:text-gray-400">
                Transaction #{transaction.id}
              </span>
            </div>
          </li>
        </ol>
      </nav>

      {/* Page Header */}
      <div className="flex justify-between items-start mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
            Transaction #{transaction.id}
          </h1>
          <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
            {isEditing ? 'Edit transaction details' : 'View transaction details'}
          </p>
        </div>
        {!isEditing && (
          <div className="flex space-x-3">
            <button
              onClick={() => setIsEditing(true)}
              className="inline-flex items-center px-4 py-2 border border-gray-300 dark:border-gray-600 text-sm font-medium rounded-md text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              Edit
            </button>
            <button
              onClick={handleDelete}
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
            >
              Delete
            </button>
          </div>
        )}
      </div>

      {/* Error Message */}
      {error && (
        <div className="mb-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-md">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg
                className="h-5 w-5 text-red-400"
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 20 20"
                fill="currentColor"
              >
                <path
                  fillRule="evenodd"
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                  clipRule="evenodd"
                />
              </svg>
            </div>
            <div className="ml-3">
              <p className="text-sm text-red-800 dark:text-red-200">{error}</p>
            </div>
          </div>
        </div>
      )}

      {/* Transaction Content */}
      <div className="bg-white dark:bg-gray-800 shadow rounded-lg">
        {isEditing ? (
          <div className="p-6">
            <TransactionForm
              transaction={transaction}
              onSubmit={handleTransactionUpdate}
              onCancel={handleCancel}
              categories={categories}
              accounts={accounts}
              recurringTemplates={recurringTemplates}
            />
          </div>
        ) : (
          <div className="p-6">
            {/* Transaction Overview */}
            <div className="border-b border-gray-200 dark:border-gray-700 pb-6 mb-6">
              <div className="flex items-center justify-between">
                <div>
                  <div className="flex items-center space-x-3">
                    <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${
                      transaction.type === 'credit'
                        ? 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400'
                        : 'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400'
                    }`}>
                      {transaction.type === 'credit' ? 'Income' : 'Expense'}
                    </div>
                    {transaction.is_recurring && (
                      <div className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-400">
                        Recurring
                      </div>
                    )}
                  </div>
                  <h2 className="mt-2 text-3xl font-bold text-gray-900 dark:text-gray-100">
                    {formatCurrency(Number(transaction.amount), transaction.currency)}
                  </h2>
                  {transaction.description && (
                    <p className="mt-1 text-gray-600 dark:text-gray-400">
                      {transaction.description}
                    </p>
                  )}
                </div>
                <div className="text-right">
                  <div className="text-sm text-gray-500 dark:text-gray-400">Transaction Date</div>
                  <div className="text-lg font-medium text-gray-900 dark:text-gray-100">
                    {formatDate(transaction.transaction_date)}
                  </div>
                </div>
              </div>
            </div>

            {/* Transaction Details */}
            <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
              <div>
                <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-4">Details</h3>
                <dl className="space-y-3">
                  <div>
                    <dt className="text-sm font-medium text-gray-500 dark:text-gray-400">Category</dt>
                    <dd className="text-sm text-gray-900 dark:text-gray-100">
                      {getCategoryName(transaction.category_id)}
                    </dd>
                  </div>
                  <div>
                    <dt className="text-sm font-medium text-gray-500 dark:text-gray-400">Account</dt>
                    <dd className="text-sm text-gray-900 dark:text-gray-100">
                      {getAccountName(transaction.account_id)}
                    </dd>
                  </div>
                  {transaction.reference_number && (
                    <div>
                      <dt className="text-sm font-medium text-gray-500 dark:text-gray-400">Reference Number</dt>
                      <dd className="text-sm text-gray-900 dark:text-gray-100">
                        {transaction.reference_number}
                      </dd>
                    </div>
                  )}
                  <div>
                    <dt className="text-sm font-medium text-gray-500 dark:text-gray-400">Currency</dt>
                    <dd className="text-sm text-gray-900 dark:text-gray-100">
                      {transaction.currency}
                    </dd>
                  </div>
                </dl>
              </div>

              <div>
                <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-4">Metadata</h3>
                <dl className="space-y-3">
                  <div>
                    <dt className="text-sm font-medium text-gray-500 dark:text-gray-400">Created</dt>
                    <dd className="text-sm text-gray-900 dark:text-gray-100">
                      {formatDateTime(transaction.created_at)}
                    </dd>
                  </div>
                  <div>
                    <dt className="text-sm font-medium text-gray-500 dark:text-gray-400">Updated</dt>
                    <dd className="text-sm text-gray-900 dark:text-gray-100">
                      {formatDateTime(transaction.updated_at)}
                    </dd>
                  </div>
                  <div>
                    <dt className="text-sm font-medium text-gray-500 dark:text-gray-400">Transaction ID</dt>
                    <dd className="text-sm text-gray-900 dark:text-gray-100">
                      {transaction.id}
                    </dd>
                  </div>
                </dl>
              </div>
            </div>

            {/* Attachments and Extra Data */}
            {(transaction.attachments && Object.keys(transaction.attachments).length > 0) ||
             (transaction.extra_data && Object.keys(transaction.extra_data).length > 0) ? (
              <div className="mt-6 pt-6 border-t border-gray-200 dark:border-gray-700">
                <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-4">Additional Information</h3>
                
                {transaction.attachments && Object.keys(transaction.attachments).length > 0 && (
                  <div className="mb-4">
                    <h4 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-2">Attachments</h4>
                    <pre className="text-sm text-gray-900 dark:text-gray-100 bg-gray-50 dark:bg-gray-700 p-3 rounded-md overflow-x-auto">
                      {JSON.stringify(transaction.attachments, null, 2)}
                    </pre>
                  </div>
                )}

                {transaction.extra_data && Object.keys(transaction.extra_data).length > 0 && (
                  <div>
                    <h4 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-2">Extra Data</h4>
                    <pre className="text-sm text-gray-900 dark:text-gray-100 bg-gray-50 dark:bg-gray-700 p-3 rounded-md overflow-x-auto">
                      {JSON.stringify(transaction.extra_data, null, 2)}
                    </pre>
                  </div>
                )}
              </div>
            ) : null}
          </div>
        )}
      </div>
    </div>
  );
}