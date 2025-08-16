'use client';

import React, { useState } from 'react';
import { ContactCreate, Contact, ContactVisibility } from '../../services/contacts';
import contactsService from '../../services/contacts';
import { RelationshipManager } from './RelationshipManager';

interface ContactFormProps {
  onSuccess?: (contact: Contact) => void;
  onCancel?: () => void;
  demoMode?: boolean;
  editingContact?: Contact | null;
  onRelationshipChange?: () => void;
}

interface FormErrors {
  first_name?: string;
  last_name?: string;
  email?: string;
  phone?: string;
  general?: string;
}

export const ContactForm: React.FC<ContactFormProps> = ({ onSuccess, onCancel, demoMode = false, editingContact = null, onRelationshipChange }) => {
  const isEditing = !!editingContact;
  
  const [formData, setFormData] = useState<ContactCreate>({
    first_name: editingContact?.first_name || '',
    last_name: editingContact?.last_name || '',
    email: editingContact?.email || '',
    phone: editingContact?.phone || '',
    job_title: editingContact?.job_title || '',
    organization_id: editingContact?.organization_id || undefined,
    notes: editingContact?.notes || '',
    visibility: editingContact?.visibility || ContactVisibility.PRIVATE,
    is_active: editingContact?.is_active ?? true,
  });

  const [errors, setErrors] = useState<FormErrors>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);

  // Update form data
  const updateFormData = (field: keyof ContactCreate, value: string | boolean | ContactVisibility | number | undefined) => {
    const newData = { ...formData, [field]: value };
    setFormData(newData);
    
    // Clear field-specific error when user starts typing
    if (errors[field as keyof FormErrors]) {
      setErrors(prev => ({ ...prev, [field]: undefined }));
    }
  };

  const validateForm = async (): Promise<boolean> => {
    const newErrors: FormErrors = {};

    // Required field validation
    if (!formData.first_name.trim()) {
      newErrors.first_name = 'First name is required';
    }

    // Email validation
    if (formData.email) {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(formData.email)) {
        newErrors.email = 'Please enter a valid email address';
      } else if (!demoMode) {
        try {
          const emailValidation = await contactsService.validateEmail(formData.email);
          // When editing, allow the same email if it belongs to the same contact
          if (emailValidation.exists && (!isEditing || editingContact?.email !== formData.email)) {
            newErrors.email = 'A contact with this email already exists';
          }
        } catch (error) {
          console.error('Email validation error:', error);
        }
      }
    }

    // Phone validation  
    if (formData.phone) {
      const phoneRegex = /^[\+]?[1-9][\d]{0,15}$/;
      if (!phoneRegex.test(formData.phone.replace(/[\s\-\(\)]/g, ''))) {
        newErrors.phone = 'Please enter a valid phone number';
      } else if (!demoMode) {
        try {
          const phoneValidation = await contactsService.validatePhone(formData.phone);
          // When editing, allow the same phone if it belongs to the same contact
          if (phoneValidation.exists && (!isEditing || editingContact?.phone !== formData.phone)) {
            newErrors.phone = 'A contact with this phone number already exists';
          }
        } catch (error) {
          console.error('Phone validation error:', error);
        }
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    setIsSubmitting(true);
    setErrors({});

    try {
      const isValid = await validateForm();
      
      if (!isValid) {
        setIsSubmitting(false);
        return;
      }

      if (demoMode) {
        // In demo mode, just simulate success
        const mockContact: Contact = {
          id: isEditing ? editingContact!.id : Date.now(),
          tenant_id: isEditing ? editingContact!.tenant_id : 1,
          created_by_user_id: isEditing ? editingContact!.created_by_user_id : 1,
          first_name: formData.first_name,
          last_name: formData.last_name,
          email: formData.email,
          phone: formData.phone,
          job_title: formData.job_title,
          organization_id: formData.organization_id,
          notes: formData.notes,
          visibility: formData.visibility || ContactVisibility.PRIVATE,
          is_active: formData.is_active ?? true,
          created_at: isEditing ? editingContact!.created_at : new Date().toISOString(),
          updated_at: isEditing ? new Date().toISOString() : undefined,
        };
        
        if (onSuccess) {
          onSuccess(mockContact);
        }
      } else {
        let updatedContact: Contact;
        
        if (isEditing) {
          updatedContact = await contactsService.updateContact(editingContact!.id, formData);
        } else {
          updatedContact = await contactsService.createContact(formData);
        }
        
        if (onSuccess) {
          onSuccess(updatedContact);
        }
      }
      
      // Reset form only if creating a new contact
      if (!isEditing) {
        setFormData({
          first_name: '',
          last_name: '',
          email: '',
          phone: '',
          job_title: '',
          organization_id: undefined,
          notes: '',
          visibility: ContactVisibility.PRIVATE,
          is_active: true,
        });
      }
      setIsExpanded(false);
      
    } catch (error: unknown) {
      console.error('Error creating contact:', error);
      if (error && typeof error === 'object' && 'response' in error) {
        const apiError = error as { response?: { data?: { detail?: string } } };
        if (apiError.response?.data?.detail) {
          setErrors({ general: apiError.response.data.detail });
        } else {
          setErrors({ general: 'An error occurred while saving the contact. Please try again.' });
        }
      } else {
        setErrors({ general: 'An error occurred while saving the contact. Please try again.' });
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto bg-white shadow-md rounded-lg p-6">
      <h2 className="text-2xl font-bold text-gray-900 mb-6">
        {isEditing ? 'Edit Contact' : 'Create New Contact'}
      </h2>
      
      {errors.general && (
        <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
          {errors.general}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Basic Required Fields */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label htmlFor="first_name" className="block text-sm font-medium text-gray-700 mb-1">
              First Name *
            </label>
            <input
              type="text"
              id="first_name"
              value={formData.first_name}
              onChange={(e) => updateFormData('first_name', e.target.value)}
              className={`w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                errors.first_name ? 'border-red-300' : 'border-gray-300'
              }`}
              disabled={isSubmitting}
            />
            {errors.first_name && (
              <p className="mt-1 text-sm text-red-600">{errors.first_name}</p>
            )}
          </div>

          <div>
            <label htmlFor="last_name" className="block text-sm font-medium text-gray-700 mb-1">
              Last Name
            </label>
            <input
              type="text"
              id="last_name"
              value={formData.last_name || ''}
              onChange={(e) => updateFormData('last_name', e.target.value)}
              className={`w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                errors.last_name ? 'border-red-300' : 'border-gray-300'
              }`}
              disabled={isSubmitting}
            />
            {errors.last_name && (
              <p className="mt-1 text-sm text-red-600">{errors.last_name}</p>
            )}
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
              Email
            </label>
            <input
              type="email"
              id="email"
              value={formData.email || ''}
              onChange={(e) => updateFormData('email', e.target.value)}
              className={`w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                errors.email ? 'border-red-300' : 'border-gray-300'
              }`}
              disabled={isSubmitting}
            />
            {errors.email && (
              <p className="mt-1 text-sm text-red-600">{errors.email}</p>
            )}
          </div>

          <div>
            <label htmlFor="phone" className="block text-sm font-medium text-gray-700 mb-1">
              Phone
            </label>
            <input
              type="tel"
              id="phone"
              value={formData.phone || ''}
              onChange={(e) => updateFormData('phone', e.target.value)}
              className={`w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                errors.phone ? 'border-red-300' : 'border-gray-300'
              }`}
              disabled={isSubmitting}
            />
            {errors.phone && (
              <p className="mt-1 text-sm text-red-600">{errors.phone}</p>
            )}
          </div>
        </div>

        {/* Visibility Field */}
        <div>
          <label htmlFor="visibility" className="block text-sm font-medium text-gray-700 mb-1">
            Visibility
          </label>
          <select
            id="visibility"
            value={formData.visibility}
            onChange={(e) => updateFormData('visibility', e.target.value as ContactVisibility)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={isSubmitting}
          >
            <option value={ContactVisibility.PRIVATE}>Private (Only you can see this contact)</option>
            <option value={ContactVisibility.PUBLIC}>Public (Visible to all users in your organization)</option>
          </select>
        </div>

        {/* Expandable Additional Fields */}
        <div className="border-t pt-4">
          <button
            type="button"
            onClick={() => setIsExpanded(!isExpanded)}
            className="flex items-center text-sm text-blue-600 hover:text-blue-800 mb-4"
          >
            <svg
              className={`w-4 h-4 mr-1 transform transition-transform ${
                isExpanded ? 'rotate-90' : 'rotate-0'
              }`}
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
            {isExpanded ? 'Hide additional fields' : 'Show additional fields'}
          </button>

          {isExpanded && (
            <div className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label htmlFor="job_title" className="block text-sm font-medium text-gray-700 mb-1">
                    Job Title
                  </label>
                  <input
                    type="text"
                    id="job_title"
                    value={formData.job_title || ''}
                    onChange={(e) => updateFormData('job_title', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                    disabled={isSubmitting}
                  />
                </div>

                <div>
                  <label htmlFor="organization_id" className="block text-sm font-medium text-gray-700 mb-1">
                    Organization ID
                  </label>
                  <input
                    type="number"
                    id="organization_id"
                    value={formData.organization_id || ''}
                    onChange={(e) => {
                      const value = e.target.value;
                      updateFormData('organization_id', value ? parseInt(value) : undefined);
                    }}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                    disabled={isSubmitting}
                  />
                </div>
              </div>

              <div>
                <label htmlFor="notes" className="block text-sm font-medium text-gray-700 mb-1">
                  Notes
                </label>
                <textarea
                  id="notes"
                  rows={3}
                  value={formData.notes || ''}
                  onChange={(e) => updateFormData('notes', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                  disabled={isSubmitting}
                />
              </div>

              {/* Relationship Management - Only show when editing existing contact */}
              {isEditing && editingContact && (
                <div>
                  <h4 className="block text-sm font-medium text-gray-700 mb-3">
                    Relationship Management
                  </h4>
                  <div className="border border-gray-200 rounded-md">
                    <RelationshipManager
                      contactId={editingContact.id}
                      onRelationshipChange={onRelationshipChange}
                    />
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Form Actions */}
        <div className="flex justify-end space-x-3 pt-4">
          {onCancel && (
            <button
              type="button"
              onClick={onCancel}
              disabled={isSubmitting}
              className="px-4 py-2 text-gray-700 bg-gray-200 border border-gray-300 rounded-md hover:bg-gray-300 focus:outline-none focus:ring-2 focus:ring-gray-500 disabled:opacity-50"
            >
              Cancel
            </button>
          )}
          <button
            type="submit"
            disabled={isSubmitting}
            className="px-4 py-2 text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isSubmitting ? (isEditing ? 'Updating...' : 'Creating...') : (isEditing ? 'Update Contact' : 'Create Contact')}
          </button>
        </div>
      </form>
    </div>
  );
};