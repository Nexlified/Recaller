'use client';

import React, { useState, useEffect, useCallback } from 'react';
import Link from 'next/link';
import { JournalEntryList } from '../../components/journal/JournalEntryList';
import { JournalEntrySummary, JournalEntryMood, JournalEntryListResponse } from '../../types/Journal';
import journalService from '../../services/journal';

export default function JournalPage() {
  const [entries, setEntries] = useState<JournalEntrySummary[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [moodFilter, setMoodFilter] = useState<JournalEntryMood | ''>('');
  const [includeArchived, setIncludeArchived] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  const loadEntries = useCallback(async (page = 1, reset = false) => {
    try {
      setIsLoading(true);
      const filters = {
        page,
        per_page: 20,
        search: searchQuery || undefined,
        mood: moodFilter || undefined,
        include_archived: includeArchived,
      };

      const response: JournalEntryListResponse = await journalService.getJournalEntries(filters);
      
      if (reset) {
        setEntries(response.items);
      } else {
        setEntries(prev => page === 1 ? response.items : [...prev, ...response.items]);
      }
      
      setTotalPages(response.pagination.total_pages);
      setCurrentPage(page);
      setError(null);
    } catch (err) {
      console.error('Failed to load journal entries:', err);
      setError('Failed to load journal entries. Please try again.');
    } finally {
      setIsLoading(false);
    }
  }, [searchQuery, moodFilter, includeArchived]);

  useEffect(() => {
    loadEntries(1, true);
  }, [searchQuery, moodFilter, includeArchived, loadEntries]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    loadEntries(1, true);
  };

  const loadMore = () => {
    if (currentPage < totalPages) {
      loadEntries(currentPage + 1);
    }
  };

  const moodOptions = [
    { value: '', label: 'All Moods' },
    { value: JournalEntryMood.VERY_HAPPY, label: '😄 Very Happy' },
    { value: JournalEntryMood.HAPPY, label: '😊 Happy' },
    { value: JournalEntryMood.CONTENT, label: '😌 Content' },
    { value: JournalEntryMood.NEUTRAL, label: '😐 Neutral' },
    { value: JournalEntryMood.ANXIOUS, label: '😰 Anxious' },
    { value: JournalEntryMood.SAD, label: '😢 Sad' },
    { value: JournalEntryMood.VERY_SAD, label: '😭 Very Sad' },
    { value: JournalEntryMood.ANGRY, label: '😠 Angry' },
    { value: JournalEntryMood.EXCITED, label: '🤩 Excited' },
    { value: JournalEntryMood.GRATEFUL, label: '🙏 Grateful' },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Journal</h1>
              <p className="mt-2 text-gray-600">
                Document your thoughts, experiences, and reflections
              </p>
            </div>
            <Link
              href="/journal/new"
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
              New Entry
            </Link>
          </div>
        </div>

        {/* Filters */}
        <div className="bg-white shadow rounded-lg p-6 mb-6">
          <form onSubmit={handleSearch} className="space-y-4 sm:space-y-0 sm:grid sm:grid-cols-12 sm:gap-4">
            <div className="sm:col-span-5">
              <label htmlFor="search" className="sr-only">
                Search entries
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <svg className="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                  </svg>
                </div>
                <input
                  id="search"
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Search your entries..."
                  className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                />
              </div>
            </div>

            <div className="sm:col-span-3">
              <label htmlFor="mood" className="sr-only">
                Filter by mood
              </label>
              <select
                id="mood"
                value={moodFilter}
                onChange={(e) => setMoodFilter(e.target.value as JournalEntryMood | '')}
                className="block w-full py-2 px-3 border border-gray-300 bg-white rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              >
                {moodOptions.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>

            <div className="sm:col-span-3 flex items-center">
              <div className="flex items-center h-5">
                <input
                  id="includeArchived"
                  type="checkbox"
                  checked={includeArchived}
                  onChange={(e) => setIncludeArchived(e.target.checked)}
                  className="focus:ring-blue-500 h-4 w-4 text-blue-600 border-gray-300 rounded"
                />
              </div>
              <div className="ml-3 text-sm">
                <label htmlFor="includeArchived" className="font-medium text-gray-700">
                  Include archived
                </label>
              </div>
            </div>

            <div className="sm:col-span-1">
              <button
                type="submit"
                className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                Search
              </button>
            </div>
          </form>
        </div>

        {/* Error State */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-md p-4 mb-6">
            <div className="flex">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div className="ml-3">
                <h3 className="text-sm font-medium text-red-800">Error</h3>
                <div className="mt-2 text-sm text-red-700">
                  <p>{error}</p>
                </div>
                <div className="mt-4">
                  <button
                    onClick={() => loadEntries(1, true)}
                    className="text-sm bg-red-100 text-red-800 hover:bg-red-200 px-3 py-1 rounded-md"
                  >
                    Try again
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Journal Entries */}
        <div className="mb-6">
          <JournalEntryList entries={entries} isLoading={isLoading && currentPage === 1} />
        </div>

        {/* Load More */}
        {!isLoading && currentPage < totalPages && (
          <div className="text-center">
            <button
              onClick={loadMore}
              className="inline-flex items-center px-6 py-3 border border-gray-300 text-base font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              Load more entries
            </button>
          </div>
        )}

        {/* Loading More */}
        {isLoading && currentPage > 1 && (
          <div className="text-center">
            <div className="inline-flex items-center px-6 py-3 text-base font-medium text-gray-500">
              <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-gray-500" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Loading more entries...
            </div>
          </div>
        )}
      </div>
    </div>
  );
}