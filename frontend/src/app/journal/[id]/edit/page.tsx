'use client';

import React, { useState, useEffect } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { JournalEntryForm } from '../../../../components/journal/JournalEntryForm';
import { JournalEntry, JournalEntryUpdate } from '../../../../types/Journal';
import journalService from '../../../../services/journal';

export default function EditJournalEntryPage() {
  const router = useRouter();
  const params = useParams();
  const entryId = parseInt(params?.id as string);
  
  const [entry, setEntry] = useState<JournalEntry | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isLoadingEntry, setIsLoadingEntry] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!entryId || isNaN(entryId)) {
      setError('Invalid entry ID');
      setIsLoadingEntry(false);
      return;
    }

    loadEntry();
  }, [entryId]);

  const loadEntry = async () => {
    try {
      setIsLoadingEntry(true);
      setError(null);
      
      const entryData = await journalService.getJournalEntry(entryId);
      setEntry(entryData);
    } catch (err: unknown) {
      console.error('Failed to load journal entry:', err);
      if (err && typeof err === 'object' && 'response' in err) {
        const errorResponse = err as { response?: { status?: number } };
        if (errorResponse.response?.status === 404) {
          setError('Journal entry not found');
        } else {
          setError('Failed to load journal entry. Please try again.');
        }
      } else {
        setError('Failed to load journal entry. Please try again.');
      }
    } finally {
      setIsLoadingEntry(false);
    }
  };

  const handleSave = async (entryData: JournalEntryUpdate) => {
    try {
      setIsLoading(true);
      setError(null);
      
      const updatedEntry = await journalService.updateJournalEntry(entryId, entryData);
      
      // Redirect to the updated entry
      router.push(`/journal/${updatedEntry.id}`);
    } catch (err) {
      console.error('Failed to update journal entry:', err);
      setError('Failed to update journal entry. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleCancel = () => {
    router.push(`/journal/${entryId}`);
  };

  if (isLoadingEntry) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading journal entry...</p>
        </div>
      </div>
    );
  }

  if (error && !entry) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center max-w-md mx-auto p-6">
          <div className="text-6xl mb-4">😞</div>
          <h1 className="text-2xl font-bold text-gray-900 mb-2">Oops!</h1>
          <p className="text-gray-600 mb-6">{error}</p>
          <div className="space-x-3">
            <button
              onClick={() => router.push('/journal')}
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              Back to Journal
            </button>
            <button
              onClick={loadEntry}
              className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              Try Again
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (!entry) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {error && (
        <div className="max-w-4xl mx-auto px-6 pt-6">
          <div className="bg-red-50 border border-red-200 rounded-md p-4">
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
              </div>
            </div>
          </div>
        </div>
      )}
      
      <JournalEntryForm
        entry={entry}
        onSave={handleSave}
        onCancel={handleCancel}
        isLoading={isLoading}
      />
    </div>
  );
}