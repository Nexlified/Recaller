import { useState, useEffect, useCallback } from 'react';
import activityService from '../services/activityService';
import {
  SharedActivity,
  SharedActivityCreate,
  SharedActivityUpdate,
} from '../types/Activity';

interface UseActivitiesParams {
  contactId?: number;
  autoLoad?: boolean;
}

interface UseActivitiesReturn {
  activities: SharedActivity[];
  loading: boolean;
  error: string | null;
  createActivity: (activity: SharedActivityCreate) => Promise<SharedActivity>;
  updateActivity: (id: number, activity: SharedActivityUpdate) => Promise<SharedActivity>;
  deleteActivity: (id: number) => Promise<void>;
  refreshActivities: () => Promise<void>;
  getActivity: (id: number) => Promise<SharedActivity>;
}

/**
 * Hook for managing activities state
 */
export const useActivities = (params: UseActivitiesParams = {}): UseActivitiesReturn => {
  const { contactId, autoLoad = true } = params;
  
  const [activities, setActivities] = useState<SharedActivity[]>([]);
  const [loading, setLoading] = useState(autoLoad);
  const [error, setError] = useState<string | null>(null);

  const loadActivities = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const data = contactId 
        ? await activityService.getActivitiesWithContact(contactId)
        : await activityService.getActivities();
      
      setActivities(data);
    } catch (err) {
      console.error('Error loading activities:', err);
      setError(err instanceof Error ? err.message : 'Failed to load activities');
    } finally {
      setLoading(false);
    }
  }, [contactId]);

  const createActivity = useCallback(async (activity: SharedActivityCreate): Promise<SharedActivity> => {
    try {
      setError(null);
      const newActivity = await activityService.createActivity(activity);
      setActivities(prev => [newActivity, ...prev]);
      return newActivity;
    } catch (err) {
      console.error('Error creating activity:', err);
      const errorMessage = err instanceof Error ? err.message : 'Failed to create activity';
      setError(errorMessage);
      throw new Error(errorMessage);
    }
  }, []);

  const updateActivity = useCallback(async (id: number, activity: SharedActivityUpdate): Promise<SharedActivity> => {
    try {
      setError(null);
      const updatedActivity = await activityService.updateActivity(id, activity);
      setActivities(prev => prev.map(a => a.id === id ? updatedActivity : a));
      return updatedActivity;
    } catch (err) {
      console.error('Error updating activity:', err);
      const errorMessage = err instanceof Error ? err.message : 'Failed to update activity';
      setError(errorMessage);
      throw new Error(errorMessage);
    }
  }, []);

  const deleteActivity = useCallback(async (id: number): Promise<void> => {
    try {
      setError(null);
      await activityService.deleteActivity(id);
      setActivities(prev => prev.filter(a => a.id !== id));
    } catch (err) {
      console.error('Error deleting activity:', err);
      const errorMessage = err instanceof Error ? err.message : 'Failed to delete activity';
      setError(errorMessage);
      throw new Error(errorMessage);
    }
  }, []);

  const getActivity = useCallback(async (id: number): Promise<SharedActivity> => {
    try {
      setError(null);
      const activity = await activityService.getActivity(id);
      
      // Update the activity in the local state if it exists
      setActivities(prev => {
        const existingIndex = prev.findIndex(a => a.id === id);
        if (existingIndex >= 0) {
          const updated = [...prev];
          updated[existingIndex] = activity;
          return updated;
        }
        return prev;
      });
      
      return activity;
    } catch (err) {
      console.error('Error getting activity:', err);
      const errorMessage = err instanceof Error ? err.message : 'Failed to get activity';
      setError(errorMessage);
      throw new Error(errorMessage);
    }
  }, []);

  const refreshActivities = useCallback(async (): Promise<void> => {
    await loadActivities();
  }, [loadActivities]);

  useEffect(() => {
    if (autoLoad) {
      loadActivities();
    }
  }, [loadActivities, autoLoad]);

  return {
    activities,
    loading,
    error,
    createActivity,
    updateActivity,
    deleteActivity,
    refreshActivities,
    getActivity,
  };
};

/**
 * Hook for upcoming activities
 */
export const useUpcomingActivities = (daysAhead: number = 30) => {
  const [activities, setActivities] = useState<SharedActivity[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadUpcomingActivities = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await activityService.getUpcomingActivities(daysAhead);
      setActivities(data);
    } catch (err) {
      console.error('Error loading upcoming activities:', err);
      setError(err instanceof Error ? err.message : 'Failed to load upcoming activities');
    } finally {
      setLoading(false);
    }
  }, [daysAhead]);

  useEffect(() => {
    loadUpcomingActivities();
  }, [loadUpcomingActivities]);

  return {
    activities,
    loading,
    error,
    refresh: loadUpcomingActivities,
  };
};

/**
 * Hook for recent activities
 */
export const useRecentActivities = (limit: number = 10) => {
  const [activities, setActivities] = useState<SharedActivity[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadRecentActivities = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await activityService.getRecentActivities(limit);
      setActivities(data);
    } catch (err) {
      console.error('Error loading recent activities:', err);
      setError(err instanceof Error ? err.message : 'Failed to load recent activities');
    } finally {
      setLoading(false);
    }
  }, [limit]);

  useEffect(() => {
    loadRecentActivities();
  }, [loadRecentActivities]);

  return {
    activities,
    loading,
    error,
    refresh: loadRecentActivities,
  };
};