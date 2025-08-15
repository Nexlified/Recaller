'use client';

import React, { useState, useEffect } from 'react';
import { useRouter, useParams } from 'next/navigation';
import Link from 'next/link';
import { JournalEntryView } from '../../../components/journal/JournalEntryView';
import { JournalEntry } from '../../../types/Journal';
import journalService from '../../../services/journal';

export default function JournalEntryPage() {
  const router = useRouter();
  const params = useParams();
  const entryId = parseInt(params?.id as string);
  
  const [entry, setEntry] = useState<JournalEntry | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!entryId || isNaN(entryId)) {
      setError('Invalid entry ID');
      setIsLoading(false);
      return;
    }

    loadEntry();
  }, [entryId]);

  const loadEntry = async () => {
    try {
      setIsLoading(true);
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
      setIsLoading(false);
    }
  };

  const handleEdit = () => {
    router.push(`/journal/${entryId}/edit`);
  };

  const handleDelete = async () => {
    if (!window.confirm('Are you sure you want to delete this journal entry? This action cannot be undone.')) {
      return;
    }

    try {
      await journalService.deleteJournalEntry(entryId);
      router.push('/journal');
    } catch (err) {
      console.error('Failed to delete journal entry:', err);
      alert('Failed to delete journal entry. Please try again.');
    }
  };

  const handleArchive = async () => {
    if (!entry) return;

    try {
      let updatedEntry;
      if (entry.is_archived) {
        updatedEntry = await journalService.unarchiveJournalEntry(entryId);
      } else {
        updatedEntry = await journalService.archiveJournalEntry(entryId);
      }
      setEntry(updatedEntry);
    } catch (err) {
      console.error('Failed to archive/unarchive journal entry:', err);
      alert('Failed to update journal entry. Please try again.');
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading journal entry...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center max-w-md mx-auto p-6">
          <div className="text-6xl mb-4">😞</div>
          <h1 className="text-2xl font-bold text-gray-900 mb-2">Oops!</h1>
          <p className="text-gray-600 mb-6">{error}</p>
          <div className="space-x-3">
            <Link
              href="/journal"
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              Back to Journal
            </Link>
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
      <div className="py-6">
        {/* Navigation */}
        <div className="max-w-4xl mx-auto px-6 mb-6">
          <nav className="flex items-center space-x-4 text-sm">
            <Link
              href="/journal"
              className="text-blue-600 hover:text-blue-800 font-medium"
            >
              ← Back to Journal
            </Link>
            <span className="text-gray-400">/</span>
            <span className="text-gray-600">
              {entry.title || `Entry from ${new Date(entry.entry_date).toLocaleDateString()}`}
            </span>
          </nav>
        </div>

        {/* Journal Entry */}
        <JournalEntryView
          entry={entry}
          onEdit={handleEdit}
          onDelete={handleDelete}
          onArchive={handleArchive}
          showActions={true}
        />
      </div>
    </div>
  );
}