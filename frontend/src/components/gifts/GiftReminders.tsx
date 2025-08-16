'use client';

import React, { useState, useEffect } from 'react';
import { Gift } from '../../types/Gift';
import giftsService from '../../services/gifts';

interface ReminderItem {
  id: string;
  gift: Gift;
  type: 'occasion' | 'shopping' | 'wrap' | 'delivery';
  title: string;
  description: string;
  date: Date;
  daysUntil: number;
  priority: 'low' | 'medium' | 'high' | 'urgent';
}

interface GiftRemindersProps {
  gifts?: Gift[];
  limit?: number;
  className?: string;
}

export const GiftReminders: React.FC<GiftRemindersProps> = ({
  gifts: propGifts,
  limit = 10,
  className = ''
}) => {
  const [gifts, setGifts] = useState<Gift[]>(propGifts || []);
  const [reminders, setReminders] = useState<ReminderItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (propGifts) {
      setGifts(propGifts);
      generateReminders(propGifts);
    } else {
      loadGiftsAndReminders();
    }
  }, [propGifts, limit]);

  const loadGiftsAndReminders = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const giftsData = await giftsService.getGifts();
      setGifts(giftsData);
      generateReminders(giftsData);
    } catch (err) {
      console.error('Error loading gifts:', err);
      setError('Failed to load gift reminders');
    } finally {
      setLoading(false);
    }
  };

  const generateReminders = (giftList: Gift[]) => {
    const reminderItems: ReminderItem[] = [];
    const now = new Date();

    giftList.forEach(gift => {
      // Skip completed gifts
      if (gift.status === 'given' || gift.status === 'returned') return;

      // Generate reminders based on gift status and dates
      const upcomingReminders = giftsService.getUpcomingReminders(gift);
      
      upcomingReminders.forEach(reminder => {
        const reminderDate = new Date(reminder.date);
        const daysUntil = Math.ceil((reminderDate.getTime() - now.getTime()) / (1000 * 60 * 60 * 24));
        
        // Only include future reminders within the next 30 days
        if (daysUntil >= 0 && daysUntil <= 30) {
          reminderItems.push({
            id: `${gift.id}-${reminder.type}`,
            gift,
            type: reminder.type as any,
            title: getReminderTitle(reminder.type, gift),
            description: getReminderDescription(reminder.type, gift),
            date: reminderDate,
            daysUntil,
            priority: getReminderPriority(daysUntil, gift.priority)
          });
        }
      });

      // Generate occasion-based reminders
      if (gift.occasion_date) {
        const occasionDate = new Date(gift.occasion_date);
        const daysUntilOccasion = Math.ceil((occasionDate.getTime() - now.getTime()) / (1000 * 60 * 60 * 24));
        
        if (daysUntilOccasion >= 0 && daysUntilOccasion <= 30) {
          // Shopping reminder (7 days before occasion)
          if (gift.status === 'idea' || gift.status === 'planned') {
            const shoppingDate = new Date(occasionDate);
            shoppingDate.setDate(shoppingDate.getDate() - 7);
            const daysUntilShopping = Math.ceil((shoppingDate.getTime() - now.getTime()) / (1000 * 60 * 60 * 24));
            
            if (daysUntilShopping >= -1 && daysUntilShopping <= 7) {
              reminderItems.push({
                id: `${gift.id}-shopping`,
                gift,
                type: 'shopping',
                title: 'Shopping Reminder',
                description: `Buy "${gift.title}" for ${gift.recipient_name || 'recipient'}`,
                date: shoppingDate,
                daysUntil: daysUntilShopping,
                priority: getReminderPriority(daysUntilShopping, gift.priority)
              });
            }
          }

          // Wrapping reminder (2 days before occasion)
          if (gift.status === 'purchased') {
            const wrapDate = new Date(occasionDate);
            wrapDate.setDate(wrapDate.getDate() - 2);
            const daysUntilWrap = Math.ceil((wrapDate.getTime() - now.getTime()) / (1000 * 60 * 60 * 24));
            
            if (daysUntilWrap >= -1 && daysUntilWrap <= 2) {
              reminderItems.push({
                id: `${gift.id}-wrap`,
                gift,
                type: 'wrap',
                title: 'Wrapping Reminder',
                description: `Wrap "${gift.title}" for ${gift.occasion}`,
                date: wrapDate,
                daysUntil: daysUntilWrap,
                priority: getReminderPriority(daysUntilWrap, gift.priority)
              });
            }
          }

          // Occasion reminder
          reminderItems.push({
            id: `${gift.id}-occasion`,
            gift,
            type: 'occasion',
            title: 'Occasion Today',
            description: `${gift.occasion} for ${gift.recipient_name || 'recipient'}`,
            date: occasionDate,
            daysUntil: daysUntilOccasion,
            priority: daysUntilOccasion === 0 ? 'urgent' : getReminderPriority(daysUntilOccasion, gift.priority)
          });
        }
      }
    });

    // Sort by priority and date, then limit
    const sortedReminders = reminderItems
      .sort((a, b) => {
        // Priority order: urgent > high > medium > low
        const priorityOrder = { urgent: 4, high: 3, medium: 2, low: 1 };
        const priorityDiff = priorityOrder[b.priority] - priorityOrder[a.priority];
        if (priorityDiff !== 0) return priorityDiff;
        
        // Then by date (soonest first)
        return a.daysUntil - b.daysUntil;
      })
      .slice(0, limit);

    setReminders(sortedReminders);
    setLoading(false);
  };

  const getReminderTitle = (type: string, gift: Gift): string => {
    switch (type) {
      case 'purchase_reminder':
        return 'Shopping Reminder';
      case 'wrap_reminder':
        return 'Wrapping Reminder';
      case 'delivery_reminder':
        return 'Delivery Reminder';
      default:
        return 'Gift Reminder';
    }
  };

  const getReminderDescription = (type: string, gift: Gift): string => {
    switch (type) {
      case 'purchase_reminder':
        return `Buy "${gift.title}" for ${gift.recipient_name || 'recipient'}`;
      case 'wrap_reminder':
        return `Wrap "${gift.title}" for ${gift.occasion}`;
      case 'delivery_reminder':
        return `Ensure "${gift.title}" is delivered on time`;
      default:
        return `Reminder about "${gift.title}"`;
    }
  };

  const getReminderPriority = (daysUntil: number, giftPriority: number): ReminderItem['priority'] => {
    if (daysUntil <= 0) return 'urgent';
    if (daysUntil <= 1) return 'high';
    if (daysUntil <= 3 || giftPriority >= 3) return 'medium';
    return 'low';
  };

  const getReminderIcon = (type: ReminderItem['type']) => {
    switch (type) {
      case 'shopping':
        return (
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
          </svg>
        );
      case 'wrap':
        return (
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
          </svg>
        );
      case 'delivery':
        return (
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        );
      case 'occasion':
        return (
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
        );
      default:
        return (
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        );
    }
  };

  const getPriorityColor = (priority: ReminderItem['priority']) => {
    switch (priority) {
      case 'urgent':
        return 'text-red-600 dark:text-red-400 bg-red-100 dark:bg-red-900/20';
      case 'high':
        return 'text-orange-600 dark:text-orange-400 bg-orange-100 dark:bg-orange-900/20';
      case 'medium':
        return 'text-yellow-600 dark:text-yellow-400 bg-yellow-100 dark:bg-yellow-900/20';
      case 'low':
        return 'text-green-600 dark:text-green-400 bg-green-100 dark:bg-green-900/20';
      default:
        return 'text-gray-600 dark:text-gray-400 bg-gray-100 dark:bg-gray-700';
    }
  };

  const formatTimeUntil = (daysUntil: number): string => {
    if (daysUntil === 0) return 'Today';
    if (daysUntil === 1) return 'Tomorrow';
    if (daysUntil === -1) return 'Yesterday';
    if (daysUntil < 0) return `${Math.abs(daysUntil)} days ago`;
    return `In ${daysUntil} days`;
  };

  if (loading) {
    return (
      <div className={`bg-white dark:bg-gray-800 rounded-lg shadow p-6 ${className}`}>
        <div className="animate-pulse">
          <div className="h-6 bg-gray-200 dark:bg-gray-700 rounded w-1/3 mb-4"></div>
          <div className="space-y-3">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="flex space-x-3">
                <div className="w-10 h-10 bg-gray-200 dark:bg-gray-700 rounded-full"></div>
                <div className="flex-1 space-y-2">
                  <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-3/4"></div>
                  <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-1/2"></div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4 ${className}`}>
        <p className="text-red-800 dark:text-red-200">{error}</p>
      </div>
    );
  }

  return (
    <div className={`bg-white dark:bg-gray-800 rounded-lg shadow ${className}`}>
      <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
        <h3 className="text-lg font-medium text-gray-900 dark:text-white">
          Gift Reminders
          {reminders.length > 0 && (
            <span className="ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-indigo-100 text-indigo-800 dark:bg-indigo-900/20 dark:text-indigo-400">
              {reminders.length}
            </span>
          )}
        </h3>
      </div>

      <div className="p-6">
        {reminders.length === 0 ? (
          <div className="text-center py-8">
            <svg
              className="mx-auto h-12 w-12 text-gray-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <h4 className="mt-4 text-sm font-medium text-gray-900 dark:text-white">No upcoming reminders</h4>
            <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
              All your gifts are on track or completed!
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {reminders.map(reminder => (
              <div
                key={reminder.id}
                className={`flex items-start space-x-3 p-4 rounded-lg border ${
                  reminder.priority === 'urgent' 
                    ? 'border-red-200 dark:border-red-800 bg-red-50 dark:bg-red-900/10' 
                    : 'border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-700'
                }`}
              >
                <div className={`flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center ${getPriorityColor(reminder.priority)}`}>
                  {getReminderIcon(reminder.type)}
                </div>
                
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between">
                    <h4 className="text-sm font-medium text-gray-900 dark:text-white truncate">
                      {reminder.title}
                    </h4>
                    <div className="flex items-center space-x-2 ml-4">
                      <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium capitalize ${getPriorityColor(reminder.priority)}`}>
                        {reminder.priority}
                      </span>
                      <span className="text-xs text-gray-500 dark:text-gray-400">
                        {formatTimeUntil(reminder.daysUntil)}
                      </span>
                    </div>
                  </div>
                  
                  <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                    {reminder.description}
                  </p>
                  
                  <div className="flex items-center justify-between mt-2">
                    <div className="flex items-center space-x-4 text-xs text-gray-500 dark:text-gray-400">
                      {reminder.gift.occasion && (
                        <span>Occasion: {reminder.gift.occasion}</span>
                      )}
                      {reminder.gift.budget_amount && (
                        <span>Budget: {giftsService.formatCurrency(reminder.gift.budget_amount, reminder.gift.currency)}</span>
                      )}
                    </div>
                    
                    <time className="text-xs text-gray-500 dark:text-gray-400">
                      {reminder.date.toLocaleDateString()}
                    </time>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};