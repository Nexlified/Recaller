'use client';

import React, { useState, useEffect } from 'react';
import { 
  GiftIdea, 
  GiftIdeaCreate, 
  GiftIdeaUpdate, 
  GiftIdeaFormData,
  GIFT_CATEGORIES,
  GIFT_OCCASIONS,
  ValidationErrors
} from '../../types/Gift';
import { Contact } from '../../services/contacts';

interface GiftIdeaFormProps {
  giftIdea?: GiftIdea;
  onSubmit: (data: GiftIdeaCreate | GiftIdeaUpdate) => void;
  onCancel: () => void;
  contacts?: Contact[];
  loading?: boolean;
  className?: string;
}

export const GiftIdeaForm: React.FC<GiftIdeaFormProps> = ({
  giftIdea,
  onSubmit,
  onCancel,
  contacts = [],
  loading = false,
  className = ''
}) => {
  const isEditing = !!giftIdea;

  const [formData, setFormData] = useState<GiftIdeaFormData>({
    title: giftIdea?.title || '',
    description: giftIdea?.description || '',
    category: giftIdea?.category || '',
    target_contact_id: giftIdea?.target_contact_id || null,
    target_demographic: giftIdea?.target_demographic || '',
    suitable_occasions: giftIdea?.suitable_occasions || [],
    price_range_min: giftIdea?.price_range_min?.toString() || '',
    price_range_max: giftIdea?.price_range_max?.toString() || '',
    currency: giftIdea?.currency || 'USD',
    source_url: giftIdea?.source_url || '',
    rating: giftIdea?.rating || 0,
    notes: giftIdea?.notes || '',
    tags: giftIdea?.tags || [],
  });

  const [errors, setErrors] = useState<ValidationErrors>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [newTag, setNewTag] = useState('');
  const [newOccasion, setNewOccasion] = useState('');

  useEffect(() => {
    if (giftIdea) {
      setFormData({
        title: giftIdea.title,
        description: giftIdea.description || '',
        category: giftIdea.category || '',
        target_contact_id: giftIdea.target_contact_id || null,
        target_demographic: giftIdea.target_demographic || '',
        suitable_occasions: giftIdea.suitable_occasions,
        price_range_min: giftIdea.price_range_min?.toString() || '',
        price_range_max: giftIdea.price_range_max?.toString() || '',
        currency: giftIdea.currency,
        source_url: giftIdea.source_url || '',
        rating: giftIdea.rating || 0,
        notes: giftIdea.notes || '',
        tags: giftIdea.tags,
      });
    }
  }, [giftIdea]);

  const updateFormData = <K extends keyof GiftIdeaFormData>(
    field: K,
    value: GiftIdeaFormData[K]
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

    if (formData.price_range_min && isNaN(parseFloat(formData.price_range_min))) {
      newErrors.price_range_min = 'Minimum price must be a valid number';
    }

    if (formData.price_range_max && isNaN(parseFloat(formData.price_range_max))) {
      newErrors.price_range_max = 'Maximum price must be a valid number';
    }

    if (formData.price_range_min && formData.price_range_max) {
      const min = parseFloat(formData.price_range_min);
      const max = parseFloat(formData.price_range_max);
      if (min > max) {
        newErrors.price_range_max = 'Maximum price must be greater than minimum price';
      }
    }

    if (formData.source_url && !isValidUrl(formData.source_url)) {
      newErrors.source_url = 'Please enter a valid URL';
    }

    if (formData.rating < 0 || formData.rating > 5) {
      newErrors.rating = 'Rating must be between 0 and 5';
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
      const submitData: GiftIdeaCreate | GiftIdeaUpdate = {
        title: formData.title.trim(),
        description: formData.description.trim() || undefined,
        category: formData.category || undefined,
        target_contact_id: formData.target_contact_id || undefined,
        target_demographic: formData.target_demographic.trim() || undefined,
        suitable_occasions: formData.suitable_occasions.length > 0 ? formData.suitable_occasions : undefined,
        price_range_min: formData.price_range_min ? parseFloat(formData.price_range_min) : undefined,
        price_range_max: formData.price_range_max ? parseFloat(formData.price_range_max) : undefined,
        currency: formData.currency,
        source_url: formData.source_url.trim() || undefined,
        rating: formData.rating || undefined,
        notes: formData.notes.trim() || undefined,
        tags: formData.tags.length > 0 ? formData.tags : undefined,
      };

      await onSubmit(submitData);
    } catch (error) {
      console.error('Error submitting gift idea:', error);
      setErrors({ general: 'Failed to save gift idea. Please try again.' });
    } finally {
      setIsSubmitting(false);
    }
  };

  const addTag = () => {
    if (newTag.trim() && !formData.tags.includes(newTag.trim())) {
      updateFormData('tags', [...formData.tags, newTag.trim()]);
      setNewTag('');
    }
  };

  const removeTag = (tagToRemove: string) => {
    updateFormData('tags', formData.tags.filter(tag => tag !== tagToRemove));
  };

  const addOccasion = () => {
    if (newOccasion.trim() && !formData.suitable_occasions.includes(newOccasion.trim())) {
      updateFormData('suitable_occasions', [...formData.suitable_occasions, newOccasion.trim()]);
      setNewOccasion('');
    }
  };

  const removeOccasion = (occasionToRemove: string) => {
    updateFormData('suitable_occasions', formData.suitable_occasions.filter(occasion => occasion !== occasionToRemove));
  };

  const toggleOccasion = (occasion: string) => {
    if (formData.suitable_occasions.includes(occasion)) {
      removeOccasion(occasion);
    } else {
      updateFormData('suitable_occasions', [...formData.suitable_occasions, occasion]);
    }
  };

  return (
    <div className={`bg-white dark:bg-gray-800 shadow rounded-lg ${className}`}>
      <div className="px-4 py-5 sm:p-6">
        <div className="flex justify-between items-center mb-6">
          <h3 className="text-lg font-medium text-gray-900 dark:text-white">
            {isEditing ? 'Edit Gift Idea' : 'Add New Gift Idea'}
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
                placeholder="Gift idea title"
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
              placeholder="Describe the gift idea..."
            />
          </div>

          {/* Target Information */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label htmlFor="target_contact_id" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                Target Contact
              </label>
              <select
                id="target_contact_id"
                value={formData.target_contact_id || ''}
                onChange={(e) => {
                  const contactId = e.target.value ? parseInt(e.target.value) : null;
                  updateFormData('target_contact_id', contactId);
                }}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:text-white"
              >
                <option value="">Select contact (optional)</option>
                {contacts.map(contact => (
                  <option key={contact.id} value={contact.id}>
                    {contact.first_name} {contact.last_name}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label htmlFor="target_demographic" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                Target Demographic
              </label>
              <input
                type="text"
                id="target_demographic"
                value={formData.target_demographic}
                onChange={(e) => updateFormData('target_demographic', e.target.value)}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:text-white"
                placeholder="e.g., tech enthusiast, book lover, fitness enthusiast"
              />
            </div>
          </div>

          {/* Price Range */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label htmlFor="price_range_min" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                Min Price
              </label>
              <input
                type="number"
                id="price_range_min"
                step="0.01"
                min="0"
                value={formData.price_range_min}
                onChange={(e) => updateFormData('price_range_min', e.target.value)}
                className={`mt-1 block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:text-white ${
                  errors.price_range_min ? 'border-red-300 dark:border-red-600' : ''
                }`}
                placeholder="0.00"
              />
              {errors.price_range_min && <p className="mt-1 text-sm text-red-600 dark:text-red-400">{errors.price_range_min}</p>}
            </div>

            <div>
              <label htmlFor="price_range_max" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                Max Price
              </label>
              <input
                type="number"
                id="price_range_max"
                step="0.01"
                min="0"
                value={formData.price_range_max}
                onChange={(e) => updateFormData('price_range_max', e.target.value)}
                className={`mt-1 block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:text-white ${
                  errors.price_range_max ? 'border-red-300 dark:border-red-600' : ''
                }`}
                placeholder="100.00"
              />
              {errors.price_range_max && <p className="mt-1 text-sm text-red-600 dark:text-red-400">{errors.price_range_max}</p>}
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

          {/* Suitable Occasions */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
              Suitable Occasions
            </label>
            <div className="space-y-4">
              {/* Selected occasions */}
              {formData.suitable_occasions.length > 0 && (
                <div className="flex flex-wrap gap-2">
                  {formData.suitable_occasions.map(occasion => (
                    <span
                      key={occasion}
                      className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-indigo-100 text-indigo-800 dark:bg-indigo-900/20 dark:text-indigo-400"
                    >
                      {occasion}
                      <button
                        type="button"
                        onClick={() => removeOccasion(occasion)}
                        className="ml-2 text-indigo-600 hover:text-indigo-800 dark:text-indigo-400 dark:hover:text-indigo-300"
                      >
                        <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                      </button>
                    </span>
                  ))}
                </div>
              )}

              {/* Quick select common occasions */}
              <div className="flex flex-wrap gap-2">
                {GIFT_OCCASIONS.slice(0, 8).map(occasion => (
                  <button
                    key={occasion}
                    type="button"
                    onClick={() => toggleOccasion(occasion)}
                    className={`px-3 py-1 rounded-md text-sm font-medium transition-colors ${
                      formData.suitable_occasions.includes(occasion)
                        ? 'bg-indigo-100 text-indigo-800 border-indigo-200 dark:bg-indigo-900/20 dark:text-indigo-400 dark:border-indigo-800'
                        : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50 dark:bg-gray-700 dark:text-gray-300 dark:border-gray-600 dark:hover:bg-gray-600'
                    } border`}
                  >
                    {occasion}
                  </button>
                ))}
              </div>

              {/* Add custom occasion */}
              <div className="flex items-center space-x-2">
                <input
                  type="text"
                  value={newOccasion}
                  onChange={(e) => setNewOccasion(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addOccasion())}
                  placeholder="Add custom occasion"
                  className="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:text-white"
                />
                <button
                  type="button"
                  onClick={addOccasion}
                  disabled={!newOccasion.trim()}
                  className="px-3 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Add
                </button>
              </div>
            </div>
          </div>

          {/* Source and Rating */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label htmlFor="source_url" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                Source URL
              </label>
              <input
                type="url"
                id="source_url"
                value={formData.source_url}
                onChange={(e) => updateFormData('source_url', e.target.value)}
                className={`mt-1 block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:text-white ${
                  errors.source_url ? 'border-red-300 dark:border-red-600' : ''
                }`}
                placeholder="https://..."
              />
              {errors.source_url && <p className="mt-1 text-sm text-red-600 dark:text-red-400">{errors.source_url}</p>}
            </div>

            <div>
              <label htmlFor="rating" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                Rating (0-5 stars)
              </label>
              <div className="mt-1 flex items-center space-x-2">
                <input
                  type="number"
                  id="rating"
                  min="0"
                  max="5"
                  step="1"
                  value={formData.rating}
                  onChange={(e) => updateFormData('rating', parseInt(e.target.value) || 0)}
                  className={`block w-20 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:text-white ${
                    errors.rating ? 'border-red-300 dark:border-red-600' : ''
                  }`}
                />
                <div className="flex items-center">
                  {[1, 2, 3, 4, 5].map(star => (
                    <button
                      key={star}
                      type="button"
                      onClick={() => updateFormData('rating', star)}
                      className={`text-xl ${
                        star <= formData.rating ? 'text-yellow-400' : 'text-gray-300 dark:text-gray-600'
                      } hover:text-yellow-400 transition-colors`}
                    >
                      ★
                    </button>
                  ))}
                </div>
              </div>
              {errors.rating && <p className="mt-1 text-sm text-red-600 dark:text-red-400">{errors.rating}</p>}
            </div>
          </div>

          {/* Tags */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
              Tags
            </label>
            <div className="space-y-3">
              {/* Existing tags */}
              {formData.tags.length > 0 && (
                <div className="flex flex-wrap gap-2">
                  {formData.tags.map(tag => (
                    <span
                      key={tag}
                      className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200"
                    >
                      {tag}
                      <button
                        type="button"
                        onClick={() => removeTag(tag)}
                        className="ml-2 text-gray-600 hover:text-gray-800 dark:text-gray-400 dark:hover:text-gray-200"
                      >
                        <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                      </button>
                    </span>
                  ))}
                </div>
              )}

              {/* Add new tag */}
              <div className="flex items-center space-x-2">
                <input
                  type="text"
                  value={newTag}
                  onChange={(e) => setNewTag(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addTag())}
                  placeholder="Add tag"
                  className="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:text-white"
                />
                <button
                  type="button"
                  onClick={addTag}
                  disabled={!newTag.trim()}
                  className="px-3 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Add Tag
                </button>
              </div>
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
              placeholder="Additional notes about this gift idea..."
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
              {isSubmitting || loading ? 'Saving...' : (isEditing ? 'Update Idea' : 'Add Idea')}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

// Helper function
function isValidUrl(string: string): boolean {
  try {
    new URL(string);
    return true;
  } catch (_) {
    return false;
  }
}