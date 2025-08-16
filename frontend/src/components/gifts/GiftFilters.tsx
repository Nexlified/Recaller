'use client';

import React, { useState, useEffect } from 'react';
import { GiftFilters as GiftFiltersType, GIFT_STATUS_OPTIONS, GIFT_CATEGORIES, GIFT_OCCASIONS } from '../../types/Gift';
import { Contact } from '../../services/contacts';

interface GiftFiltersProps {
  filters: GiftFiltersType;
  onFiltersChange: (filters: GiftFiltersType) => void;
  contacts?: Contact[];
  className?: string;
  collapsible?: boolean;
}

export const GiftFilters: React.FC<GiftFiltersProps> = ({
  filters,
  onFiltersChange,
  contacts = [],
  className = '',
  collapsible = true
}) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [localFilters, setLocalFilters] = useState<GiftFiltersType>(filters);

  // Update local filters when external filters change
  useEffect(() => {
    setLocalFilters(filters);
  }, [filters]);

  // Check if any filters are active
  const hasActiveFilters = Object.values(filters).some(value => {
    if (Array.isArray(value)) return value.length > 0;
    return value !== undefined && value !== '';
  });

  const updateFilter = <K extends keyof GiftFiltersType>(
    key: K,
    value: GiftFiltersType[K]
  ) => {
    const newFilters = { ...localFilters, [key]: value };
    setLocalFilters(newFilters);
    onFiltersChange(newFilters);
  };

  const clearFilters = () => {
    const emptyFilters: GiftFiltersType = {};
    setLocalFilters(emptyFilters);
    onFiltersChange(emptyFilters);
  };

  const toggleArrayFilter = <K extends keyof GiftFiltersType>(
    key: K,
    value: string,
    currentArray: string[] = []
  ) => {
    const newArray = currentArray.includes(value)
      ? currentArray.filter(item => item !== value)
      : [...currentArray, value];
    updateFilter(key, newArray.length > 0 ? newArray as GiftFiltersType[K] : undefined);
  };

  const filterContent = (
    <div className="space-y-6">
      {/* Status Filters */}
      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
          Status
        </label>
        <div className="flex flex-wrap gap-2">
          {GIFT_STATUS_OPTIONS.map(option => (
            <button
              key={option.value}
              onClick={() => toggleArrayFilter('status', option.value, localFilters.status)}
              className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                localFilters.status?.includes(option.value)
                  ? 'bg-indigo-100 text-indigo-800 border-indigo-200 dark:bg-indigo-900/20 dark:text-indigo-400 dark:border-indigo-800'
                  : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50 dark:bg-gray-700 dark:text-gray-300 dark:border-gray-600 dark:hover:bg-gray-600'
              } border`}
            >
              {option.label}
            </button>
          ))}
        </div>
      </div>

      {/* Category Filters */}
      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
          Category
        </label>
        <div className="flex flex-wrap gap-2">
          {GIFT_CATEGORIES.slice(0, 8).map(category => (
            <button
              key={category}
              onClick={() => toggleArrayFilter('category', category, localFilters.category)}
              className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                localFilters.category?.includes(category)
                  ? 'bg-green-100 text-green-800 border-green-200 dark:bg-green-900/20 dark:text-green-400 dark:border-green-800'
                  : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50 dark:bg-gray-700 dark:text-gray-300 dark:border-gray-600 dark:hover:bg-gray-600'
              } border`}
            >
              {category}
            </button>
          ))}
        </div>
        {GIFT_CATEGORIES.length > 8 && (
          <details className="mt-2">
            <summary className="cursor-pointer text-sm text-indigo-600 dark:text-indigo-400 hover:text-indigo-800 dark:hover:text-indigo-300">
              Show more categories
            </summary>
            <div className="flex flex-wrap gap-2 mt-2">
              {GIFT_CATEGORIES.slice(8).map(category => (
                <button
                  key={category}
                  onClick={() => toggleArrayFilter('category', category, localFilters.category)}
                  className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                    localFilters.category?.includes(category)
                      ? 'bg-green-100 text-green-800 border-green-200 dark:bg-green-900/20 dark:text-green-400 dark:border-green-800'
                      : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50 dark:bg-gray-700 dark:text-gray-300 dark:border-gray-600 dark:hover:bg-gray-600'
                  } border`}
                >
                  {category}
                </button>
              ))}
            </div>
          </details>
        )}
      </div>

      {/* Occasion Filters */}
      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
          Occasion
        </label>
        <div className="flex flex-wrap gap-2">
          {GIFT_OCCASIONS.slice(0, 6).map(occasion => (
            <button
              key={occasion}
              onClick={() => toggleArrayFilter('occasion', occasion, localFilters.occasion)}
              className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                localFilters.occasion?.includes(occasion)
                  ? 'bg-purple-100 text-purple-800 border-purple-200 dark:bg-purple-900/20 dark:text-purple-400 dark:border-purple-800'
                  : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50 dark:bg-gray-700 dark:text-gray-300 dark:border-gray-600 dark:hover:bg-gray-600'
              } border`}
            >
              {occasion}
            </button>
          ))}
        </div>
      </div>

      {/* Budget Range */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label htmlFor="min_budget" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Min Budget
          </label>
          <input
            type="number"
            id="min_budget"
            min="0"
            step="0.01"
            value={localFilters.min_budget || ''}
            onChange={(e) => updateFilter('min_budget', e.target.value ? parseFloat(e.target.value) : undefined)}
            placeholder="0.00"
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:text-white"
          />
        </div>
        <div>
          <label htmlFor="max_budget" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Max Budget
          </label>
          <input
            type="number"
            id="max_budget"
            min="0"
            step="0.01"
            value={localFilters.max_budget || ''}
            onChange={(e) => updateFilter('max_budget', e.target.value ? parseFloat(e.target.value) : undefined)}
            placeholder="1000.00"
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:text-white"
          />
        </div>
      </div>

      {/* Recipients (if contacts are provided) */}
      {contacts.length > 0 && (
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
            Recipients
          </label>
          <div className="max-h-32 overflow-y-auto space-y-2">
            {contacts.slice(0, 10).map(contact => (
              <label key={contact.id} className="flex items-center">
                <input
                  type="checkbox"
                  checked={localFilters.recipient_contact_id?.includes(contact.id) || false}
                  onChange={(e) => {
                    const currentIds = localFilters.recipient_contact_id || [];
                    const newIds = e.target.checked
                      ? [...currentIds, contact.id]
                      : currentIds.filter(id => id !== contact.id);
                    updateFilter('recipient_contact_id', newIds.length > 0 ? newIds : undefined);
                  }}
                  className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 dark:border-gray-600 rounded dark:bg-gray-700"
                />
                <span className="ml-2 text-sm text-gray-700 dark:text-gray-300">
                  {contact.first_name} {contact.last_name}
                </span>
              </label>
            ))}
          </div>
        </div>
      )}

      {/* Currency Filter */}
      <div>
        <label htmlFor="currency" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Currency
        </label>
        <select
          id="currency"
          value={localFilters.currency || ''}
          onChange={(e) => updateFilter('currency', e.target.value || undefined)}
          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:text-white"
        >
          <option value="">All currencies</option>
          <option value="USD">USD</option>
          <option value="EUR">EUR</option>
          <option value="GBP">GBP</option>
          <option value="CAD">CAD</option>
          <option value="AUD">AUD</option>
        </select>
      </div>

      {/* Surprise Filter */}
      <div>
        <label className="flex items-center">
          <input
            type="checkbox"
            checked={localFilters.is_surprise === true}
            onChange={(e) => updateFilter('is_surprise', e.target.checked ? true : undefined)}
            className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 dark:border-gray-600 rounded dark:bg-gray-700"
          />
          <span className="ml-2 text-sm text-gray-700 dark:text-gray-300">
            Surprise gifts only
          </span>
        </label>
      </div>

      {/* Clear Filters */}
      {hasActiveFilters && (
        <div className="pt-4 border-t border-gray-200 dark:border-gray-700">
          <button
            onClick={clearFilters}
            className="text-sm text-indigo-600 dark:text-indigo-400 hover:text-indigo-800 dark:hover:text-indigo-300 font-medium"
          >
            Clear all filters
          </button>
        </div>
      )}
    </div>
  );

  if (!collapsible) {
    return (
      <div className={`bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-6 ${className}`}>
        <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">Filters</h3>
        {filterContent}
      </div>
    );
  }

  return (
    <div className={`bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg ${className}`}>
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full px-6 py-4 text-left flex items-center justify-between hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
      >
        <div className="flex items-center space-x-3">
          <h3 className="text-lg font-medium text-gray-900 dark:text-white">Filters</h3>
          {hasActiveFilters && (
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-indigo-100 text-indigo-800 dark:bg-indigo-900/20 dark:text-indigo-400">
              {Object.values(filters).reduce((count, value) => {
                if (Array.isArray(value)) return count + value.length;
                return value !== undefined ? count + 1 : count;
              }, 0)} active
            </span>
          )}
        </div>
        <svg
          className={`w-5 h-5 text-gray-500 transition-transform ${isExpanded ? 'transform rotate-180' : ''}`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>
      
      {isExpanded && (
        <div className="px-6 pb-6">
          {filterContent}
        </div>
      )}
    </div>
  );
};