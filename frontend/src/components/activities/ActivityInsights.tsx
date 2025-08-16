'use client';

import React from 'react';
import { ActivityInsights } from '../../types/Activity';

interface ActivityInsightsProps {
  insights: ActivityInsights;
  timeRange: 'month' | 'quarter' | 'year';
  className?: string;
}

export const ActivityInsightsComponent: React.FC<ActivityInsightsProps> = ({
  insights,
  timeRange,
  className = '',
}) => {
  const getTimeRangeLabel = () => {
    switch (timeRange) {
      case 'month':
        return 'This Month';
      case 'quarter':
        return 'This Quarter';
      case 'year':
        return 'This Year';
      default:
        return 'Period';
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(amount);
  };

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white dark:bg-gray-800 overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
                  <span className="text-white text-sm">📊</span>
                </div>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 dark:text-gray-400 truncate">
                    Total Activities
                  </dt>
                  <dd className="text-lg font-medium text-gray-900 dark:text-gray-100">
                    {insights.total_activities}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center">
                  <span className="text-white text-sm">📅</span>
                </div>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 dark:text-gray-400 truncate">
                    {getTimeRangeLabel()}
                  </dt>
                  <dd className="text-lg font-medium text-gray-900 dark:text-gray-100">
                    {insights.activities_this_month}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-yellow-500 rounded-full flex items-center justify-center">
                  <span className="text-white text-sm">⭐</span>
                </div>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 dark:text-gray-400 truncate">
                    Avg. Rating
                  </dt>
                  <dd className="text-lg font-medium text-gray-900 dark:text-gray-100">
                    {insights.average_quality_rating 
                      ? `${insights.average_quality_rating.toFixed(1)}/10`
                      : 'N/A'
                    }
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-purple-500 rounded-full flex items-center justify-center">
                  <span className="text-white text-sm">💰</span>
                </div>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 dark:text-gray-400 truncate">
                    Total Spent
                  </dt>
                  <dd className="text-lg font-medium text-gray-900 dark:text-gray-100">
                    {insights.total_spent ? formatCurrency(insights.total_spent) : '$0'}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Activity Frequency Chart */}
        <div className="bg-white dark:bg-gray-800 shadow rounded-lg">
          <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
            <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100">Activity Types</h3>
            <p className="text-sm text-gray-500 dark:text-gray-400">
              Breakdown by activity type
            </p>
          </div>
          <div className="px-6 py-4">
            {Object.keys(insights.activity_frequency).length > 0 ? (
              <div className="space-y-3">
                {Object.entries(insights.activity_frequency)
                  .sort(([, a], [, b]) => b - a)
                  .slice(0, 8)
                  .map(([type, count]) => {
                    const percentage = Math.round((count / insights.total_activities) * 100);
                    return (
                      <div key={type} className="flex items-center justify-between">
                        <div className="flex items-center space-x-2">
                          <span className="text-sm font-medium text-gray-900 dark:text-gray-100 capitalize">
                            {type.replace('_', ' ')}
                          </span>
                        </div>
                        <div className="flex items-center space-x-2">
                          <div className="w-24 h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                            <div 
                              className="h-full bg-blue-500 rounded-full"
                              style={{ width: `${percentage}%` }}
                            />
                          </div>
                          <span className="text-sm text-gray-600 dark:text-gray-400 w-8 text-right">
                            {count}
                          </span>
                        </div>
                      </div>
                    );
                  })}
              </div>
            ) : (
              <div className="text-center py-8">
                <p className="text-gray-500 dark:text-gray-400">No activity data available</p>
              </div>
            )}
          </div>
        </div>

        {/* Top Contacts */}
        <div className="bg-white dark:bg-gray-800 shadow rounded-lg">
          <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
            <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100">Most Active Contacts</h3>
            <p className="text-sm text-gray-500 dark:text-gray-400">
              People you spend the most time with
            </p>
          </div>
          <div className="px-6 py-4">
            {insights.most_active_contacts.length > 0 ? (
              <div className="space-y-4">
                {insights.most_active_contacts.slice(0, 5).map((contact, index) => (
                  <div key={contact.contact_id} className="flex items-center space-x-3">
                    <div className="flex-shrink-0">
                      <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full flex items-center justify-center">
                        <span className="text-xs font-medium text-white">
                          #{index + 1}
                        </span>
                      </div>
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-900 dark:text-gray-100 truncate">
                        {contact.contact_name}
                      </p>
                      <div className="flex items-center space-x-2 text-xs text-gray-500 dark:text-gray-400">
                        <span>{contact.activity_count} activities</span>
                        {contact.favorite_activity_type && (
                          <>
                            <span>•</span>
                            <span className="capitalize">{contact.favorite_activity_type.replace('_', ' ')}</span>
                          </>
                        )}
                        {contact.average_quality_rating && (
                          <>
                            <span>•</span>
                            <span>⭐ {contact.average_quality_rating.toFixed(1)}</span>
                          </>
                        )}
                      </div>
                      {contact.last_activity_date && (
                        <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                          Last activity: {new Date(contact.last_activity_date).toLocaleDateString()}
                        </p>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <p className="text-gray-500 dark:text-gray-400">No contact data available</p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Favorite Activity Type */}
      {insights.favorite_activity_type && (
        <div className="bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-6">
          <div className="flex items-center space-x-3">
            <div className="flex-shrink-0">
              <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full flex items-center justify-center">
                <span className="text-white text-xl">🏆</span>
              </div>
            </div>
            <div>
              <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100">
                Your Favorite Activity
              </h3>
              <p className="text-blue-600 dark:text-blue-400 capitalize font-medium">
                {insights.favorite_activity_type.replace('_', ' ')}
              </p>
              <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                Based on frequency and quality ratings
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Quality Rating Distribution (Future Enhancement) */}
      <div className="bg-white dark:bg-gray-800 shadow rounded-lg">
        <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
          <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100">Activity Quality</h3>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            How you rate your experiences
          </p>
        </div>
        <div className="px-6 py-4">
          {insights.average_quality_rating ? (
            <div className="text-center">
              <div className="text-4xl font-bold text-gray-900 dark:text-gray-100 mb-2">
                {insights.average_quality_rating.toFixed(1)}
              </div>
              <div className="flex justify-center mb-2">
                {Array.from({ length: 5 }, (_, i) => (
                  <span
                    key={i}
                    className={`text-xl ${
                      i < Math.round(insights.average_quality_rating! / 2)
                        ? 'text-yellow-400'
                        : 'text-gray-300 dark:text-gray-600'
                    }`}
                  >
                    ★
                  </span>
                ))}
              </div>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Average quality rating out of 10
              </p>
            </div>
          ) : (
            <div className="text-center py-8">
              <p className="text-gray-500 dark:text-gray-400">
                Complete some activities and rate them to see quality insights
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};