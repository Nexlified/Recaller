import { useState, useEffect, useCallback } from 'react';
import activityService from '../services/activityService';
import { ActivityInsights } from '../types/Activity';

interface UseActivityInsightsParams {
  daysBack?: number;
  autoLoad?: boolean;
}

interface UseActivityInsightsReturn {
  insights: ActivityInsights | null;
  loading: boolean;
  error: string | null;
  refreshInsights: () => Promise<void>;
}

/**
 * Hook for managing activity insights and analytics
 */
export const useActivityInsights = (params: UseActivityInsightsParams = {}): UseActivityInsightsReturn => {
  const { daysBack = 365, autoLoad = true } = params;
  
  const [insights, setInsights] = useState<ActivityInsights | null>(null);
  const [loading, setLoading] = useState(autoLoad);
  const [error, setError] = useState<string | null>(null);

  const loadInsights = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await activityService.getActivityInsights(daysBack);
      setInsights(data);
    } catch (err) {
      console.error('Error loading activity insights:', err);
      setError(err instanceof Error ? err.message : 'Failed to load activity insights');
    } finally {
      setLoading(false);
    }
  }, [daysBack]);

  const refreshInsights = useCallback(async (): Promise<void> => {
    await loadInsights();
  }, [loadInsights]);

  useEffect(() => {
    if (autoLoad) {
      loadInsights();
    }
  }, [loadInsights, autoLoad]);

  return {
    insights,
    loading,
    error,
    refreshInsights,
  };
};