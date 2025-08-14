'use client';

import React, { useState } from 'react';
import { 
  TransactionCategory, 
  TransactionCategoryCreate, 
  TransactionCategoryUpdate,
  TRANSACTION_CATEGORY_TYPE_OPTIONS 
} from '../../types/Transaction';

interface CategoryManagerProps {
  categories: TransactionCategory[];
  onCategoryCreate: (category: TransactionCategoryCreate) => void;
  onCategoryUpdate: (category: TransactionCategory) => void;
  onCategoryDelete: (categoryId: number) => void;
  loading?: boolean;
  className?: string;
}

interface FormErrors {
  name?: string;
  color?: string;
  general?: string;
}

export const CategoryManager: React.FC<CategoryManagerProps> = ({
  categories,
  onCategoryCreate,
  onCategoryUpdate,
  onCategoryDelete,
  loading = false,
  className = ''
}) => {
  const [showForm, setShowForm] = useState(false);
  const [editingCategory, setEditingCategory] = useState<TransactionCategory | null>(null);
  const [formData, setFormData] = useState<TransactionCategoryCreate>({
    name: '',
    type: 'expense',
    color: '#EF4444',
    icon: '',
  });
  const [errors, setErrors] = useState<FormErrors>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  const resetForm = () => {
    setFormData({ name: '', type: 'expense', color: '#EF4444', icon: '' });
    setErrors({});
    setEditingCategory(null);
    setShowForm(false);
  };

  const handleEdit = (category: TransactionCategory) => {
    setFormData({
      name: category.name,
      type: category.type,
      color: category.color || '#EF4444',
      icon: category.icon || '',
    });
    setEditingCategory(category);
    setShowForm(true);
  };

  const validateForm = (): boolean => {
    const newErrors: FormErrors = {};

    if (!formData.name.trim()) {
      newErrors.name = 'Category name is required';
    } else if (formData.name.length > 100) {
      newErrors.name = 'Category name must be 100 characters or less';
    }

    if (formData.color && !/^#[0-9A-Fa-f]{6}$/.test(formData.color)) {
      newErrors.color = 'Invalid color format';
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
      if (editingCategory) {
        const updatedCategory: TransactionCategory = {
          ...editingCategory,
          ...formData,
        };
        await onCategoryUpdate(updatedCategory);
      } else {
        await onCategoryCreate(formData);
      }
      resetForm();
    } catch (error) {
      console.error('Failed to save category:', error);
      setErrors({ general: 'Failed to save category. Please try again.' });
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDelete = async (categoryId: number, categoryName: string) => {
    if (!window.confirm(`Are you sure you want to delete "${categoryName}"? This action cannot be undone.`)) {
      return;
    }

    try {
      await onCategoryDelete(categoryId);
    } catch (error) {
      console.error('Failed to delete category:', error);
    }
  };

  const getCategoryTypeColor = (type?: string): string => {
    switch (type) {
      case 'income': return 'text-green-600 dark:text-green-400';
      case 'expense': return 'text-red-600 dark:text-red-400';
      case 'transfer': return 'text-blue-600 dark:text-blue-400';
      default: return 'text-gray-600 dark:text-gray-400';
    }
  };

  const getCategoryTypeBg = (type?: string): string => {
    switch (type) {
      case 'income': return 'bg-green-100 dark:bg-green-900/20';
      case 'expense': return 'bg-red-100 dark:bg-red-900/20';
      case 'transfer': return 'bg-blue-100 dark:bg-blue-900/20';
      default: return 'bg-gray-100 dark:bg-gray-900/20';
    }
  };

  return (
    <div className={`space-y-6 ${className}`}>
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100">
          Transaction Categories
        </h2>
        <button
          onClick={() => setShowForm(!showForm)}
          className="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
        >
          {showForm ? 'Cancel' : 'Add Category'}
        </button>
      </div>

      {/* Category Form */}
      {showForm && (
        <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-4">
            {editingCategory ? 'Edit Category' : 'Create New Category'}
          </h3>
          
          {errors.general && (
            <div className="mb-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-md p-4">
              <p className="text-sm text-red-600 dark:text-red-400">{errors.general}</p>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Category Name */}
              <div>
                <label htmlFor="name" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Category Name *
                </label>
                <input
                  type="text"
                  id="name"
                  value={formData.name}
                  onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="e.g., Groceries, Salary, Rent"
                  required
                />
                {errors.name && <p className="mt-1 text-sm text-red-600 dark:text-red-400">{errors.name}</p>}
              </div>

              {/* Category Type */}
              <div>
                <label htmlFor="type" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Category Type
                </label>
                <select
                  id="type"
                  value={formData.type || ''}
                  onChange={(e) => setFormData(prev => ({ ...prev, type: (e.target.value || undefined) as 'income' | 'expense' | 'transfer' | undefined }))}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="">Select type</option>
                  {TRANSACTION_CATEGORY_TYPE_OPTIONS.map((option) => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              </div>

              {/* Color */}
              <div>
                <label htmlFor="color" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Color
                </label>
                <div className="flex items-center space-x-2">
                  <input
                    type="color"
                    id="color"
                    value={formData.color || '#EF4444'}
                    onChange={(e) => setFormData(prev => ({ ...prev, color: e.target.value }))}
                    className="h-10 w-16 border border-gray-300 dark:border-gray-600 rounded-md"
                  />
                  <input
                    type="text"
                    value={formData.color || '#EF4444'}
                    onChange={(e) => setFormData(prev => ({ ...prev, color: e.target.value }))}
                    className="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    placeholder="#RRGGBB"
                  />
                </div>
                {errors.color && <p className="mt-1 text-sm text-red-600 dark:text-red-400">{errors.color}</p>}
              </div>

              {/* Icon */}
              <div>
                <label htmlFor="icon" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Icon (Optional)
                </label>
                <input
                  type="text"
                  id="icon"
                  value={formData.icon || ''}
                  onChange={(e) => setFormData(prev => ({ ...prev, icon: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="🛒 💰 🏠 or text"
                />
              </div>
            </div>

            <div className="flex items-center justify-end space-x-3">
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
                disabled={isSubmitting || loading}
              >
                {isSubmitting ? 'Saving...' : editingCategory ? 'Update' : 'Create'}
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Categories List */}
      <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg">
        {categories.length === 0 ? (
          <div className="p-6 text-center">
            <div className="text-4xl mb-2">📁</div>
            <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">
              No categories yet
            </h3>
            <p className="text-gray-500 dark:text-gray-400">
              Create your first transaction category to get started.
            </p>
          </div>
        ) : (
          <div className="divide-y divide-gray-200 dark:divide-gray-700">
            {categories.map((category) => (
              <div key={category.id} className="p-4 hover:bg-gray-50 dark:hover:bg-gray-700/50">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div
                      className="w-4 h-4 rounded-full"
                      style={{ backgroundColor: category.color || '#EF4444' }}
                    />
                    <div>
                      <div className="flex items-center space-x-2">
                        {category.icon && (
                          <span className="text-lg">{category.icon}</span>
                        )}
                        <h3 className="text-sm font-medium text-gray-900 dark:text-gray-100">
                          {category.name}
                        </h3>
                        {category.type && (
                          <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getCategoryTypeBg(category.type)} ${getCategoryTypeColor(category.type)}`}>
                            {category.type}
                          </span>
                        )}
                        {category.is_system && (
                          <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 dark:bg-gray-900/20 text-gray-600 dark:text-gray-400">
                            System
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                  
                  {!category.is_system && (
                    <div className="flex items-center space-x-2">
                      <button
                        onClick={() => handleEdit(category)}
                        className="p-1 text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300"
                        aria-label="Edit category"
                      >
                        ✏️
                      </button>
                      <button
                        onClick={() => handleDelete(category.id, category.name)}
                        className="p-1 text-red-600 hover:text-red-800 dark:text-red-400 dark:hover:text-red-300"
                        aria-label="Delete category"
                      >
                        🗑️
                      </button>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};