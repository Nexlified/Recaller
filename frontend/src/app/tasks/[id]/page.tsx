'use client';

import React, { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { Header } from '@/components/layout/Header';
import { TaskForm } from '@/components/tasks/TaskForm';
import { TaskStatusBadge } from '@/components/tasks/TaskStatusBadge';
import { TaskPriorityBadge } from '@/components/tasks/TaskPriorityBadge';
import { DueDateIndicator } from '@/components/tasks/DueDateIndicator';
import authService from '@/services/auth';
import tasksService from '@/services/tasks';
import { Task, TaskCategory, TaskUpdate } from '@/types/Task';
import type { User } from '@/services/auth';

// Task Header Component
const TaskHeader = ({ 
  task, 
  isEditing, 
  onEdit, 
  onSave, 
  onCancel, 
  onDelete 
}: {
  task: Task;
  isEditing: boolean;
  onEdit: () => void;
  onSave: () => void;
  onCancel: () => void;
  onDelete: () => void;
}) => {
  return (
    <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6 mb-6">
      <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between">
        <div className="flex-1">
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">{task.title}</h1>
          <div className="flex items-center space-x-4 mt-3">
            <TaskStatusBadge status={task.status} />
            <TaskPriorityBadge priority={task.priority} />
            {task.due_date && <DueDateIndicator dueDate={task.due_date} />}
          </div>
        </div>
        
        <div className="flex items-center space-x-2 mt-4 sm:mt-0">
          {isEditing ? (
            <>
              <button
                onClick={onSave}
                className="inline-flex items-center px-3 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700"
              >
                Save
              </button>
              <button
                onClick={onCancel}
                className="inline-flex items-center px-3 py-2 border border-gray-300 dark:border-gray-600 text-sm font-medium rounded-md text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700"
              >
                Cancel
              </button>
            </>
          ) : (
            <>
              <button
                onClick={onEdit}
                className="inline-flex items-center px-3 py-2 border border-gray-300 dark:border-gray-600 text-sm font-medium rounded-md text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700"
              >
                <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                </svg>
                Edit
              </button>
              <button
                onClick={onDelete}
                className="inline-flex items-center px-3 py-2 border border-red-300 dark:border-red-600 text-sm font-medium rounded-md text-red-700 dark:text-red-300 bg-white dark:bg-gray-800 hover:bg-red-50 dark:hover:bg-red-900/20"
              >
                <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
                Delete
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

// Task Content Component
const TaskContent = ({ task }: { task: Task }) => {
  return (
    <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6 mb-6">
      <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">Description</h3>
      {task.description ? (
        <div className="prose dark:prose-invert max-w-none">
          <p className="text-gray-700 dark:text-gray-300 whitespace-pre-wrap">{task.description}</p>
        </div>
      ) : (
        <p className="text-gray-500 dark:text-gray-400 italic">No description provided</p>
      )}
    </div>
  );
};

// Task Contacts Component
const TaskContacts = ({ task }: { task: Task }) => {
  if (!task.contacts || task.contacts.length === 0) {
    return (
      <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6 mb-6">
        <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">Associated Contacts</h3>
        <p className="text-gray-500 dark:text-gray-400">No contacts associated with this task</p>
      </div>
    );
  }

  return (
    <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6 mb-6">
      <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">Associated Contacts</h3>
      <div className="space-y-3">
        {task.contacts.map(contact => (
          <div key={contact.id} className="flex items-center space-x-3 p-3 bg-gray-50 dark:bg-gray-700 rounded">
            <div className="w-8 h-8 bg-indigo-500 rounded-full flex items-center justify-center">
              <span className="text-xs font-medium text-white">
                {contact.first_name ? `${contact.first_name[0]}${contact.last_name?.[0] || ''}`.toUpperCase() : contact.email?.[0]?.toUpperCase() || 'C'}
              </span>
            </div>
            <div>
              <p className="font-medium text-gray-900 dark:text-white">
                {contact.first_name ? `${contact.first_name} ${contact.last_name || ''}`.trim() : contact.email}
              </p>
              {contact.first_name && contact.email && (
                <p className="text-sm text-gray-500 dark:text-gray-400">{contact.email}</p>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

// Task Categories Component
const TaskCategories = ({ task }: { task: Task }) => {
  if (!task.categories || task.categories.length === 0) {
    return (
      <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6 mb-6">
        <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">Categories</h3>
        <p className="text-gray-500 dark:text-gray-400">No categories assigned</p>
      </div>
    );
  }

  return (
    <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6 mb-6">
      <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">Categories</h3>
      <div className="flex flex-wrap gap-2">
        {task.categories.map(category => (
          <span
            key={category.id}
            className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium"
            style={{
              backgroundColor: category.color ? `${category.color}20` : '#6B728020',
              color: category.color || '#6B7280'
            }}
          >
            <span
              className="w-2 h-2 rounded-full mr-2"
              style={{ backgroundColor: category.color || '#6B7280' }}
            ></span>
            {category.name}
          </span>
        ))}
      </div>
    </div>
  );
};

// Task History Component
const TaskHistory = ({ task }: { task: Task }) => {
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  return (
    <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
      <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">Task Information</h3>
      <div className="space-y-3 text-sm">
        <div className="flex justify-between">
          <span className="text-gray-500 dark:text-gray-400">Created:</span>
          <span className="text-gray-900 dark:text-white">{formatDate(task.created_at)}</span>
        </div>
        {task.start_date && (
          <div className="flex justify-between">
            <span className="text-gray-500 dark:text-gray-400">Start Date:</span>
            <span className="text-gray-900 dark:text-white">{new Date(task.start_date).toLocaleDateString()}</span>
          </div>
        )}
        {task.due_date && (
          <div className="flex justify-between">
            <span className="text-gray-500 dark:text-gray-400">Due Date:</span>
            <span className="text-gray-900 dark:text-white">{new Date(task.due_date).toLocaleDateString()}</span>
          </div>
        )}
        <div className="flex justify-between">
          <span className="text-gray-500 dark:text-gray-400">Status:</span>
          <TaskStatusBadge status={task.status} />
        </div>
        <div className="flex justify-between">
          <span className="text-gray-500 dark:text-gray-400">Priority:</span>
          <TaskPriorityBadge priority={task.priority} />
        </div>
        {task.is_recurring && (
          <div className="flex justify-between">
            <span className="text-gray-500 dark:text-gray-400">Recurring:</span>
            <span className="text-green-600 dark:text-green-400">Yes</span>
          </div>
        )}
      </div>
    </div>
  );
};

export default function TaskDetailPage() {
  const params = useParams();
  const router = useRouter();
  const taskId = parseInt(params.id as string);
  
  const [user, setUser] = useState<User | null>(null);
  const [task, setTask] = useState<Task | null>(null);
  const [categories, setCategories] = useState<TaskCategory[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isEditing, setIsEditing] = useState(false);

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

  const handleEdit = () => {
    setIsEditing(true);
  };

  const handleSave = async (taskData: TaskUpdate) => {
    if (!task) return;
    
    try {
      setError(null);
      
      const updatedTask = await tasksService.updateTask(task.id, taskData);
      setTask(updatedTask);
      setIsEditing(false);
    } catch (err) {
      console.error('Error updating task:', err);
      setError('Failed to update task');
    }
  };

  const handleCancel = () => {
    setIsEditing(false);
  };

  const handleDelete = async () => {
    if (!task) return;
    
    if (!confirm('Are you sure you want to delete this task? This action cannot be undone.')) {
      return;
    }
    
    try {
      await tasksService.deleteTask(task.id);
      router.push('/tasks');
    } catch (err) {
      console.error('Error deleting task:', err);
      setError('Failed to delete task');
    }
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
        <Header user={user} title="Task Details" onLogout={handleLogout} />
        <main className="max-w-4xl mx-auto py-6 sm:px-6 lg:px-8">
          <div className="px-4 py-6 sm:px-0">
            <div className="animate-pulse space-y-6">
              <div className="h-32 bg-gray-200 dark:bg-gray-700 rounded-lg"></div>
              <div className="h-48 bg-gray-200 dark:bg-gray-700 rounded-lg"></div>
              <div className="h-24 bg-gray-200 dark:bg-gray-700 rounded-lg"></div>
            </div>
          </div>
        </main>
      </div>
    );
  }

  if (error || !task) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
        <Header user={user} title="Task Details" onLogout={handleLogout} />
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
      <Header user={user} title="Task Details" onLogout={handleLogout} />

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
                  <span className="ml-1 text-gray-500 dark:text-gray-400 truncate max-w-md">
                    {task.title}
                  </span>
                </div>
              </li>
            </ol>
          </nav>

          {/* Error Message */}
          {error && (
            <div className="mb-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-md">
              <p className="text-red-800 dark:text-red-200">{error}</p>
            </div>
          )}

          {/* Task Content */}
          {isEditing ? (
            <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
              <TaskForm
                task={task}
                onSubmit={handleSave}
                onCancel={handleCancel}
                categories={categories}
                contacts={[]} // Will be loaded from contacts service
              />
            </div>
          ) : (
            <>
              <TaskHeader
                task={task}
                isEditing={isEditing}
                onEdit={handleEdit}
                onSave={() => {}}
                onCancel={handleCancel}
                onDelete={handleDelete}
              />
              
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div className="lg:col-span-2 space-y-6">
                  <TaskContent task={task} />
                  <TaskContacts task={task} />
                  <TaskCategories task={task} />
                </div>
                
                <div>
                  <TaskHistory task={task} />
                </div>
              </div>
            </>
          )}
        </div>
      </main>
    </div>
  );
}