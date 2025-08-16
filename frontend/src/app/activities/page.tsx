'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { useActivities, useUpcomingActivities, useRecentActivities } from '../../hooks/useActivities';
import { useActivityInsights } from '../../hooks/useActivityInsights';
import { ActivityTimeline } from '../../components/activities/ActivityTimeline';
import { ActivityCard } from '../../components/activities/ActivityCard';
import { SharedActivity } from '../../types/Activity';

export default function ActivitiesPage() {
  const [viewMode, setViewMode] = useState<'grid' | 'timeline'>('timeline');
  const [timelineGroupBy, setTimelineGroupBy] = useState<'month' | 'week' | 'day'>('month');

  const { activities, loading, error, refreshActivities } = useActivities();
  const { activities: upcomingActivities, loading: upcomingLoading } = useUpcomingActivities(7);
  const { activities: recentActivities, loading: recentLoading } = useRecentActivities(5);
  const { insights, loading: insightsLoading } = useActivityInsights();

  const handleActivityClick = (activity: SharedActivity) => {
    window.location.href = `/activities/${activity.id}`;
  };

  const handleActivityEdit = (activity: SharedActivity) => {
    window.location.href = `/activities/${activity.id}/edit`;
  };

  const handleActivityDelete = async (id: number) => {
    try {
      await refreshActivities();
    } catch (error) {
      console.error('Error deleting activity:', error);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="animate-pulse space-y-8">
            <div className="h-8 bg-gray-200 dark:bg-gray-700 rounded w-1/4"></div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {[...Array(3)].map((_, i) => (
                <div key={i} className="h-32 bg-gray-200 dark:bg-gray-700 rounded-lg"></div>
              ))}
            </div>
            <div className="h-64 bg-gray-200 dark:bg-gray-700 rounded-lg"></div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center">
            <div className="text-red-400 mb-4">
              <svg className="mx-auto h-12 w-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
              </svg>
            </div>
            <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">
              Error loading activities
            </h3>
            <p className="text-gray-500 dark:text-gray-400 mb-4">{error}</p>
            <button
              onClick={refreshActivities}
              className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              Try Again
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="md:flex md:items-center md:justify-between mb-8">
          <div className="flex-1 min-w-0">
            <h1 className="text-2xl font-bold leading-7 text-gray-900 dark:text-gray-100 sm:text-3xl sm:truncate">
              Activities
            </h1>
            <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
              Track and manage your shared activities and experiences
            </p>
          </div>
          <div className="mt-4 flex md:mt-0 md:ml-4">
            <Link
              href="/activities/new"
              className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
              New Activity
            </Link>
          </div>
        </div>

        {/* Quick Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          {/* Total Activities */}
          <div className="bg-white dark:bg-gray-800 overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
                    <span className="text-white text-sm">📅</span>
                  </div>
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 dark:text-gray-400 truncate">
                      Total Activities
                    </dt>
                    <dd className="text-lg font-medium text-gray-900 dark:text-gray-100">
                      {insightsLoading ? '...' : insights?.total_activities || activities.length}
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>

          {/* This Month */}
          <div className="bg-white dark:bg-gray-800 overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center">
                    <span className="text-white text-sm">📊</span>
                  </div>
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 dark:text-gray-400 truncate">
                      This Month
                    </dt>
                    <dd className="text-lg font-medium text-gray-900 dark:text-gray-100">
                      {insightsLoading ? '...' : insights?.activities_this_month || 0}
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>

          {/* Average Rating */}
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
                      {insightsLoading ? '...' : insights?.average_quality_rating ? 
                        `${insights.average_quality_rating.toFixed(1)}/10` : 'N/A'}
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>

          {/* Total Spent */}
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
                      {insightsLoading ? '...' : insights?.total_spent ? 
                        `$${insights.total_spent}` : '$0'}
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Upcoming Activities */}
        {!upcomingLoading && upcomingActivities.length > 0 && (
          <div className="mb-8">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-medium text-gray-900 dark:text-gray-100">
                Upcoming Activities
              </h2>
              <Link
                href="/activities?filter=upcoming"
                className="text-sm text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300"
              >
                View all
              </Link>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {upcomingActivities.slice(0, 3).map(activity => (
                <ActivityCard
                  key={activity.id}
                  activity={activity}
                  onClick={handleActivityClick}
                  onEdit={handleActivityEdit}
                  onDelete={handleActivityDelete}
                />
              ))}
            </div>
          </div>
        )}

        {/* Recent Activities */}
        {!recentLoading && recentActivities.length > 0 && (
          <div className="mb-8">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-medium text-gray-900 dark:text-gray-100">
                Recent Activities
              </h2>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {recentActivities.slice(0, 3).map(activity => (
                <ActivityCard
                  key={activity.id}
                  activity={activity}
                  onClick={handleActivityClick}
                  onEdit={handleActivityEdit}
                  onDelete={handleActivityDelete}
                />
              ))}
            </div>
          </div>
        )}

        {/* View Controls */}
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-lg font-medium text-gray-900 dark:text-gray-100">
            All Activities
          </h2>
          <div className="flex items-center space-x-4">
            {/* Timeline Grouping */}
            {viewMode === 'timeline' && (
              <div className="flex items-center space-x-2">
                <label className="text-sm text-gray-600 dark:text-gray-400">Group by:</label>
                <select
                  value={timelineGroupBy}
                  onChange={(e) => setTimelineGroupBy(e.target.value as 'month' | 'week' | 'day')}
                  className="text-sm px-2 py-1 border border-gray-300 dark:border-gray-600 rounded dark:bg-gray-700 dark:text-gray-100"
                >
                  <option value="month">Month</option>
                  <option value="week">Week</option>
                  <option value="day">Day</option>
                </select>
              </div>
            )}

            {/* View Mode Toggle */}
            <div className="flex items-center space-x-1 bg-gray-100 dark:bg-gray-700 rounded-lg p-1">
              <button
                onClick={() => setViewMode('timeline')}
                className={`px-3 py-1 text-sm rounded-md transition-colors ${
                  viewMode === 'timeline'
                    ? 'bg-white dark:bg-gray-600 text-gray-900 dark:text-gray-100 shadow-sm'
                    : 'text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-gray-100'
                }`}
              >
                Timeline
              </button>
              <button
                onClick={() => setViewMode('grid')}
                className={`px-3 py-1 text-sm rounded-md transition-colors ${
                  viewMode === 'grid'
                    ? 'bg-white dark:bg-gray-600 text-gray-900 dark:text-gray-100 shadow-sm'
                    : 'text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-gray-100'
                }`}
              >
                Grid
              </button>
            </div>
          </div>
        </div>

        {/* Activities List */}
        {viewMode === 'timeline' ? (
          <ActivityTimeline
            activities={activities}
            groupBy={timelineGroupBy}
            onActivityClick={handleActivityClick}
            onActivityEdit={handleActivityEdit}
            onActivityDelete={handleActivityDelete}
          />
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {activities.map(activity => (
              <ActivityCard
                key={activity.id}
                activity={activity}
                onClick={handleActivityClick}
                onEdit={handleActivityEdit}
                onDelete={handleActivityDelete}
              />
            ))}
          </div>
        )}

        {/* Empty State */}
        {activities.length === 0 && (
          <div className="text-center py-12">
            <div className="text-gray-400 dark:text-gray-500 mb-4">
              <svg className="mx-auto h-12 w-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
            </div>
            <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">
              No activities yet
            </h3>
            <p className="text-gray-500 dark:text-gray-400 mb-4">
              Start tracking your shared activities and experiences.
            </p>
            <Link
              href="/activities/new"
              className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              Create Your First Activity
            </Link>
          </div>
        )}
      </div>
    </div>
  );
}