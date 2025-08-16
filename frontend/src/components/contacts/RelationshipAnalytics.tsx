import React, { useEffect, useState } from 'react';
import { ContactRelationship } from '../../types/ContactRelationship';
import relationshipService, { RelationshipAnalytics } from '../../services/relationships';

interface RelationshipAnalyticsProps {
  contactId?: number;
  relationships: ContactRelationship[];
}

interface ChartData {
  label: string;
  value: number;
  percentage: number;
  color: string;
}

export const RelationshipAnalyticsDashboard: React.FC<RelationshipAnalyticsProps> = ({
  contactId,
  relationships
}) => {
  const [analytics, setAnalytics] = useState<RelationshipAnalytics | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    calculateAnalytics();
  }, [contactId, relationships]);

  const calculateAnalytics = async () => {
    try {
      setIsLoading(true);
      
      // Calculate analytics from relationships data
      const totalRelationships = relationships.length;
      
      if (totalRelationships === 0) {
        setAnalytics(null);
        return;
      }

      // Category distribution
      const categoryCount = relationships.reduce((acc, rel) => {
        acc[rel.relationship_category] = (acc[rel.relationship_category] || 0) + 1;
        return acc;
      }, {} as Record<string, number>);

      const categoryDistribution = {
        family: categoryCount.family || 0,
        professional: categoryCount.professional || 0,
        social: categoryCount.social || 0,
        romantic: categoryCount.romantic || 0
      };

      // Strength distribution
      const strengthDistribution = relationships.reduce((acc, rel) => {
        const strength = rel.relationship_strength || 5;
        if (strength <= 3) acc.weak++;
        else if (strength <= 6) acc.moderate++;
        else acc.strong++;
        return acc;
      }, { weak: 0, moderate: 0, strong: 0 });

      // Status distribution
      const statusDistribution = relationships.reduce((acc, rel) => {
        acc[rel.relationship_status]++;
        return acc;
      }, { active: 0, distant: 0, ended: 0 } as Record<string, number>);

      // Top categories
      const topCategories = Object.entries(categoryDistribution)
        .map(([category, count]) => ({
          category,
          count,
          percentage: (count / totalRelationships) * 100
        }))
        .sort((a, b) => b.count - a.count);

      // Network insights
      const strengthValues = relationships
        .map(rel => rel.relationship_strength || 5)
        .filter(strength => strength > 0);
      
      const averageStrength = strengthValues.length > 0 
        ? strengthValues.reduce((sum, strength) => sum + strength, 0) / strengthValues.length
        : 0;

      const mostConnectedCategory = topCategories[0]?.category || 'none';

      // Find oldest and newest relationships
      const sortedByDate = relationships
        .filter(rel => rel.created_at)
        .sort((a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime());

      const analyticsData: RelationshipAnalytics = {
        totalRelationships,
        categoryDistribution,
        strengthDistribution,
        statusDistribution,
        topCategories,
        networkInsights: {
          averageStrength,
          mostConnectedCategory,
          oldestRelationship: sortedByDate[0],
          newestRelationship: sortedByDate[sortedByDate.length - 1]
        }
      };

      setAnalytics(analyticsData);
    } catch (error) {
      console.error('Error calculating analytics:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const renderPieChart = (data: ChartData[], title: string) => {
    const total = data.reduce((sum, item) => sum + item.value, 0);
    if (total === 0) return null;

    let cumulativePercentage = 0;

    return (
      <div className="bg-white dark:bg-gray-800 p-4 rounded-lg border border-gray-200 dark:border-gray-700">
        <h4 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">{title}</h4>
        <div className="flex items-center space-x-4">
          <div className="relative">
            <svg width="120" height="120" className="transform -rotate-90">
              {data.map((item, index) => {
                const percentage = (item.value / total) * 100;
                const strokeDasharray = `${percentage * 2.51} 251.2`; // 2π * 40 = 251.2
                const strokeDashoffset = -cumulativePercentage * 2.51;
                cumulativePercentage += percentage;

                return (
                  <circle
                    key={index}
                    cx="60"
                    cy="60"
                    r="40"
                    fill="transparent"
                    stroke={item.color}
                    strokeWidth="12"
                    strokeDasharray={strokeDasharray}
                    strokeDashoffset={strokeDashoffset}
                    className="transition-all duration-300"
                  />
                );
              })}
            </svg>
            <div className="absolute inset-0 flex items-center justify-center">
              <span className="text-lg font-bold text-gray-900 dark:text-white">{total}</span>
            </div>
          </div>
          <div className="flex-1 space-y-2">
            {data.map((item, index) => (
              <div key={index} className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <div 
                    className="w-3 h-3 rounded-full" 
                    style={{ backgroundColor: item.color }}
                  />
                  <span className="text-sm text-gray-700 dark:text-gray-300 capitalize">
                    {item.label}
                  </span>
                </div>
                <div className="text-right">
                  <span className="text-sm font-medium text-gray-900 dark:text-white">
                    {item.value}
                  </span>
                  <span className="text-xs text-gray-500 dark:text-gray-400 ml-1">
                    ({item.percentage.toFixed(1)}%)
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  };

  const renderBarChart = (data: ChartData[], title: string) => {
    const maxValue = Math.max(...data.map(item => item.value));
    if (maxValue === 0) return null;

    return (
      <div className="bg-white dark:bg-gray-800 p-4 rounded-lg border border-gray-200 dark:border-gray-700">
        <h4 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">{title}</h4>
        <div className="space-y-3">
          {data.map((item, index) => (
            <div key={index} className="space-y-1">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-700 dark:text-gray-300 capitalize">
                  {item.label}
                </span>
                <span className="text-sm font-medium text-gray-900 dark:text-white">
                  {item.value}
                </span>
              </div>
              <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                <div
                  className="h-2 rounded-full transition-all duration-300"
                  style={{ 
                    width: `${(item.value / maxValue) * 100}%`,
                    backgroundColor: item.color
                  }}
                />
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-2 text-gray-600 dark:text-gray-400">Loading analytics...</p>
        </div>
      </div>
    );
  }

  if (!analytics || analytics.totalRelationships === 0) {
    return (
      <div className="flex items-center justify-center h-64 bg-gray-50 dark:bg-gray-800 rounded-lg">
        <div className="text-center">
          <div className="text-4xl mb-2">📊</div>
          <p className="text-gray-600 dark:text-gray-400">No relationships to analyze</p>
          <p className="text-sm text-gray-500 dark:text-gray-500 mt-1">
            Add some relationships to see analytics and insights
          </p>
        </div>
      </div>
    );
  }

  const categoryData: ChartData[] = [
    { label: 'family', value: analytics.categoryDistribution.family, percentage: (analytics.categoryDistribution.family / analytics.totalRelationships) * 100, color: '#3B82F6' },
    { label: 'professional', value: analytics.categoryDistribution.professional, percentage: (analytics.categoryDistribution.professional / analytics.totalRelationships) * 100, color: '#10B981' },
    { label: 'social', value: analytics.categoryDistribution.social, percentage: (analytics.categoryDistribution.social / analytics.totalRelationships) * 100, color: '#F59E0B' },
    { label: 'romantic', value: analytics.categoryDistribution.romantic, percentage: (analytics.categoryDistribution.romantic / analytics.totalRelationships) * 100, color: '#EF4444' }
  ].filter(item => item.value > 0);

  const strengthData: ChartData[] = [
    { label: 'weak (1-3)', value: analytics.strengthDistribution.weak, percentage: (analytics.strengthDistribution.weak / analytics.totalRelationships) * 100, color: '#EF4444' },
    { label: 'moderate (4-6)', value: analytics.strengthDistribution.moderate, percentage: (analytics.strengthDistribution.moderate / analytics.totalRelationships) * 100, color: '#F59E0B' },
    { label: 'strong (7-10)', value: analytics.strengthDistribution.strong, percentage: (analytics.strengthDistribution.strong / analytics.totalRelationships) * 100, color: '#10B981' }
  ].filter(item => item.value > 0);

  const statusData: ChartData[] = [
    { label: 'active', value: analytics.statusDistribution.active, percentage: (analytics.statusDistribution.active / analytics.totalRelationships) * 100, color: '#10B981' },
    { label: 'distant', value: analytics.statusDistribution.distant, percentage: (analytics.statusDistribution.distant / analytics.totalRelationships) * 100, color: '#F59E0B' },
    { label: 'ended', value: analytics.statusDistribution.ended, percentage: (analytics.statusDistribution.ended / analytics.totalRelationships) * 100, color: '#EF4444' }
  ].filter(item => item.value > 0);

  return (
    <div className="space-y-6">
      {/* Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white dark:bg-gray-800 p-4 rounded-lg border border-gray-200 dark:border-gray-700">
          <div className="flex items-center">
            <div className="p-2 bg-blue-100 dark:bg-blue-900/20 rounded-lg">
              <span className="text-2xl">👥</span>
            </div>
            <div className="ml-3">
              <p className="text-sm text-gray-600 dark:text-gray-400">Total</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">
                {analytics.totalRelationships}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 p-4 rounded-lg border border-gray-200 dark:border-gray-700">
          <div className="flex items-center">
            <div className="p-2 bg-green-100 dark:bg-green-900/20 rounded-lg">
              <span className="text-2xl">💪</span>
            </div>
            <div className="ml-3">
              <p className="text-sm text-gray-600 dark:text-gray-400">Avg Strength</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">
                {analytics.networkInsights.averageStrength.toFixed(1)}/10
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 p-4 rounded-lg border border-gray-200 dark:border-gray-700">
          <div className="flex items-center">
            <div className="p-2 bg-yellow-100 dark:bg-yellow-900/20 rounded-lg">
              <span className="text-2xl">⭐</span>
            </div>
            <div className="ml-3">
              <p className="text-sm text-gray-600 dark:text-gray-400">Top Category</p>
              <p className="text-lg font-bold text-gray-900 dark:text-white capitalize">
                {analytics.networkInsights.mostConnectedCategory}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 p-4 rounded-lg border border-gray-200 dark:border-gray-700">
          <div className="flex items-center">
            <div className="p-2 bg-purple-100 dark:bg-purple-900/20 rounded-lg">
              <span className="text-2xl">✅</span>
            </div>
            <div className="ml-3">
              <p className="text-sm text-gray-600 dark:text-gray-400">Active</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">
                {analytics.statusDistribution.active}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {renderPieChart(categoryData, 'Relationship Categories')}
        {renderBarChart(strengthData, 'Relationship Strength')}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {renderBarChart(statusData, 'Relationship Status')}
        
        {/* Network Insights */}
        <div className="bg-white dark:bg-gray-800 p-4 rounded-lg border border-gray-200 dark:border-gray-700">
          <h4 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Network Insights</h4>
          <div className="space-y-3">
            {analytics.networkInsights.oldestRelationship && (
              <div className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded">
                <span className="text-sm text-gray-600 dark:text-gray-400">Oldest Connection</span>
                <span className="text-sm font-medium text-gray-900 dark:text-white">
                  {new Date(analytics.networkInsights.oldestRelationship.created_at).getFullYear()}
                </span>
              </div>
            )}
            
            {analytics.networkInsights.newestRelationship && (
              <div className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded">
                <span className="text-sm text-gray-600 dark:text-gray-400">Newest Connection</span>
                <span className="text-sm font-medium text-gray-900 dark:text-white">
                  {new Date(analytics.networkInsights.newestRelationship.created_at).toLocaleDateString()}
                </span>
              </div>
            )}

            <div className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded">
              <span className="text-sm text-gray-600 dark:text-gray-400">Strong Relationships</span>
              <span className="text-sm font-medium text-gray-900 dark:text-white">
                {analytics.strengthDistribution.strong} ({((analytics.strengthDistribution.strong / analytics.totalRelationships) * 100).toFixed(1)}%)
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RelationshipAnalyticsDashboard;