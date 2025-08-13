'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { Header } from '@/components/layout/Header';
import { CategoryManager } from '@/components/tasks/CategoryManager';
import authService from '@/services/auth';
import tasksService from '@/services/tasks';
import { Task, TaskCategory, TaskCategoryCreate, TaskCategoryUpdate } from '@/types/Task';
import type { User } from '@/services/auth';

// Category Usage Stats Component
const CategoryUsageStats = ({ 
  categories, 
  tasks 
}: { 
  categories: TaskCategory[];
  tasks: Task[]; // Use proper Task type
}) => {
  const getCategoryStats = (categoryId: number) => {
    const categoryTasks = tasks.filter(task => 
      task.categories?.some((cat: TaskCategory) => cat.id === categoryId)
    );
    const completedTasks = categoryTasks.filter(task => task.status === 'completed');
    return {
      total: categoryTasks.length,
      completed: completedTasks.length,
      pending: categoryTasks.length - completedTasks.length
    };
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
      <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">Category Usage</h3>
      <div className="space-y-4">
        {categories.length === 0 ? (
          <p className="text-gray-500 dark:text-gray-400">No categories created yet</p>
        ) : (
          categories.map(category => {
            const stats = getCategoryStats(category.id);
            const completionRate = stats.total > 0 ? (stats.completed / stats.total * 100).toFixed(1) : '0';
            
            return (
              <div key={category.id} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded">
                <div className="flex items-center space-x-3">
                  <div 
                    className="w-4 h-4 rounded-full"
                    style={{ backgroundColor: category.color || '#6B7280' }}
                  ></div>
                  <div>
                    <h4 className="font-medium text-gray-900 dark:text-white">{category.name}</h4>
                    {category.description && (
                      <p className="text-sm text-gray-500 dark:text-gray-400">{category.description}</p>
                    )}
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-sm text-gray-600 dark:text-gray-400">
                    {stats.total} task{stats.total !== 1 ? 's' : ''}
                  </div>
                  <div className="text-xs text-gray-500 dark:text-gray-500">
                    {completionRate}% complete
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};

// Category Form Component
const CategoryForm = ({ 
  category,
  onSubmit, 
  onCancel,
  isSubmitting = false 
}: { 
  category?: TaskCategory;
  onSubmit: (data: TaskCategoryCreate | TaskCategoryUpdate) => void;
  onCancel: () => void;
  isSubmitting?: boolean;
}) => {
  const [formData, setFormData] = useState<TaskCategoryCreate>({
    name: category?.name || '',
    color: category?.color || '#6366F1',
    description: category?.description || ''
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (formData.name.trim()) {
      if (category) {
        // For update, we can pass partial data
        onSubmit(formData as TaskCategoryUpdate);
      } else {
        // For create, we need full data
        onSubmit(formData);
      }
    }
  };

  const handleInputChange = (field: keyof TaskCategoryCreate, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const colorOptions = [
    '#6366F1', '#8B5CF6', '#EC4899', '#EF4444', '#F59E0B',
    '#10B981', '#06B6D4', '#84CC16', '#F97316', '#6B7280'
  ];

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
      <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
        {category ? 'Edit Category' : 'New Category'}
      </h3>
      
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="name" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
            Name
          </label>
          <input
            type="text"
            id="name"
            value={formData.name}
            onChange={(e) => handleInputChange('name', e.target.value)}
            className="mt-1 block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:text-white"
            placeholder="Category name"
            required
          />
        </div>

        <div>
          <label htmlFor="description" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
            Description (optional)
          </label>
          <textarea
            id="description"
            value={formData.description}
            onChange={(e) => handleInputChange('description', e.target.value)}
            rows={3}
            className="mt-1 block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:text-white"
            placeholder="What type of tasks belong in this category?"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Color
          </label>
          <div className="flex flex-wrap gap-2">
            {colorOptions.map(color => (
              <button
                key={color}
                type="button"
                onClick={() => handleInputChange('color', color)}
                className={`w-8 h-8 rounded-full border-2 ${
                  formData.color === color ? 'border-gray-900 dark:border-white' : 'border-gray-300 dark:border-gray-600'
                }`}
                style={{ backgroundColor: color }}
              />
            ))}
          </div>
          <input
            type="color"
            value={formData.color}
            onChange={(e) => handleInputChange('color', e.target.value)}
            className="mt-2 w-16 h-8 border border-gray-300 dark:border-gray-600 rounded cursor-pointer"
          />
        </div>

        <div className="flex justify-end space-x-3 pt-4">
          <button
            type="button"
            onClick={onCancel}
            className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm hover:bg-gray-50 dark:hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={isSubmitting || !formData.name.trim()}
            className="px-4 py-2 text-sm font-medium text-white bg-indigo-600 border border-transparent rounded-md shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isSubmitting ? 'Saving...' : (category ? 'Update' : 'Create')}
          </button>
        </div>
      </form>
    </div>
  );
};

export default function CategoriesPage() {
  const [user, setUser] = useState<User | null>(null);
  const [categories, setCategories] = useState<TaskCategory[]>([]);
  const [tasks, setTasks] = useState<Task[]>([]); // Use proper Task type
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [editingCategory, setEditingCategory] = useState<TaskCategory | null>(null);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    const currentUser = authService.getCurrentUser();
    if (!currentUser) {
      window.location.href = '/login';
      return;
    }
    setUser(currentUser);
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const [categoriesData, tasksData] = await Promise.all([
        tasksService.getCategories(),
        tasksService.getTasks(0, 1000) // Get all tasks for stats
      ]);
      
      setCategories(categoriesData);
      setTasks(tasksData);
    } catch (err) {
      console.error('Error loading data:', err);
      setError('Failed to load categories');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    await authService.logout();
    setUser(null);
    window.location.href = '/login';
  };

  const handleCategoryCreate = async (categoryData: TaskCategoryCreate) => {
    try {
      setSubmitting(true);
      setError(null);
      
      const newCategory = await tasksService.createTaskCategory(categoryData);
      setCategories(prev => [...prev, newCategory]);
      setShowForm(false);
    } catch (err) {
      console.error('Error creating category:', err);
      setError('Failed to create category');
    } finally {
      setSubmitting(false);
    }
  };

  const handleCategoryUpdate = async (categoryData: TaskCategoryUpdate) => {
    if (!editingCategory) return;
    
    try {
      setSubmitting(true);
      setError(null);
      
      const updatedCategory = await tasksService.updateTaskCategory(editingCategory.id, categoryData);
      setCategories(prev => prev.map(cat => cat.id === updatedCategory.id ? updatedCategory : cat));
      setEditingCategory(null);
      setShowForm(false);
    } catch (err) {
      console.error('Error updating category:', err);
      setError('Failed to update category');
    } finally {
      setSubmitting(false);
    }
  };

  const handleCategoryDelete = async (categoryId: number) => {
    if (!confirm('Are you sure you want to delete this category? This action cannot be undone.')) {
      return;
    }
    
    try {
      await tasksService.deleteTaskCategory(categoryId);
      setCategories(prev => prev.filter(cat => cat.id !== categoryId));
    } catch (err) {
      console.error('Error deleting category:', err);
      setError('Failed to delete category');
    }
  };

  const handleCategoryUpdateForManager = async (updatedCategory: TaskCategory) => {
    try {
      setSubmitting(true);
      setError(null);
      
      const categoryUpdate: TaskCategoryUpdate = {
        name: updatedCategory.name,
        color: updatedCategory.color,
        description: updatedCategory.description
      };
      
      const updated = await tasksService.updateTaskCategory(updatedCategory.id, categoryUpdate);
      setCategories(prev => prev.map(cat => cat.id === updated.id ? updated : cat));
    } catch (err) {
      console.error('Error updating category:', err);
      setError('Failed to update category');
    } finally {
      setSubmitting(false);
    }
  };

  const handleFormSubmit = async (data: TaskCategoryCreate | TaskCategoryUpdate) => {
    if (editingCategory) {
      await handleCategoryUpdate(data as TaskCategoryUpdate);
    } else {
      await handleCategoryCreate(data as TaskCategoryCreate);
    }
  };

  const handleCancelForm = () => {
    setShowForm(false);
    setEditingCategory(null);
  };

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
        <div className="text-lg text-gray-600 dark:text-gray-400">Redirecting to login...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <Header user={user} title="Task Categories" onLogout={handleLogout} />

      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          {/* Breadcrumb Navigation */}
          <nav className="flex mb-6" aria-label="Breadcrumb">
            <ol className="inline-flex items-center space-x-1 md:space-x-3">
              <li className="inline-flex items-center">
                <Link
                  href="/tasks"
                  className="text-gray-700 hover:text-gray-900 dark:text-gray-300 dark:hover:text-white"
                >
                  Tasks
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
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-6">
            <div>
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Task Categories</h1>
              <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
                Organize your tasks with custom categories
              </p>
            </div>
            
            <div className="mt-4 sm:mt-0">
              <button
                onClick={() => setShowForm(true)}
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
              >
                <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                </svg>
                New Category
              </button>
            </div>
          </div>

          {/* Error Message */}
          {error && (
            <div className="mb-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-md">
              <p className="text-red-800 dark:text-red-200">{error}</p>
            </div>
          )}

          {loading ? (
            <div className="animate-pulse">
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="h-64 bg-gray-200 dark:bg-gray-700 rounded-lg"></div>
                <div className="h-64 bg-gray-200 dark:bg-gray-700 rounded-lg"></div>
              </div>
            </div>
          ) : (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Left Column - Category Management */}
              <div className="space-y-6">
                {showForm && (
                  <CategoryForm
                    category={editingCategory || undefined}
                    onSubmit={handleFormSubmit}
                    onCancel={handleCancelForm}
                    isSubmitting={submitting}
                  />
                )}

                <CategoryManager
                  categories={categories}
                  onCategoryCreate={handleCategoryCreate}
                  onCategoryUpdate={handleCategoryUpdateForManager}
                  onCategoryDelete={handleCategoryDelete}
                />
              </div>

              {/* Right Column - Usage Stats */}
              <div>
                <CategoryUsageStats categories={categories} tasks={tasks} />
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}