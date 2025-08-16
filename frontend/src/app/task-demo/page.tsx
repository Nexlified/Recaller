'use client';

import React, { useState } from 'react';
import {
  TaskList,
  TaskForm,
  TaskFormData,
  TaskFilters,
  CategoryManager,
  TaskPriorityBadge,
  TaskStatusBadge,
  DueDateIndicator
} from '../../components/tasks';
import {
  Task,
  TaskCreate,
  TaskUpdate,
  TaskCategory,
  TaskFilters as ITaskFilters,
  TaskCategoryCreate
} from '../../types/Task';
import { Contact, ContactVisibility } from '../../services/contacts';

// Mock data for demo
const mockTasks: Task[] = [
  {
    id: 1,
    tenant_id: 1,
    user_id: 1,
    title: 'Complete project proposal',
    description: 'Write and review the Q1 project proposal document',
    status: 'in_progress',
    priority: 'high',
    start_date: '2025-01-10T09:00:00Z',
    due_date: '2025-01-15T17:00:00Z',
    is_recurring: false,
    created_at: '2025-01-08T10:00:00Z',
    updated_at: '2025-01-10T14:30:00Z',
    categories: [
      { id: 1, tenant_id: 1, user_id: 1, name: 'Work', color: '#3B82F6', created_at: '2025-01-08T10:00:00Z' }
    ],
    contacts: [
      { id: 1, tenant_id: 1, created_by_user_id: 1, first_name: 'John', last_name: 'Smith', email: 'john@example.com', visibility: ContactVisibility.PRIVATE, is_active: true, created_at: '2025-01-08T10:00:00Z' }
    ]
  },
  {
    id: 2,
    tenant_id: 1,
    user_id: 1,
    title: 'Schedule dentist appointment',
    description: '',
    status: 'pending',
    priority: 'medium',
    due_date: '2025-01-12T10:00:00Z',
    is_recurring: true,
    created_at: '2025-01-08T11:00:00Z',
    categories: [
      { id: 2, tenant_id: 1, user_id: 1, name: 'Personal', color: '#10B981', created_at: '2025-01-08T10:00:00Z' }
    ],
    contacts: [],
    recurrence: {
      id: 1,
      task_id: 2,
      recurrence_type: 'monthly',
      recurrence_interval: 6,
      lead_time_days: 7,
      created_at: '2025-01-08T11:00:00Z'
    }
  },
  {
    id: 3,
    tenant_id: 1,
    user_id: 1,
    title: 'Review quarterly budget',
    description: 'Analyze Q4 expenses and plan Q1 budget allocations',
    status: 'completed',
    priority: 'high',
    start_date: '2025-01-05T09:00:00Z',
    due_date: '2025-01-08T17:00:00Z',
    completed_at: '2025-01-08T16:30:00Z',
    is_recurring: false,
    created_at: '2025-01-05T09:00:00Z',
    updated_at: '2025-01-08T16:30:00Z',
    categories: [
      { id: 1, tenant_id: 1, user_id: 1, name: 'Work', color: '#3B82F6', created_at: '2025-01-08T10:00:00Z' },
      { id: 3, tenant_id: 1, user_id: 1, name: 'Finance', color: '#F59E0B', created_at: '2025-01-08T10:00:00Z' }
    ],
    contacts: []
  },
  {
    id: 4,
    tenant_id: 1,
    user_id: 1,
    title: 'Overdue task example',
    description: 'This task is overdue to demonstrate styling',
    status: 'pending',
    priority: 'low',
    due_date: '2025-01-05T17:00:00Z',
    is_recurring: false,
    created_at: '2025-01-01T10:00:00Z',
    categories: [],
    contacts: []
  }
];

const mockCategories: TaskCategory[] = [
  { id: 1, tenant_id: 1, user_id: 1, name: 'Work', color: '#3B82F6', created_at: '2025-01-08T10:00:00Z' },
  { id: 2, tenant_id: 1, user_id: 1, name: 'Personal', color: '#10B981', created_at: '2025-01-08T10:00:00Z' },
  { id: 3, tenant_id: 1, user_id: 1, name: 'Finance', color: '#F59E0B', created_at: '2025-01-08T10:00:00Z' },
  { id: 4, tenant_id: 1, user_id: 1, name: 'Health', color: '#EF4444', created_at: '2025-01-08T10:00:00Z' }
];

