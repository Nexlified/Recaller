'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import transactionsService from '@/services/transactions';
import { 
  FinancialAccount, 
  FinancialAccountCreate, 
  FinancialAccountUpdate 
} from '@/types/Transaction';

interface AccountFormData {
  account_name: string;
  account_type: string;
  account_number: string;
  bank_name: string;
  current_balance: number;
  currency: string;
  is_active: boolean;
}

export default function AccountsPage() {
  const [accounts, setAccounts] = useState<FinancialAccount[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [editingAccount, setEditingAccount] = useState<FinancialAccount | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const [formData, setFormData] = useState<AccountFormData>({
    account_name: '',
    account_type: 'checking',
    account_number: '',
    bank_name: '',
    current_balance: 0,
    currency: 'USD',
    is_active: true,
  });

  const [formErrors, setFormErrors] = useState<Record<string, string>>({});

  const accountTypes = [
    { value: 'checking', label: 'Checking' },
    { value: 'savings', label: 'Savings' },
    { value: 'credit_card', label: 'Credit Card' },
    { value: 'investment', label: 'Investment' },
    { value: 'cash', label: 'Cash' },
    { value: 'other', label: 'Other' },
  ];

  useEffect(() => {
    loadAccounts();
  }, []);

  const loadAccounts = async () => {
    try {
      setLoading(true);
      const accountsData = await transactionsService.getFinancialAccounts();
      setAccounts(accountsData);
    } catch (err) {
      console.error('Error loading accounts:', err);
      setError('Failed to load accounts');
    } finally {
      setLoading(false);
    }
  };

  const resetForm = () => {
    setFormData({
      account_name: '',
      account_type: 'checking',
      account_number: '',
      bank_name: '',
      current_balance: 0,
      currency: 'USD',
      is_active: true,
    });
    setFormErrors({});
    setEditingAccount(null);
    setShowForm(false);
  };

  const validateForm = (): boolean => {
    const errors: Record<string, string> = {};

    if (!formData.account_name.trim()) {
      errors.account_name = 'Account name is required';
    }

    if (!formData.account_type) {
      errors.account_type = 'Account type is required';
    }

    if (!formData.currency.trim()) {
      errors.currency = 'Currency is required';
    }

    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setIsSubmitting(true);
    setError(null);

    try {
      if (editingAccount) {
        // Update existing account
        const updatedAccount = await transactionsService.updateFinancialAccount(editingAccount.id, formData);
        setAccounts(prev => prev.map(acc => acc.id === editingAccount.id ? updatedAccount : acc));
      } else {
        // Create new account
        const newAccount = await transactionsService.createFinancialAccount(formData);
        setAccounts(prev => [...prev, newAccount]);
      }
      resetForm();
    } catch (err) {
      console.error('Error saving account:', err);
      setError(editingAccount ? 'Failed to update account' : 'Failed to create account');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleEdit = (account: FinancialAccount) => {
    setFormData({
      account_name: account.account_name,
      account_type: account.account_type || 'checking',
      account_number: account.account_number || '',
      bank_name: account.bank_name || '',
      current_balance: Number(account.current_balance),
      currency: account.currency,
      is_active: account.is_active,
    });
    setEditingAccount(account);
    setShowForm(true);
  };

  const handleDelete = async (accountId: number) => {
    if (!window.confirm('Are you sure you want to delete this account? This action cannot be undone.')) {
      return;
    }

    try {
      await transactionsService.deleteFinancialAccount(accountId);
      setAccounts(prev => prev.filter(acc => acc.id !== accountId));
    } catch (err) {
      console.error('Error deleting account:', err);
      setError('Failed to delete account');
    }
  };

  const formatCurrency = (amount: number, currency: string) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency,
    }).format(amount);
  };

  const getAccountTypeIcon = (type: string) => {
    const icons: Record<string, string> = {
      checking: '🏦',
      savings: '💰',
      credit_card: '💳',
      investment: '📈',
      cash: '💵',
      other: '🏛️',
    };
    return icons[type] || '🏛️';
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
              <span className="ml-1 text-gray-500 dark:text-gray-400">Accounts</span>
            </div>
          </li>
        </ol>
      </nav>

      {/* Page Header */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Financial Accounts</h1>
          <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
            Manage your bank accounts, credit cards, and other financial accounts
          </p>
        </div>
        <button
          onClick={() => setShowForm(!showForm)}
          className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
        >
          {showForm ? 'Cancel' : 'Add Account'}
        </button>
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

      {/* Account Form */}
      {showForm && (
        <div className="mb-6 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-4">
            {editingAccount ? 'Edit Account' : 'Create New Account'}
          </h3>
          
          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Account Name */}
            <div>
              <label htmlFor="account_name" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Account Name *
              </label>
              <input
                type="text"
                id="account_name"
                value={formData.account_name}
                onChange={(e) => setFormData(prev => ({ ...prev, account_name: e.target.value }))}
                className={`w-full px-3 py-2 border rounded-md shadow-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                  formErrors.account_name ? 'border-red-300 dark:border-red-600' : 'border-gray-300 dark:border-gray-600'
                }`}
                placeholder="e.g., Chase Checking"
              />
              {formErrors.account_name && (
                <p className="mt-1 text-sm text-red-600 dark:text-red-400">{formErrors.account_name}</p>
              )}
            </div>

            {/* Account Type and Bank Name */}
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div>
                <label htmlFor="account_type" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Account Type *
                </label>
                <select
                  id="account_type"
                  value={formData.account_type}
                  onChange={(e) => setFormData(prev => ({ ...prev, account_type: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  {accountTypes.map(type => (
                    <option key={type.value} value={type.value}>{type.label}</option>
                  ))}
                </select>
              </div>

              <div>
                <label htmlFor="bank_name" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Bank/Institution Name
                </label>
                <input
                  type="text"
                  id="bank_name"
                  value={formData.bank_name}
                  onChange={(e) => setFormData(prev => ({ ...prev, bank_name: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="e.g., Chase Bank"
                />
              </div>
            </div>

            {/* Account Number and Balance */}
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div>
                <label htmlFor="account_number" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Account Number
                </label>
                <input
                  type="text"
                  id="account_number"
                  value={formData.account_number}
                  onChange={(e) => setFormData(prev => ({ ...prev, account_number: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="e.g., ****1234"
                />
              </div>

              <div>
                <label htmlFor="current_balance" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Current Balance
                </label>
                <input
                  type="number"
                  step="0.01"
                  id="current_balance"
                  value={formData.current_balance}
                  onChange={(e) => setFormData(prev => ({ ...prev, current_balance: parseFloat(e.target.value) || 0 }))}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="0.00"
                />
              </div>
            </div>

            {/* Currency and Active Status */}
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div>
                <label htmlFor="currency" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Currency *
                </label>
                <input
                  type="text"
                  id="currency"
                  value={formData.currency}
                  onChange={(e) => setFormData(prev => ({ ...prev, currency: e.target.value.toUpperCase() }))}
                  className={`w-full px-3 py-2 border rounded-md shadow-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                    formErrors.currency ? 'border-red-300 dark:border-red-600' : 'border-gray-300 dark:border-gray-600'
                  }`}
                  placeholder="USD"
                  maxLength={3}
                />
                {formErrors.currency && (
                  <p className="mt-1 text-sm text-red-600 dark:text-red-400">{formErrors.currency}</p>
                )}
              </div>

              <div className="flex items-center pt-6">
                <input
                  type="checkbox"
                  id="is_active"
                  checked={formData.is_active}
                  onChange={(e) => setFormData(prev => ({ ...prev, is_active: e.target.checked }))}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <label htmlFor="is_active" className="ml-2 block text-sm text-gray-900 dark:text-gray-100">
                  Account is active
                </label>
              </div>
            </div>

            {/* Form Actions */}
            <div className="flex justify-end space-x-4 pt-4">
              <button
                type="button"
                onClick={resetForm}
                className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-md hover:bg-gray-50 dark:hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                disabled={isSubmitting}
              >
                Cancel
              </button>
              <button
                type="submit"
                className="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
                disabled={isSubmitting}
              >
                {isSubmitting ? 'Saving...' : editingAccount ? 'Update Account' : 'Create Account'}
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Accounts List */}
      <div className="bg-white dark:bg-gray-800 shadow rounded-lg">
        {loading ? (
          <div className="p-6">
            <div className="animate-pulse space-y-4">
              {[...Array(3)].map((_, i) => (
                <div key={i} className="flex items-center justify-between py-4 border-b border-gray-200 dark:border-gray-700">
                  <div className="flex items-center space-x-4">
                    <div className="w-12 h-12 bg-gray-200 dark:bg-gray-700 rounded-lg"></div>
                    <div className="space-y-2">
                      <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-32"></div>
                      <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-24"></div>
                    </div>
                  </div>
                  <div className="flex items-center space-x-4">
                    <div className="text-right">
                      <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-20"></div>
                      <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-16 mt-1"></div>
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
        ) : accounts.length === 0 ? (
          <div className="text-center py-12">
            <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 48 48">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5a2 2 0 00-2 2v8a2 2 0 002 2h14m0-12v12m0-12a2 2 0 012-2h4a2 2 0 012 2v2a1 1 0 001 1h3a1 1 0 001-1V9a2 2 0 00-2-2h-3a1 1 0 00-1 1v1h-4z" />
            </svg>
            <h3 className="mt-2 text-sm font-medium text-gray-900 dark:text-gray-100">No accounts</h3>
            <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
              Get started by adding your first financial account.
            </p>
            <div className="mt-6">
              <button
                onClick={() => setShowForm(true)}
                className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                Add Account
              </button>
            </div>
          </div>
        ) : (
          <div className="divide-y divide-gray-200 dark:divide-gray-700">
            {accounts.map((account) => (
              <div key={account.id} className="p-6 hover:bg-gray-50 dark:hover:bg-gray-700/50">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    <div className="flex-shrink-0">
                      <div className="w-12 h-12 bg-gray-100 dark:bg-gray-700 rounded-lg flex items-center justify-center text-2xl">
                        {getAccountTypeIcon(account.account_type || 'other')}
                      </div>
                    </div>
                    <div>
                      <div className="flex items-center space-x-2">
                        <h3 className="text-sm font-medium text-gray-900 dark:text-gray-100">
                          {account.account_name}
                        </h3>
                        {!account.is_active && (
                          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300">
                            Inactive
                          </span>
                        )}
                      </div>
                      <div className="text-sm text-gray-500 dark:text-gray-400">
                        {account.bank_name && `${account.bank_name} • `}
                        {accountTypes.find(t => t.value === account.account_type)?.label || 'Unknown'}
                        {account.account_number && ` • ****${account.account_number.slice(-4)}`}
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center space-x-4">
                    <div className="text-right">
                      <div className="text-sm font-medium text-gray-900 dark:text-gray-100">
                        {formatCurrency(Number(account.current_balance), account.currency)}
                      </div>
                      <div className="text-sm text-gray-500 dark:text-gray-400">
                        Current Balance
                      </div>
                    </div>
                    <div className="flex space-x-2">
                      <button
                        onClick={() => handleEdit(account)}
                        className="text-blue-600 hover:text-blue-900 dark:text-blue-400 dark:hover:text-blue-300 text-sm font-medium"
                      >
                        Edit
                      </button>
                      <button
                        onClick={() => handleDelete(account.id)}
                        className="text-red-600 hover:text-red-900 dark:text-red-400 dark:hover:text-red-300 text-sm font-medium"
                      >
                        Delete
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            ))}
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
            <h3 className="text-sm font-medium text-blue-800 dark:text-blue-200">About Financial Accounts</h3>
            <div className="mt-2 text-sm text-blue-700 dark:text-blue-300">
              <ul className="list-disc list-inside space-y-1">
                <li>Link transactions to accounts to automatically track balances</li>
                <li>Account numbers are masked for security (only last 4 digits shown)</li>
                <li>Set accounts as inactive to hide them without deleting transaction history</li>
                <li>Current balance updates automatically when you create linked transactions</li>
                <li>Support for multiple currencies allows international account management</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}