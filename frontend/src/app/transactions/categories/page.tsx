'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { CategoryManager } from '@/components/transactions/CategoryManager';
import transactionsService from '@/services/transactions';
import { 
  TransactionCategory, 
  TransactionCategoryCreate, 
  TransactionCategoryUpdate 
} from '@/types/Transaction';

export default function CategoriesPage() {
  const [categories, setCategories] = useState<TransactionCategory[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadCategories();
  }, []);

  const loadCategories = async () => {
    try {
      setLoading(true);
      const categoriesData = await transactionsService.getTransactionCategories();
      setCategories(categoriesData);
    } catch (err) {
      console.error('Error loading categories:', err);
      setError('Failed to load categories');
    } finally {
      setLoading(false);
    }
  };

  const handleCategoryCreate = async (categoryData: TransactionCategoryCreate) => {
    try {
      setError(null);
      const newCategory = await transactionsService.createTransactionCategory(categoryData);
      setCategories(prev => [...prev, newCategory]);
    } catch (err) {
      console.error('Error creating category:', err);
      setError('Failed to create category');
      throw err; // Re-throw to be handled by the form component
    }
  };

  const handleCategoryUpdate = async (category: TransactionCategory) => {
    try {
      setError(null);
      const updatedCategory = await transactionsService.updateTransactionCategory(category.id, category);
      setCategories(prev => prev.map(cat => cat.id === category.id ? updatedCategory : cat));
    } catch (err) {
      console.error('Error updating category:', err);
      setError('Failed to update category');
      throw err; // Re-throw to be handled by the form component
    }
  };

  const handleCategoryDelete = async (categoryId: number) => {
    try {
      setError(null);
      await transactionsService.deleteTransactionCategory(categoryId);
      setCategories(prev => prev.filter(cat => cat.id !== categoryId));
    } catch (err) {
      console.error('Error deleting category:', err);
      setError('Failed to delete category');
      throw err; // Re-throw to be handled by the form component
    }
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
              <span className="ml-1 text-gray-500 dark:text-gray-400">Categories</span>
            </div>
          </li>
        </ol>
      </nav>

      {/* Page Header */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Transaction Categories</h1>
        <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
          Organize your transactions with custom categories
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

      {/* Category Manager */}
      <div className="bg-white dark:bg-gray-800 shadow rounded-lg">
        {loading ? (
          <div className="p-6">
            <div className="animate-pulse">
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <div className="h-6 bg-gray-200 dark:bg-gray-700 rounded w-1/3"></div>
                  <div className="h-8 bg-gray-200 dark:bg-gray-700 rounded w-24"></div>
                </div>
                {[...Array(3)].map((_, i) => (
                  <div key={i} className="flex items-center justify-between py-4 border-b border-gray-200 dark:border-gray-700">
                    <div className="flex items-center space-x-3">
                      <div className="w-4 h-4 bg-gray-200 dark:bg-gray-700 rounded-full"></div>
                      <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-32"></div>
                      <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-16"></div>
                    </div>
                    <div className="flex space-x-2">
                      <div className="h-6 bg-gray-200 dark:bg-gray-700 rounded w-12"></div>
                      <div className="h-6 bg-gray-200 dark:bg-gray-700 rounded w-12"></div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        ) : (
          <div className="p-6">
            <CategoryManager
              categories={categories}
              onCategoryCreate={handleCategoryCreate}
              onCategoryUpdate={handleCategoryUpdate}
              onCategoryDelete={handleCategoryDelete}
              loading={loading}
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
            <h3 className="text-sm font-medium text-blue-800 dark:text-blue-200">About Transaction Categories</h3>
            <div className="mt-2 text-sm text-blue-700 dark:text-blue-300">
              <ul className="list-disc list-inside space-y-1">
                <li>Categories help organize and analyze your spending patterns</li>
                <li>Use different colors and icons to make categories easily recognizable</li>
                <li>Choose between &quot;Income&quot;, &quot;Expense&quot;, or &quot;Transfer&quot; types</li>
                <li>Popular categories include: Food & Dining, Transportation, Shopping, Utilities, Entertainment</li>
                <li>You can edit or delete categories that aren&apos;t being used by any transactions</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}