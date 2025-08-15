import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { JournalEntry, JournalEntryMood } from '../../types/Journal';

interface JournalEntryViewProps {
  entry: JournalEntry;
  onEdit?: () => void;
  onDelete?: () => void;
  onArchive?: () => void;
  showActions?: boolean;
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

const moodColors: Record<JournalEntryMood, string> = {
  [JournalEntryMood.VERY_HAPPY]: 'text-green-600',
  [JournalEntryMood.HAPPY]: 'text-green-500',
  [JournalEntryMood.CONTENT]: 'text-green-400',
  [JournalEntryMood.NEUTRAL]: 'text-gray-500',
  [JournalEntryMood.ANXIOUS]: 'text-yellow-500',
  [JournalEntryMood.SAD]: 'text-blue-500',
  [JournalEntryMood.VERY_SAD]: 'text-blue-600',
  [JournalEntryMood.ANGRY]: 'text-red-500',
  [JournalEntryMood.EXCITED]: 'text-purple-500',
  [JournalEntryMood.GRATEFUL]: 'text-pink-500',
};

export const JournalEntryView: React.FC<JournalEntryViewProps> = ({
  entry,
  onEdit,
  onDelete,
  onArchive,
  showActions = true,
}) => {
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  const formatTimestamp = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
    });
  };

  return (
    <article className="max-w-4xl mx-auto bg-white shadow-lg rounded-lg overflow-hidden">
      {/* Header */}
      <header className="px-6 py-4 border-b border-gray-200">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            {entry.title && (
              <h1 className="text-2xl font-bold text-gray-900 mb-2">{entry.title}</h1>
            )}
            <div className="flex items-center space-x-4 text-sm text-gray-600">
              <time dateTime={entry.entry_date} className="font-medium">
                {formatDate(entry.entry_date)}
              </time>
              {entry.mood && (
                <span className={`flex items-center space-x-1 ${moodColors[entry.mood]}`}>
                  <span className="text-lg">{moodEmojis[entry.mood]}</span>
                  <span className="capitalize font-medium">
                    {entry.mood.replace('_', ' ')}
                  </span>
                </span>
              )}
              {entry.location && (
                <span className="flex items-center space-x-1">
                  <span className="text-gray-400">📍</span>
                  <span>{entry.location}</span>
                </span>
              )}
              {entry.weather && (
                <span className="flex items-center space-x-1">
                  <span className="text-gray-400">🌤️</span>
                  <span>{entry.weather}</span>
                </span>
              )}
              {entry.is_private && (
                <span className="flex items-center space-x-1 text-yellow-600">
                  <span>🔒</span>
                  <span>Private</span>
                </span>
              )}
            </div>
          </div>
          {showActions && (
            <div className="flex items-center space-x-2 ml-4">
              {onEdit && (
                <button
                  onClick={onEdit}
                  className="p-2 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-md"
                  title="Edit entry"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                  </svg>
                </button>
              )}
              {onArchive && (
                <button
                  onClick={onArchive}
                  className="p-2 text-gray-400 hover:text-yellow-600 hover:bg-yellow-50 rounded-md"
                  title={entry.is_archived ? "Unarchive entry" : "Archive entry"}
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h8a2 2 0 002-2V8m-9 4h4" />
                  </svg>
                </button>
              )}
              {onDelete && (
                <button
                  onClick={onDelete}
                  className="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-md"
                  title="Delete entry"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                </button>
              )}
            </div>
          )}
        </div>

        {/* Tags */}
        {entry.tags && entry.tags.length > 0 && (
          <div className="mt-3 flex flex-wrap gap-2">
            {entry.tags.map((tag) => (
              <span
                key={tag.id}
                className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium text-white"
                style={{ backgroundColor: tag.tag_color || '#3B82F6' }}
              >
                {tag.tag_name}
              </span>
            ))}
          </div>
        )}
      </header>

      {/* Content */}
      <div className="px-6 py-6">
        <div className="prose prose-sm sm:prose lg:prose-lg xl:prose-xl max-w-none dark:prose-invert">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>
            {entry.content}
          </ReactMarkdown>
        </div>
      </div>

      {/* Attachments */}
      {entry.attachments && entry.attachments.length > 0 && (
        <div className="px-6 py-4 border-t border-gray-200">
          <h3 className="text-sm font-medium text-gray-900 mb-3">Attachments</h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {entry.attachments.map((attachment) => (
              <div
                key={attachment.id}
                className="flex items-center p-3 border border-gray-200 rounded-md hover:bg-gray-50"
              >
                <div className="flex-shrink-0">
                  <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </div>
                <div className="ml-3 flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 truncate">
                    {attachment.original_filename}
                  </p>
                  <p className="text-xs text-gray-500">
                    {Math.round(attachment.file_size / 1024)} KB
                    {attachment.description && ` • ${attachment.description}`}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Footer */}
      <footer className="px-6 py-3 bg-gray-50 border-t border-gray-200">
        <div className="flex items-center justify-between text-xs text-gray-500">
          <span>
            Created {formatTimestamp(entry.created_at)}
          </span>
          {entry.updated_at && entry.updated_at !== entry.created_at && (
            <span>
              Updated {formatTimestamp(entry.updated_at)}
            </span>
          )}
        </div>
      </footer>
    </article>
  );
};