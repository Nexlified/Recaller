'use client';

import React, { useMemo } from 'react';
import { SharedActivity, ACTIVITY_TYPES } from '../../types/Activity';

interface ActivitySuggestion {
  id: string;
  title: string;
  description: string;
  activity_type: string;
  icon: string;
  reasoning: string;
  confidence: number; // 0-100
}

interface ActivitySuggestionsProps {
  contactId?: number;
  pastActivities: SharedActivity[];
  currentSeason?: 'spring' | 'summer' | 'fall' | 'winter';
  className?: string;
}

export const ActivitySuggestions: React.FC<ActivitySuggestionsProps> = ({
  contactId,
  pastActivities,
  currentSeason = 'fall', // Default to fall as an example
  className = '',
}) => {
  const suggestions = useMemo(() => {
    const generateSuggestions = (): ActivitySuggestion[] => {
      const suggestions: ActivitySuggestion[] = [];

      // Analyze past activities for patterns
      const activityTypeFrequency = pastActivities.reduce((acc, activity) => {
        acc[activity.activity_type] = (acc[activity.activity_type] || 0) + 1;
        return acc;
      }, {} as Record<string, number>);

      const favoriteTypes = Object.entries(activityTypeFrequency)
        .sort(([, a], [, b]) => b - a)
        .slice(0, 3)
        .map(([type]) => type);

      const recentActivities = pastActivities
        .slice(-5)
        .map(a => a.activity_type);

      const hasRecentActivity = (type: string) => 
        recentActivities.includes(type);

      // Base suggestions based on patterns
      if (favoriteTypes.includes('dinner') && !hasRecentActivity('dinner')) {
        suggestions.push({
          id: 'dinner-suggestion',
          title: 'Try a New Restaurant',
          description: 'You both enjoy dining out - explore a new cuisine together',
          activity_type: 'dinner',
          icon: '🍽️',
          reasoning: 'Based on your dining history',
          confidence: 85,
        });
      }

      if (favoriteTypes.includes('movie') && !hasRecentActivity('movie')) {
        suggestions.push({
          id: 'movie-suggestion',
          title: 'Movie Night',
          description: 'Watch the latest blockbuster or a classic film',
          activity_type: 'movie',
          icon: '🎬',
          reasoning: 'You both love movies',
          confidence: 80,
        });
      }

      if (favoriteTypes.includes('coffee') && !hasRecentActivity('coffee')) {
        suggestions.push({
          id: 'coffee-suggestion',
          title: 'Coffee Catch-up',
          description: 'Find a cozy cafe and catch up over great coffee',
          activity_type: 'coffee',
          icon: '☕',
          reasoning: 'Perfect for a casual meetup',
          confidence: 75,
        });
      }

      // Seasonal suggestions
      const seasonalSuggestions = getSeasonalSuggestions(currentSeason);
      suggestions.push(...seasonalSuggestions.filter(s => 
        !hasRecentActivity(s.activity_type)
      ));

      // Activity type diversity suggestions
      const allTypes = ACTIVITY_TYPES.map(t => t.value);
      const untriedTypes = allTypes.filter(type => 
        !activityTypeFrequency[type] && !hasRecentActivity(type)
      );

      untriedTypes.slice(0, 2).forEach(type => {
        const activityType = ACTIVITY_TYPES.find(t => t.value === type);
        if (activityType) {
          suggestions.push({
            id: `new-${type}`,
            title: `Try ${activityType.label}`,
            description: `Experience something new together - ${activityType.label.toLowerCase()}`,
            activity_type: type,
            icon: activityType.icon,
            reasoning: 'Expand your experiences',
            confidence: 60,
          });
        }
      });

      // Time-based suggestions (haven't seen in a while)
      if (pastActivities.length > 0) {
        const lastActivity = pastActivities[pastActivities.length - 1];
        const daysSinceLastActivity = Math.floor(
          (new Date().getTime() - new Date(lastActivity.activity_date).getTime()) / 
          (1000 * 60 * 60 * 24)
        );

        if (daysSinceLastActivity > 30) {
          suggestions.push({
            id: 'overdue-meetup',
            title: 'Long Overdue Meetup',
            description: 'It\'s been a while - plan something special to reconnect',
            activity_type: 'dinner',
            icon: '🤝',
            reasoning: `Haven't met in ${daysSinceLastActivity} days`,
            confidence: 90,
          });
        }
      }

      // Budget-friendly suggestions
      const hasExpensiveRecent = pastActivities
        .slice(-3)
        .some(a => (a.total_cost || a.cost_per_person || 0) > 50);

      if (hasExpensiveRecent) {
        suggestions.push({
          id: 'budget-friendly',
          title: 'Budget-Friendly Hangout',
          description: 'Enjoy quality time without breaking the bank',
          activity_type: 'coffee',
          icon: '💰',
          reasoning: 'Balance your recent spending',
          confidence: 70,
        });
      }

      // Sort by confidence and return top suggestions
      return suggestions
        .sort((a, b) => b.confidence - a.confidence)
        .slice(0, 6);
    };

    return generateSuggestions();
  }, [pastActivities, currentSeason, contactId]);

  const getSeasonalSuggestions = (season: string): ActivitySuggestion[] => {
    switch (season) {
      case 'spring':
        return [
          {
            id: 'spring-outdoor',
            title: 'Spring Picnic',
            description: 'Enjoy the beautiful spring weather with an outdoor picnic',
            activity_type: 'outdoor',
            icon: '🌸',
            reasoning: 'Perfect spring weather',
            confidence: 75,
          },
          {
            id: 'spring-garden',
            title: 'Visit a Garden',
            description: 'Explore botanical gardens or flower festivals',
            activity_type: 'cultural',
            icon: '🌷',
            reasoning: 'Spring blooms are beautiful',
            confidence: 70,
          },
        ];
      case 'summer':
        return [
          {
            id: 'summer-beach',
            title: 'Beach Day',
            description: 'Soak up the sun at the beach or lake',
            activity_type: 'outdoor',
            icon: '🏖️',
            reasoning: 'Perfect summer weather',
            confidence: 80,
          },
          {
            id: 'summer-bbq',
            title: 'BBQ Party',
            description: 'Fire up the grill for a fun outdoor meal',
            activity_type: 'party',
            icon: '🔥',
            reasoning: 'Great for summer gatherings',
            confidence: 75,
          },
        ];
      case 'fall':
        return [
          {
            id: 'fall-hiking',
            title: 'Fall Foliage Hike',
            description: 'Enjoy the beautiful autumn colors on a nature hike',
            activity_type: 'outdoor',
            icon: '🍂',
            reasoning: 'Beautiful fall scenery',
            confidence: 78,
          },
          {
            id: 'fall-festival',
            title: 'Harvest Festival',
            description: 'Visit a local harvest festival or farmers market',
            activity_type: 'cultural',
            icon: '🎃',
            reasoning: 'Seasonal festivities',
            confidence: 72,
          },
        ];
      case 'winter':
        return [
          {
            id: 'winter-cozy',
            title: 'Cozy Indoor Activity',
            description: 'Stay warm with hot chocolate and board games',
            activity_type: 'game_night',
            icon: '☕',
            reasoning: 'Perfect for cold weather',
            confidence: 76,
          },
          {
            id: 'winter-holidays',
            title: 'Holiday Celebration',
            description: 'Celebrate the holiday season together',
            activity_type: 'party',
            icon: '🎄',
            reasoning: 'Holiday spirit',
            confidence: 74,
          },
        ];
      default:
        return [];
    }
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 80) return 'text-green-600 dark:text-green-400';
    if (confidence >= 70) return 'text-yellow-600 dark:text-yellow-400';
    return 'text-gray-600 dark:text-gray-400';
  };

  const getConfidenceLabel = (confidence: number) => {
    if (confidence >= 80) return 'High match';
    if (confidence >= 70) return 'Good match';
    return 'Worth trying';
  };

  if (suggestions.length === 0) {
    return (
      <div className={`text-center py-8 ${className}`}>
        <div className="text-gray-400 dark:text-gray-500 mb-3">
          <svg className="mx-auto h-8 w-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
          </svg>
        </div>
        <p className="text-sm text-gray-500 dark:text-gray-400">
          Build more activity history to get personalized suggestions
        </p>
      </div>
    );
  }

  return (
    <div className={`space-y-4 ${className}`}>
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100">
          Activity Suggestions
        </h3>
        <span className="text-sm text-gray-500 dark:text-gray-400">
          AI-powered recommendations
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {suggestions.map((suggestion) => (
          <div
            key={suggestion.id}
            className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-4 hover:border-blue-300 dark:hover:border-blue-600 hover:shadow-md transition-all cursor-pointer"
            onClick={() => {
              // This could trigger activity creation with pre-filled data
              window.location.href = `/activities/new?template=${suggestion.id}`;
            }}
          >
            <div className="flex items-start space-x-3">
              <div className="flex-shrink-0">
                <span className="text-2xl">{suggestion.icon}</span>
              </div>
              <div className="flex-1 min-w-0">
                <h4 className="text-sm font-medium text-gray-900 dark:text-gray-100">
                  {suggestion.title}
                </h4>
                <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                  {suggestion.description}
                </p>
                
                <div className="flex items-center justify-between mt-3">
                  <div className="flex items-center space-x-2">
                    <span className="text-xs text-gray-500 dark:text-gray-400">
                      {suggestion.reasoning}
                    </span>
                  </div>
                  <div className="flex items-center space-x-1">
                    <span className={`text-xs font-medium ${getConfidenceColor(suggestion.confidence)}`}>
                      {getConfidenceLabel(suggestion.confidence)}
                    </span>
                    <span className="text-xs text-gray-400">
                      {suggestion.confidence}%
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Call to action */}
      <div className="text-center pt-4 border-t border-gray-200 dark:border-gray-700">
        <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
          These suggestions improve as you log more activities
        </p>
        <button className="text-sm text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 font-medium">
          View all activity ideas →
        </button>
      </div>
    </div>
  );
};