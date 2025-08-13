'use client';

import React, { useState } from 'react';
import { TaskCategory, TaskCategoryCreate, TaskCategoryUpdate } from '../../types/Task';

interface CategoryManagerProps {
  categories: TaskCategory[];
  onCategoryCreate: (category: TaskCategoryCreate) => void;
  onCategoryUpdate: (category: TaskCategory) => void;
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
  const [editingCategory, setEditingCategory] = useState<TaskCategory | null>(null);
  const [formData, setFormData] = useState<TaskCategoryCreate>({
    name: '',
    color: '#3B82F6',
    description: '',
  });
  const [errors, setErrors] = useState<FormErrors>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  const resetForm = () => {
    setFormData({ name: '', color: '#3B82F6', description: '' });
    setErrors({});
    setEditingCategory(null);
    setShowForm(false);
  };

  const handleEdit = (category: TaskCategory) => {
    setFormData({
      name: category.name,
      color: category.color || '#3B82F6',
      description: category.description || '',
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
        // Update existing category
        const updateData: TaskCategoryUpdate = {};
        if (formData.name !== editingCategory.name) updateData.name = formData.name;
        if (formData.color !== editingCategory.color) updateData.color = formData.color;
        if (formData.description !== editingCategory.description) updateData.description = formData.description;

        const updatedCategory = { ...editingCategory, ...updateData };
        onCategoryUpdate(updatedCategory);
      } else {
        // Create new category
        onCategoryCreate(formData);
      }
      resetForm();
    } catch (error) {
      setErrors({
        general: error instanceof Error ? error.message : 'An error occurred while saving the category'
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDelete = async (category: TaskCategory) => {
    if (!window.confirm(`Are you sure you want to delete the category "${category.name}"? This action cannot be undone.`)) {
      return;
    }

    try {
      onCategoryDelete(category.id);
    } catch (error) {
      console.error('Failed to delete category:', error);
    }
  };

  const updateFormData = <K extends keyof TaskCategoryCreate>(
    field: K,
    value: TaskCategoryCreate[K]
  ) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    
    // Clear field-specific error when user starts typing
    if (errors[field as keyof FormErrors]) {
      setErrors(prev => ({ ...prev, [field]: undefined }));
    }
  };

  return (
    <div className={`bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg ${className}`}>
      <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100">
            Task Categories
          </h2>
          <button
            onClick={() => setShowForm(!showForm)}
            className="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50"
            disabled={loading}
          >
            {showForm ? 'Cancel' : 'Add Category'}
          </button>
        </div>
      </div>

      <div className="p-6">
        {/* Form */}
        {showForm && (
          <form onSubmit={handleSubmit} className="mb-6 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
            <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-4">
              {editingCategory ? 'Edit Category' : 'Create New Category'}
            </h3>

            {/* General Error */}
            {errors.general && (
              <div className="mb-4 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-md">
                <p className="text-sm text-red-600 dark:text-red-400">{errors.general}</p>
              </div>
            )}

            <div className="space-y-4">
              {/* Name and Color */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div className="sm:col-span-2">
                  <label htmlFor="category-name" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Name *
                  </label>
                  <input
                    type="text"
                    id="category-name"
                    value={formData.name}
                    onChange={(e) => updateFormData('name', e.target.value)}
                    className={`w-full px-3 py-2 border rounded-md shadow-sm bg-white dark:bg-gray-600 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                      errors.name ? 'border-red-300 dark:border-red-600' : 'border-gray-300 dark:border-gray-500'
                    }`}
                    placeholder="Enter category name"
                    disabled={loading || isSubmitting}
                  />
                  {errors.name && (
                    <p className="mt-1 text-sm text-red-600 dark:text-red-400">{errors.name}</p>
                  )}
                </div>

                <div>
                  <label htmlFor="category-color" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Color
                  </label>
                  <div className="flex items-center space-x-2">
                    <input
                      type="color"
                      id="category-color"
                      value={formData.color}
                      onChange={(e) => updateFormData('color', e.target.value)}
                      className="w-12 h-10 border border-gray-300 dark:border-gray-500 rounded cursor-pointer disabled:opacity-50"
                      disabled={loading || isSubmitting}
                    />
                    <input
                      type="text"
                      value={formData.color}
                      onChange={(e) => updateFormData('color', e.target.value)}
                      className={`flex-1 px-3 py-2 border rounded-md shadow-sm bg-white dark:bg-gray-600 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                        errors.color ? 'border-red-300 dark:border-red-600' : 'border-gray-300 dark:border-gray-500'
                      }`}
                      placeholder="#3B82F6"
                      disabled={loading || isSubmitting}
                    />
                  </div>
                  {errors.color && (
                    <p className="mt-1 text-sm text-red-600 dark:text-red-400">{errors.color}</p>
                  )}
                </div>
              </div>

              {/* Description */}
              <div>
                <label htmlFor="category-description" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Description
                </label>
                <textarea
                  id="category-description"
                  rows={2}
                  value={formData.description}
                  onChange={(e) => updateFormData('description', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-500 rounded-md shadow-sm bg-white dark:bg-gray-600 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Enter category description (optional)"
                  disabled={loading || isSubmitting}
                />
              </div>

              {/* Actions */}
              <div className="flex items-center justify-end space-x-3">
                <button
                  type="button"
                  onClick={resetForm}
                  className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-600 border border-gray-300 dark:border-gray-500 rounded-md shadow-sm hover:bg-gray-50 dark:hover:bg-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  disabled={loading || isSubmitting}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
                  disabled={loading || isSubmitting}
                >
                  {isSubmitting ? 'Saving...' : editingCategory ? 'Update Category' : 'Create Category'}
                </button>
              </div>
            </div>
          </form>
        )}

        {/* Categories List */}
        {categories.length === 0 ? (
          <div className="text-center py-8">
            <svg
              className="mx-auto h-12 w-12 text-gray-400"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              aria-hidden="true"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"
              />
            </svg>
            <h3 className="mt-2 text-sm font-medium text-gray-900 dark:text-gray-100">No categories</h3>
            <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
              Create your first category to organize your tasks.
            </p>
          </div>
        ) : (
          <div className="space-y-3">
            {categories.map(category => (
              <div
                key={category.id}
                className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors"
              >
                <div className="flex items-center space-x-3 flex-1 min-w-0">
                  <div
                    className="w-4 h-4 rounded-full flex-shrink-0"
                    style={{ backgroundColor: category.color || '#3B82F6' }}
                    aria-hidden="true"
                  />
                  <div className="flex-1 min-w-0">
                    <h4 className="text-sm font-medium text-gray-900 dark:text-gray-100 truncate">
                      {category.name}
                    </h4>
                    {category.description && (
                      <p className="text-sm text-gray-500 dark:text-gray-400 truncate">
                        {category.description}
                      </p>
                    )}
                  </div>
                </div>

                <div className="flex items-center space-x-2 flex-shrink-0">
                  <button
                    onClick={() => handleEdit(category)}
                    className="p-2 text-gray-600 hover:text-gray-800 dark:text-gray-400 dark:hover:text-gray-200"
                    aria-label={`Edit ${category.name}`}
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                    </svg>
                  </button>
                  <button
                    onClick={() => handleDelete(category)}
                    className="p-2 text-red-600 hover:text-red-800 dark:text-red-400 dark:hover:text-red-200"
                    aria-label={`Delete ${category.name}`}
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Summary */}
        {categories.length > 0 && (
          <div className="mt-6 pt-4 border-t border-gray-200 dark:border-gray-600">
            <p className="text-sm text-gray-500 dark:text-gray-400">
              {categories.length} categor{categories.length === 1 ? 'y' : 'ies'} total
            </p>
          </div>
        )}
      </div>
    </div>
  );
};