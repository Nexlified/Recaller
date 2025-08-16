'use client';

import React from 'react';
import { Gift, GIFT_STATUS_OPTIONS, GIFT_PRIORITY_OPTIONS } from '../../types/Gift';
import giftsService from '../../services/gifts';

interface GiftItemProps {
  gift: Gift;
  onEdit?: (gift: Gift) => void;
  onDelete?: (giftId: number) => void;
  onStatusChange?: (giftId: number, status: Gift['status']) => void;
  showActions?: boolean;
  className?: string;
}

export const GiftItem: React.FC<GiftItemProps> = ({
  gift,
  onEdit,
  onDelete,
  onStatusChange,
  showActions = true,
  className = ''
}) => {
  const statusConfig = GIFT_STATUS_OPTIONS.find(s => s.value === gift.status);
  const priorityConfig = GIFT_PRIORITY_OPTIONS.find(p => p.value === gift.priority);
  
  const isOverdue = giftsService.isGiftOverdue(gift);
  const displayName = giftsService.getGiftDisplayName(gift);
  const formattedOccasionDate = gift.occasion_date ? giftsService.formatOccasionDate(gift.occasion_date) : null;
  const formattedBudget = gift.budget_amount ? giftsService.formatCurrency(gift.budget_amount, gift.currency) : null;
  const formattedActual = gift.actual_amount ? giftsService.formatCurrency(gift.actual_amount, gift.currency) : null;

  const handleStatusChange = (newStatus: Gift['status']) => {
    if (onStatusChange) {
      onStatusChange(gift.id, newStatus);
    }
  };

  const getStatusBadgeColor = (status: Gift['status']) => {
    const colors = {
      idea: 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200',
      planned: 'bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-400',
      purchased: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-400',
      wrapped: 'bg-purple-100 text-purple-800 dark:bg-purple-900/20 dark:text-purple-400',
      given: 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400',
      returned: 'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400',
    };
    return colors[status] || colors.idea;
  };

  const getPriorityBadgeColor = (priority: Gift['priority']) => {
    const colors = {
      1: 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400',
      2: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-400',
      3: 'bg-orange-100 text-orange-800 dark:bg-orange-900/20 dark:text-orange-400',
      4: 'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400',
    };
    return colors[priority] || colors[2];
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
              <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusBadgeColor(gift.status)}`}>
                {statusConfig?.label || gift.status}
              </span>
              <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getPriorityBadgeColor(gift.priority)}`}>
                {priorityConfig?.label || `Priority ${gift.priority}`}
              </span>
              {isOverdue && (
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400">
                  Overdue
                </span>
              )}
              {gift.is_surprise && (
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-pink-100 text-pink-800 dark:bg-pink-900/20 dark:text-pink-400">
                  Surprise
                </span>
              )}
            </div>
          </div>
          
          {showActions && (
            <div className="flex items-center space-x-2 ml-4">
              {onEdit && (
                <button
                  onClick={() => onEdit(gift)}
                  className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                  title="Edit gift"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                  </svg>
                </button>
              )}
              {onDelete && (
                <button
                  onClick={() => onDelete(gift.id)}
                  className="text-gray-400 hover:text-red-600 dark:hover:text-red-400"
                  title="Delete gift"
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
        {gift.description && (
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-4 line-clamp-2">
            {gift.description}
          </p>
        )}

        {/* Details Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
          {/* Recipient */}
          {(gift.recipient_name || gift.recipient_contact_id) && (
            <div>
              <span className="font-medium text-gray-700 dark:text-gray-300">Recipient:</span>
              <span className="ml-2 text-gray-600 dark:text-gray-400">
                {gift.recipient_name || `Contact ID: ${gift.recipient_contact_id}`}
              </span>
            </div>
          )}

          {/* Category */}
          {gift.category && (
            <div>
              <span className="font-medium text-gray-700 dark:text-gray-300">Category:</span>
              <span className="ml-2 text-gray-600 dark:text-gray-400">{gift.category}</span>
            </div>
          )}

          {/* Occasion */}
          {gift.occasion && (
            <div>
              <span className="font-medium text-gray-700 dark:text-gray-300">Occasion:</span>
              <span className="ml-2 text-gray-600 dark:text-gray-400">{gift.occasion}</span>
            </div>
          )}

          {/* Occasion Date */}
          {formattedOccasionDate && (
            <div>
              <span className="font-medium text-gray-700 dark:text-gray-300">Date:</span>
              <span className={`ml-2 ${isOverdue ? 'text-red-600 dark:text-red-400' : 'text-gray-600 dark:text-gray-400'}`}>
                {formattedOccasionDate}
              </span>
            </div>
          )}

          {/* Budget */}
          {formattedBudget && (
            <div>
              <span className="font-medium text-gray-700 dark:text-gray-300">Budget:</span>
              <span className="ml-2 text-gray-600 dark:text-gray-400">{formattedBudget}</span>
            </div>
          )}

          {/* Actual Amount */}
          {formattedActual && (
            <div>
              <span className="font-medium text-gray-700 dark:text-gray-300">Spent:</span>
              <span className="ml-2 text-gray-600 dark:text-gray-400">{formattedActual}</span>
            </div>
          )}

          {/* Store */}
          {gift.store_name && (
            <div>
              <span className="font-medium text-gray-700 dark:text-gray-300">Store:</span>
              <span className="ml-2 text-gray-600 dark:text-gray-400">{gift.store_name}</span>
            </div>
          )}

          {/* Purchase URL */}
          {gift.purchase_url && (
            <div className="md:col-span-2">
              <span className="font-medium text-gray-700 dark:text-gray-300">Link:</span>
              <a
                href={gift.purchase_url}
                target="_blank"
                rel="noopener noreferrer"
                className="ml-2 text-indigo-600 dark:text-indigo-400 hover:text-indigo-800 dark:hover:text-indigo-300 truncate inline-block max-w-xs"
                title={gift.purchase_url}
              >
                {gift.purchase_url}
              </a>
            </div>
          )}
        </div>

        {/* Notes */}
        {gift.notes && (
          <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
            <p className="text-sm text-gray-600 dark:text-gray-400">
              <span className="font-medium text-gray-700 dark:text-gray-300">Notes:</span> {gift.notes}
            </p>
          </div>
        )}

        {/* Quick Status Change */}
        {onStatusChange && (
          <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
            <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-2">
              Quick Status Update:
            </label>
            <div className="flex flex-wrap gap-2">
              {GIFT_STATUS_OPTIONS
                .filter(status => status.value !== gift.status)
                .slice(0, 3) // Show only next 3 logical statuses
                .map(status => (
                  <button
                    key={status.value}
                    onClick={() => handleStatusChange(status.value)}
                    className={`px-3 py-1 rounded-full text-xs font-medium border transition-colors ${
                      status.color === 'green' 
                        ? 'border-green-200 text-green-700 hover:bg-green-50 dark:border-green-800 dark:text-green-400 dark:hover:bg-green-900/20'
                        : status.color === 'blue'
                        ? 'border-blue-200 text-blue-700 hover:bg-blue-50 dark:border-blue-800 dark:text-blue-400 dark:hover:bg-blue-900/20'
                        : status.color === 'yellow'
                        ? 'border-yellow-200 text-yellow-700 hover:bg-yellow-50 dark:border-yellow-800 dark:text-yellow-400 dark:hover:bg-yellow-900/20'
                        : 'border-gray-200 text-gray-700 hover:bg-gray-50 dark:border-gray-700 dark:text-gray-400 dark:hover:bg-gray-800'
                    }`}
                  >
                    {status.label}
                  </button>
                ))}
            </div>
          </div>
        )}

        {/* Timestamp */}
        <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
          <p className="text-xs text-gray-500 dark:text-gray-500">
            Created {new Date(gift.created_at).toLocaleDateString()}
            {gift.updated_at && gift.updated_at !== gift.created_at && (
              <span> • Updated {new Date(gift.updated_at).toLocaleDateString()}</span>
            )}
          </p>
        </div>
      </div>
    </div>
  );
};