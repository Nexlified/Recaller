'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { useParams, useRouter } from 'next/navigation';
import { SharedActivity, ACTIVITY_TYPES } from '../../../types/Activity';
import activityService from '../../../services/activityService';

interface ActivityDetailPageProps {
  params: { id: string };
}

export default function ActivityDetailPage({ params }: ActivityDetailPageProps) {
  const router = useRouter();
  const { id } = params;
  const [activity, setActivity] = useState<SharedActivity | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (id) {
      loadActivity();
    }
  }, [id]);

  const loadActivity = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await activityService.getActivity(parseInt(id));
      setActivity(data);
    } catch (err) {
      console.error('Error loading activity:', err);
      setError(err instanceof Error ? err.message : 'Failed to load activity');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!activity || !window.confirm('Are you sure you want to delete this activity?')) {
      return;
    }

    try {
      await activityService.deleteActivity(activity.id);
      router.push('/activities');
    } catch (err) {
      console.error('Error deleting activity:', err);
      setError(err instanceof Error ? err.message : 'Failed to delete activity');
    }
  };

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
      weekday: 'long',
      year: 'numeric',
      month: 'long',
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

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="animate-pulse space-y-8">
            <div className="h-8 bg-gray-200 dark:bg-gray-700 rounded w-1/3"></div>
            <div className="h-64 bg-gray-200 dark:bg-gray-700 rounded-lg"></div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="h-32 bg-gray-200 dark:bg-gray-700 rounded-lg"></div>
              <div className="h-32 bg-gray-200 dark:bg-gray-700 rounded-lg"></div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error || !activity) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center">
            <div className="text-red-400 mb-4">
              <svg className="mx-auto h-12 w-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
              </svg>
            </div>
            <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">
              {error || 'Activity not found'}
            </h3>
            <div className="space-x-3">
              <button
                onClick={() => router.back()}
                className="inline-flex items-center px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700"
              >
                Go Back
              </button>
              <Link
                href="/activities"
                className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700"
              >
                View All Activities
              </Link>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <Link
                href="/activities"
                className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
                </svg>
              </Link>
              <div>
                <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                  {activity.title}
                </h1>
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  {getActivityTypeLabel(activity.activity_type)}
                </p>
              </div>
            </div>
            
            <div className="flex items-center space-x-3">
              <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(activity.status)}`}>
                {activity.status.charAt(0).toUpperCase() + activity.status.slice(1)}
              </span>
              <Link
                href={`/activities/${activity.id}/edit`}
                className="inline-flex items-center px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700"
              >
                <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                </svg>
                Edit
              </Link>
              <button
                onClick={handleDelete}
                className="inline-flex items-center px-3 py-2 border border-red-300 dark:border-red-600 rounded-md shadow-sm text-sm font-medium text-red-700 dark:text-red-400 bg-white dark:bg-gray-800 hover:bg-red-50 dark:hover:bg-red-900/20"
              >
                <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
                Delete
              </button>
            </div>
          </div>
        </div>

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Column - Main Details */}
          <div className="lg:col-span-2 space-y-6">
            {/* Activity Overview Card */}
            <div className="bg-white dark:bg-gray-800 shadow rounded-lg">
              <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
                <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100">Activity Details</h3>
              </div>
              <div className="px-6 py-4 space-y-4">
                <div className="flex items-center space-x-3">
                  <span className="text-3xl">{getActivityTypeIcon(activity.activity_type)}</span>
                  <div>
                    <p className="text-sm font-medium text-gray-500 dark:text-gray-400">Activity Type</p>
                    <p className="text-base text-gray-900 dark:text-gray-100">{getActivityTypeLabel(activity.activity_type)}</p>
                  </div>
                </div>

                <div className="flex items-center space-x-3">
                  <span className="text-xl">📅</span>
                  <div>
                    <p className="text-sm font-medium text-gray-500 dark:text-gray-400">Date & Time</p>
                    <p className="text-base text-gray-900 dark:text-gray-100">
                      {formatDate(activity.activity_date)}
                      {activity.start_time && (
                        <span className="ml-2">
                          at {formatTime(activity.start_time)}
                          {activity.end_time && ` - ${formatTime(activity.end_time)}`}
                        </span>
                      )}
                    </p>
                  </div>
                </div>

                {activity.location && (
                  <div className="flex items-center space-x-3">
                    <span className="text-xl">📍</span>
                    <div>
                      <p className="text-sm font-medium text-gray-500 dark:text-gray-400">Location</p>
                      <p className="text-base text-gray-900 dark:text-gray-100">{activity.location}</p>
                    </div>
                  </div>
                )}

                {(activity.cost_per_person || activity.total_cost) && (
                  <div className="flex items-center space-x-3">
                    <span className="text-xl">💰</span>
                    <div>
                      <p className="text-sm font-medium text-gray-500 dark:text-gray-400">Cost</p>
                      <p className="text-base text-gray-900 dark:text-gray-100">
                        {activity.cost_per_person && (
                          <span>{activity.currency} {activity.cost_per_person} per person</span>
                        )}
                        {activity.total_cost && activity.cost_per_person && (
                          <span className="mx-2">•</span>
                        )}
                        {activity.total_cost && (
                          <span>{activity.currency} {activity.total_cost} total</span>
                        )}
                      </p>
                    </div>
                  </div>
                )}

                {activity.quality_rating && activity.status === 'completed' && (
                  <div className="flex items-center space-x-3">
                    <span className="text-xl">⭐</span>
                    <div>
                      <p className="text-sm font-medium text-gray-500 dark:text-gray-400">Quality Rating</p>
                      <div className="flex items-center space-x-2">
                        <span className="text-base text-gray-900 dark:text-gray-100">{activity.quality_rating}/10</span>
                        <div className="flex">
                          {Array.from({ length: 5 }, (_, i) => (
                            <span
                              key={i}
                              className={`text-sm ${
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
                  </div>
                )}
              </div>
            </div>

            {/* Description */}
            {activity.description && (
              <div className="bg-white dark:bg-gray-800 shadow rounded-lg">
                <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
                  <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100">Description</h3>
                </div>
                <div className="px-6 py-4">
                  <p className="text-gray-700 dark:text-gray-300 whitespace-pre-wrap">{activity.description}</p>
                </div>
              </div>
            )}

            {/* Memorable Moments */}
            {activity.memorable_moments && (
              <div className="bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-lg">
                <div className="px-6 py-4 border-b border-amber-200 dark:border-amber-800">
                  <h3 className="text-lg font-medium text-amber-800 dark:text-amber-400 flex items-center">
                    <span className="mr-2">💫</span>
                    Memorable Moments
                  </h3>
                </div>
                <div className="px-6 py-4">
                  <p className="text-amber-800 dark:text-amber-400 whitespace-pre-wrap">{activity.memorable_moments}</p>
                </div>
              </div>
            )}

            {/* Notes */}
            {activity.notes && (
              <div className="bg-white dark:bg-gray-800 shadow rounded-lg">
                <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
                  <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100">Notes</h3>
                </div>
                <div className="px-6 py-4">
                  <p className="text-gray-700 dark:text-gray-300 whitespace-pre-wrap">{activity.notes}</p>
                </div>
              </div>
            )}

            {/* Photos */}
            {activity.photos && activity.photos.length > 0 && (
              <div className="bg-white dark:bg-gray-800 shadow rounded-lg">
                <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
                  <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100">Photos</h3>
                </div>
                <div className="px-6 py-4">
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                    {activity.photos.map((photo) => (
                      <div key={photo.id} className="aspect-square bg-gray-100 dark:bg-gray-700 rounded-lg overflow-hidden">
                        <img
                          src={photo.url}
                          alt={photo.caption || 'Activity photo'}
                          className="w-full h-full object-cover hover:scale-105 transition-transform cursor-pointer"
                        />
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Right Column - Participants & Meta */}
          <div className="space-y-6">
            {/* Participants */}
            <div className="bg-white dark:bg-gray-800 shadow rounded-lg">
              <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
                <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100">Participants</h3>
              </div>
              <div className="px-6 py-4">
                <div className="space-y-3">
                  {activity.participants.map(participant => (
                    <div key={participant.id} className="flex items-center space-x-3">
                      <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
                        <span className="text-xs font-medium text-white">
                          {participant.contact?.first_name?.[0]?.toUpperCase() || 'U'}
                        </span>
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-gray-900 dark:text-gray-100">
                          {participant.contact?.first_name} {participant.contact?.last_name || ''}
                        </p>
                        <div className="flex items-center space-x-2 text-xs text-gray-500 dark:text-gray-400">
                          <span className={`px-2 py-1 rounded-full ${
                            participant.participation_level === 'organizer' 
                              ? 'bg-purple-100 text-purple-800 dark:bg-purple-900/20 dark:text-purple-400'
                              : participant.participation_level === 'participant'
                              ? 'bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-400'
                              : 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300'
                          }`}>
                            {participant.participation_level}
                          </span>
                          <span className={`px-2 py-1 rounded-full ${
                            participant.attendance_status === 'attended' 
                              ? 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400'
                              : participant.attendance_status === 'confirmed'
                              ? 'bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-400'
                              : participant.attendance_status === 'declined'
                              ? 'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400'
                              : 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-400'
                          }`}>
                            {participant.attendance_status}
                          </span>
                        </div>
                        {participant.participant_notes && (
                          <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                            {participant.participant_notes}
                          </p>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Activity Meta */}
            <div className="bg-white dark:bg-gray-800 shadow rounded-lg">
              <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
                <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100">Activity Info</h3>
              </div>
              <div className="px-6 py-4 space-y-3">
                <div>
                  <p className="text-sm font-medium text-gray-500 dark:text-gray-400">Created</p>
                  <p className="text-sm text-gray-900 dark:text-gray-100">
                    {new Date(activity.created_at).toLocaleDateString('en-US', {
                      year: 'numeric',
                      month: 'long',
                      day: 'numeric',
                      hour: 'numeric',
                      minute: '2-digit',
                    })}
                  </p>
                </div>
                
                {activity.updated_at && (
                  <div>
                    <p className="text-sm font-medium text-gray-500 dark:text-gray-400">Last Updated</p>
                    <p className="text-sm text-gray-900 dark:text-gray-100">
                      {new Date(activity.updated_at).toLocaleDateString('en-US', {
                        year: 'numeric',
                        month: 'long',
                        day: 'numeric',
                        hour: 'numeric',
                        minute: '2-digit',
                      })}
                    </p>
                  </div>
                )}

                <div>
                  <p className="text-sm font-medium text-gray-500 dark:text-gray-400">Privacy</p>
                  <p className="text-sm text-gray-900 dark:text-gray-100 flex items-center">
                    {activity.is_private ? (
                      <>
                        <span className="mr-1">🔒</span>
                        Private
                      </>
                    ) : (
                      <>
                        <span className="mr-1">🌐</span>
                        Shared
                      </>
                    )}
                  </p>
                </div>

                {activity.duration_minutes && (
                  <div>
                    <p className="text-sm font-medium text-gray-500 dark:text-gray-400">Duration</p>
                    <p className="text-sm text-gray-900 dark:text-gray-100">
                      {Math.floor(activity.duration_minutes / 60)}h {activity.duration_minutes % 60}m
                    </p>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}