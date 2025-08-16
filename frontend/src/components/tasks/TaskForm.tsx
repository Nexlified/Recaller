'use client';

import React, { useState, useEffect } from 'react';
import { 
  Task, 
  TaskCreate, 
  TaskUpdate, 
  TaskCategory,
  TaskRecurrenceCreate,
  TASK_STATUS_OPTIONS,
  TASK_PRIORITY_OPTIONS
} from '../../types/Task';
import { Contact } from '../../services/contacts';
import { RecurrenceSettings } from './RecurrenceSettings';

interface TaskFormProps {
  task?: Task;
  onSubmit: (task: TaskCreate | TaskUpdate) => void;
  onCancel: () => void;
  contacts?: Contact[];
  categories?: TaskCategory[];
  loading?: boolean;
  className?: string;
}

interface FormErrors {
  title?: string;
  description?: string;
  start_date?: string;
  due_date?: string;
  general?: string;
}

export const TaskForm: React.FC<TaskFormProps> = ({
  task,
  onSubmit,
  onCancel,
  contacts = [],
  categories = [],
  loading = false,
  className = ''
}) => {
  const isEditing = !!task;

  const [formData, setFormData] = useState<TaskCreate>({
    title: task?.title || '',
    description: task?.description || '',
    status: task?.status || 'pending',
    priority: task?.priority || 'medium',
    start_date: task?.start_date ? formatDateForInput(task.start_date) : '',
    due_date: task?.due_date ? formatDateForInput(task.due_date) : '',
    category_ids: task?.categories.map(c => c.id) || [],
    contact_ids: task?.contacts.map(c => c.id) || [],
  });

  const [recurrence, setRecurrence] = useState<TaskRecurrenceCreate | null>(
    task?.recurrence ? {
      recurrence_type: task.recurrence.recurrence_type,
      recurrence_interval: task.recurrence.recurrence_interval,
      days_of_week: task.recurrence.days_of_week,
      day_of_month: task.recurrence.day_of_month,
      end_date: task.recurrence.end_date,
      max_occurrences: task.recurrence.max_occurrences,
      lead_time_days: task.recurrence.lead_time_days,
    } : null
  );

  const [errors, setErrors] = useState<FormErrors>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    if (task) {
      setFormData({
        title: task.title,
        description: task.description,
        status: task.status,
        priority: task.priority,
        start_date: task.start_date ? formatDateForInput(task.start_date) : '',
        due_date: task.due_date ? formatDateForInput(task.due_date) : '',
        category_ids: task.categories.map(c => c.id),
        contact_ids: task.contacts.map(c => c.id),
      });
    }
  }, [task]);

  const updateFormData = <K extends keyof TaskCreate>(
    field: K,
    value: TaskCreate[K]
  ) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    
    // Clear field-specific error when user starts typing
    if (errors[field as keyof FormErrors]) {
      setErrors(prev => ({ ...prev, [field]: undefined }));
    }
  };

  const validateForm = (): boolean => {
    const newErrors: FormErrors = {};

    if (!formData.title.trim()) {
      newErrors.title = 'Title is required';
    }

    if (formData.start_date && formData.due_date) {
      const startDate = new Date(formData.start_date);
      const dueDate = new Date(formData.due_date);
      if (startDate > dueDate) {
        newErrors.due_date = 'Due date must be after start date';
      }
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
      const submitData = {
        ...formData,
        start_date: formData.start_date || undefined,
        due_date: formData.due_date || undefined,
        recurrence: recurrence || undefined,
      };

      if (isEditing) {
        // For updates, send core fields only
        const updateData: TaskUpdate = {
          title: submitData.title,
          description: submitData.description,
          status: submitData.status,
          priority: submitData.priority,
          start_date: submitData.start_date || undefined,
          due_date: submitData.due_date || undefined,
        };

        onSubmit(updateData);
      } else {
        onSubmit(submitData as TaskCreate);
      }
    } catch (error) {
      setErrors({
        general: error instanceof Error ? error.message : 'An error occurred while saving the task'
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  const toggleCategory = (categoryId: number) => {
    const currentIds = formData.category_ids || [];
    const newIds = currentIds.includes(categoryId)
      ? currentIds.filter(id => id !== categoryId)
      : [...currentIds, categoryId];
    updateFormData('category_ids', newIds);
  };

  const toggleContact = (contactId: number) => {
    const currentIds = formData.contact_ids || [];
    const newIds = currentIds.includes(contactId)
      ? currentIds.filter(id => id !== contactId)
      : [...currentIds, contactId];
    updateFormData('contact_ids', newIds);
  };

  return (
    <div className={`bg-white dark:bg-gray-800 rounded-lg shadow-lg ${className}`}>
      <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100">
          {isEditing ? 'Edit Task' : 'Create New Task'}
        </h2>
      </div>

      <form onSubmit={handleSubmit} className="p-6 space-y-6">
        {/* General Error */}
        {errors.general && (
          <div className="p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-md">
            <p className="text-sm text-red-600 dark:text-red-400">{errors.general}</p>
          </div>
        )}

        {/* Title */}
        <div>
          <label htmlFor="title" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Title *
          </label>
          <input
            type="text"
            id="title"
            value={formData.title}
            onChange={(e) => updateFormData('title', e.target.value)}
            className={`w-full px-3 py-2 border rounded-md shadow-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
              errors.title ? 'border-red-300 dark:border-red-600' : 'border-gray-300 dark:border-gray-600'
            }`}
            placeholder="Enter task title"
            disabled={loading || isSubmitting}
          />
          {errors.title && (
            <p className="mt-1 text-sm text-red-600 dark:text-red-400">{errors.title}</p>
          )}
        </div>

        {/* Description */}
        <div>
          <label htmlFor="description" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Description
          </label>
          <textarea
            id="description"
            rows={3}
            value={formData.description}
            onChange={(e) => updateFormData('description', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            placeholder="Enter task description (optional)"
            disabled={loading || isSubmitting}
          />
        </div>

        {/* Status and Priority */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label htmlFor="status" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Status
            </label>
            <select
              id="status"
              value={formData.status}
              onChange={(e) => updateFormData('status', e.target.value as TaskCreate['status'])}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              disabled={loading || isSubmitting}
            >
              {TASK_STATUS_OPTIONS.map(option => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label htmlFor="priority" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Priority
            </label>
            <select
              id="priority"
              value={formData.priority}
              onChange={(e) => updateFormData('priority', e.target.value as TaskCreate['priority'])}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              disabled={loading || isSubmitting}
            >
              {TASK_PRIORITY_OPTIONS.map(option => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Dates */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label htmlFor="start_date" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Start Date
            </label>
            <input
              type="datetime-local"
              id="start_date"
              value={formData.start_date}
              onChange={(e) => updateFormData('start_date', e.target.value)}
              className={`w-full px-3 py-2 border rounded-md shadow-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                errors.start_date ? 'border-red-300 dark:border-red-600' : 'border-gray-300 dark:border-gray-600'
              }`}
              disabled={loading || isSubmitting}
            />
            {errors.start_date && (
              <p className="mt-1 text-sm text-red-600 dark:text-red-400">{errors.start_date}</p>
            )}
          </div>

          <div>
            <label htmlFor="due_date" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Due Date
            </label>
            <input
              type="datetime-local"
              id="due_date"
              value={formData.due_date}
              onChange={(e) => updateFormData('due_date', e.target.value)}
              className={`w-full px-3 py-2 border rounded-md shadow-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                errors.due_date ? 'border-red-300 dark:border-red-600' : 'border-gray-300 dark:border-gray-600'
              }`}
              disabled={loading || isSubmitting}
            />
            {errors.due_date && (
              <p className="mt-1 text-sm text-red-600 dark:text-red-400">{errors.due_date}</p>
            )}
          </div>
        </div>

        {/* Categories */}
        {categories.length > 0 && (
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Categories
            </label>
            <div className="flex flex-wrap gap-2">
              {categories.map(category => (
                <button
                  key={category.id}
                  type="button"
                  onClick={() => toggleCategory(category.id)}
                  className={`inline-flex items-center px-3 py-1 rounded text-sm font-medium transition-colors ${
                    formData.category_ids?.includes(category.id)
                      ? 'bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-400'
                      : 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                  }`}
                  disabled={loading || isSubmitting}
                >
                  {category.color && (
                    <span
                      className="w-3 h-3 rounded-full mr-2"
                      style={{ backgroundColor: category.color }}
                      aria-hidden="true"
                    />
                  )}
                  {category.name}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Contacts */}
        {contacts.length > 0 && (
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Related Contacts
            </label>
            <div className="flex flex-wrap gap-2">
              {contacts.map(contact => (
                <button
                  key={contact.id}
                  type="button"
                  onClick={() => toggleContact(contact.id)}
                  className={`inline-flex items-center px-3 py-1 rounded text-sm font-medium transition-colors ${
                    formData.contact_ids?.includes(contact.id)
                      ? 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400'
                      : 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                  }`}
                  disabled={loading || isSubmitting}
                >
                  👤 {contact.first_name} {contact.last_name}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Recurrence Settings */}
        {!isEditing && (
          <RecurrenceSettings
            recurrence={undefined}
            onChange={setRecurrence}
          />
        )}

        {/* Actions */}
        <div className="flex items-center justify-end space-x-3 pt-4 border-t border-gray-200 dark:border-gray-700">
          <button
            type="button"
            onClick={onCancel}
            className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm hover:bg-gray-50 dark:hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            disabled={loading || isSubmitting}
          >
            Cancel
          </button>
          <button
            type="submit"
            className="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
            disabled={loading || isSubmitting}
          >
            {isSubmitting ? 'Saving...' : isEditing ? 'Update Task' : 'Create Task'}
          </button>
        </div>
      </form>
    </div>
  );
};

function formatDateForInput(dateString: string): string {
  const date = new Date(dateString);
  // Format as YYYY-MM-DDTHH:MM for datetime-local input
  return date.toISOString().slice(0, 16);
}