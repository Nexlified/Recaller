'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { TransactionForm } from '@/components/transactions/TransactionForm';
import transactionsService from '@/services/transactions';
import { 
  TransactionCreate, 
  TransactionUpdate, 
  TransactionCategory, 
  FinancialAccount,
  RecurringTransaction
} from '@/types/Transaction';

export default function CreateTransactionPage() {
  const router = useRouter();
  const [categories, setCategories] = useState<TransactionCategory[]>([]);
  const [accounts, setAccounts] = useState<FinancialAccount[]>([]);
  const [recurringTemplates, setRecurringTemplates] = useState<RecurringTransaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadFormData();
  }, []);

  const loadFormData = async () => {
    try {
      setLoading(true);
      const [categoriesData, accountsData, recurringData] = await Promise.all([
        transactionsService.getTransactionCategories(),
        transactionsService.getFinancialAccounts(),
        transactionsService.getRecurringTransactions()
      ]);
      setCategories(categoriesData);
      setAccounts(accountsData);
      setRecurringTemplates(recurringData);
    } catch (err) {
      console.error('Error loading form data:', err);
      setError('Failed to load form data');
    } finally {
      setLoading(false);
    }
  };

  const handleTransactionCreate = async (transactionData: TransactionCreate) => {
    try {
      setError(null);
      
      const createdTransaction = await transactionsService.createTransaction(transactionData);
      
      // Redirect to transaction detail page or back to transaction list
      router.push(`/transactions`);
    } catch (err) {
      console.error('Error creating transaction:', err);
      setError('Failed to create transaction. Please try again.');
    }
  };

  const handleTransactionSubmit = async (transactionData: TransactionCreate | TransactionUpdate) => {
    // For create page, this will always be TransactionCreate
    await handleTransactionCreate(transactionData as TransactionCreate);
  };

  const handleCancel = () => {
    router.push('/transactions');
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
              <span className="ml-1 text-gray-500 dark:text-gray-400">Create New Transaction</span>
            </div>
          </li>
        </ol>
      </nav>

      {/* Page Header */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Create New Transaction</h1>
        <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
          Add a new transaction to your financial records
        </p>
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

      {/* Transaction Creation Form */}
      <div className="bg-white dark:bg-gray-800 shadow rounded-lg">
        {loading ? (
          <div className="p-6">
            <div className="animate-pulse">
              <div className="space-y-4">
                <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-1/4"></div>
                <div className="h-10 bg-gray-200 dark:bg-gray-700 rounded"></div>
                <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-1/4"></div>
                <div className="h-10 bg-gray-200 dark:bg-gray-700 rounded"></div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="h-10 bg-gray-200 dark:bg-gray-700 rounded"></div>
                  <div className="h-10 bg-gray-200 dark:bg-gray-700 rounded"></div>
                </div>
                <div className="h-24 bg-gray-200 dark:bg-gray-700 rounded"></div>
              </div>
            </div>
          </div>
        ) : (
          <div className="p-6">
            <TransactionForm
              onSubmit={handleTransactionSubmit}
              onCancel={handleCancel}
              categories={categories}
              accounts={accounts}
              recurringTemplates={recurringTemplates}
            />
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
            <h3 className="text-sm font-medium text-blue-800 dark:text-blue-200">Tips for creating transactions</h3>
            <div className="mt-2 text-sm text-blue-700 dark:text-blue-300">
              <ul className="list-disc list-inside space-y-1">
                <li>Choose the correct transaction type: &quot;Credit&quot; for money coming in, &quot;Debit&quot; for money going out</li>
                <li>Select the appropriate category to help with budget tracking</li>
                <li>Link to a financial account to automatically update account balances</li>
                <li>Add a reference number for receipts or transaction IDs</li>
                <li>Set up recurring transactions for regular payments or income</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}