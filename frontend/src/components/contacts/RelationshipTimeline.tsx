import React, { useState, useEffect, useCallback } from 'react';
import { ContactRelationship } from '../../types/ContactRelationship';
import { Contact } from '../../services/contacts';
import contactRelationshipService from '../../services/contactRelationships';
import contactsService from '../../services/contacts';

interface TimelineEvent {
  id: string;
  date: Date;
  type: 'relationship_started' | 'relationship_ended' | 'relationship_changed';
  title: string;
  description: string;
  relationship: ContactRelationship;
  otherContact: Contact;
}

interface RelationshipTimelineProps {
  contactId: number;
}

export const RelationshipTimeline: React.FC<RelationshipTimelineProps> = ({ contactId }) => {
  const [events, setEvents] = useState<TimelineEvent[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [timeRange, setTimeRange] = useState<'all' | '1year' | '6months' | '3months'>('all');

  useEffect(() => {
    loadTimelineData();
  }, [loadTimelineData]);

  const loadTimelineData = useCallback(async () => {
    try {
      setIsLoading(true);
      const [relationships, contacts] = await Promise.all([
        contactRelationshipService.getContactRelationships(contactId, true), // Include inactive
        contactsService.getContacts()
      ]);

      const timelineEvents: TimelineEvent[] = [];
      const now = new Date();
      const cutoffDate = getCutoffDate(timeRange, now);

      relationships.forEach((relationship) => {
        const otherContactId = relationship.contact_a_id === contactId 
          ? relationship.contact_b_id 
          : relationship.contact_a_id;
        
        const otherContact = contacts.find(c => c.id === otherContactId);
        if (!otherContact) return;

        // Relationship started event
        if (relationship.start_date) {
          const startDate = new Date(relationship.start_date);
          if (!cutoffDate || startDate >= cutoffDate) {
            timelineEvents.push({
              id: `${relationship.id}-start`,
              date: startDate,
              type: 'relationship_started',
              title: `Relationship Started`,
              description: `Started ${relationship.relationship_type} relationship with ${otherContact.first_name} ${otherContact.last_name || ''}`,
              relationship,
              otherContact
            });
          }
        }

        // Relationship ended event
        if (relationship.end_date) {
          const endDate = new Date(relationship.end_date);
          if (!cutoffDate || endDate >= cutoffDate) {
            timelineEvents.push({
              id: `${relationship.id}-end`,
              date: endDate,
              type: 'relationship_ended',
              title: `Relationship Ended`,
              description: `Ended ${relationship.relationship_type} relationship with ${otherContact.first_name} ${otherContact.last_name || ''}`,
              relationship,
              otherContact
            });
          }
        }

        // If no specific dates, use creation date
        if (!relationship.start_date && !relationship.end_date) {
          const createdDate = new Date(relationship.created_at);
          if (!cutoffDate || createdDate >= cutoffDate) {
            timelineEvents.push({
              id: `${relationship.id}-created`,
              date: createdDate,
              type: 'relationship_started',
              title: `Relationship Added`,
              description: `Added ${relationship.relationship_type} relationship with ${otherContact.first_name} ${otherContact.last_name || ''}`,
              relationship,
              otherContact
            });
          }
        }
      });

      // Sort by date (newest first)
      timelineEvents.sort((a, b) => b.date.getTime() - a.date.getTime());
      setEvents(timelineEvents);
    } catch (error) {
      console.error('Error loading timeline data:', error);
    } finally {
      setIsLoading(false);
    }
  }, [contactId, timeRange]);

  const getCutoffDate = (range: string, now: Date): Date | null => {
    switch (range) {
      case '3months':
        return new Date(now.getFullYear(), now.getMonth() - 3, now.getDate());
      case '6months':
        return new Date(now.getFullYear(), now.getMonth() - 6, now.getDate());
      case '1year':
        return new Date(now.getFullYear() - 1, now.getMonth(), now.getDate());
      default:
        return null;
    }
  };

  const formatDate = (date: Date) => {
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const getEventIcon = (type: TimelineEvent['type']) => {
    switch (type) {
      case 'relationship_started':
        return (
          <div className="w-3 h-3 bg-green-500 rounded-full border-2 border-white dark:border-gray-800" />
        );
      case 'relationship_ended':
        return (
          <div className="w-3 h-3 bg-red-500 rounded-full border-2 border-white dark:border-gray-800" />
        );
      case 'relationship_changed':
        return (
          <div className="w-3 h-3 bg-blue-500 rounded-full border-2 border-white dark:border-gray-800" />
        );
      default:
        return (
          <div className="w-3 h-3 bg-gray-500 rounded-full border-2 border-white dark:border-gray-800" />
        );
    }
  };

  const getEventColor = (type: TimelineEvent['type']) => {
    switch (type) {
      case 'relationship_started':
        return 'text-green-600 dark:text-green-400';
      case 'relationship_ended':
        return 'text-red-600 dark:text-red-400';
      case 'relationship_changed':
        return 'text-blue-600 dark:text-blue-400';
      default:
        return 'text-gray-600 dark:text-gray-400';
    }
  };

  if (isLoading) {
    return (
      <div className="p-4">
        <div className="text-center text-gray-600 dark:text-gray-400">
          Loading timeline...
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
          Relationship Timeline
        </h3>
        <select
          value={timeRange}
          onChange={(e) => setTimeRange(e.target.value as 'all' | '1year' | '6months' | '3months')}
          className="text-sm border border-gray-300 dark:border-gray-600 rounded px-3 py-1 focus:outline-none focus:ring-1 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
        >
          <option value="all">All Time</option>
          <option value="1year">Last Year</option>
          <option value="6months">Last 6 Months</option>
          <option value="3months">Last 3 Months</option>
        </select>
      </div>

      {events.length === 0 ? (
        <div className="text-center py-8 text-gray-500 dark:text-gray-400">
          No relationship events found for the selected time period.
        </div>
      ) : (
        <div className="relative">
          {/* Timeline line */}
          <div className="absolute left-4 top-6 bottom-0 w-px bg-gray-200 dark:bg-gray-700"></div>
          
          <div className="space-y-6">
            {events.map((event) => (
              <div key={event.id} className="relative flex items-start">
                {/* Timeline dot */}
                <div className="relative z-10 flex items-center justify-center">
                  {getEventIcon(event.type)}
                </div>
                
                {/* Event content */}
                <div className="ml-4 flex-1">
                  <div className="bg-white dark:bg-gray-800 p-4 rounded-lg border border-gray-200 dark:border-gray-700 shadow-sm">
                    <div className="flex justify-between items-start">
                      <div>
                        <h4 className={`font-medium ${getEventColor(event.type)}`}>
                          {event.title}
                        </h4>
                        <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                          {event.description}
                        </p>
                        
                        {/* Additional relationship details */}
                        <div className="mt-2 flex flex-wrap gap-2 text-xs">
                          {event.relationship.relationship_strength && (
                            <span className="bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded">
                              Strength: {event.relationship.relationship_strength}/10
                            </span>
                          )}
                          <span className="bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded">
                            {event.relationship.relationship_category}
                          </span>
                          {event.relationship.is_mutual && (
                            <span className="bg-blue-100 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300 px-2 py-1 rounded">
                              Mutual
                            </span>
                          )}
                        </div>
                        
                        {event.relationship.notes && (
                          <p className="text-xs text-gray-500 dark:text-gray-500 mt-2 italic">
                            &quot;{event.relationship.notes}&quot;
                          </p>
                        )}
                      </div>
                      
                      <time className="text-xs text-gray-500 dark:text-gray-500 ml-4">
                        {formatDate(event.date)}
                      </time>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
      
      {/* Timeline summary */}
      {events.length > 0 && (
        <div className="mt-6 p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
          <h4 className="font-medium text-gray-900 dark:text-white mb-2">Timeline Summary</h4>
          <div className="grid grid-cols-3 gap-4 text-center">
            <div>
              <div className="text-lg font-bold text-green-600 dark:text-green-400">
                {events.filter(e => e.type === 'relationship_started').length}
              </div>
              <div className="text-xs text-gray-600 dark:text-gray-400">Started</div>
            </div>
            <div>
              <div className="text-lg font-bold text-red-600 dark:text-red-400">
                {events.filter(e => e.type === 'relationship_ended').length}
              </div>
              <div className="text-xs text-gray-600 dark:text-gray-400">Ended</div>
            </div>
            <div>
              <div className="text-lg font-bold text-blue-600 dark:text-blue-400">
                {events.filter(e => e.type === 'relationship_changed').length}
              </div>
              <div className="text-xs text-gray-600 dark:text-gray-400">Changed</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};