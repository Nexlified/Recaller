'use client';

import React, { useState, useEffect } from 'react';
import { 
  RecurringTransaction,
  RecurringTransactionCreate, 
  RecurringFrequency,
  RECURRING_FREQUENCY_OPTIONS 
} from '../../types/Transaction';

interface RecurrenceSettingsProps {
  recurrence?: RecurringTransaction;
  onChange: (recurrence: RecurringTransactionCreate | null) => void;
  className?: string;
}

export const RecurrenceSettings: React.FC<RecurrenceSettingsProps> = ({
  recurrence,
  onChange,
  className = ''
}) => {
  const [isEnabled, setIsEnabled] = useState(!!recurrence);
  const [formData, setFormData] = useState<RecurringTransactionCreate>({
    template_name: '',
    type: 'debit',
    amount: 0,
    frequency: 'monthly',
    interval_count: 1,
    start_date: formatDateForInput(new Date().toISOString()),
    reminder_days: 3,
    is_active: true,
  });

  useEffect(() => {
    if (recurrence) {
      setFormData({
        template_name: recurrence.template_name,
        type: recurrence.type,
        amount: recurrence.amount,
        currency: recurrence.currency,
        description: recurrence.description,
        category_id: recurrence.category_id,
        subcategory_id: recurrence.subcategory_id,
        account_id: recurrence.account_id,
        frequency: recurrence.frequency,
        interval_count: recurrence.interval_count,
        start_date: formatDateForInput(recurrence.start_date),
        end_date: recurrence.end_date ? formatDateForInput(recurrence.end_date) : undefined,
        reminder_days: recurrence.reminder_days,
        is_active: recurrence.is_active,
        extra_data: recurrence.extra_data,
      });
      setIsEnabled(true);
    }
  }, [recurrence]);

  const updateFormData = <K extends keyof RecurringTransactionCreate>(
    key: K,
    value: RecurringTransactionCreate[K]
  ) => {
    const newData = { ...formData, [key]: value };
    setFormData(newData);
    if (isEnabled) {
      onChange(newData);
    }
  };

  const handleToggle = (enabled: boolean) => {
    setIsEnabled(enabled);
    onChange(enabled ? formData : null);
  };

  function formatDateForInput(dateString: string): string {
    try {
      const date = new Date(dateString);
      return date.toISOString().split('T')[0];
    } catch {
      return '';
    }
  }

  return (
    <div className={`p-4 border border-gray-200 dark:border-gray-700 rounded-lg ${className}`}>
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100">
          Recurring Transaction Settings
        </h3>
        <label className="flex items-center">
          <input
            type="checkbox"
            checked={isEnabled}
            onChange={(e) => handleToggle(e.target.checked)}
            className="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
          />
          <span className="ml-2 text-sm text-gray-700 dark:text-gray-300">
            Enable recurring
          </span>
        </label>
      </div>

      {isEnabled && (
        <div className="space-y-4">
          {/* Template Name */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Template Name *
            </label>
            <input
              type="text"
              value={formData.template_name}
              onChange={(e) => updateFormData('template_name', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="e.g., Monthly Rent Payment"
              required
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Frequency */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Frequency *
              </label>
              <select
                value={formData.frequency}
                onChange={(e) => updateFormData('frequency', e.target.value as RecurringFrequency)}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                required
              >
                {RECURRING_FREQUENCY_OPTIONS.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>

            {/* Interval Count */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Repeat Every
              </label>
              <div className="flex items-center space-x-2">
                <input
                  type="number"
                  min="1"
                  value={formData.interval_count}
                  onChange={(e) => updateFormData('interval_count', parseInt(e.target.value) || 1)}
                  className="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
                <span className="text-sm text-gray-500 dark:text-gray-400">
                  {formData.frequency === 'daily' && 'day(s)'}
                  {formData.frequency === 'weekly' && 'week(s)'}
                  {formData.frequency === 'monthly' && 'month(s)'}
                  {formData.frequency === 'quarterly' && 'quarter(s)'}
                  {formData.frequency === 'yearly' && 'year(s)'}
                </span>
              </div>
            </div>

            {/* Start Date */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Start Date *
              </label>
              <input
                type="date"
                value={formData.start_date}
                onChange={(e) => updateFormData('start_date', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                required
              />
            </div>

            {/* End Date */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                End Date (Optional)
              </label>
              <input
                type="date"
                value={formData.end_date || ''}
                onChange={(e) => updateFormData('end_date', e.target.value || undefined)}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            {/* Reminder Days */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Reminder Days Before
              </label>
              <input
                type="number"
                min="0"
                max="30"
                value={formData.reminder_days}
                onChange={(e) => updateFormData('reminder_days', parseInt(e.target.value) || 0)}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="0"
              />
              <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
                How many days before the due date to send reminders
              </p>
            </div>

            {/* Is Active */}
            <div className="flex items-center">
              <input
                type="checkbox"
                id="is_active"
                checked={formData.is_active}
                onChange={(e) => updateFormData('is_active', e.target.checked)}
                className="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
              />
              <label htmlFor="is_active" className="ml-2 text-sm text-gray-700 dark:text-gray-300">
                Active recurring template
              </label>
            </div>
          </div>

          {/* Preview */}
          <div className="mt-4 p-3 bg-gray-50 dark:bg-gray-800 rounded-md">
            <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Preview</h4>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              {formData.template_name && (
                <>
                  <strong>{formData.template_name}</strong> will repeat{' '}
                  {(formData.interval_count || 1) > 1 && `every ${formData.interval_count} `}
                  {formData.frequency === 'daily' && ((formData.interval_count || 1) === 1 ? 'daily' : 'days')}
                  {formData.frequency === 'weekly' && ((formData.interval_count || 1) === 1 ? 'weekly' : 'weeks')}
                  {formData.frequency === 'monthly' && ((formData.interval_count || 1) === 1 ? 'monthly' : 'months')}
                  {formData.frequency === 'quarterly' && ((formData.interval_count || 1) === 1 ? 'quarterly' : 'quarters')}
                  {formData.frequency === 'yearly' && ((formData.interval_count || 1) === 1 ? 'yearly' : 'years')}
                  {' '}starting from {formData.start_date}
                  {formData.end_date && ` until ${formData.end_date}`}
                  {(formData.reminder_days || 0) > 0 && `, with reminders ${formData.reminder_days} day(s) before each occurrence`}.
                </>
              )}
            </p>
          </div>
        </div>
      )}
    </div>
  );
};