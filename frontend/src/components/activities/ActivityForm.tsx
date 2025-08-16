'use client';

import React, { useState, useEffect } from 'react';
import {
  SharedActivity,
  SharedActivityCreate,
  SharedActivityUpdate,
  SharedActivityParticipantCreate,
  ACTIVITY_TYPES,
  PARTICIPATION_LEVELS,
  ATTENDANCE_STATUS,
  ACTIVITY_STATUS,
} from '../../types/Activity';
import { Contact } from '../../services/contacts';

interface ActivityFormProps {
  activity?: SharedActivity;
  contacts: Contact[];
  onSubmit: (activity: SharedActivityCreate | SharedActivityUpdate) => void;
  onCancel: () => void;
  loading?: boolean;
  className?: string;
}

interface FormErrors {
  title?: string;
  activity_type?: string;
  activity_date?: string;
  participants?: string;
  cost_per_person?: string;
  total_cost?: string;
  quality_rating?: string;
  general?: string;
}

export const ActivityForm: React.FC<ActivityFormProps> = ({
  activity,
  contacts,
  onSubmit,
  onCancel,
  loading = false,
  className = '',
}) => {
  const isEditing = !!activity;

  const [formData, setFormData] = useState<SharedActivityCreate>({
    activity_type: activity?.activity_type || '',
    title: activity?.title || '',
    description: activity?.description || '',
    location: activity?.location || '',
    activity_date: activity?.activity_date || '',
    start_time: activity?.start_time || '',
    end_time: activity?.end_time || '',
    duration_minutes: activity?.duration_minutes || undefined,
    cost_per_person: activity?.cost_per_person || undefined,
    total_cost: activity?.total_cost || undefined,
    currency: activity?.currency || 'USD',
    quality_rating: activity?.quality_rating || undefined,
    notes: activity?.notes || '',
    memorable_moments: activity?.memorable_moments || '',
    status: activity?.status || 'planned',
    is_private: activity?.is_private || false,
    participants: activity?.participants.map(p => ({
      contact_id: p.contact_id,
      participation_level: p.participation_level,
      attendance_status: p.attendance_status,
      participant_notes: p.participant_notes,
      satisfaction_rating: p.satisfaction_rating,
    })) || [],
  });

  const [errors, setErrors] = useState<FormErrors>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [selectedContacts, setSelectedContacts] = useState<number[]>(
    activity?.participants.map(p => p.contact_id) || []
  );

  const updateFormData = <K extends keyof SharedActivityCreate>(
    field: K,
    value: SharedActivityCreate[K]
  ) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    
    // Clear field-specific error when user starts typing
    if (errors[field as keyof FormErrors]) {
      setErrors(prev => ({ ...prev, [field]: undefined }));
    }
  };

  const validateForm = (): boolean => {
    const newErrors: FormErrors = {};

    if (!formData.title.trim()) {
      newErrors.title = 'Title is required';
    }

    if (!formData.activity_type) {
      newErrors.activity_type = 'Activity type is required';
    }

    if (!formData.activity_date) {
      newErrors.activity_date = 'Activity date is required';
    }

    if (formData.participants.length === 0) {
      newErrors.participants = 'At least one participant is required';
    }

    // Check for at least one organizer
    const organizers = formData.participants.filter(p => p.participation_level === 'organizer');
    if (organizers.length === 0 && formData.participants.length > 0) {
      newErrors.participants = 'At least one organizer is required';
    }

    if (formData.cost_per_person && formData.cost_per_person < 0) {
      newErrors.cost_per_person = 'Cost per person must be positive';
    }

    if (formData.total_cost && formData.total_cost < 0) {
      newErrors.total_cost = 'Total cost must be positive';
    }

    if (formData.quality_rating && (formData.quality_rating < 1 || formData.quality_rating > 10)) {
      newErrors.quality_rating = 'Quality rating must be between 1 and 10';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    setIsSubmitting(true);
    setErrors({});

    try {
      const isValid = validateForm();
      
      if (!isValid) {
        setIsSubmitting(false);
        return;
      }

      if (isEditing) {
        const updateData: SharedActivityUpdate = {
          activity_type: formData.activity_type,
          title: formData.title,
          description: formData.description || undefined,
          location: formData.location || undefined,
          activity_date: formData.activity_date,
          start_time: formData.start_time || undefined,
          end_time: formData.end_time || undefined,
          duration_minutes: formData.duration_minutes || undefined,
          cost_per_person: formData.cost_per_person || undefined,
          total_cost: formData.total_cost || undefined,
          currency: formData.currency,
          quality_rating: formData.quality_rating || undefined,
          notes: formData.notes || undefined,
          memorable_moments: formData.memorable_moments || undefined,
          status: formData.status,
          is_private: formData.is_private,
        };
        onSubmit(updateData);
      } else {
        onSubmit(formData);
      }
    } catch (error: unknown) {
      console.error('Error submitting activity:', error);
      setErrors({ general: 'An error occurred while saving the activity. Please try again.' });
    } finally {
      setIsSubmitting(false);
    }
  };

  const toggleContact = (contactId: number) => {
    const isSelected = selectedContacts.includes(contactId);
    let newSelected: number[];
    let newParticipants: SharedActivityParticipantCreate[];

    if (isSelected) {
      newSelected = selectedContacts.filter(id => id !== contactId);
      newParticipants = formData.participants.filter(p => p.contact_id !== contactId);
    } else {
      newSelected = [...selectedContacts, contactId];
      newParticipants = [
        ...formData.participants,
        {
          contact_id: contactId,
          participation_level: 'participant',
          attendance_status: 'confirmed',
        },
      ];
    }

    setSelectedContacts(newSelected);
    updateFormData('participants', newParticipants);
  };

  const updateParticipant = (
    contactId: number,
    field: keyof SharedActivityParticipantCreate,
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    value: any
  ) => {
    const updatedParticipants = formData.participants.map(p =>
      p.contact_id === contactId ? { ...p, [field]: value } : p
    );
    updateFormData('participants', updatedParticipants);
  };

  const getActivityTypeIcon = (type: string) => {
    const activityType = ACTIVITY_TYPES.find(t => t.value === type);
    return activityType?.icon || '📝';
  };

  return (
    <div className={`bg-white dark:bg-gray-800 rounded-lg shadow-lg ${className}`}>
      <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100">
          {isEditing ? 'Edit Activity' : 'Create New Activity'}
        </h2>
      </div>

      <form onSubmit={handleSubmit} className="p-6 space-y-6">
        {/* General Error */}
        {errors.general && (
          <div className="p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-md">
            <p className="text-sm text-red-600 dark:text-red-400">{errors.general}</p>
          </div>
        )}

        {/* Title */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Title *
          </label>
          <input
            type="text"
            value={formData.title}
            onChange={(e) => updateFormData('title', e.target.value)}
            className={`w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-gray-100 ${
              errors.title ? 'border-red-300 dark:border-red-600' : 'border-gray-300 dark:border-gray-600'
            }`}
            placeholder="What's the activity?"
            disabled={loading || isSubmitting}
          />
          {errors.title && (
            <p className="mt-1 text-sm text-red-600 dark:text-red-400">{errors.title}</p>
          )}
        </div>

        {/* Activity Type */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Activity Type *
          </label>
          <div className="grid grid-cols-3 md:grid-cols-5 gap-2">
            {ACTIVITY_TYPES.map(type => (
              <button
                key={type.value}
                type="button"
                onClick={() => updateFormData('activity_type', type.value)}
                className={`flex flex-col items-center p-3 rounded-md border transition-colors ${
                  formData.activity_type === type.value
                    ? 'bg-blue-100 border-blue-300 text-blue-800 dark:bg-blue-900/20 dark:border-blue-600 dark:text-blue-400'
                    : 'bg-gray-50 border-gray-200 text-gray-700 hover:bg-gray-100 dark:bg-gray-700 dark:border-gray-600 dark:text-gray-300 dark:hover:bg-gray-600'
                }`}
                disabled={loading || isSubmitting}
              >
                <span className="text-2xl mb-1">{type.icon}</span>
                <span className="text-xs font-medium">{type.label}</span>
              </button>
            ))}
          </div>
          {errors.activity_type && (
            <p className="mt-1 text-sm text-red-600 dark:text-red-400">{errors.activity_type}</p>
          )}
        </div>

        {/* Description */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Description
          </label>
          <textarea
            value={formData.description}
            onChange={(e) => updateFormData('description', e.target.value)}
            rows={3}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-gray-100"
            placeholder="Describe the activity..."
            disabled={loading || isSubmitting}
          />
        </div>

        {/* Date and Time */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Date *
            </label>
            <input
              type="date"
              value={formData.activity_date}
              onChange={(e) => updateFormData('activity_date', e.target.value)}
              className={`w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-gray-100 ${
                errors.activity_date ? 'border-red-300 dark:border-red-600' : 'border-gray-300 dark:border-gray-600'
              }`}
              disabled={loading || isSubmitting}
            />
            {errors.activity_date && (
              <p className="mt-1 text-sm text-red-600 dark:text-red-400">{errors.activity_date}</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Start Time
            </label>
            <input
              type="time"
              value={formData.start_time}
              onChange={(e) => updateFormData('start_time', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-gray-100"
              disabled={loading || isSubmitting}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              End Time
            </label>
            <input
              type="time"
              value={formData.end_time}
              onChange={(e) => updateFormData('end_time', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-gray-100"
              disabled={loading || isSubmitting}
            />
          </div>
        </div>

        {/* Location */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Location
          </label>
          <input
            type="text"
            value={formData.location}
            onChange={(e) => updateFormData('location', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-gray-100"
            placeholder="Where is this happening?"
            disabled={loading || isSubmitting}
          />
        </div>

        {/* Cost Information */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Cost per Person
            </label>
            <input
              type="number"
              min="0"
              step="0.01"
              value={formData.cost_per_person || ''}
              onChange={(e) => updateFormData('cost_per_person', e.target.value ? parseFloat(e.target.value) : undefined)}
              className={`w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-gray-100 ${
                errors.cost_per_person ? 'border-red-300 dark:border-red-600' : 'border-gray-300 dark:border-gray-600'
              }`}
              placeholder="0.00"
              disabled={loading || isSubmitting}
            />
            {errors.cost_per_person && (
              <p className="mt-1 text-sm text-red-600 dark:text-red-400">{errors.cost_per_person}</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Total Cost
            </label>
            <input
              type="number"
              min="0"
              step="0.01"
              value={formData.total_cost || ''}
              onChange={(e) => updateFormData('total_cost', e.target.value ? parseFloat(e.target.value) : undefined)}
              className={`w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-gray-100 ${
                errors.total_cost ? 'border-red-300 dark:border-red-600' : 'border-gray-300 dark:border-gray-600'
              }`}
              placeholder="0.00"
              disabled={loading || isSubmitting}
            />
            {errors.total_cost && (
              <p className="mt-1 text-sm text-red-600 dark:text-red-400">{errors.total_cost}</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Currency
            </label>
            <select
              value={formData.currency}
              onChange={(e) => updateFormData('currency', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-gray-100"
              disabled={loading || isSubmitting}
            >
              <option value="USD">USD</option>
              <option value="EUR">EUR</option>
              <option value="GBP">GBP</option>
              <option value="CAD">CAD</option>
              <option value="AUD">AUD</option>
            </select>
          </div>
        </div>

        {/* Participants */}
        {contacts.length > 0 && (
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Participants *
            </label>
            <div className="space-y-3">
              {contacts.map(contact => {
                const isSelected = selectedContacts.includes(contact.id);
                const participant = formData.participants.find(p => p.contact_id === contact.id);
                
                return (
                  <div key={contact.id} className="flex items-center space-x-3 p-3 bg-gray-50 dark:bg-gray-700 rounded">
                    <input
                      type="checkbox"
                      checked={isSelected}
                      onChange={() => toggleContact(contact.id)}
                      className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                      disabled={loading || isSubmitting}
                    />
                    <div className="flex-1">
                      <p className="font-medium text-gray-900 dark:text-gray-100">
                        {contact.first_name} {contact.last_name || ''}
                      </p>
                      {contact.email && (
                        <p className="text-sm text-gray-500 dark:text-gray-400">{contact.email}</p>
                      )}
                    </div>
                    
                    {isSelected && participant && (
                      <div className="flex space-x-2">
                        <select
                          value={participant.participation_level}
                          onChange={(e) => updateParticipant(contact.id, 'participation_level', e.target.value)}
                          className="text-xs px-2 py-1 border border-gray-300 dark:border-gray-600 rounded dark:bg-gray-800 dark:text-gray-100"
                          disabled={loading || isSubmitting}
                        >
                          {PARTICIPATION_LEVELS.map(level => (
                            <option key={level.value} value={level.value}>
                              {level.label}
                            </option>
                          ))}
                        </select>
                        <select
                          value={participant.attendance_status}
                          onChange={(e) => updateParticipant(contact.id, 'attendance_status', e.target.value)}
                          className="text-xs px-2 py-1 border border-gray-300 dark:border-gray-600 rounded dark:bg-gray-800 dark:text-gray-100"
                          disabled={loading || isSubmitting}
                        >
                          {ATTENDANCE_STATUS.map(status => (
                            <option key={status.value} value={status.value}>
                              {status.label}
                            </option>
                          ))}
                        </select>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
            {errors.participants && (
              <p className="mt-1 text-sm text-red-600 dark:text-red-400">{errors.participants}</p>
            )}
          </div>
        )}

        {/* Quality Rating */}
        {formData.status === 'completed' && (
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Quality Rating (1-10)
            </label>
            <input
              type="range"
              min="1"
              max="10"
              value={formData.quality_rating || 5}
              onChange={(e) => updateFormData('quality_rating', parseInt(e.target.value))}
              className="w-full"
              disabled={loading || isSubmitting}
            />
            <div className="flex justify-between text-xs text-gray-500 dark:text-gray-400">
              <span>Poor (1)</span>
              <span>Average (5)</span>
              <span>Excellent (10)</span>
            </div>
            <p className="text-center text-sm text-gray-600 dark:text-gray-400 mt-1">
              Current: {formData.quality_rating || 5}
            </p>
            {errors.quality_rating && (
              <p className="mt-1 text-sm text-red-600 dark:text-red-400">{errors.quality_rating}</p>
            )}
          </div>
        )}

        {/* Status */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Status
          </label>
          <select
            value={formData.status}
            onChange={(e) => updateFormData('status', e.target.value as 'planned' | 'completed' | 'cancelled' | 'postponed')}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-gray-100"
            disabled={loading || isSubmitting}
          >
            {ACTIVITY_STATUS.map(status => (
              <option key={status.value} value={status.value}>
                {status.label}
              </option>
            ))}
          </select>
        </div>

        {/* Notes */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Notes
          </label>
          <textarea
            value={formData.notes}
            onChange={(e) => updateFormData('notes', e.target.value)}
            rows={3}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-gray-100"
            placeholder="Any additional notes..."
            disabled={loading || isSubmitting}
          />
        </div>

        {/* Memorable Moments */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Memorable Moments
          </label>
          <textarea
            value={formData.memorable_moments}
            onChange={(e) => updateFormData('memorable_moments', e.target.value)}
            rows={3}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-gray-100"
            placeholder="What made this special?"
            disabled={loading || isSubmitting}
          />
        </div>

        {/* Privacy Setting */}
        <div className="flex items-center">
          <input
            type="checkbox"
            id="is_private"
            checked={formData.is_private}
            onChange={(e) => updateFormData('is_private', e.target.checked)}
            className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            disabled={loading || isSubmitting}
          />
          <label htmlFor="is_private" className="ml-2 text-sm text-gray-700 dark:text-gray-300">
            Private activity (visible only to me)
          </label>
        </div>

        {/* Actions */}
        <div className="flex items-center justify-end space-x-3 pt-4 border-t border-gray-200 dark:border-gray-700">
          <button
            type="button"
            onClick={onCancel}
            className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            disabled={loading || isSubmitting}
          >
            Cancel
          </button>
          <button
            type="submit"
            className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
            disabled={loading || isSubmitting}
          >
            {isSubmitting ? 'Saving...' : isEditing ? 'Update Activity' : 'Create Activity'}
          </button>
        </div>
      </form>
    </div>
  );
};