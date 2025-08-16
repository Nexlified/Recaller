'use client';

import React, { useState, useEffect } from 'react';
import { 
  Gift, 
  GiftCreate, 
  GiftUpdate, 
  GiftFormData,
  GIFT_STATUS_OPTIONS,
  GIFT_PRIORITY_OPTIONS,
  GIFT_CATEGORIES,
  GIFT_OCCASIONS,
  ValidationErrors
} from '../../types/Gift';
import { Contact } from '../../services/contacts';

interface GiftFormProps {
  gift?: Gift;
  onSubmit: (data: GiftCreate | GiftUpdate) => void;
  onCancel: () => void;
  contacts?: Contact[];
  loading?: boolean;
  className?: string;
}

export const GiftForm: React.FC<GiftFormProps> = ({
  gift,
  onSubmit,
  onCancel,
  contacts = [],
  loading = false,
  className = ''
}) => {
  const isEditing = !!gift;

  const [formData, setFormData] = useState<GiftFormData>({
    title: gift?.title || '',
    description: gift?.description || '',
    category: gift?.category || '',
    recipient_contact_id: gift?.recipient_contact_id || null,
    recipient_name: gift?.recipient_name || '',
    occasion: gift?.occasion || '',
    occasion_date: gift?.occasion_date ? formatDateForInput(gift.occasion_date) : '',
    budget_amount: gift?.budget_amount?.toString() || '',
    currency: gift?.currency || 'USD',
    status: gift?.status || 'idea',
    priority: gift?.priority || 2,
    store_name: gift?.store_name || '',
    purchase_url: gift?.purchase_url || '',
    gift_details: gift?.gift_details || {},
    notes: gift?.notes || '',
    is_surprise: gift?.is_surprise || false,
  });

  const [errors, setErrors] = useState<ValidationErrors>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    if (gift) {
      setFormData({
        title: gift.title,
        description: gift.description || '',
        category: gift.category || '',
        recipient_contact_id: gift.recipient_contact_id || null,
        recipient_name: gift.recipient_name || '',
        occasion: gift.occasion || '',
        occasion_date: gift.occasion_date ? formatDateForInput(gift.occasion_date) : '',
        budget_amount: gift.budget_amount?.toString() || '',
        currency: gift.currency,
        status: gift.status,
        priority: gift.priority,
        store_name: gift.store_name || '',
        purchase_url: gift.purchase_url || '',
        gift_details: gift.gift_details,
        notes: gift.notes || '',
        is_surprise: gift.is_surprise,
      });
    }
  }, [gift]);

  const updateFormData = <K extends keyof GiftFormData>(
    field: K,
    value: GiftFormData[K]
  ) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    
    // Clear field-specific error when user starts typing
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }));
    }
  };

  const validateForm = (): boolean => {
    const newErrors: ValidationErrors = {};

    if (!formData.title.trim()) {
      newErrors.title = 'Title is required';
    }

    if (formData.budget_amount && isNaN(parseFloat(formData.budget_amount))) {
      newErrors.budget_amount = 'Budget amount must be a valid number';
    }

    if (formData.occasion_date) {
      const date = new Date(formData.occasion_date);
      if (isNaN(date.getTime())) {
        newErrors.occasion_date = 'Please enter a valid date';
      }
    }

    if (formData.purchase_url && !isValidUrl(formData.purchase_url)) {
      newErrors.purchase_url = 'Please enter a valid URL';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setIsSubmitting(true);
    
    try {
      const submitData: GiftCreate | GiftUpdate = {
        title: formData.title.trim(),
        description: formData.description.trim() || undefined,
        category: formData.category || undefined,
        recipient_contact_id: formData.recipient_contact_id || undefined,
        recipient_name: formData.recipient_name.trim() || undefined,
        occasion: formData.occasion || undefined,
        occasion_date: formData.occasion_date || undefined,
        budget_amount: formData.budget_amount ? parseFloat(formData.budget_amount) : undefined,
        currency: formData.currency,
        status: formData.status,
        priority: formData.priority,
        store_name: formData.store_name.trim() || undefined,
        purchase_url: formData.purchase_url.trim() || undefined,
        gift_details: formData.gift_details,
        notes: formData.notes.trim() || undefined,
        is_surprise: formData.is_surprise,
      };

      await onSubmit(submitData);
    } catch (error) {
      console.error('Error submitting gift:', error);
      setErrors({ general: 'Failed to save gift. Please try again.' });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className={`bg-white dark:bg-gray-800 shadow rounded-lg ${className}`}>
      <div className="px-4 py-5 sm:p-6">
        <div className="flex justify-between items-center mb-6">
          <h3 className="text-lg font-medium text-gray-900 dark:text-white">
            {isEditing ? 'Edit Gift' : 'Add New Gift'}
          </h3>
        </div>

        {errors.general && (
          <div className="mb-4 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-md">
            <p className="text-sm text-red-800 dark:text-red-200">{errors.general}</p>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Basic Information */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label htmlFor="title" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                Title *
              </label>
              <input
                type="text"
                id="title"
                value={formData.title}
                onChange={(e) => updateFormData('title', e.target.value)}
                className={`mt-1 block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:text-white ${
                  errors.title ? 'border-red-300 dark:border-red-600' : ''
                }`}
                placeholder="Gift title"
              />
              {errors.title && <p className="mt-1 text-sm text-red-600 dark:text-red-400">{errors.title}</p>}
            </div>

            <div>
              <label htmlFor="category" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                Category
              </label>
              <select
                id="category"
                value={formData.category}
                onChange={(e) => updateFormData('category', e.target.value)}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:text-white"
              >
                <option value="">Select category</option>
                {GIFT_CATEGORIES.map(category => (
                  <option key={category} value={category}>{category}</option>
                ))}
              </select>
            </div>
          </div>

          <div>
            <label htmlFor="description" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
              Description
            </label>
            <textarea
              id="description"
              rows={3}
              value={formData.description}
              onChange={(e) => updateFormData('description', e.target.value)}
              className="mt-1 block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:text-white"
              placeholder="Describe the gift..."
            />
          </div>

          {/* Recipient Information */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label htmlFor="recipient_contact_id" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                Recipient (from contacts)
              </label>
              <select
                id="recipient_contact_id"
                value={formData.recipient_contact_id || ''}
                onChange={(e) => {
                  const contactId = e.target.value ? parseInt(e.target.value) : null;
                  updateFormData('recipient_contact_id', contactId);
                  if (contactId) {
                    const contact = contacts.find(c => c.id === contactId);
                    if (contact) {
                      updateFormData('recipient_name', `${contact.first_name} ${contact.last_name || ''}`.trim());
                    }
                  }
                }}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:text-white"
              >
                <option value="">Select contact</option>
                {contacts.map(contact => (
                  <option key={contact.id} value={contact.id}>
                    {contact.first_name} {contact.last_name}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label htmlFor="recipient_name" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                Recipient Name
              </label>
              <input
                type="text"
                id="recipient_name"
                value={formData.recipient_name}
                onChange={(e) => updateFormData('recipient_name', e.target.value)}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:text-white"
                placeholder="Enter recipient name"
              />
            </div>
          </div>

          {/* Occasion Information */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label htmlFor="occasion" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                Occasion
              </label>
              <select
                id="occasion"
                value={formData.occasion}
                onChange={(e) => updateFormData('occasion', e.target.value)}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:text-white"
              >
                <option value="">Select occasion</option>
                {GIFT_OCCASIONS.map(occasion => (
                  <option key={occasion} value={occasion}>{occasion}</option>
                ))}
              </select>
            </div>

            <div>
              <label htmlFor="occasion_date" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                Occasion Date
              </label>
              <input
                type="date"
                id="occasion_date"
                value={formData.occasion_date}
                onChange={(e) => updateFormData('occasion_date', e.target.value)}
                className={`mt-1 block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:text-white ${
                  errors.occasion_date ? 'border-red-300 dark:border-red-600' : ''
                }`}
              />
              {errors.occasion_date && <p className="mt-1 text-sm text-red-600 dark:text-red-400">{errors.occasion_date}</p>}
            </div>
          </div>

          {/* Budget Information */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label htmlFor="budget_amount" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                Budget Amount
              </label>
              <input
                type="number"
                id="budget_amount"
                step="0.01"
                min="0"
                value={formData.budget_amount}
                onChange={(e) => updateFormData('budget_amount', e.target.value)}
                className={`mt-1 block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:text-white ${
                  errors.budget_amount ? 'border-red-300 dark:border-red-600' : ''
                }`}
                placeholder="0.00"
              />
              {errors.budget_amount && <p className="mt-1 text-sm text-red-600 dark:text-red-400">{errors.budget_amount}</p>}
            </div>

            <div>
              <label htmlFor="currency" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                Currency
              </label>
              <select
                id="currency"
                value={formData.currency}
                onChange={(e) => updateFormData('currency', e.target.value)}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:text-white"
              >
                <option value="USD">USD</option>
                <option value="EUR">EUR</option>
                <option value="GBP">GBP</option>
                <option value="CAD">CAD</option>
                <option value="AUD">AUD</option>
              </select>
            </div>
          </div>

          {/* Status and Priority */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label htmlFor="status" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                Status
              </label>
              <select
                id="status"
                value={formData.status}
                onChange={(e) => updateFormData('status', e.target.value as any)}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:text-white"
              >
                {GIFT_STATUS_OPTIONS.map(option => (
                  <option key={option.value} value={option.value}>{option.label}</option>
                ))}
              </select>
            </div>

            <div>
              <label htmlFor="priority" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                Priority
              </label>
              <select
                id="priority"
                value={formData.priority}
                onChange={(e) => updateFormData('priority', parseInt(e.target.value) as any)}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:text-white"
              >
                {GIFT_PRIORITY_OPTIONS.map(option => (
                  <option key={option.value} value={option.value}>{option.label}</option>
                ))}
              </select>
            </div>
          </div>

          {/* Purchase Information */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label htmlFor="store_name" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                Store Name
              </label>
              <input
                type="text"
                id="store_name"
                value={formData.store_name}
                onChange={(e) => updateFormData('store_name', e.target.value)}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:text-white"
                placeholder="Where to buy"
              />
            </div>

            <div>
              <label htmlFor="purchase_url" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                Purchase URL
              </label>
              <input
                type="url"
                id="purchase_url"
                value={formData.purchase_url}
                onChange={(e) => updateFormData('purchase_url', e.target.value)}
                className={`mt-1 block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:text-white ${
                  errors.purchase_url ? 'border-red-300 dark:border-red-600' : ''
                }`}
                placeholder="https://..."
              />
              {errors.purchase_url && <p className="mt-1 text-sm text-red-600 dark:text-red-400">{errors.purchase_url}</p>}
            </div>
          </div>

          {/* Additional Options */}
          <div>
            <div className="flex items-center">
              <input
                type="checkbox"
                id="is_surprise"
                checked={formData.is_surprise}
                onChange={(e) => updateFormData('is_surprise', e.target.checked)}
                className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 dark:border-gray-600 rounded dark:bg-gray-700"
              />
              <label htmlFor="is_surprise" className="ml-2 block text-sm text-gray-700 dark:text-gray-300">
                This is a surprise gift
              </label>
            </div>
          </div>

          {/* Notes */}
          <div>
            <label htmlFor="notes" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
              Notes
            </label>
            <textarea
              id="notes"
              rows={3}
              value={formData.notes}
              onChange={(e) => updateFormData('notes', e.target.value)}
              className="mt-1 block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:text-white"
              placeholder="Additional notes about this gift..."
            />
          </div>

          {/* Form Actions */}
          <div className="flex justify-end space-x-3 pt-6 border-t border-gray-200 dark:border-gray-700">
            <button
              type="button"
              onClick={onCancel}
              className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting || loading}
              className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isSubmitting || loading ? 'Saving...' : (isEditing ? 'Update Gift' : 'Add Gift')}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

// Helper functions
function formatDateForInput(dateString: string): string {
  const date = new Date(dateString);
  if (isNaN(date.getTime())) return '';
  return date.toISOString().split('T')[0];
}

function isValidUrl(string: string): boolean {
  try {
    new URL(string);
    return true;
  } catch (_) {
    return false;
  }
}