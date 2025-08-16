'use client';

import React from 'react';
import { SharedActivity, ACTIVITY_TYPES } from '../../types/Activity';

interface ActivityCardProps {
  activity: SharedActivity;
  onEdit: (activity: SharedActivity) => void;
  onDelete: (id: number) => void;
  onClick: (activity: SharedActivity) => void;
  className?: string;
}

export const ActivityCard: React.FC<ActivityCardProps> = ({
  activity,
  onEdit,
  onDelete,
  onClick,
  className = '',
}) => {
  const getActivityTypeIcon = (type: string) => {
    const activityType = ACTIVITY_TYPES.find(t => t.value === type);
    return activityType?.icon || '📝';
  };

  const getActivityTypeLabel = (type: string) => {
    const activityType = ACTIVITY_TYPES.find(t => t.value === type);
    return activityType?.label || type;
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'planned':
        return 'bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-400';
      case 'completed':
        return 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400';
      case 'cancelled':
        return 'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400';
      case 'postponed':
        return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-400';
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-900/20 dark:text-gray-400';
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      weekday: 'short',
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  const formatTime = (timeString?: string) => {
    if (!timeString) return '';
    const [hours, minutes] = timeString.split(':');
    const date = new Date();
    date.setHours(parseInt(hours), parseInt(minutes));
    return date.toLocaleTimeString('en-US', {
      hour: 'numeric',
      minute: '2-digit',
      hour12: true,
    });
  };

  const participantNames = activity.participants
    .slice(0, 3)
    .map(p => p.contact?.first_name || 'Unknown')
    .join(', ');

  const remainingParticipants = activity.participants.length - 3;

  const handleEditClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    onEdit(activity);
  };

  const handleDeleteClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (window.confirm('Are you sure you want to delete this activity?')) {
      onDelete(activity.id);
    }
  };

  return (
    <div
      className={`bg-white dark:bg-gray-800 rounded-lg shadow-md hover:shadow-lg transition-shadow cursor-pointer border border-gray-200 dark:border-gray-700 ${className}`}
      onClick={() => onClick(activity)}
    >
      <div className="p-6">
        {/* Header */}
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center space-x-3">
            <div className="flex-shrink-0">
              <span className="text-3xl">{getActivityTypeIcon(activity.activity_type)}</span>
            </div>
            <div className="flex-1 min-w-0">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 truncate">
                {activity.title}
              </h3>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                {getActivityTypeLabel(activity.activity_type)}
              </p>
            </div>
          </div>
          
          {/* Status Badge */}
          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(activity.status)}`}>
            {activity.status.charAt(0).toUpperCase() + activity.status.slice(1)}
          </span>
        </div>

        {/* Date and Time */}
        <div className="mb-4">
          <div className="flex items-center text-sm text-gray-600 dark:text-gray-400">
            <span className="mr-1">📅</span>
            <span>{formatDate(activity.activity_date)}</span>
            {activity.start_time && (
              <>
                <span className="mx-2">•</span>
                <span className="mr-1">🕐</span>
                <span>{formatTime(activity.start_time)}</span>
                {activity.end_time && (
                  <span> - {formatTime(activity.end_time)}</span>
                )}
              </>
            )}
          </div>
        </div>

        {/* Location */}
        {activity.location && (
          <div className="mb-4">
            <div className="flex items-center text-sm text-gray-600 dark:text-gray-400">
              <span className="mr-1">📍</span>
              <span className="truncate">{activity.location}</span>
            </div>
          </div>
        )}

        {/* Participants */}
        <div className="mb-4">
          <div className="flex items-center text-sm text-gray-600 dark:text-gray-400">
            <span className="mr-1">👥</span>
            <span className="truncate">
              {participantNames}
              {remainingParticipants > 0 && (
                <span className="text-gray-500"> and {remainingParticipants} more</span>
              )}
            </span>
          </div>
        </div>

        {/* Cost */}
        {(activity.cost_per_person || activity.total_cost) && (
          <div className="mb-4">
            <div className="flex items-center text-sm text-gray-600 dark:text-gray-400">
              <span className="mr-1">💰</span>
              {activity.cost_per_person && (
                <span>{activity.currency} {activity.cost_per_person} per person</span>
              )}
              {activity.total_cost && activity.cost_per_person && (
                <span className="mx-1">•</span>
              )}
              {activity.total_cost && (
                <span>{activity.currency} {activity.total_cost} total</span>
              )}
            </div>
          </div>
        )}

        {/* Quality Rating */}
        {activity.quality_rating && activity.status === 'completed' && (
          <div className="mb-4">
            <div className="flex items-center text-sm text-gray-600 dark:text-gray-400">
              <span className="mr-1">⭐</span>
              <span>{activity.quality_rating}/10</span>
              <div className="ml-2 flex">
                {Array.from({ length: 5 }, (_, i) => (
                  <span
                    key={i}
                    className={`text-xs ${
                      i < Math.round(activity.quality_rating! / 2)
                        ? 'text-yellow-400'
                        : 'text-gray-300 dark:text-gray-600'
                    }`}
                  >
                    ★
                  </span>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Photos Preview */}
        {activity.photos && activity.photos.length > 0 && (
          <div className="mb-4">
            <div className="flex items-center space-x-2">
              <span className="text-sm text-gray-600 dark:text-gray-400 mr-1">📷</span>
              <div className="flex space-x-1">
                {activity.photos.slice(0, 3).map((photo, index) => (
                  <div
                    key={photo.id}
                    className="w-8 h-8 bg-gray-200 dark:bg-gray-700 rounded overflow-hidden"
                  >
                    <img
                      src={photo.thumbnail_url || photo.url}
                      alt={photo.caption || 'Activity photo'}
                      className="w-full h-full object-cover"
                    />
                  </div>
                ))}
                {activity.photos.length > 3 && (
                  <div className="w-8 h-8 bg-gray-200 dark:bg-gray-700 rounded flex items-center justify-center">
                    <span className="text-xs text-gray-600 dark:text-gray-400">
                      +{activity.photos.length - 3}
                    </span>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Description Preview */}
        {activity.description && (
          <div className="mb-4">
            <p className="text-sm text-gray-600 dark:text-gray-400 line-clamp-2">
              {activity.description}
            </p>
          </div>
        )}

        {/* Memorable Moments Preview */}
        {activity.memorable_moments && (
          <div className="mb-4">
            <div className="bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-md p-2">
              <p className="text-sm text-amber-800 dark:text-amber-400 line-clamp-2">
                💫 {activity.memorable_moments}
              </p>
            </div>
          </div>
        )}

        {/* Actions */}
        <div className="flex items-center justify-between pt-4 border-t border-gray-200 dark:border-gray-700">
          <div className="flex items-center space-x-2 text-xs text-gray-500 dark:text-gray-400">
            {activity.is_private && (
              <span className="flex items-center">
                <span className="mr-1">🔒</span>
                Private
              </span>
            )}
            <span>
              Created {new Date(activity.created_at).toLocaleDateString()}
            </span>
          </div>
          
          <div className="flex items-center space-x-2">
            <button
              onClick={handleEditClick}
              className="text-gray-400 hover:text-blue-600 dark:hover:text-blue-400 transition-colors"
              title="Edit activity"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
              </svg>
            </button>
            <button
              onClick={handleDeleteClick}
              className="text-gray-400 hover:text-red-600 dark:hover:text-red-400 transition-colors"
              title="Delete activity"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};