'use client';

import React, { useState, useEffect } from 'react';
import { 
  Transaction,
  TransactionCreate, 
  TransactionUpdate, 
  TransactionCategory,
  FinancialAccount,
  RecurringTransaction,
  TRANSACTION_TYPE_OPTIONS,
  ValidationErrors
} from '../../types/Transaction';
import { Currency, currencyService } from '../../services/currencyService';
import { RecurrenceSettings } from './RecurrenceSettings';

interface TransactionFormProps {
  transaction?: Transaction;
  onSubmit: (transaction: TransactionCreate | TransactionUpdate) => void;
  onCancel: () => void;
  categories?: TransactionCategory[];
  accounts?: FinancialAccount[];
  recurringTemplates?: RecurringTransaction[];
  loading?: boolean;
  className?: string;
}

export const TransactionForm: React.FC<TransactionFormProps> = ({
  transaction,
  onSubmit,
  onCancel,
  categories = [],
  accounts = [],
  recurringTemplates = [],
  loading = false,
  className = ''
}) => {
  const isEditing = !!transaction;

  const [formData, setFormData] = useState<TransactionCreate>({
    type: transaction?.type || 'debit',
    amount: transaction?.amount || 0,
    currency: transaction?.currency || 'USD',
    description: transaction?.description || '',
    transaction_date: transaction?.transaction_date ? formatDateForInput(transaction.transaction_date) : formatDateForInput(new Date().toISOString()),
    category_id: transaction?.category_id,
    subcategory_id: transaction?.subcategory_id,
    account_id: transaction?.account_id,
    reference_number: transaction?.reference_number || '',
    is_recurring: transaction?.is_recurring || false,
    recurring_template_id: transaction?.recurring_template_id,
    attachments: transaction?.attachments || {},
    extra_data: transaction?.extra_data || {},
  });

  const [errors, setErrors] = useState<ValidationErrors>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [currencies, setCurrencies] = useState<Currency[]>([]);
  const [currenciesLoading, setCurrenciesLoading] = useState(true);
  const [defaultCurrency, setDefaultCurrency] = useState<Currency | null>(null);

  // Load currencies and default currency
  useEffect(() => {
    const loadCurrencies = async () => {
      setCurrenciesLoading(true);
      try {
        const [activeCurrencies, defaultCurr] = await Promise.all([
          currencyService.getActiveCurrencies(),
          currencyService.getDefaultCurrency()
        ]);
        
        setCurrencies(activeCurrencies);
        setDefaultCurrency(defaultCurr);
        
        // Set default currency if no transaction is being edited
        if (!transaction && defaultCurr) {
          setFormData(prev => ({ ...prev, currency: defaultCurr.code }));
        }
      } catch (error) {
        console.error('Failed to load currencies:', error);
        // Fallback to hardcoded currencies
        setCurrencies([
          {
            id: 1, code: 'USD', name: 'US Dollar', symbol: '$', 
            decimal_places: 2, is_active: true, is_default: true,
            country_codes: ['US'], created_at: '', updated_at: ''
          },
          {
            id: 2, code: 'EUR', name: 'Euro', symbol: '€', 
            decimal_places: 2, is_active: true, is_default: false,
            country_codes: ['DE', 'FR'], created_at: '', updated_at: ''
          },
          {
            id: 3, code: 'GBP', name: 'British Pound', symbol: '£', 
            decimal_places: 2, is_active: true, is_default: false,
            country_codes: ['GB'], created_at: '', updated_at: ''
          },
          {
            id: 4, code: 'JPY', name: 'Japanese Yen', symbol: '¥', 
            decimal_places: 0, is_active: true, is_default: false,
            country_codes: ['JP'], created_at: '', updated_at: ''
          }
        ]);
      } finally {
        setCurrenciesLoading(false);
      }
    };

    loadCurrencies();
  }, []);

  useEffect(() => {
    if (transaction) {
      setFormData({
        type: transaction.type,
        amount: transaction.amount,
        currency: transaction.currency,
        description: transaction.description,
        transaction_date: formatDateForInput(transaction.transaction_date),
        category_id: transaction.category_id,
        subcategory_id: transaction.subcategory_id,
        account_id: transaction.account_id,
        reference_number: transaction.reference_number,
        is_recurring: transaction.is_recurring,
        recurring_template_id: transaction.recurring_template_id,
        attachments: transaction.attachments,
        extra_data: transaction.extra_data,
      });
    }
  }, [transaction]);

  const updateFormData = <K extends keyof TransactionCreate>(
    field: K,
    value: TransactionCreate[K]
  ) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    
    // Clear field-specific error when user starts typing
    if (errors[field as keyof ValidationErrors]) {
      setErrors(prev => ({ ...prev, [field]: undefined }));
    }
  };

  const validateForm = (): boolean => {
    const newErrors: ValidationErrors = {};

    if (!formData.type) {
      newErrors.type = 'Transaction type is required';
    }

    if (!formData.amount || formData.amount <= 0) {
      newErrors.amount = 'Amount must be greater than 0';
    }

    if (!formData.currency || formData.currency.trim() === '') {
      newErrors.currency = 'Currency is required';
    }

    if (!formData.transaction_date) {
      newErrors.transaction_date = 'Transaction date is required';
    }

    // Validate date format
    if (formData.transaction_date && isNaN(new Date(formData.transaction_date).getTime())) {
      newErrors.transaction_date = 'Invalid date format';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setIsSubmitting(true);
    setErrors({});

    try {
      // Convert string inputs to appropriate types
      const submitData: TransactionCreate | TransactionUpdate = {
        ...formData,
        amount: typeof formData.amount === 'string' ? parseFloat(formData.amount) : formData.amount,
        category_id: formData.category_id || undefined,
        subcategory_id: formData.subcategory_id || undefined,
        account_id: formData.account_id || undefined,
        recurring_template_id: formData.recurring_template_id || undefined,
        reference_number: formData.reference_number || undefined,
      };

      await onSubmit(submitData);
    } catch (error) {
      console.error('Form submission error:', error);
      setErrors({ general: 'Failed to save transaction. Please try again.' });
    } finally {
      setIsSubmitting(false);
    }
  };

  function formatDateForInput(dateString: string): string {
    try {
      const date = new Date(dateString);
      return date.toISOString().split('T')[0];
    } catch {
      return '';
    }
  }

  return (
    <form onSubmit={handleSubmit} className={`space-y-6 ${className}`}>
      {errors.general && (
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-md p-4">
          <p className="text-sm text-red-600 dark:text-red-400">{errors.general}</p>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Transaction Type */}
        <div>
          <label htmlFor="type" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Transaction Type *
          </label>
          <select
            id="type"
            value={formData.type}
            onChange={(e) => updateFormData('type', e.target.value as 'credit' | 'debit')}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            required
          >
            {TRANSACTION_TYPE_OPTIONS.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
          {errors.type && <p className="mt-1 text-sm text-red-600 dark:text-red-400">{errors.type}</p>}
        </div>

        {/* Amount */}
        <div>
          <label htmlFor="amount" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Amount *
          </label>
          <input
            type="number"
            id="amount"
            step="0.01"
            min="0"
            value={formData.amount}
            onChange={(e) => updateFormData('amount', parseFloat(e.target.value) || 0)}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            placeholder="0.00"
            required
          />
          {errors.amount && <p className="mt-1 text-sm text-red-600 dark:text-red-400">{errors.amount}</p>}
        </div>

        {/* Currency */}
        <div>
          <label htmlFor="currency" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Currency *
          </label>
          <select
            id="currency"
            value={formData.currency}
            onChange={(e) => updateFormData('currency', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            required
            disabled={currenciesLoading}
          >
            {currenciesLoading ? (
              <option value="">Loading currencies...</option>
            ) : currencies.length > 0 ? (
              <>
                <option value="">Select currency</option>
                {currencies.map((currency) => (
                  <option key={currency.id} value={currency.code}>
                    {currency.code} - {currency.name} ({currency.symbol})
                  </option>
                ))}
              </>
            ) : (
              <>
                <option value="USD">USD - US Dollar ($)</option>
                <option value="EUR">EUR - Euro (€)</option>
                <option value="GBP">GBP - British Pound (£)</option>
                <option value="CAD">CAD - Canadian Dollar (C$)</option>
                <option value="AUD">AUD - Australian Dollar (A$)</option>
                <option value="JPY">JPY - Japanese Yen (¥)</option>
              </>
            )}
          </select>
          {errors.currency && <p className="mt-1 text-sm text-red-600 dark:text-red-400">{errors.currency}</p>}
        </div>

        {/* Transaction Date */}
        <div>
          <label htmlFor="transaction_date" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Transaction Date *
          </label>
          <input
            type="date"
            id="transaction_date"
            value={formData.transaction_date}
            onChange={(e) => updateFormData('transaction_date', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            required
          />
          {errors.transaction_date && <p className="mt-1 text-sm text-red-600 dark:text-red-400">{errors.transaction_date}</p>}
        </div>

        {/* Category */}
        <div>
          <label htmlFor="category_id" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Category
          </label>
          <select
            id="category_id"
            value={formData.category_id || ''}
            onChange={(e) => updateFormData('category_id', e.target.value ? parseInt(e.target.value) : undefined)}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="">Select a category</option>
            {categories.map((category) => (
              <option key={category.id} value={category.id}>
                {category.name}
              </option>
            ))}
          </select>
          {errors.category_id && <p className="mt-1 text-sm text-red-600 dark:text-red-400">{errors.category_id}</p>}
        </div>

        {/* Account */}
        <div>
          <label htmlFor="account_id" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Account
          </label>
          <select
            id="account_id"
            value={formData.account_id || ''}
            onChange={(e) => updateFormData('account_id', e.target.value ? parseInt(e.target.value) : undefined)}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="">Select an account</option>
            {accounts.map((account) => (
              <option key={account.id} value={account.id}>
                {account.account_name}
              </option>
            ))}
          </select>
          {errors.account_id && <p className="mt-1 text-sm text-red-600 dark:text-red-400">{errors.account_id}</p>}
        </div>
      </div>

      {/* Description */}
      <div>
        <label htmlFor="description" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Description
        </label>
        <textarea
          id="description"
          rows={3}
          value={formData.description || ''}
          onChange={(e) => updateFormData('description', e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          placeholder="Enter transaction description..."
        />
        {errors.description && <p className="mt-1 text-sm text-red-600 dark:text-red-400">{errors.description}</p>}
      </div>

      {/* Reference Number */}
      <div>
        <label htmlFor="reference_number" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Reference Number
        </label>
        <input
          type="text"
          id="reference_number"
          value={formData.reference_number || ''}
          onChange={(e) => updateFormData('reference_number', e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          placeholder="Optional reference number"
        />
        {errors.reference_number && <p className="mt-1 text-sm text-red-600 dark:text-red-400">{errors.reference_number}</p>}
      </div>

      {/* Recurring Transaction Checkbox */}
      <div className="flex items-center">
        <input
          type="checkbox"
          id="is_recurring"
          checked={formData.is_recurring}
          onChange={(e) => updateFormData('is_recurring', e.target.checked)}
          className="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
        />
        <label htmlFor="is_recurring" className="ml-2 text-sm text-gray-700 dark:text-gray-300">
          This is a recurring transaction
        </label>
      </div>

      {/* Recurring Template Selection */}
      {formData.is_recurring && (
        <div>
          <label htmlFor="recurring_template_id" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Recurring Template
          </label>
          <select
            id="recurring_template_id"
            value={formData.recurring_template_id || ''}
            onChange={(e) => updateFormData('recurring_template_id', e.target.value ? parseInt(e.target.value) : undefined)}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="">Select a recurring template</option>
            {recurringTemplates.map((template) => (
              <option key={template.id} value={template.id}>
                {template.template_name} ({template.frequency})
              </option>
            ))}
          </select>
        </div>
      )}

      {/* Form Actions */}
      <div className="flex items-center justify-end space-x-4 pt-6 border-t border-gray-200 dark:border-gray-700">
        <button
          type="button"
          onClick={onCancel}
          className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-md hover:bg-gray-50 dark:hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          disabled={isSubmitting}
        >
          Cancel
        </button>
        <button
          type="submit"
          className="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
          disabled={isSubmitting || loading}
        >
          {isSubmitting ? 'Saving...' : isEditing ? 'Update Transaction' : 'Create Transaction'}
        </button>
      </div>
    </form>
  );
};