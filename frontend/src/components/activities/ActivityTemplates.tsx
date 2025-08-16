'use client';

import React from 'react';
import { ACTIVITY_TYPES, SharedActivityCreate } from '../../types/Activity';

interface ActivityTemplate {
  id: string;
  name: string;
  description: string;
  activity_type: string;
  icon: string;
  defaultData: Partial<SharedActivityCreate>;
  category: 'popular' | 'social' | 'entertainment' | 'food' | 'sports' | 'work';
}

interface ActivityTemplatesProps {
  onSelectTemplate: (template: ActivityTemplate) => void;
  className?: string;
}

const activityTemplates: ActivityTemplate[] = [
  // Popular Templates
  {
    id: 'dinner-out',
    name: 'Dinner Out',
    description: 'Restaurant meal with friends or family',
    activity_type: 'dinner',
    icon: '🍽️',
    category: 'popular',
    defaultData: {
      activity_type: 'dinner',
      title: 'Dinner at [Restaurant Name]',
      description: 'Enjoyed a delicious meal together',
      currency: 'USD',
    },
  },
  {
    id: 'coffee-chat',
    name: 'Coffee Chat',
    description: 'Casual meetup over coffee',
    activity_type: 'coffee',
    icon: '☕',
    category: 'popular',
    defaultData: {
      activity_type: 'coffee',
      title: 'Coffee with [Friend\'s Name]',
      description: 'Caught up over coffee',
      currency: 'USD',
    },
  },
  {
    id: 'movie-night',
    name: 'Movie Night',
    description: 'Cinema or home movie viewing',
    activity_type: 'movie',
    icon: '🎬',
    category: 'popular',
    defaultData: {
      activity_type: 'movie',
      title: 'Movie: [Movie Title]',
      description: 'Watched a great movie together',
      currency: 'USD',
    },
  },

  // Social Templates
  {
    id: 'birthday-party',
    name: 'Birthday Party',
    description: 'Celebrate someone\'s special day',
    activity_type: 'party',
    icon: '🎉',
    category: 'social',
    defaultData: {
      activity_type: 'party',
      title: '[Name]\'s Birthday Party',
      description: 'Celebrated another year of life!',
      currency: 'USD',
    },
  },
  {
    id: 'game-night',
    name: 'Game Night',
    description: 'Board games or video games with friends',
    activity_type: 'game_night',
    icon: '🎲',
    category: 'social',
    defaultData: {
      activity_type: 'game_night',
      title: 'Game Night',
      description: 'Fun evening playing games together',
    },
  },

  // Entertainment Templates
  {
    id: 'concert',
    name: 'Concert',
    description: 'Live music performance',
    activity_type: 'cultural',
    icon: '🎵',
    category: 'entertainment',
    defaultData: {
      activity_type: 'cultural',
      title: 'Concert: [Artist Name]',
      description: 'Amazing live music experience',
      currency: 'USD',
    },
  },
  {
    id: 'museum-visit',
    name: 'Museum Visit',
    description: 'Educational and cultural experience',
    activity_type: 'cultural',
    icon: '🏛️',
    category: 'entertainment',
    defaultData: {
      activity_type: 'cultural',
      title: 'Visit to [Museum Name]',
      description: 'Explored fascinating exhibits',
      currency: 'USD',
    },
  },

  // Food Templates
  {
    id: 'cooking-together',
    name: 'Cooking Together',
    description: 'Preparing a meal at home',
    activity_type: 'dinner',
    icon: '👨‍🍳',
    category: 'food',
    defaultData: {
      activity_type: 'dinner',
      title: 'Cooking [Dish Name]',
      description: 'Prepared a delicious home-cooked meal',
    },
  },
  {
    id: 'food-festival',
    name: 'Food Festival',
    description: 'Exploring different cuisines',
    activity_type: 'dinner',
    icon: '🍕',
    category: 'food',
    defaultData: {
      activity_type: 'dinner',
      title: '[Festival Name] Food Festival',
      description: 'Tried amazing food from different vendors',
      currency: 'USD',
    },
  },

  // Sports Templates
  {
    id: 'basketball-game',
    name: 'Basketball Game',
    description: 'Playing or watching basketball',
    activity_type: 'sports',
    icon: '🏀',
    category: 'sports',
    defaultData: {
      activity_type: 'sports',
      title: 'Basketball Game',
      description: 'Great game with friends',
    },
  },
  {
    id: 'hiking',
    name: 'Hiking',
    description: 'Outdoor adventure in nature',
    activity_type: 'outdoor',
    icon: '🥾',
    category: 'sports',
    defaultData: {
      activity_type: 'outdoor',
      title: 'Hiking at [Trail Name]',
      description: 'Beautiful hike with amazing views',
    },
  },

  // Work Templates
  {
    id: 'team-lunch',
    name: 'Team Lunch',
    description: 'Work-related meal with colleagues',
    activity_type: 'work_meeting',
    icon: '👥',
    category: 'work',
    defaultData: {
      activity_type: 'work_meeting',
      title: 'Team Lunch',
      description: 'Great team bonding over lunch',
      currency: 'USD',
    },
  },
  {
    id: 'conference',
    name: 'Conference',
    description: 'Professional development event',
    activity_type: 'conference',
    icon: '🎤',
    category: 'work',
    defaultData: {
      activity_type: 'conference',
      title: '[Conference Name]',
      description: 'Valuable learning and networking experience',
      currency: 'USD',
    },
  },
];