const mockContacts: Contact[] = [
  { id: 1, tenant_id: 1, created_by_user_id: 1, first_name: 'John', last_name: 'Smith', email: 'john@example.com', visibility: ContactVisibility.PRIVATE, is_active: true, created_at: '2025-01-08T10:00:00Z' },
  { id: 2, tenant_id: 1, created_by_user_id: 1, first_name: 'Jane', last_name: 'Doe', email: 'jane@example.com', visibility: ContactVisibility.PRIVATE, is_active: true, created_at: '2025-01-08T10:00:00Z' },
  { id: 3, tenant_id: 1, created_by_user_id: 1, first_name: 'Bob', last_name: 'Wilson', email: 'bob@example.com', visibility: ContactVisibility.PRIVATE, is_active: true, created_at: '2025-01-08T10:00:00Z' }
];

export default function TaskManagementDemo() {
  const [tasks, setTasks] = useState<Task[]>(mockTasks);
  const [categories, setCategories] = useState<TaskCategory[]>(mockCategories);
  const [filters, setFilters] = useState<ITaskFilters>({});
  const [showTaskForm, setShowTaskForm] = useState(false);
  const [showCategoryManager, setShowCategoryManager] = useState(false);
  const [editingTask, setEditingTask] = useState<Task | undefined>();

  // Filter tasks based on current filters
  const filteredTasks = tasks.filter(task => {
    if (filters.status && filters.status.length > 0 && !filters.status.includes(task.status)) return false;
    if (filters.priority && filters.priority.length > 0 && !filters.priority.includes(task.priority)) return false;
    if (filters.is_recurring !== undefined && task.is_recurring !== filters.is_recurring) return false;
    if (filters.is_overdue && (!task.due_date || new Date(task.due_date) >= new Date() || task.status === 'completed')) return false;
    if (filters.category_ids && filters.category_ids.length > 0) {
      const taskCategoryIds = task.categories.map(c => c.id);
      if (!filters.category_ids.some(id => taskCategoryIds.includes(id))) return false;
    }
    if (filters.contact_ids && filters.contact_ids.length > 0) {
      const taskContactIds = task.contacts.map(c => c.id);
      if (!filters.contact_ids.some(id => taskContactIds.includes(id))) return false;
    }
    return true;
  });

  const handleTaskUpdate = (updatedTask: Task) => {
    setTasks(prev => prev.map(task => task.id === updatedTask.id ? updatedTask : task));
  };

  const handleTaskDelete = (taskId: number) => {
    setTasks(prev => prev.filter(task => task.id !== taskId));
  };

  const handleTaskComplete = (taskId: number) => {
    console.log(`Task ${taskId} completed`);
  };

  const handleTaskSubmit = (data: TaskFormData) => {
    if (editingTask) {
      // Update existing task - cast to any to handle the type mismatch safely
      const updatedTask = { ...editingTask, ...data.core } as Task;
      handleTaskUpdate(updatedTask);
      setEditingTask(undefined);
    } else {
      // Create new task
      const createData = data.core as TaskCreate;
      const newTask: Task = {
        id: Math.max(...tasks.map(t => t.id)) + 1,
        tenant_id: 1,
        user_id: 1,
        title: createData.title,
        description: createData.description,
        status: createData.status || 'pending',
        priority: createData.priority || 'medium',
        start_date: createData.start_date,
        due_date: createData.due_date,
        is_recurring: !!createData.recurrence,
        created_at: new Date().toISOString(),
        categories: categories.filter(c => createData.category_ids?.includes(c.id)) || [],
        contacts: mockContacts.filter(c => createData.contact_ids?.includes(c.id)) || [],
        recurrence: createData.recurrence ? {
          id: Math.max(...tasks.map(t => t.recurrence?.id || 0)) + 1,
          task_id: Math.max(...tasks.map(t => t.id)) + 1,
          recurrence_type: createData.recurrence.recurrence_type,
          recurrence_interval: createData.recurrence.recurrence_interval || 1,
          days_of_week: createData.recurrence.days_of_week,
          day_of_month: createData.recurrence.day_of_month,
          end_date: createData.recurrence.end_date,
          max_occurrences: createData.recurrence.max_occurrences,
          lead_time_days: createData.recurrence.lead_time_days || 0,
          created_at: new Date().toISOString()
        } : undefined
      };
      setTasks(prev => [newTask, ...prev]);
    }
    setShowTaskForm(false);
  };

  const handleCategoryCreate = (categoryData: TaskCategoryCreate) => {
    const newCategory: TaskCategory = {
      id: Math.max(...categories.map(c => c.id)) + 1,
      tenant_id: 1,
      user_id: 1,
      ...categoryData,
      created_at: new Date().toISOString()
    };
    setCategories(prev => [...prev, newCategory]);
  };

  const handleCategoryUpdate = (updatedCategory: TaskCategory) => {
    setCategories(prev => prev.map(cat => cat.id === updatedCategory.id ? updatedCategory : cat));
  };

  const handleCategoryDelete = (categoryId: number) => {
    setCategories(prev => prev.filter(cat => cat.id !== categoryId));
  };

  // Remove unused function - editing tasks can be implemented later
  // const handleEditTask = (task: Task) => {
  //   setEditingTask(task);
  //   setShowTaskForm(true);
  // };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100">
            Task Management Demo
          </h1>
          <p className="mt-2 text-gray-600 dark:text-gray-400">
            Demonstrating the task management components and functionality
          </p>
        </div>

        {/* Utility Components Demo */}
        <div className="mb-8 bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700">
          <h2 className="text-xl font-semibold mb-4 text-gray-900 dark:text-gray-100">
            Utility Components
          </h2>
          <div className="space-y-4">
            <div>
              <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Priority Badges</h3>
              <div className="flex space-x-2">
                <TaskPriorityBadge priority="high" />
                <TaskPriorityBadge priority="medium" />
                <TaskPriorityBadge priority="low" />
              </div>
            </div>
            <div>
              <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Status Badges</h3>
              <div className="flex space-x-2">
                <TaskStatusBadge status="pending" />
                <TaskStatusBadge status="in_progress" />
                <TaskStatusBadge status="completed" />
                <TaskStatusBadge status="cancelled" />
              </div>
            </div>
            <div>
              <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Due Date Indicators</h3>
              <div className="flex flex-wrap gap-2">
                <DueDateIndicator dueDate="2025-01-15T17:00:00Z" />
                <DueDateIndicator dueDate="2025-01-05T17:00:00Z" />
                <DueDateIndicator dueDate={new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString()} />
                <DueDateIndicator dueDate={new Date().toISOString()} />
              </div>
            </div>
          </div>
        </div>

        {/* Actions */}
        <div className="mb-6 flex flex-wrap gap-3">
          <button
            onClick={() => setShowTaskForm(true)}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            Create Task
          </button>
          <button
            onClick={() => setShowCategoryManager(!showCategoryManager)}
            className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500"
          >
            {showCategoryManager ? 'Hide' : 'Show'} Category Manager
          </button>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Filters Sidebar */}
          <div className="lg:col-span-1">
            <TaskFilters
              filters={filters}
              onFiltersChange={setFilters}
              categories={categories}
              contacts={mockContacts}
            />
          </div>

          {/* Main Content */}
          <div className="lg:col-span-3">
            <TaskList
              tasks={filteredTasks}
              onTaskUpdate={handleTaskUpdate}
              onTaskDelete={handleTaskDelete}
              onTaskComplete={handleTaskComplete}
              emptyState={
                <div>
                  <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100">No tasks match your filters</h3>
                  <p className="text-gray-500 dark:text-gray-400">Try adjusting your filters or create a new task.</p>
                </div>
              }
            />
          </div>
        </div>

        {/* Category Manager */}
        {showCategoryManager && (
          <div className="mt-8">
            <CategoryManager
              categories={categories}
              onCategoryCreate={handleCategoryCreate}
              onCategoryUpdate={handleCategoryUpdate}
              onCategoryDelete={handleCategoryDelete}
            />
          </div>
        )}

        {/* Task Form Modal */}
        {showTaskForm && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className="bg-white dark:bg-gray-800 rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
              <TaskForm
                task={editingTask}
                onSubmit={handleTaskSubmit}
                onCancel={() => {
                  setShowTaskForm(false);
                  setEditingTask(undefined);
                }}
                contacts={mockContacts}
                categories={categories}
              />
            </div>
          </div>
        )}
      </div>
    </div>
  );
}