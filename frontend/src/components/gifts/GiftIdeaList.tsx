'use client';

import React, { useState, useEffect } from 'react';
import { GiftIdea, GiftIdeaFilters, GiftIdeaSortBy } from '../../types/Gift';
import { GiftIdeaCard } from './GiftIdeaCard';
import { Contact } from '../../services/contacts';

interface GiftIdeaListProps {
  giftIdeas?: GiftIdea[];
  onIdeaEdit?: (giftIdea: GiftIdea) => void;
  onIdeaDelete?: (ideaId: number) => void;
  onIdeaConvertToGift?: (giftIdea: GiftIdea) => void;
  onRefresh?: () => void;
  contacts?: Contact[];
  loading?: boolean;
  className?: string;
  showFilters?: boolean;
}

export const GiftIdeaList: React.FC<GiftIdeaListProps> = ({
  giftIdeas: propGiftIdeas,
  onIdeaEdit,
  onIdeaDelete,
  onIdeaConvertToGift,
  onRefresh,
  contacts = [],
  loading = false,
  className = '',
  showFilters = true
}) => {
  const [giftIdeas, setGiftIdeas] = useState<GiftIdea[]>(propGiftIdeas || []);
  const [filteredIdeas, setFilteredIdeas] = useState<GiftIdea[]>([]);
  const [filters, setFilters] = useState<GiftIdeaFilters>({});
  const [sortBy, setSortBy] = useState<GiftIdeaSortBy>({ field: 'created_at', direction: 'desc' });
  const [searchQuery, setSearchQuery] = useState('');

  // Update ideas when prop changes
  useEffect(() => {
    if (propGiftIdeas) {
      setGiftIdeas(propGiftIdeas);
    }
  }, [propGiftIdeas]);

  // Apply filters and sorting
  useEffect(() => {
    let filtered = [...giftIdeas];

    // Apply search filter
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(idea =>
        idea.title.toLowerCase().includes(query) ||
        idea.description?.toLowerCase().includes(query) ||
        idea.category?.toLowerCase().includes(query) ||
        idea.target_demographic?.toLowerCase().includes(query) ||
        idea.notes?.toLowerCase().includes(query) ||
        idea.tags.some(tag => tag.toLowerCase().includes(query)) ||
        idea.suitable_occasions.some(occasion => occasion.toLowerCase().includes(query))
      );
    }

    // Apply category filter
    if (filters.category && filters.category.length > 0) {
      filtered = filtered.filter(idea => idea.category && filters.category!.includes(idea.category));
    }

    // Apply target contact filter
    if (filters.target_contact_id && filters.target_contact_id.length > 0) {
      filtered = filtered.filter(idea => 
        idea.target_contact_id && filters.target_contact_id!.includes(idea.target_contact_id)
      );
    }

    // Apply rating filter
    if (filters.min_rating !== undefined) {
      filtered = filtered.filter(idea => (idea.rating || 0) >= filters.min_rating!);
    }

    // Apply price filters
    if (filters.min_price !== undefined) {
      filtered = filtered.filter(idea => 
        idea.price_range_min !== undefined && idea.price_range_min >= filters.min_price!
      );
    }
    if (filters.max_price !== undefined) {
      filtered = filtered.filter(idea => 
        idea.price_range_max !== undefined && idea.price_range_max <= filters.max_price!
      );
    }

    // Apply currency filter
    if (filters.currency) {
      filtered = filtered.filter(idea => idea.currency === filters.currency);
    }

    // Apply sorting
    filtered.sort((a, b) => {
      let aValue: any, bValue: any;

      switch (sortBy.field) {
        case 'title':
          aValue = a.title.toLowerCase();
          bValue = b.title.toLowerCase();
          break;
        case 'rating':
          aValue = a.rating || 0;
          bValue = b.rating || 0;
          break;
        case 'price_range_min':
          aValue = a.price_range_min || 0;
          bValue = b.price_range_min || 0;
          break;
        case 'created_at':
          aValue = new Date(a.created_at).getTime();
          bValue = new Date(b.created_at).getTime();
          break;
        case 'times_gifted':
          aValue = a.times_gifted;
          bValue = b.times_gifted;
          break;
        default:
          aValue = a.created_at;
          bValue = b.created_at;
      }

      if (aValue < bValue) return sortBy.direction === 'asc' ? -1 : 1;
      if (aValue > bValue) return sortBy.direction === 'asc' ? 1 : -1;
      return 0;
    });

    setFilteredIdeas(filtered);
  }, [giftIdeas, filters, sortBy, searchQuery]);

  const handleFilterChange = (field: keyof GiftIdeaFilters, value: any) => {
    setFilters(prev => ({ ...prev, [field]: value }));
  };

  const handleSortChange = (field: GiftIdeaSortBy['field']) => {
    setSortBy(prev => ({
      field,
      direction: prev.field === field && prev.direction === 'asc' ? 'desc' : 'asc'
    }));
  };

  const clearFilters = () => {
    setFilters({});
    setSearchQuery('');
  };

  const getSortIcon = (field: GiftIdeaSortBy['field']) => {
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

  const hasActiveFilters = Object.values(filters).some(value => {
    if (Array.isArray(value)) return value.length > 0;
    return value !== undefined && value !== '';
  }) || searchQuery.trim() !== '';

  if (loading) {
    return (
      <div className={`${className}`}>
        <div className="animate-pulse">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[...Array(6)].map((_, i) => (
              <div key={i} className="h-64 bg-gray-200 dark:bg-gray-700 rounded-lg"></div>
            ))}
          </div>
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
                placeholder="Search gift ideas..."
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
        </div>

        {/* Sort Options */}
        <div className="mt-4 flex flex-wrap items-center gap-2">
          <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Sort by:</span>
          {[
            { field: 'created_at' as const, label: 'Created' },
            { field: 'title' as const, label: 'Title' },
            { field: 'rating' as const, label: 'Rating' },
            { field: 'price_range_min' as const, label: 'Price' },
            { field: 'times_gifted' as const, label: 'Usage' },
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
        <div className="mb-6 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Rating Filter */}
            <div>
              <label htmlFor="min_rating" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Min Rating
              </label>
              <select
                id="min_rating"
                value={filters.min_rating || ''}
                onChange={(e) => handleFilterChange('min_rating', e.target.value ? parseInt(e.target.value) : undefined)}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:text-white text-sm"
              >
                <option value="">Any rating</option>
                <option value="1">1+ stars</option>
                <option value="2">2+ stars</option>
                <option value="3">3+ stars</option>
                <option value="4">4+ stars</option>
                <option value="5">5 stars</option>
              </select>
            </div>

            {/* Min Price Filter */}
            <div>
              <label htmlFor="min_price" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Min Price
              </label>
              <input
                type="number"
                id="min_price"
                min="0"
                step="0.01"
                value={filters.min_price || ''}
                onChange={(e) => handleFilterChange('min_price', e.target.value ? parseFloat(e.target.value) : undefined)}
                placeholder="0.00"
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:text-white text-sm"
              />
            </div>

            {/* Max Price Filter */}
            <div>
              <label htmlFor="max_price" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Max Price
              </label>
              <input
                type="number"
                id="max_price"
                min="0"
                step="0.01"
                value={filters.max_price || ''}
                onChange={(e) => handleFilterChange('max_price', e.target.value ? parseFloat(e.target.value) : undefined)}
                placeholder="1000.00"
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:text-white text-sm"
              />
            </div>

            {/* Target Contact Filter */}
            {contacts.length > 0 && (
              <div>
                <label htmlFor="target_contact" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Target Contact
                </label>
                <select
                  id="target_contact"
                  value={filters.target_contact_id?.[0] || ''}
                  onChange={(e) => {
                    const contactId = e.target.value ? parseInt(e.target.value) : undefined;
                    handleFilterChange('target_contact_id', contactId ? [contactId] : undefined);
                  }}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:text-white text-sm"
                >
                  <option value="">Any contact</option>
                  {contacts.map(contact => (
                    <option key={contact.id} value={contact.id}>
                      {contact.first_name} {contact.last_name}
                    </option>
                  ))}
                </select>
              </div>
            )}
          </div>

          {/* Clear Filters */}
          {hasActiveFilters && (
            <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
              <button
                onClick={clearFilters}
                className="text-sm text-indigo-600 dark:text-indigo-400 hover:text-indigo-800 dark:hover:text-indigo-300 font-medium"
              >
                Clear all filters
              </button>
            </div>
          )}
        </div>
      )}

      {/* Results Summary */}
      <div className="mb-4">
        <p className="text-sm text-gray-600 dark:text-gray-400">
          Showing {filteredIdeas.length} of {giftIdeas.length} gift ideas
          {searchQuery && (
            <span> for "{searchQuery}"</span>
          )}
        </p>
      </div>

      {/* Gift Ideas Grid */}
      {filteredIdeas.length === 0 ? (
        <div className="text-center py-12">
          <svg
            className="mx-auto h-12 w-12 text-gray-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
          </svg>
          <h3 className="mt-4 text-sm font-medium text-gray-900 dark:text-white">No gift ideas found</h3>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
            {searchQuery || hasActiveFilters
              ? 'Try adjusting your search or filters'
              : 'Get started by creating your first gift idea'
            }
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredIdeas.map(giftIdea => (
            <GiftIdeaCard
              key={giftIdea.id}
              giftIdea={giftIdea}
              onEdit={onIdeaEdit}
              onDelete={onIdeaDelete}
              onConvertToGift={onIdeaConvertToGift}
            />
          ))}
        </div>
      )}
    </div>
  );
};