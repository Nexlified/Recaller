import React from 'react';
import Link from 'next/link';
import { JournalEntrySummary, JournalEntryMood } from '../../types/Journal';

interface JournalEntryListProps {
  entries: JournalEntrySummary[];
  onEntryClick?: (id: number) => void;
  isLoading?: boolean;
}

const moodEmojis: Record<JournalEntryMood, string> = {
  [JournalEntryMood.VERY_HAPPY]: '😄',
  [JournalEntryMood.HAPPY]: '😊',
  [JournalEntryMood.CONTENT]: '😌',
  [JournalEntryMood.NEUTRAL]: '😐',
  [JournalEntryMood.ANXIOUS]: '😰',
  [JournalEntryMood.SAD]: '😢',
  [JournalEntryMood.VERY_SAD]: '😭',
  [JournalEntryMood.ANGRY]: '😠',
  [JournalEntryMood.EXCITED]: '🤩',
  [JournalEntryMood.GRATEFUL]: '🙏',
};

export const JournalEntryList: React.FC<JournalEntryListProps> = ({
  entries,
  onEntryClick,
  isLoading = false,
}) => {
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const today = new Date();
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);

    if (date.toDateString() === today.toDateString()) {
      return 'Today';
    } else if (date.toDateString() === yesterday.toDateString()) {
      return 'Yesterday';
    } else {
      return date.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: date.getFullYear() !== today.getFullYear() ? 'numeric' : undefined,
      });
    }
  };

  const formatTime = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleTimeString('en-US', {
      hour: 'numeric',
      minute: '2-digit',
    });
  };

  if (isLoading) {
    return (
      <div className="space-y-4">
        {[...Array(5)].map((_, index) => (
          <div key={index} className="bg-white shadow rounded-lg p-6 animate-pulse">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
                <div className="h-3 bg-gray-200 rounded w-1/2"></div>
              </div>
              <div className="h-6 w-6 bg-gray-200 rounded-full ml-4"></div>
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (entries.length === 0) {
    return (
      <div className="text-center py-12">
        <div className="text-6xl mb-4">📝</div>
        <h3 className="text-lg font-medium text-gray-900 mb-2">No journal entries yet</h3>
        <p className="text-gray-500 mb-6">Start documenting your thoughts and experiences.</p>
        <Link
          href="/journal/new"
          className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
        >
          Write your first entry
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {entries.map((entry) => (
        <div
          key={entry.id}
          className="bg-white shadow hover:shadow-md transition-shadow duration-200 rounded-lg border border-gray-200 overflow-hidden"
        >
          <Link
            href={`/journal/${entry.id}`}
            className="block p-6 hover:bg-gray-50"
            onClick={() => onEntryClick?.(entry.id)}
          >
            <div className="flex items-start justify-between">
              <div className="flex-1 min-w-0">
                <div className="flex items-center space-x-3 mb-2">
                  <time
                    dateTime={entry.entry_date}
                    className="text-sm font-medium text-gray-900"
                  >
                    {formatDate(entry.entry_date)}
                  </time>
                  <span className="text-xs text-gray-500">
                    {formatTime(entry.created_at)}
                  </span>
                  {entry.mood && (
                    <span className="text-lg" title={entry.mood.replace('_', ' ')}>
                      {moodEmojis[entry.mood]}
                    </span>
                  )}
                </div>

                {entry.title && (
                  <h3 className="text-lg font-medium text-gray-900 mb-1 truncate">
                    {entry.title}
                  </h3>
                )}

                <div className="flex items-center space-x-4 text-xs text-gray-500">
                  {entry.tag_count > 0 && (
                    <span className="flex items-center space-x-1">
                      <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M17.707 9.293a1 1 0 010 1.414l-7 7a1 1 0 01-1.414 0l-7-7A.997.997 0 012 10V5a3 3 0 013-3h5c.256 0 .512.098.707.293l7 7zM5 6a1 1 0 100-2 1 1 0 000 2z" clipRule="evenodd" />
                      </svg>
                      <span>{entry.tag_count} tag{entry.tag_count !== 1 ? 's' : ''}</span>
                    </span>
                  )}
                  {entry.attachment_count > 0 && (
                    <span className="flex items-center space-x-1">
                      <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zM6.293 6.707a1 1 0 010-1.414l3-3a1 1 0 011.414 0l3 3a1 1 0 01-1.414 1.414L11 5.414V13a1 1 0 11-2 0V5.414L7.707 6.707a1 1 0 01-1.414 0z" clipRule="evenodd" />
                      </svg>
                      <span>{entry.attachment_count} file{entry.attachment_count !== 1 ? 's' : ''}</span>
                    </span>
                  )}
                  {entry.is_private && (
                    <span className="flex items-center space-x-1 text-yellow-600">
                      <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clipRule="evenodd" />
                      </svg>
                      <span>Private</span>
                    </span>
                  )}
                  {entry.is_archived && (
                    <span className="flex items-center space-x-1 text-gray-400">
                      <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                        <path d="M4 3a2 2 0 100 4h12a2 2 0 100-4H4z" />
                        <path fillRule="evenodd" d="M3 8h14v7a2 2 0 01-2 2H5a2 2 0 01-2-2V8zm5 3a1 1 0 011-1h2a1 1 0 110 2H9a1 1 0 01-1-1z" clipRule="evenodd" />
                      </svg>
                      <span>Archived</span>
                    </span>
                  )}
                </div>
              </div>

              <div className="flex-shrink-0 ml-4">
                <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </div>
            </div>
          </Link>
        </div>
      ))}
    </div>
  );
};