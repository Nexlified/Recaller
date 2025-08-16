'use client';

import React, { useState, useMemo } from 'react';
import { SharedActivity } from '../../types/Activity';
import { ActivityCard } from './ActivityCard';

interface ActivityTimelineProps {
  activities: SharedActivity[];
  groupBy: 'month' | 'week' | 'day';
  onActivityClick: (activity: SharedActivity) => void;
  onActivityEdit?: (activity: SharedActivity) => void;
  onActivityDelete?: (id: number) => void;
  className?: string;
}

interface GroupedActivities {
  [key: string]: SharedActivity[];
}

export const ActivityTimeline: React.FC<ActivityTimelineProps> = ({
  activities,
  groupBy,
  onActivityClick,
  onActivityEdit,
  onActivityDelete,
  className = '',
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [filterStatus, setFilterStatus] = useState<string>('all');
  const [filterType, setFilterType] = useState<string>('all');

  // Filter activities based on search and filters
  const filteredActivities = useMemo(() => {
    return activities.filter(activity => {
      const matchesSearch = 
        activity.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        activity.description?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        activity.location?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        activity.participants.some(p => 
          p.contact?.first_name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
          p.contact?.last_name?.toLowerCase().includes(searchQuery.toLowerCase())
        );

      const matchesStatus = filterStatus === 'all' || activity.status === filterStatus;
      const matchesType = filterType === 'all' || activity.activity_type === filterType;

      return matchesSearch && matchesStatus && matchesType;
    });
  }, [activities, searchQuery, filterStatus, filterType]);

  // Group activities by the specified time period
  const groupedActivities = useMemo(() => {
    const groups: GroupedActivities = {};

    filteredActivities.forEach(activity => {
      const date = new Date(activity.activity_date);
      let groupKey: string;

      switch (groupBy) {
        case 'day':
          groupKey = date.toLocaleDateString('en-US', {
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric',
          });
          break;
        case 'week':
          const startOfWeek = new Date(date);
          startOfWeek.setDate(date.getDate() - date.getDay());
          const endOfWeek = new Date(startOfWeek);
          endOfWeek.setDate(startOfWeek.getDate() + 6);
          groupKey = `Week of ${startOfWeek.toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric',
          })} - ${endOfWeek.toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric',
            year: 'numeric',
          })}`;
          break;
        case 'month':
          groupKey = date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
          });
          break;
      }

      if (!groups[groupKey]) {
        groups[groupKey] = [];
      }
      groups[groupKey].push(activity);
    });

    // Sort activities within each group by date
    Object.keys(groups).forEach(key => {
      groups[key].sort((a, b) => 
        new Date(b.activity_date).getTime() - new Date(a.activity_date).getTime()
      );
    });

    return groups;
  }, [filteredActivities, groupBy]);

  // Sort group keys chronologically (most recent first)
  const sortedGroupKeys = useMemo(() => {
    return Object.keys(groupedActivities).sort((a, b) => {
      // For month grouping, parse the month/year
      if (groupBy === 'month') {
        const dateA = new Date(a + ' 1');
        const dateB = new Date(b + ' 1');
        return dateB.getTime() - dateA.getTime();
      }
      
      // For week grouping, parse the start date
      if (groupBy === 'week') {
        const startDateA = a.split(' - ')[0].replace('Week of ', '');
        const startDateB = b.split(' - ')[0].replace('Week of ', '');
        const dateA = new Date(startDateA + ', ' + new Date().getFullYear());
        const dateB = new Date(startDateB + ', ' + new Date().getFullYear());
        return dateB.getTime() - dateA.getTime();
      }
      
      // For day grouping, compare the full dates
      const dateA = new Date(a);
      const dateB = new Date(b);
      return dateB.getTime() - dateA.getTime();
    });
  }, [groupedActivities, groupBy]);

  const getUniqueActivityTypes = () => {
    const types = new Set(activities.map(a => a.activity_type));
    return Array.from(types);
  };

  const handleActivityEdit = (activity: SharedActivity) => {
    if (onActivityEdit) {
      onActivityEdit(activity);
    }
  };

  const handleActivityDelete = (id: number) => {
    if (onActivityDelete) {
      onActivityDelete(id);
    }
  };

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Search and Filters */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-4">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {/* Search */}
          <div className="md:col-span-2">
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Search Activities
            </label>
            <div className="relative">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search by title, description, location, or participants..."
                className="w-full pl-10 pr-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-gray-100"
              />
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <svg className="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </div>
            </div>
          </div>

          {/* Status Filter */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Status
            </label>
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-gray-100"
            >
              <option value="all">All Statuses</option>
              <option value="planned">Planned</option>
              <option value="completed">Completed</option>
              <option value="cancelled">Cancelled</option>
              <option value="postponed">Postponed</option>
            </select>
          </div>

          {/* Type Filter */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Type
            </label>
            <select
              value={filterType}
              onChange={(e) => setFilterType(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-gray-100"
            >
              <option value="all">All Types</option>
              {getUniqueActivityTypes().map(type => (
                <option key={type} value={type}>
                  {type.charAt(0).toUpperCase() + type.slice(1).replace('_', ' ')}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Results Summary */}
        <div className="mt-4 flex items-center justify-between text-sm text-gray-600 dark:text-gray-400">
          <span>
            {filteredActivities.length} of {activities.length} activities
          </span>
          {(searchQuery || filterStatus !== 'all' || filterType !== 'all') && (
            <button
              onClick={() => {
                setSearchQuery('');
                setFilterStatus('all');
                setFilterType('all');
              }}
              className="text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300"
            >
              Clear filters
            </button>
          )}
        </div>
      </div>

      {/* Timeline */}
      {sortedGroupKeys.length === 0 ? (
        <div className="text-center py-12">
          <div className="text-gray-400 dark:text-gray-500 mb-4">
            <svg className="mx-auto h-12 w-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
          </div>
          <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">
            No activities found
          </h3>
          <p className="text-gray-500 dark:text-gray-400">
            {searchQuery || filterStatus !== 'all' || filterType !== 'all'
              ? 'Try adjusting your search or filters.'
              : 'No activities have been created yet.'}
          </p>
        </div>
      ) : (
        <div className="space-y-8">
          {sortedGroupKeys.map(groupKey => (
            <div key={groupKey} className="relative">
              {/* Group Header */}
              <div className="sticky top-0 z-10 bg-gray-50 dark:bg-gray-900 border-b border-gray-200 dark:border-gray-700 px-4 py-3 rounded-t-lg">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                  {groupKey}
                </h3>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  {groupedActivities[groupKey].length} activities
                </p>
              </div>

              {/* Activities Grid */}
              <div className="bg-gray-50 dark:bg-gray-900 px-4 pb-4 rounded-b-lg">
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 pt-4">
                  {groupedActivities[groupKey].map(activity => (
                    <ActivityCard
                      key={activity.id}
                      activity={activity}
                      onClick={onActivityClick}
                      onEdit={handleActivityEdit}
                      onDelete={handleActivityDelete}
                      className="transform transition-transform hover:scale-105"
                    />
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Load More / Pagination could go here */}
    </div>
  );
};