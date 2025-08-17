'use client';

import React, { useState, useEffect } from 'react';
import { Gift, GiftFilters, GiftSortBy, GiftViewMode } from '../../types/Gift';
import { GiftItem } from './GiftItem';
import { GiftFilters as GiftFiltersComponent } from './GiftFilters';
import giftsService from '../../services/gifts';

interface GiftListProps {
  gifts?: Gift[];
  onGiftEdit?: (gift: Gift) => void;
  onGiftDelete?: (giftId: number) => void;
  onGiftStatusChange?: (giftId: number, status: Gift['status']) => void;
  onRefresh?: () => void;
  loading?: boolean;
  className?: string;
  showFilters?: boolean;
  showViewModeToggle?: boolean;
  initialViewMode?: GiftViewMode;
}

export const GiftList: React.FC<GiftListProps> = ({
  gifts: propGifts,
  onGiftEdit,
  onGiftDelete,
  onGiftStatusChange,
  onRefresh,
  loading = false,
  className = '',
  showFilters = true,
  showViewModeToggle = true,
  initialViewMode = 'list'
}) => {
  const [gifts, setGifts] = useState<Gift[]>(propGifts || []);
  const [filteredGifts, setFilteredGifts] = useState<Gift[]>([]);
  const [filters, setFilters] = useState<GiftFilters>({});
  const [sortBy, setSortBy] = useState<GiftSortBy>({ field: 'created_at', direction: 'desc' });
  const [viewMode, setViewMode] = useState<GiftViewMode>(initialViewMode);
  const [searchQuery, setSearchQuery] = useState('');

  // Update gifts when prop changes
  useEffect(() => {
    if (propGifts) {
      setGifts(propGifts);
    }
  }, [propGifts]);

  // Apply filters and sorting
  useEffect(() => {
    let filtered = [...gifts];

    // Apply search filter
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(gift =>
        gift.title.toLowerCase().includes(query) ||
        gift.description?.toLowerCase().includes(query) ||
        gift.recipient_name?.toLowerCase().includes(query) ||
        gift.category?.toLowerCase().includes(query) ||
        gift.occasion?.toLowerCase().includes(query) ||
        gift.notes?.toLowerCase().includes(query)
      );
    }

    // Apply status filter
    if (filters.status && filters.status.length > 0) {
      filtered = filtered.filter(gift => filters.status!.includes(gift.status));
    }

    // Apply category filter
    if (filters.category && filters.category.length > 0) {
      filtered = filtered.filter(gift => gift.category && filters.category!.includes(gift.category));
    }

    // Apply occasion filter
    if (filters.occasion && filters.occasion.length > 0) {
      filtered = filtered.filter(gift => gift.occasion && filters.occasion!.includes(gift.occasion));
    }

    // Apply recipient filter
    if (filters.recipient_contact_id && filters.recipient_contact_id.length > 0) {
      filtered = filtered.filter(gift => 
        gift.recipient_contact_id && filters.recipient_contact_id!.includes(gift.recipient_contact_id)
      );
    }

    // Apply budget filters
    if (filters.min_budget !== undefined) {
      filtered = filtered.filter(gift => 
        gift.budget_amount !== undefined && gift.budget_amount >= filters.min_budget!
      );
    }
    if (filters.max_budget !== undefined) {
      filtered = filtered.filter(gift => 
        gift.budget_amount !== undefined && gift.budget_amount <= filters.max_budget!
      );
    }

    // Apply surprise filter
    if (filters.is_surprise !== undefined) {
      filtered = filtered.filter(gift => gift.is_surprise === filters.is_surprise);
    }

    // Apply sorting
    filtered.sort((a, b) => {
      let aValue: any, bValue: any;

      switch (sortBy.field) {
        case 'title':
          aValue = a.title.toLowerCase();
          bValue = b.title.toLowerCase();
          break;
        case 'occasion_date':
          aValue = a.occasion_date ? new Date(a.occasion_date).getTime() : 0;
          bValue = b.occasion_date ? new Date(b.occasion_date).getTime() : 0;
          break;
        case 'budget_amount':
          aValue = a.budget_amount || 0;
          bValue = b.budget_amount || 0;
          break;
        case 'created_at':
          aValue = new Date(a.created_at).getTime();
          bValue = new Date(b.created_at).getTime();
          break;
        case 'status':
          aValue = a.status;
          bValue = b.status;
          break;
        case 'priority':
          aValue = a.priority;
          bValue = b.priority;
          break;
        default:
          aValue = a.created_at;
          bValue = b.created_at;
      }

      if (aValue < bValue) return sortBy.direction === 'asc' ? -1 : 1;
      if (aValue > bValue) return sortBy.direction === 'asc' ? 1 : -1;
      return 0;
    });

    setFilteredGifts(filtered);
  }, [gifts, filters, sortBy, searchQuery]);

  const handleFilterChange = (newFilters: GiftFilters) => {
    setFilters(newFilters);
  };

  const handleSortChange = (field: GiftSortBy['field']) => {
    setSortBy(prev => ({
      field,
      direction: prev.field === field && prev.direction === 'asc' ? 'desc' : 'asc'
    }));
  };

  const getSortIcon = (field: GiftSortBy['field']) => {
    if (sortBy.field !== field) {
      return (
        <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16V4m0 0L3 8m4-4l4 4m6 0v12m0 0l4-4m-4 4l-4-4" />
        </svg>
      );
    }
    
    return sortBy.direction === 'asc' ? (
      <svg className="w-4 h-4 text-indigo-600 dark:text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
      </svg>
    ) : (
      <svg className="w-4 h-4 text-indigo-600 dark:text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
      </svg>
    );
  };

  const getViewModeIcon = (mode: GiftViewMode) => {
    switch (mode) {
      case 'list':
        return (
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 10h16M4 14h16M4 18h16" />
          </svg>
        );
      case 'grid':
        return (
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
          </svg>
        );
      case 'timeline':
        return (
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        );
    }
  };

  if (loading) {
    return (
      <div className={`${className}`}>
        <div className="animate-pulse space-y-4">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="h-48 bg-gray-200 dark:bg-gray-700 rounded-lg"></div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className={`${className}`}>
      {/* Header */}
      <div className="mb-6">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          {/* Search and Refresh */}
          <div className="flex items-center space-x-4 flex-1">
            <div className="relative flex-1 max-w-md">
              <input
                type="text"
                placeholder="Search gifts..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:text-white"
              />
              <svg
                className="absolute left-3 top-2.5 h-4 w-4 text-gray-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
            
            {onRefresh && (
              <button
                onClick={onRefresh}
                className="p-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                title="Refresh"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
              </button>
            )}
          </div>

          {/* View Mode Toggle */}
          {showViewModeToggle && (
            <div className="flex items-center space-x-1 bg-gray-100 dark:bg-gray-700 rounded-md p-1">
              {(['list', 'grid', 'timeline'] as GiftViewMode[]).map((mode) => (
                <button
                  key={mode}
                  onClick={() => setViewMode(mode)}
                  className={`p-2 rounded text-sm font-medium transition-colors ${
                    viewMode === mode
                      ? 'bg-white dark:bg-gray-600 text-gray-900 dark:text-white shadow-sm'
                      : 'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300'
                  }`}
                  title={`${mode.charAt(0).toUpperCase() + mode.slice(1)} view`}
                >
                  {getViewModeIcon(mode)}
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Sort Options */}
        <div className="mt-4 flex flex-wrap items-center gap-2">
          <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Sort by:</span>
          {[
            { field: 'created_at' as const, label: 'Created' },
            { field: 'title' as const, label: 'Title' },
            { field: 'occasion_date' as const, label: 'Occasion Date' },
            { field: 'budget_amount' as const, label: 'Budget' },
            { field: 'status' as const, label: 'Status' },
            { field: 'priority' as const, label: 'Priority' },
          ].map(({ field, label }) => (
            <button
              key={field}
              onClick={() => handleSortChange(field)}
              className={`flex items-center space-x-1 px-3 py-1 rounded-md text-sm font-medium transition-colors ${
                sortBy.field === field
                  ? 'bg-indigo-100 text-indigo-800 dark:bg-indigo-900/20 dark:text-indigo-400'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200 dark:bg-gray-700 dark:text-gray-300 dark:hover:bg-gray-600'
              }`}
            >
              <span>{label}</span>
              {getSortIcon(field)}
            </button>
          ))}
        </div>
      </div>

      {/* Filters */}
      {showFilters && (
        <GiftFiltersComponent
          filters={filters}
          onFiltersChange={handleFilterChange}
          className="mb-6"
        />
      )}

      {/* Results Summary */}
      <div className="mb-4">
        <p className="text-sm text-gray-600 dark:text-gray-400">
          Showing {filteredGifts.length} of {gifts.length} gifts
          {searchQuery && (
            <span> for "{searchQuery}"</span>
          )}
        </p>
      </div>

      {/* Gift List/Grid */}
      {filteredGifts.length === 0 ? (
        <div className="text-center py-12">
          <svg
            className="mx-auto h-12 w-12 text-gray-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
          </svg>
          <h3 className="mt-4 text-sm font-medium text-gray-900 dark:text-white">No gifts found</h3>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
            {searchQuery || Object.keys(filters).length > 0
              ? 'Try adjusting your search or filters'
              : 'Get started by creating your first gift'
            }
          </p>
        </div>
      ) : (
        <div className={
          viewMode === 'grid'
            ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6'
            : 'space-y-6'
        }>
          {filteredGifts.map(gift => (
            <GiftItem
              key={gift.id}
              gift={gift}
              onEdit={onGiftEdit}
              onDelete={onGiftDelete}
              onStatusChange={onGiftStatusChange}
              className={viewMode === 'grid' ? '' : 'w-full'}
            />
          ))}
        </div>
      )}
    </div>
  );
};