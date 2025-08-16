'use client';

import React, { useState, useEffect } from 'react';
import { Gift } from '../../types/Gift';
import giftsService from '../../services/gifts';
import { Contact } from '../../services/contacts';

interface TimelineEvent {
  id: string;
  date: Date;
  type: 'gift_given' | 'gift_planned' | 'gift_idea_created';
  title: string;
  description: string;
  gift: Gift;
}

interface GiftHistoryTimelineProps {
  contactId: number;
  contact?: Contact;
  className?: string;
}

export const GiftHistoryTimeline: React.FC<GiftHistoryTimelineProps> = ({
  contactId,
  contact,
  className = ''
}) => {
  const [events, setEvents] = useState<TimelineEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadGiftHistory();
  }, [contactId]);

  const loadGiftHistory = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const gifts = await giftsService.getGiftsByContact(contactId);
      const timelineEvents = createTimelineEvents(gifts);
      setEvents(timelineEvents);
    } catch (err) {
      console.error('Error loading gift history:', err);
      setError('Failed to load gift history');
    } finally {
      setLoading(false);
    }
  };

  const createTimelineEvents = (gifts: Gift[]): TimelineEvent[] => {
    const events: TimelineEvent[] = [];

    gifts.forEach(gift => {
      // Gift creation event
      events.push({
        id: `gift-created-${gift.id}`,
        date: new Date(gift.created_at),
        type: 'gift_idea_created',
        title: 'Gift idea created',
        description: `Added "${gift.title}" as a gift idea`,
        gift
      });

      // Gift given event
      if (gift.status === 'given' && gift.occasion_date) {
        events.push({
          id: `gift-given-${gift.id}`,
          date: new Date(gift.occasion_date),
          type: 'gift_given',
          title: 'Gift given',
          description: `Gave "${gift.title}" for ${gift.occasion || 'special occasion'}`,
          gift
        });
      }

      // Gift planned event
      if (gift.status === 'planned' && gift.occasion_date) {
        events.push({
          id: `gift-planned-${gift.id}`,
          date: new Date(gift.occasion_date),
          type: 'gift_planned',
          title: 'Gift planned',
          description: `Planned "${gift.title}" for ${gift.occasion || 'upcoming occasion'}`,
          gift
        });
      }
    });

    // Sort by date (most recent first)
    return events.sort((a, b) => b.date.getTime() - a.date.getTime());
  };

  const getEventIcon = (type: TimelineEvent['type']) => {
    switch (type) {
      case 'gift_given':
        return (
          <div className="flex items-center justify-center w-8 h-8 bg-green-100 dark:bg-green-900/20 rounded-full">
            <svg className="w-4 h-4 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
            </svg>
          </div>
        );
      case 'gift_planned':
        return (
          <div className="flex items-center justify-center w-8 h-8 bg-blue-100 dark:bg-blue-900/20 rounded-full">
            <svg className="w-4 h-4 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
            </svg>
          </div>
        );
      case 'gift_idea_created':
        return (
          <div className="flex items-center justify-center w-8 h-8 bg-yellow-100 dark:bg-yellow-900/20 rounded-full">
            <svg className="w-4 h-4 text-yellow-600 dark:text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
          </div>
        );
    }
  };

  const getEventColor = (type: TimelineEvent['type']) => {
    switch (type) {
      case 'gift_given':
        return 'text-green-600 dark:text-green-400';
      case 'gift_planned':
        return 'text-blue-600 dark:text-blue-400';
      case 'gift_idea_created':
        return 'text-yellow-600 dark:text-yellow-400';
    }
  };

  if (loading) {
    return (
      <div className={`${className}`}>
        <div className="animate-pulse space-y-4">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="flex space-x-4">
              <div className="w-8 h-8 bg-gray-200 dark:bg-gray-700 rounded-full"></div>
              <div className="flex-1 space-y-2">
                <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-3/4"></div>
                <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-1/2"></div>
              </div>
            </div>
          ))}
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
          Gift History
          {contact && (
            <span className="text-sm font-normal text-gray-500 dark:text-gray-400 ml-2">
              for {contact.first_name} {contact.last_name}
            </span>
          )}
        </h3>
      </div>

      <div className="p-6">
        {events.length === 0 ? (
          <div className="text-center py-8">
            <svg
              className="mx-auto h-12 w-12 text-gray-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
            </svg>
            <h4 className="mt-4 text-sm font-medium text-gray-900 dark:text-white">No gift history</h4>
            <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
              Start by adding a gift for this contact
            </p>
          </div>
        ) : (
          <div className="flow-root">
            <ul className="-mb-8">
              {events.map((event, eventIdx) => (
                <li key={event.id}>
                  <div className="relative pb-8">
                    {eventIdx !== events.length - 1 && (
                      <span
                        className="absolute top-4 left-4 -ml-px h-full w-0.5 bg-gray-200 dark:bg-gray-700"
                        aria-hidden="true"
                      />
                    )}
                    <div className="relative flex space-x-3">
                      {/* Timeline dot */}
                      <div className="relative z-10 flex items-center justify-center">
                        {getEventIcon(event.type)}
                      </div>
                      
                      {/* Event content */}
                      <div className="min-w-0 flex-1">
                        <div className="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg border border-gray-200 dark:border-gray-600">
                          <div className="flex justify-between items-start">
                            <div className="flex-1">
                              <h4 className={`font-medium ${getEventColor(event.type)}`}>
                                {event.title}
                              </h4>
                              <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                                {event.description}
                              </p>
                              
                              {/* Gift details */}
                              <div className="mt-3 flex flex-wrap gap-4 text-xs text-gray-500 dark:text-gray-400">
                                {event.gift.category && (
                                  <span className="inline-flex items-center px-2 py-1 bg-gray-100 dark:bg-gray-600 rounded">
                                    Category: {event.gift.category}
                                  </span>
                                )}
                                {event.gift.budget_amount && (
                                  <span className="inline-flex items-center px-2 py-1 bg-gray-100 dark:bg-gray-600 rounded">
                                    Budget: {giftsService.formatCurrency(event.gift.budget_amount, event.gift.currency)}
                                  </span>
                                )}
                                {event.gift.status && (
                                  <span className={`inline-flex items-center px-2 py-1 rounded capitalize ${
                                    event.gift.status === 'given' ? 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400' :
                                    event.gift.status === 'planned' ? 'bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-400' :
                                    'bg-gray-100 text-gray-800 dark:bg-gray-600 dark:text-gray-200'
                                  }`}>
                                    {event.gift.status}
                                  </span>
                                )}
                              </div>

                              {/* Gift notes */}
                              {event.gift.notes && (
                                <p className="mt-2 text-sm text-gray-600 dark:text-gray-400 italic">
                                  "{event.gift.notes}"
                                </p>
                              )}
                            </div>
                            
                            <div className="text-right ml-4">
                              <time className="text-xs text-gray-500 dark:text-gray-400">
                                {event.date.toLocaleDateString()}
                              </time>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Summary section */}
        {events.length > 0 && (
          <div className="mt-6 pt-6 border-t border-gray-200 dark:border-gray-700">
            <h4 className="font-medium text-gray-900 dark:text-white mb-2">Summary</h4>
            <div className="grid grid-cols-3 gap-4 text-center">
              <div>
                <div className="text-lg font-bold text-green-600 dark:text-green-400">
                  {events.filter(e => e.type === 'gift_given').length}
                </div>
                <div className="text-xs text-gray-600 dark:text-gray-400">Gifts Given</div>
              </div>
              <div>
                <div className="text-lg font-bold text-blue-600 dark:text-blue-400">
                  {events.filter(e => e.type === 'gift_planned').length}
                </div>
                <div className="text-xs text-gray-600 dark:text-gray-400">Planned</div>
              </div>
              <div>
                <div className="text-lg font-bold text-yellow-600 dark:text-yellow-400">
                  {events.filter(e => e.type === 'gift_idea_created').length}
                </div>
                <div className="text-xs text-gray-600 dark:text-gray-400">Ideas Created</div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};