export const ActivityTemplates: React.FC<ActivityTemplatesProps> = ({
  onSelectTemplate,
  className = '',
}) => {
  const categories = [
    { id: 'popular', name: 'Popular', emoji: '⭐' },
    { id: 'social', name: 'Social', emoji: '👥' },
    { id: 'entertainment', name: 'Entertainment', emoji: '🎭' },
    { id: 'food', name: 'Food & Dining', emoji: '🍽️' },
    { id: 'sports', name: 'Sports & Outdoor', emoji: '⚽' },
    { id: 'work', name: 'Work & Professional', emoji: '💼' },
  ];

  const getTemplatesByCategory = (categoryId: string) => {
    return activityTemplates.filter(template => template.category === categoryId);
  };

  return (
    <div className={`space-y-8 ${className}`}>
      <div className="text-center">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-2">
          Activity Templates
        </h2>
        <p className="text-gray-600 dark:text-gray-400">
          Choose a template to quickly create an activity with pre-filled details
        </p>
      </div>

      {categories.map(category => {
        const templates = getTemplatesByCategory(category.id);
        
        if (templates.length === 0) return null;

        return (
          <div key={category.id} className="space-y-4">
            <div className="flex items-center space-x-2">
              <span className="text-2xl">{category.emoji}</span>
              <h3 className="text-xl font-semibold text-gray-900 dark:text-gray-100">
                {category.name}
              </h3>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {templates.map(template => (
                <button
                  key={template.id}
                  onClick={() => onSelectTemplate(template)}
                  className="group p-6 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg hover:border-blue-300 dark:hover:border-blue-600 hover:shadow-md transition-all text-left"
                >
                  <div className="flex items-start space-x-4">
                    <div className="flex-shrink-0">
                      <span className="text-3xl">{template.icon}</span>
                    </div>
                    <div className="flex-1 min-w-0">
                      <h4 className="text-lg font-medium text-gray-900 dark:text-gray-100 group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors">
                        {template.name}
                      </h4>
                      <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                        {template.description}
                      </p>
                      
                      {/* Preview of default data */}
                      <div className="mt-3 space-y-1">
                        {template.defaultData.title && (
                          <div className="text-xs text-gray-500 dark:text-gray-400">
                            <span className="font-medium">Title:</span> {template.defaultData.title}
                          </div>
                        )}
                        {template.defaultData.description && (
                          <div className="text-xs text-gray-500 dark:text-gray-400">
                            <span className="font-medium">Description:</span> {template.defaultData.description}
                          </div>
                        )}
                      </div>

                      {/* Activity type badge */}
                      <div className="mt-3">
                        <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-400">
                          {ACTIVITY_TYPES.find(type => type.value === template.activity_type)?.label || template.activity_type}
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* Use template button overlay */}
                  <div className="mt-4 flex items-center justify-between">
                    <span className="text-sm text-gray-500 dark:text-gray-400">
                      Click to use template
                    </span>
                    <svg className="w-5 h-5 text-gray-400 group-hover:text-blue-500 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                    </svg>
                  </div>
                </button>
              ))}
            </div>
          </div>
        );
      })}

      {/* Custom Activity Option */}
      <div className="border-t border-gray-200 dark:border-gray-700 pt-8">
        <div className="text-center">
          <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">
            Don't see what you're looking for?
          </h3>
          <p className="text-gray-600 dark:text-gray-400 mb-4">
            Create a custom activity from scratch
          </p>
          <button
            onClick={() => onSelectTemplate({
              id: 'custom',
              name: 'Custom Activity',
              description: 'Create a custom activity',
              activity_type: 'other',
              icon: '📝',
              category: 'popular',
              defaultData: {
                activity_type: 'other',
                title: '',
                description: '',
                currency: 'USD',
              },
            })}
            className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            Create Custom Activity
          </button>
        </div>
      </div>
    </div>
  );
};