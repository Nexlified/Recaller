'use client';

import React from 'react';
import { 
  TaskFilters, 
  TaskCategory,
  TaskStatus,
  TaskPriority,
  TASK_STATUS_OPTIONS,
  TASK_PRIORITY_OPTIONS
} from '../../types/Task';
import { Contact } from '../../services/contacts';

interface TaskFiltersProps {
  filters: TaskFilters;
  onFiltersChange: (filters: TaskFilters) => void;
  categories: TaskCategory[];
  contacts: Contact[];
  className?: string;
}

export const TaskFiltersComponent: React.FC<TaskFiltersProps> = ({
  filters,
  onFiltersChange,
  categories,
  contacts,
  className = ''
}) => {
  const updateFilter = <K extends keyof TaskFilters>(
    key: K,
    value: TaskFilters[K]
  ) => {
    onFiltersChange({
      ...filters,
      [key]: value
    });
  };

  const toggleStatusFilter = (status: string) => {
    const currentStatus = filters.status || [];
    const newStatus = currentStatus.includes(status as TaskStatus)
      ? currentStatus.filter(s => s !== status)
      : [...currentStatus, status as TaskStatus];
    updateFilter('status', newStatus.length > 0 ? newStatus : undefined);
  };

  const togglePriorityFilter = (priority: string) => {
    const currentPriority = filters.priority || [];
    const newPriority = currentPriority.includes(priority as TaskPriority)
      ? currentPriority.filter(p => p !== priority)
      : [...currentPriority, priority as TaskPriority];
    updateFilter('priority', newPriority.length > 0 ? newPriority : undefined);
  };

  const toggleCategoryFilter = (categoryId: number) => {
    const currentCategoryIds = filters.category_ids || [];
    const newCategoryIds = currentCategoryIds.includes(categoryId)
      ? currentCategoryIds.filter(id => id !== categoryId)
      : [...currentCategoryIds, categoryId];
    
    updateFilter('category_ids', newCategoryIds.length > 0 ? newCategoryIds : undefined);
  };

  const toggleContactFilter = (contactId: number) => {
    const currentContactIds = filters.contact_ids || [];
    const newContactIds = currentContactIds.includes(contactId)
      ? currentContactIds.filter(id => id !== contactId)
      : [...currentContactIds, contactId];
    
    updateFilter('contact_ids', newContactIds.length > 0 ? newContactIds : undefined);
  };

  const clearFilters = () => {
    onFiltersChange({});
  };

  const hasActiveFilters = Object.keys(filters).length > 0;

  return (
    <div className={`bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-4 ${className}`}>
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100">
          Filters
        </h3>
        {hasActiveFilters && (
          <button
            onClick={clearFilters}
            className="text-sm text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-200"
          >
            Clear all
          </button>
        )}
      </div>

      <div className="space-y-4">
        {/* Status Filter */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Status
          </label>
          <div className="flex flex-wrap gap-2">
            <button
              onClick={() => updateFilter('status', undefined)}
              className={`px-3 py-1 rounded text-sm font-medium transition-colors ${
                !filters.status || filters.status.length === 0
                  ? 'bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-400'
                  : 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
              }`}
            >
              All
            </button>
            {TASK_STATUS_OPTIONS.map(option => (
              <button
                key={option.value}
                onClick={() => toggleStatusFilter(option.value)}
                className={`px-3 py-1 rounded text-sm font-medium transition-colors ${
                  filters.status?.includes(option.value)
                    ? 'bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-400'
                    : 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                }`}
              >
                {option.label}
              </button>
            ))}
          </div>
        </div>

        {/* Priority Filter */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Priority
          </label>
          <div className="flex flex-wrap gap-2">
            <button
              onClick={() => updateFilter('priority', undefined)}
              className={`px-3 py-1 rounded text-sm font-medium transition-colors ${
                !filters.priority || filters.priority.length === 0
                  ? 'bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-400'
                  : 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
              }`}
            >
              All
            </button>
            {TASK_PRIORITY_OPTIONS.map(option => (
              <button
                key={option.value}
                onClick={() => togglePriorityFilter(option.value)}
                className={`px-3 py-1 rounded text-sm font-medium transition-colors ${
                  filters.priority?.includes(option.value)
                    ? 'bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-400'
                    : 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                }`}
              >
                {option.label}
              </button>
            ))}
          </div>
        </div>

        {/* Date Range Filters */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Due Date Range
          </label>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
            <div>
              <label className="block text-xs text-gray-500 dark:text-gray-400 mb-1">From</label>
              <input
                type="date"
                value={filters.due_date_start || ''}
                onChange={(e) => updateFilter('due_date_start', e.target.value || undefined)}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            <div>
              <label className="block text-xs text-gray-500 dark:text-gray-400 mb-1">To</label>
              <input
                type="date"
                value={filters.due_date_end || ''}
                onChange={(e) => updateFilter('due_date_end', e.target.value || undefined)}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
          </div>
        </div>

        {/* Boolean Filters */}
        <div className="space-y-2">
          <label className="flex items-center">
            <input
              type="checkbox"
              checked={filters.is_recurring === true}
              onChange={(e) => updateFilter('is_recurring', e.target.checked ? true : undefined)}
              className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 dark:border-gray-600 rounded"
            />
            <span className="ml-2 text-sm text-gray-700 dark:text-gray-300">
              Recurring tasks only
            </span>
          </label>
          <label className="flex items-center">
            <input
              type="checkbox"
              checked={filters.is_overdue === true}
              onChange={(e) => updateFilter('is_overdue', e.target.checked ? true : undefined)}
              className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 dark:border-gray-600 rounded"
            />
            <span className="ml-2 text-sm text-gray-700 dark:text-gray-300">
              Overdue tasks only
            </span>
          </label>
        </div>

        {/* Categories Filter */}
        {categories.length > 0 && (
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Categories
            </label>
            <div className="space-y-1 max-h-32 overflow-y-auto">
              {categories.map(category => (
                <label key={category.id} className="flex items-center">
                  <input
                    type="checkbox"
                    checked={filters.category_ids?.includes(category.id) || false}
                    onChange={() => toggleCategoryFilter(category.id)}
                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 dark:border-gray-600 rounded"
                  />
                  <span className="ml-2 text-sm text-gray-700 dark:text-gray-300 flex items-center">
                    {category.color && (
                      <span
                        className="w-3 h-3 rounded-full mr-2"
                        style={{ backgroundColor: category.color }}
                        aria-hidden="true"
                      />
                    )}
                    {category.name}
                  </span>
                </label>
              ))}
            </div>
          </div>
        )}

        {/* Contacts Filter */}
        {contacts.length > 0 && (
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Contacts
            </label>
            <div className="space-y-1 max-h-32 overflow-y-auto">
              {contacts.map(contact => (
                <label key={contact.id} className="flex items-center">
                  <input
                    type="checkbox"
                    checked={filters.contact_ids?.includes(contact.id) || false}
                    onChange={() => toggleContactFilter(contact.id)}
                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 dark:border-gray-600 rounded"
                  />
                  <span className="ml-2 text-sm text-gray-700 dark:text-gray-300">
                    {contact.first_name} {contact.last_name}
                  </span>
                </label>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Active Filters Summary */}
      {hasActiveFilters && (
        <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-600">
          <div className="text-xs text-gray-500 dark:text-gray-400">
            {Object.entries(filters).filter(([, value]) => value !== undefined).length} filter(s) active
          </div>
        </div>
      )}
    </div>
  );
};