'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { ActivityForm } from '../../../components/activities/ActivityForm';
import { SharedActivityCreate } from '../../../types/Activity';
import { Contact } from '../../../services/contacts';
import { useActivities } from '../../../hooks/useActivities';
import contactsService from '../../../services/contacts';

export default function NewActivityPage() {
  const router = useRouter();
  const { createActivity } = useActivities({ autoLoad: false });
  const [contacts, setContacts] = useState<Contact[]>([]);
  const [contactsLoading, setContactsLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    loadContacts();
  }, []);

  const loadContacts = async () => {
    try {
      setContactsLoading(true);
      const data = await contactsService.getContacts();
      setContacts(data);
    } catch (error) {
      console.error('Error loading contacts:', error);
    } finally {
      setContactsLoading(false);
    }
  };

  const handleSubmit = async (activityData: SharedActivityCreate | SharedActivityUpdate) => {
    try {
      setSubmitting(true);
      const newActivity = await createActivity(activityData as SharedActivityCreate);
      router.push(`/activities/${newActivity.id}`);
    } catch (error) {
      console.error('Error creating activity:', error);
      // Error will be handled by the form component
    } finally {
      setSubmitting(false);
    }
  };

  const handleCancel = () => {
    router.back();
  };

  if (contactsLoading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="animate-pulse space-y-8">
            <div className="h-8 bg-gray-200 dark:bg-gray-700 rounded w-1/3"></div>
            <div className="h-96 bg-gray-200 dark:bg-gray-700 rounded-lg"></div>
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
                Create New Activity
              </h1>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                Plan and track your shared activities and experiences
              </p>
            </div>
          </div>
        </div>

        {/* Activity Creation Wizard/Form */}
        <div className="space-y-8">
          {/* Quick Tips */}
          <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
            <div className="flex">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-blue-400" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3">
                <h3 className="text-sm font-medium text-blue-800 dark:text-blue-400">
                  Tips for creating great activities
                </h3>
                <div className="mt-2 text-sm text-blue-700 dark:text-blue-300">
                  <ul className="list-disc list-inside space-y-1">
                    <li>Choose a clear, descriptive title that captures the essence of your activity</li>
                    <li>Add participants to share the experience and track who's involved</li>
                    <li>Include location details to remember where special moments happened</li>
                    <li>Set at least one person as an organizer for each activity</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>

          {/* Activity Templates (Future Feature) */}
          <div className="bg-white dark:bg-gray-800 shadow rounded-lg">
            <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
              <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100">Quick Start Templates</h3>
              <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                Choose a template to get started quickly, or create from scratch below
              </p>
            </div>
            <div className="px-6 py-4">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {[
                  { type: 'dinner', icon: '🍽️', label: 'Dinner Out', description: 'Restaurant meal with friends' },
                  { type: 'movie', icon: '🎬', label: 'Movie Night', description: 'Cinema or home viewing' },
                  { type: 'coffee', icon: '☕', label: 'Coffee Chat', description: 'Casual meetup over coffee' },
                  { type: 'sports', icon: '⚽', label: 'Sports Activity', description: 'Playing or watching sports' },
                ].map(template => (
                  <button
                    key={template.type}
                    className="p-4 border border-gray-200 dark:border-gray-600 rounded-lg hover:border-blue-300 dark:hover:border-blue-600 hover:bg-blue-50 dark:hover:bg-blue-900/20 transition-colors text-left"
                    onClick={() => {
                      // Future: Pre-fill form with template data
                      const form = document.querySelector('form');
                      if (form) {
                        form.scrollIntoView({ behavior: 'smooth' });
                      }
                    }}
                  >
                    <div className="text-2xl mb-2">{template.icon}</div>
                    <h4 className="font-medium text-gray-900 dark:text-gray-100 text-sm">{template.label}</h4>
                    <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">{template.description}</p>
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Main Form */}
          <ActivityForm
            contacts={contacts}
            onSubmit={handleSubmit}
            onCancel={handleCancel}
            loading={submitting}
          />

          {/* Help Section */}
          <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-6">
            <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-4">Need Help?</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h4 className="font-medium text-gray-900 dark:text-gray-100 mb-2">Activity Types</h4>
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                  Choose the type that best describes your activity. This helps with organization and insights.
                </p>
                <ul className="text-sm text-gray-600 dark:text-gray-400 space-y-1">
                  <li>• <strong>Dinner:</strong> Restaurant meals, home dinners, food events</li>
                  <li>• <strong>Movie:</strong> Cinema visits, streaming parties, film festivals</li>
                  <li>• <strong>Sports:</strong> Playing sports, watching games, fitness activities</li>
                  <li>• <strong>Travel:</strong> Trips, vacations, day excursions</li>
                </ul>
              </div>
              <div>
                <h4 className="font-medium text-gray-900 dark:text-gray-100 mb-2">Participant Roles</h4>
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                  Assign roles to help organize responsibilities and track involvement.
                </p>
                <ul className="text-sm text-gray-600 dark:text-gray-400 space-y-1">
                  <li>• <strong>Organizer:</strong> Plans and coordinates the activity</li>
                  <li>• <strong>Participant:</strong> Actively joins the activity</li>
                  <li>• <strong>Invitee:</strong> Invited but hasn't confirmed yet</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}