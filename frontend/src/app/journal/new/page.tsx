'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { JournalEntryForm } from '../../../components/journal/JournalEntryForm';
import { JournalEntryCreate, JournalEntryUpdate } from '../../../types/Journal';
import journalService from '../../../services/journal';

export default function NewJournalEntryPage() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSave = async (entryData: JournalEntryCreate | JournalEntryUpdate) => {
    try {
      setIsLoading(true);
      setError(null);
      
      // Since this is the new page, we always create
      const entry = await journalService.createJournalEntry(entryData as JournalEntryCreate);
      
      // Redirect to the newly created entry
      router.push(`/journal/${entry.id}`);
    } catch (err) {
      console.error('Failed to create journal entry:', err);
      setError('Failed to create journal entry. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleCancel = () => {
    router.push('/journal');
  };

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
        onSave={handleSave}
        onCancel={handleCancel}
        isLoading={isLoading}
      />
    </div>
  );
}