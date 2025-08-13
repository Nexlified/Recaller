'use client';

import React, { useState, useEffect } from 'react';
import { 
  TaskRecurrence, 
  TaskRecurrenceCreate, 
  RecurrenceType,
  RECURRENCE_TYPE_OPTIONS 
} from '../../types/Task';

interface RecurrenceSettingsProps {
  recurrence?: TaskRecurrence;
  onChange: (recurrence: TaskRecurrenceCreate | null) => void;
  className?: string;
}

export const RecurrenceSettings: React.FC<RecurrenceSettingsProps> = ({
  recurrence,
  onChange,
  className = ''
}) => {
  const [isEnabled, setIsEnabled] = useState(!!recurrence);
  const [formData, setFormData] = useState<TaskRecurrenceCreate>({
    recurrence_type: 'daily',
    recurrence_interval: 1,
    lead_time_days: 0,
  });

  useEffect(() => {
    if (recurrence) {
      setFormData({
        recurrence_type: recurrence.recurrence_type,
        recurrence_interval: recurrence.recurrence_interval,
        days_of_week: recurrence.days_of_week,
        day_of_month: recurrence.day_of_month,
        end_date: recurrence.end_date,
        max_occurrences: recurrence.max_occurrences,
        lead_time_days: recurrence.lead_time_days,
      });
      setIsEnabled(true);
    }
  }, [recurrence]);

  const updateFormData = <K extends keyof TaskRecurrenceCreate>(
    key: K,
    value: TaskRecurrenceCreate[K]
  ) => {
    const newData = { ...formData, [key]: value };
    setFormData(newData);
    if (isEnabled) {
      onChange(newData);
    }
  };

  const handleToggle = (enabled: boolean) => {
    setIsEnabled(enabled);
    if (enabled) {
      onChange(formData);
    } else {
      onChange(null);
    }
  };

  const getDaysOfWeekArray = () => {
    return formData.days_of_week ? formData.days_of_week.split(',').map(Number) : [];
  };

  const setDaysOfWeek = (days: number[]) => {
    updateFormData('days_of_week', days.length > 0 ? days.join(',') : undefined);
  };

  const toggleDayOfWeek = (day: number) => {
    const currentDays = getDaysOfWeekArray();
    const newDays = currentDays.includes(day)
      ? currentDays.filter(d => d !== day)
      : [...currentDays, day].sort();
    setDaysOfWeek(newDays);
  };

  const weekDays = [
    { value: 1, label: 'Mon' },
    { value: 2, label: 'Tue' },
    { value: 3, label: 'Wed' },
    { value: 4, label: 'Thu' },
    { value: 5, label: 'Fri' },
    { value: 6, label: 'Sat' },
    { value: 0, label: 'Sun' }, // Sunday is 0
  ];

  return (
    <div className={`bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-4 ${className}`}>
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100">
          Recurrence Settings
        </h3>
        <label className="flex items-center">
          <input
            type="checkbox"
            checked={isEnabled}
            onChange={(e) => handleToggle(e.target.checked)}
            className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 dark:border-gray-600 rounded"
          />
          <span className="ml-2 text-sm text-gray-700 dark:text-gray-300">
            Make this task recurring
          </span>
        </label>
      </div>

      {isEnabled && (
        <div className="space-y-4">
          {/* Recurrence Type */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Repeat every
            </label>
            <div className="flex items-center space-x-2">
              <input
                type="number"
                min="1"
                max="365"
                value={formData.recurrence_interval}
                onChange={(e) => updateFormData('recurrence_interval', parseInt(e.target.value) || 1)}
                className="w-20 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
              <select
                value={formData.recurrence_type}
                onChange={(e) => updateFormData('recurrence_type', e.target.value as RecurrenceType)}
                className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                {RECURRENCE_TYPE_OPTIONS.map(option => (
                  <option key={option.value} value={option.value}>
                    {option.label}{formData.recurrence_interval !== 1 ? 's' : ''}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Weekly - Days of Week */}
          {formData.recurrence_type === 'weekly' && (
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                On these days
              </label>
              <div className="flex flex-wrap gap-2">
                {weekDays.map(day => (
                  <button
                    key={day.value}
                    type="button"
                    onClick={() => toggleDayOfWeek(day.value)}
                    className={`px-3 py-1 rounded text-sm font-medium transition-colors ${
                      getDaysOfWeekArray().includes(day.value)
                        ? 'bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-400'
                        : 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                    }`}
                  >
                    {day.label}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Monthly - Day of Month */}
          {formData.recurrence_type === 'monthly' && (
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                On day of month
              </label>
              <input
                type="number"
                min="1"
                max="31"
                value={formData.day_of_month || ''}
                onChange={(e) => updateFormData('day_of_month', parseInt(e.target.value) || undefined)}
                placeholder="e.g., 15"
                className="w-20 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
              <span className="ml-2 text-sm text-gray-500 dark:text-gray-400">
                (leave empty for same day each month)
              </span>
            </div>
          )}

          {/* Lead Time */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Create next task
            </label>
            <div className="flex items-center space-x-2">
              <input
                type="number"
                min="0"
                max="30"
                value={formData.lead_time_days}
                onChange={(e) => updateFormData('lead_time_days', parseInt(e.target.value) || 0)}
                className="w-20 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
              <span className="text-sm text-gray-700 dark:text-gray-300">
                days before the due date
              </span>
            </div>
            <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
              0 means create the next task when the current one is completed
            </p>
          </div>

          {/* End Conditions */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              End recurrence (optional)
            </label>
            <div className="space-y-2">
              <div>
                <label className="block text-xs text-gray-500 dark:text-gray-400 mb-1">
                  End date
                </label>
                <input
                  type="date"
                  value={formData.end_date || ''}
                  onChange={(e) => updateFormData('end_date', e.target.value || undefined)}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              <div className="flex items-center space-x-2">
                <span className="text-sm text-gray-700 dark:text-gray-300">or after</span>
                <input
                  type="number"
                  min="1"
                  max="999"
                  value={formData.max_occurrences || ''}
                  onChange={(e) => updateFormData('max_occurrences', parseInt(e.target.value) || undefined)}
                  placeholder="10"
                  className="w-20 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
                <span className="text-sm text-gray-700 dark:text-gray-300">occurrences</span>
              </div>
            </div>
          </div>

          {/* Preview */}
          <div className="p-3 bg-gray-50 dark:bg-gray-700 rounded-md">
            <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Preview
            </h4>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              {getRecurrenceDescription(formData)}
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

function getRecurrenceDescription(recurrence: TaskRecurrenceCreate): string {
  const { recurrence_type, recurrence_interval, days_of_week, day_of_month, end_date, max_occurrences } = recurrence;
  
  let description = '';
  
  if (recurrence_interval === 1) {
    switch (recurrence_type) {
      case 'daily':
        description = 'Repeats daily';
        break;
      case 'weekly':
        if (days_of_week) {
          const dayNames = days_of_week.split(',').map(d => {
            const dayMap: { [key: string]: string } = {
              '0': 'Sun', '1': 'Mon', '2': 'Tue', '3': 'Wed', '4': 'Thu', '5': 'Fri', '6': 'Sat'
            };
            return dayMap[d];
          });
          description = `Repeats weekly on ${dayNames.join(', ')}`;
        } else {
          description = 'Repeats weekly';
        }
        break;
      case 'monthly':
        if (day_of_month) {
          description = `Repeats monthly on day ${day_of_month}`;
        } else {
          description = 'Repeats monthly';
        }
        break;
      case 'yearly':
        description = 'Repeats yearly';
        break;
      default:
        description = 'Custom recurrence';
    }
  } else {
    description = `Repeats every ${recurrence_interval} ${recurrence_type}s`;
  }
  
  if (end_date) {
    description += ` until ${new Date(end_date).toLocaleDateString()}`;
  } else if (max_occurrences) {
    description += ` for ${max_occurrences} occurrences`;
  }
  
  return description;
}