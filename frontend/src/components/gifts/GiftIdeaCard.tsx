'use client';

import React from 'react';
import { GiftIdea } from '../../types/Gift';
import giftsService from '../../services/gifts';

interface GiftIdeaCardProps {
  giftIdea: GiftIdea;
  onEdit?: (giftIdea: GiftIdea) => void;
  onDelete?: (ideaId: number) => void;
  onConvertToGift?: (giftIdea: GiftIdea) => void;
  showActions?: boolean;
  className?: string;
}

export const GiftIdeaCard: React.FC<GiftIdeaCardProps> = ({
  giftIdea,
  onEdit,
  onDelete,
  onConvertToGift,
  showActions = true,
  className = ''
}) => {
  const displayName = giftIdea.title.trim() || 'Untitled Idea';
  const formattedPriceRange = formatPriceRange(giftIdea.price_range_min, giftIdea.price_range_max, giftIdea.currency);
  const hasBeenUsed = giftIdea.times_gifted > 0;

  const getRatingStars = (rating: number) => {
    return Array.from({ length: 5 }, (_, i) => (
      <span key={i} className={`text-sm ${i < rating ? 'text-yellow-400' : 'text-gray-300 dark:text-gray-600'}`}>
        ★
      </span>
    ));
  };

  return (
    <div className={`bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-sm hover:shadow-md transition-shadow ${className}`}>
      <div className="p-6">
        {/* Header */}
        <div className="flex items-start justify-between mb-4">
          <div className="flex-1 min-w-0">
            <h3 className="text-lg font-medium text-gray-900 dark:text-white truncate">
              {displayName}
            </h3>
            <div className="flex items-center space-x-2 mt-1">
              {giftIdea.category && (
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-400">
                  {giftIdea.category}
                </span>
              )}
              {giftIdea.rating > 0 && (
                <div className="flex items-center space-x-1">
                  {getRatingStars(giftIdea.rating)}
                  <span className="text-xs text-gray-500 dark:text-gray-400">({giftIdea.rating})</span>
                </div>
              )}
              {hasBeenUsed && (
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400">
                  Used {giftIdea.times_gifted} time{giftIdea.times_gifted > 1 ? 's' : ''}
                </span>
              )}
            </div>
          </div>
          
          {showActions && (
            <div className="flex items-center space-x-2 ml-4">
              {onConvertToGift && (
                <button
                  onClick={() => onConvertToGift(giftIdea)}
                  className="text-gray-400 hover:text-green-600 dark:hover:text-green-400"
                  title="Convert to gift"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                  </svg>
                </button>
              )}
              {onEdit && (
                <button
                  onClick={() => onEdit(giftIdea)}
                  className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                  title="Edit idea"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                  </svg>
                </button>
              )}
              {onDelete && (
                <button
                  onClick={() => onDelete(giftIdea.id)}
                  className="text-gray-400 hover:text-red-600 dark:hover:text-red-400"
                  title="Delete idea"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                </button>
              )}
            </div>
          )}
        </div>

        {/* Description */}
        {giftIdea.description && (
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-4 line-clamp-3">
            {giftIdea.description}
          </p>
        )}

        {/* Details Grid */}
        <div className="space-y-3 text-sm">
          {/* Target Demographic */}
          {giftIdea.target_demographic && (
            <div>
              <span className="font-medium text-gray-700 dark:text-gray-300">Target:</span>
              <span className="ml-2 text-gray-600 dark:text-gray-400">{giftIdea.target_demographic}</span>
            </div>
          )}

          {/* Price Range */}
          {formattedPriceRange && (
            <div>
              <span className="font-medium text-gray-700 dark:text-gray-300">Price Range:</span>
              <span className="ml-2 text-gray-600 dark:text-gray-400">{formattedPriceRange}</span>
            </div>
          )}

          {/* Suitable Occasions */}
          {giftIdea.suitable_occasions.length > 0 && (
            <div>
              <span className="font-medium text-gray-700 dark:text-gray-300">Occasions:</span>
              <div className="mt-1 flex flex-wrap gap-1">
                {giftIdea.suitable_occasions.slice(0, 3).map(occasion => (
                  <span
                    key={occasion}
                    className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-purple-100 text-purple-800 dark:bg-purple-900/20 dark:text-purple-400"
                  >
                    {occasion}
                  </span>
                ))}
                {giftIdea.suitable_occasions.length > 3 && (
                  <span className="text-xs text-gray-500 dark:text-gray-400">
                    +{giftIdea.suitable_occasions.length - 3} more
                  </span>
                )}
              </div>
            </div>
          )}

          {/* Tags */}
          {giftIdea.tags.length > 0 && (
            <div>
              <span className="font-medium text-gray-700 dark:text-gray-300">Tags:</span>
              <div className="mt-1 flex flex-wrap gap-1">
                {giftIdea.tags.slice(0, 4).map(tag => (
                  <span
                    key={tag}
                    className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200"
                  >
                    {tag}
                  </span>
                ))}
                {giftIdea.tags.length > 4 && (
                  <span className="text-xs text-gray-500 dark:text-gray-400">
                    +{giftIdea.tags.length - 4} more
                  </span>
                )}
              </div>
            </div>
          )}

          {/* Source URL */}
          {giftIdea.source_url && (
            <div>
              <span className="font-medium text-gray-700 dark:text-gray-300">Source:</span>
              <a
                href={giftIdea.source_url}
                target="_blank"
                rel="noopener noreferrer"
                className="ml-2 text-indigo-600 dark:text-indigo-400 hover:text-indigo-800 dark:hover:text-indigo-300 truncate inline-block max-w-xs"
                title={giftIdea.source_url}
              >
                {getDomainFromUrl(giftIdea.source_url)}
              </a>
            </div>
          )}

          {/* Usage History */}
          {hasBeenUsed && giftIdea.last_gifted_date && (
            <div>
              <span className="font-medium text-gray-700 dark:text-gray-300">Last used:</span>
              <span className="ml-2 text-gray-600 dark:text-gray-400">
                {new Date(giftIdea.last_gifted_date).toLocaleDateString()}
              </span>
            </div>
          )}
        </div>

        {/* Notes */}
        {giftIdea.notes && (
          <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
            <p className="text-sm text-gray-600 dark:text-gray-400">
              <span className="font-medium text-gray-700 dark:text-gray-300">Notes:</span> {giftIdea.notes}
            </p>
          </div>
        )}

        {/* Quick Actions */}
        {onConvertToGift && (
          <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
            <button
              onClick={() => onConvertToGift(giftIdea)}
              className="w-full px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-colors text-sm font-medium"
            >
              Convert to Gift
            </button>
          </div>
        )}

        {/* Timestamp */}
        <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
          <p className="text-xs text-gray-500 dark:text-gray-500">
            Created {new Date(giftIdea.created_at).toLocaleDateString()}
            {giftIdea.updated_at && giftIdea.updated_at !== giftIdea.created_at && (
              <span> • Updated {new Date(giftIdea.updated_at).toLocaleDateString()}</span>
            )}
          </p>
        </div>
      </div>
    </div>
  );
};

// Helper functions
function formatPriceRange(min?: number, max?: number, currency: string = 'USD'): string | null {
  if (!min && !max) return null;
  
  const formatter = new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: currency,
  });
  
  if (min && max) {
    return `${formatter.format(min)} - ${formatter.format(max)}`;
  } else if (min) {
    return `From ${formatter.format(min)}`;
  } else if (max) {
    return `Up to ${formatter.format(max)}`;
  }
  
  return null;
}

function getDomainFromUrl(url: string): string {
  try {
    const domain = new URL(url).hostname;
    return domain.startsWith('www.') ? domain.slice(4) : domain;
  } catch {
    return url;
  }
}