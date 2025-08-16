'use client';

import React, { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { Header } from '@/components/layout/Header';
import { TaskForm, TaskFormData } from '@/components/tasks/TaskForm';
import authService from '@/services/auth';
import tasksService from '@/services/tasks';
import { Task, TaskCategory, TaskUpdate } from '@/types/Task';
import type { User } from '@/services/auth';

export default function EditTaskPage() {
  const params = useParams();
  const router = useRouter();
  const taskId = parseInt(params.id as string);
  
  const [user, setUser] = useState<User | null>(null);
  const [task, setTask] = useState<Task | null>(null);
  const [categories, setCategories] = useState<TaskCategory[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const currentUser = authService.getCurrentUser();
    if (!currentUser) {
      router.push('/login');
      return;
    }
    setUser(currentUser);
    
    if (taskId) {
      loadTaskData();
    }
    
    async function loadTaskData() {
      try {
        setLoading(true);
        setError(null);
        
        const [taskData, categoriesData] = await Promise.all([
          tasksService.getTask(taskId),
          tasksService.getCategories()
        ]);
        
        setTask(taskData);
        setCategories(categoriesData);
      } catch (err) {
        console.error('Error loading task:', err);
        setError('Failed to load task details');
      } finally {
        setLoading(false);
      }
    }
  }, [taskId, router]);

  const handleLogout = async () => {
    await authService.logout();
    setUser(null);
    router.push('/login');
  };

  const handleTaskUpdate = async (data: TaskFormData) => {
    if (!task) return;
    
    try {
      setError(null);
      
      // Update the core task fields
      const updatedTask = await tasksService.updateTask(task.id, data.core as TaskUpdate);
      
      // Handle category associations if they changed
      if (data.associations) {
        const currentCategoryIds = task.categories.map(c => c.id);
        const newCategoryIds = data.associations.category_ids;
        
        // Remove categories that are no longer selected
        const categoriesToRemove = currentCategoryIds.filter(id => !newCategoryIds.includes(id));
        for (const categoryId of categoriesToRemove) {
          await tasksService.removeCategoryFromTask(task.id, categoryId);
        }
        
        // Add new categories
        const categoriesToAdd = newCategoryIds.filter(id => !currentCategoryIds.includes(id));
        for (const categoryId of categoriesToAdd) {
          await tasksService.assignCategoryToTask(task.id, { category_id: categoryId });
        }
        
        // Handle contact associations if they changed
        const currentContactIds = task.contacts.map(c => c.id);
        const newContactIds = data.associations.contact_ids;
        
        // Remove contacts that are no longer selected
        const contactsToRemove = currentContactIds.filter(id => !newContactIds.includes(id));
        for (const contactId of contactsToRemove) {
          await tasksService.removeContactFromTask(task.id, contactId);
        }
        
        // Add new contacts
        const contactsToAdd = newContactIds.filter(id => !currentContactIds.includes(id));
        for (const contactId of contactsToAdd) {
          await tasksService.addContactToTask(task.id, contactId);
        }
      }
      
      // Redirect to task detail page after successful update
      router.push(`/tasks/${updatedTask.id}`);
    } catch (err) {
      console.error('Error updating task:', err);
      setError('Failed to update task. Please try again.');
    }
  };

  const handleCancel = () => {
    router.push(`/tasks/${taskId}`);
  };

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
        <div className="text-lg text-gray-600 dark:text-gray-400">Redirecting to login...</div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
        <Header user={user} title="Edit Task" onLogout={handleLogout} />
        <main className="max-w-4xl mx-auto py-6 sm:px-6 lg:px-8">
          <div className="px-4 py-6 sm:px-0">
            <div className="animate-pulse space-y-6">
              <div className="h-8 bg-gray-200 dark:bg-gray-700 rounded w-1/4"></div>
              <div className="h-64 bg-gray-200 dark:bg-gray-700 rounded-lg"></div>
            </div>
          </div>
        </main>
      </div>
    );
  }

  if (error || !task) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
        <Header user={user} title="Edit Task" onLogout={handleLogout} />
        <main className="max-w-4xl mx-auto py-6 sm:px-6 lg:px-8">
          <div className="px-4 py-6 sm:px-0">
            <div className="text-center py-12">
              <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <h3 className="mt-2 text-sm font-medium text-gray-900 dark:text-white">Task not found</h3>
              <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">{error || 'The task you are looking for does not exist.'}</p>
              <div className="mt-6">
                <Link
                  href="/tasks"
                  className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700"
                >
                  Back to Tasks
                </Link>
              </div>
            </div>
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <Header user={user} title="Edit Task" onLogout={handleLogout} />

      <main className="max-w-4xl mx-auto py-6 sm:px-6 lg:px-8">
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
                  <Link
                    href={`/tasks/${task.id}`}
                    className="ml-1 text-gray-700 hover:text-gray-900 dark:text-gray-300 dark:hover:text-white truncate max-w-md"
                  >
                    {task.title}
                  </Link>
                </div>
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
                  <span className="ml-1 text-gray-500 dark:text-gray-400">Edit</span>
                </div>
              </li>
            </ol>
          </nav>

          {/* Page Header */}
          <div className="mb-6">
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Edit Task</h1>
            <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
              Update the task details
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

          {/* Task Edit Form */}
          <div className="bg-white dark:bg-gray-800 shadow rounded-lg">
            <div className="p-6">
              <TaskForm
                task={task}
                onSubmit={handleTaskUpdate}
                onCancel={handleCancel}
                categories={categories}
                contacts={[]} // Will be loaded from contacts service
              />
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

// Metadata will be handled by the page component itself