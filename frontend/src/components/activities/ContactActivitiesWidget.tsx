'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { SharedActivity, ACTIVITY_TYPES } from '../../types/Activity';
import activityService from '../../services/activityService';

interface ContactActivitiesWidgetProps {
  contactId: number;
  limit?: number;
  className?: string;
}

export const ContactActivitiesWidget: React.FC<ContactActivitiesWidgetProps> = ({
  contactId,
  limit = 5,
  className = '',
}) => {
  const [activities, setActivities] = useState<SharedActivity[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadActivities();
  }, [contactId, limit]);

  const loadActivities = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await activityService.getActivitiesWithContact(contactId);
      // Sort by date descending and limit
      const sortedAndLimited = data
        .sort((a, b) => new Date(b.activity_date).getTime() - new Date(a.activity_date).getTime())
        .slice(0, limit);
      setActivities(sortedAndLimited);
    } catch (err) {
      console.error('Error loading contact activities:', err);
      setError(err instanceof Error ? err.message : 'Failed to load activities');
    } finally {
      setLoading(false);
    }
  };

  const getActivityTypeIcon = (type: string) => {
    const activityType = ACTIVITY_TYPES.find(t => t.value === type);
    return activityType?.icon || '📝';
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
    const now = new Date();
    const diffTime = now.getTime() - date.getTime();
    const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));

    if (diffDays === 0) {
      return 'Today';
    } else if (diffDays === 1) {
      return 'Yesterday';
    } else if (diffDays < 7) {
      return `${diffDays} days ago`;
    } else if (diffDays < 30) {
      const weeks = Math.floor(diffDays / 7);
      return `${weeks} week${weeks > 1 ? 's' : ''} ago`;
    } else if (diffDays < 365) {
      const months = Math.floor(diffDays / 30);
      return `${months} month${months > 1 ? 's' : ''} ago`;
    } else {
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
      });
    }
  };

  const getLastActivityIndicator = () => {
    if (activities.length === 0) return null;
    
    const lastActivity = activities[0];
    const daysSinceLastActivity = Math.floor(
      (new Date().getTime() - new Date(lastActivity.activity_date).getTime()) / (1000 * 60 * 60 * 24)
    );

    if (daysSinceLastActivity > 30) {
      return (
        <div className="mb-4 p-3 bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-md">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-amber-400" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <p className="text-sm font-medium text-amber-800 dark:text-amber-400">
                Haven't seen in {daysSinceLastActivity} days
              </p>
              <p className="text-xs text-amber-700 dark:text-amber-300 mt-1">
                Consider planning something together soon!
              </p>
            </div>
          </div>
        </div>
      );
    }

    return null;
  };

  if (loading) {
    return (
      <div className={`bg-white dark:bg-gray-800 shadow rounded-lg ${className}`}>
        <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
          <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100">Recent Activities</h3>
        </div>
        <div className="px-6 py-4">
          <div className="animate-pulse space-y-3">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="flex items-center space-x-3">
                <div className="w-8 h-8 bg-gray-200 dark:bg-gray-700 rounded"></div>
                <div className="flex-1">
                  <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-3/4"></div>
                  <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-1/2 mt-1"></div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`bg-white dark:bg-gray-800 shadow rounded-lg ${className}`}>
        <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
          <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100">Recent Activities</h3>
        </div>
        <div className="px-6 py-4">
          <div className="text-center py-4">
            <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
            <button
              onClick={loadActivities}
              className="mt-2 text-sm text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300"
            >
              Try again
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={`bg-white dark:bg-gray-800 shadow rounded-lg ${className}`}>
      <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100">Recent Activities</h3>
          {activities.length > 0 && (
            <Link
              href={`/activities?contact=${contactId}`}
              className="text-sm text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300"
            >
              View all
            </Link>
          )}
        </div>
      </div>
      
      <div className="px-6 py-4">
        {getLastActivityIndicator()}
        
        {activities.length === 0 ? (
          <div className="text-center py-8">
            <div className="text-gray-400 dark:text-gray-500 mb-3">
              <svg className="mx-auto h-8 w-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
            </div>
            <p className="text-sm text-gray-500 dark:text-gray-400 mb-3">
              No shared activities yet
            </p>
            <Link
              href="/activities/new"
              className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
              Plan Activity
            </Link>
          </div>
        ) : (
          <div className="space-y-4">
            {activities.map((activity) => (
              <div key={activity.id} className="flex items-start space-x-3">
                <div className="flex-shrink-0">
                  <span className="text-xl">{getActivityTypeIcon(activity.activity_type)}</span>
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between">
                    <Link
                      href={`/activities/${activity.id}`}
                      className="text-sm font-medium text-gray-900 dark:text-gray-100 hover:text-blue-600 dark:hover:text-blue-400 truncate"
                    >
                      {activity.title}
                    </Link>
                    <span className={`ml-2 inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${getStatusColor(activity.status)}`}>
                      {activity.status}
                    </span>
                  </div>
                  <div className="flex items-center space-x-2 mt-1">
                    <span className="text-xs text-gray-500 dark:text-gray-400">
                      {formatDate(activity.activity_date)}
                    </span>
                    {activity.location && (
                      <>
                        <span className="text-xs text-gray-400">•</span>
                        <span className="text-xs text-gray-500 dark:text-gray-400 truncate">
                          {activity.location}
                        </span>
                      </>
                    )}
                    {activity.quality_rating && activity.status === 'completed' && (
                      <>
                        <span className="text-xs text-gray-400">•</span>
                        <span className="text-xs text-gray-500 dark:text-gray-400">
                          ⭐ {activity.quality_rating}/10
                        </span>
                      </>
                    )}
                  </div>
                  {activity.description && (
                    <p className="text-xs text-gray-600 dark:text-gray-400 mt-1 line-clamp-2">
                      {activity.description}
                    </p>
                  )}
                </div>
              </div>
            ))}
            
            {/* Quick Add Activity */}
            <div className="border-t border-gray-200 dark:border-gray-700 pt-4">
              <Link
                href={`/activities/new?contact=${contactId}`}
                className="flex items-center justify-center w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                </svg>
                Plan New Activity
              </Link>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};