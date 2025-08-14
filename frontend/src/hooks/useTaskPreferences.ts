import { useLocalStorage } from './useLocalStorage';
import { TaskFilters, TaskSortBy, TaskViewMode } from '../types/Task';

interface TaskPreferences {
  viewMode: TaskViewMode;
  sortBy: TaskSortBy;
  defaultFilters: TaskFilters;
  compactView: boolean;
  showCompleted: boolean;
  autoRefresh: boolean;
  refreshInterval: number; // in minutes
  pageSize: number;
  showDueDates: boolean;
  showCategories: boolean;
  showPriority: boolean;
  groupByCategory: boolean;
  enableNotifications: boolean;
  notificationTime: number; // minutes before due date
}

const defaultPreferences: TaskPreferences = {
  viewMode: 'list',
  sortBy: { field: 'created_at', direction: 'desc' },
  defaultFilters: {},
  compactView: false,
  showCompleted: true,
  autoRefresh: true,
  refreshInterval: 5,
  pageSize: 50,
  showDueDates: true,
  showCategories: true,
  showPriority: true,
  groupByCategory: false,
  enableNotifications: true,
  notificationTime: 60, // 1 hour before due date
};

/**
 * Hook for managing task preferences with localStorage persistence
 */
export const useTaskPreferences = () => {
  const [preferences, setPreferences] = useLocalStorage<TaskPreferences>(
    'task-preferences',
    defaultPreferences
  );
  
  const updatePreference = <K extends keyof TaskPreferences>(
    key: K,
    value: TaskPreferences[K]
  ) => {
    setPreferences(prev => ({ ...prev, [key]: value }));
  };
  
  const updateMultiplePreferences = (updates: Partial<TaskPreferences>) => {
    setPreferences(prev => ({ ...prev, ...updates }));
  };
  
  const resetPreferences = () => {
    setPreferences(defaultPreferences);
  };
  
  const resetToDefaults = (keys: (keyof TaskPreferences)[]) => {
    const updates: Partial<TaskPreferences> = {};
    keys.forEach(key => {
      updates[key] = defaultPreferences[key];
    });
    updateMultiplePreferences(updates);
  };
  
  return {
    preferences,
    updatePreference,
    updateMultiplePreferences,
    resetPreferences,
    resetToDefaults,
  };
};

/**
 * Hook for UI-specific preferences
 */
export const useUIPreferences = () => {
  const { preferences, updatePreference } = useTaskPreferences();
  
  const toggleCompactView = () => {
    updatePreference('compactView', !preferences.compactView);
  };
  
  const toggleShowCompleted = () => {
    updatePreference('showCompleted', !preferences.showCompleted);
  };
  
  const toggleAutoRefresh = () => {
    updatePreference('autoRefresh', !preferences.autoRefresh);
  };
  
  const toggleGroupByCategory = () => {
    updatePreference('groupByCategory', !preferences.groupByCategory);
  };
  
  const setViewMode = (mode: TaskViewMode) => {
    updatePreference('viewMode', mode);
  };
  
  const setSortBy = (sortBy: TaskSortBy) => {
    updatePreference('sortBy', sortBy);
  };
  
  const setPageSize = (size: number) => {
    updatePreference('pageSize', Math.max(10, Math.min(100, size)));
  };
  
  const setRefreshInterval = (minutes: number) => {
    updatePreference('refreshInterval', Math.max(1, Math.min(60, minutes)));
  };
  
  return {
    compactView: preferences.compactView,
    showCompleted: preferences.showCompleted,
    autoRefresh: preferences.autoRefresh,
    groupByCategory: preferences.groupByCategory,
    viewMode: preferences.viewMode,
    sortBy: preferences.sortBy,
    pageSize: preferences.pageSize,
    refreshInterval: preferences.refreshInterval,
    toggleCompactView,
    toggleShowCompleted,
    toggleAutoRefresh,
    toggleGroupByCategory,
    setViewMode,
    setSortBy,
    setPageSize,
    setRefreshInterval,
  };
};

/**
 * Hook for notification preferences
 */
export const useNotificationPreferences = () => {
  const { preferences, updatePreference } = useTaskPreferences();
  
  const toggleNotifications = () => {
    updatePreference('enableNotifications', !preferences.enableNotifications);
  };
  
  const setNotificationTime = (minutes: number) => {
    updatePreference('notificationTime', Math.max(5, Math.min(1440, minutes))); // 5 min to 24 hours
  };
  
  return {
    enableNotifications: preferences.enableNotifications,
    notificationTime: preferences.notificationTime,
    toggleNotifications,
    setNotificationTime,
  };
};

/**
 * Hook for display preferences
 */
export const useDisplayPreferences = () => {
  const { preferences, updatePreference, updateMultiplePreferences } = useTaskPreferences();
  
  const toggleShowDueDates = () => {
    updatePreference('showDueDates', !preferences.showDueDates);
  };
  
  const toggleShowCategories = () => {
    updatePreference('showCategories', !preferences.showCategories);
  };
  
  const toggleShowPriority = () => {
    updatePreference('showPriority', !preferences.showPriority);
  };
  
  const setDisplayOptions = (options: {
    showDueDates?: boolean;
    showCategories?: boolean;
    showPriority?: boolean;
  }) => {
    updateMultiplePreferences(options);
  };
  
  return {
    showDueDates: preferences.showDueDates,
    showCategories: preferences.showCategories,
    showPriority: preferences.showPriority,
    toggleShowDueDates,
    toggleShowCategories,
    toggleShowPriority,
    setDisplayOptions,
  };
};

/**
 * Hook for filter preferences
 */
export const useFilterPreferences = () => {
  const { preferences, updatePreference } = useTaskPreferences();
  
  const updateDefaultFilters = (filters: Partial<TaskFilters>) => {
    updatePreference('defaultFilters', { ...preferences.defaultFilters, ...filters });
  };
  
  const clearDefaultFilters = () => {
    updatePreference('defaultFilters', {});
  };
  
  const setDefaultFilter = <K extends keyof TaskFilters>(
    key: K,
    value: TaskFilters[K]
  ) => {
    updatePreference('defaultFilters', {
      ...preferences.defaultFilters,
      [key]: value,
    });
  };
  
  const removeDefaultFilter = (key: keyof TaskFilters) => {
    const newFilters = { ...preferences.defaultFilters };
    delete newFilters[key];
    updatePreference('defaultFilters', newFilters);
  };
  
  return {
    defaultFilters: preferences.defaultFilters,
    updateDefaultFilters,
    clearDefaultFilters,
    setDefaultFilter,
    removeDefaultFilter,
  };
};

/**
 * Export/import preferences
 */
export const usePreferencesManager = () => {
  const { preferences, updateMultiplePreferences, resetPreferences } = useTaskPreferences();
  
  const exportPreferences = (): string => {
    return JSON.stringify(preferences, null, 2);
  };
  
  const importPreferences = (jsonString: string): boolean => {
    try {
      const imported = JSON.parse(jsonString);
      
      // Validate the structure
      if (typeof imported !== 'object' || imported === null) {
        throw new Error('Invalid preferences format');
      }
      
      // Merge with defaults to ensure all required fields exist
      const validatedPreferences = { ...defaultPreferences, ...imported };
      updateMultiplePreferences(validatedPreferences);
      
      return true;
    } catch (error) {
      console.error('Failed to import preferences:', error);
      return false;
    }
  };
  
  const downloadPreferences = () => {
    const dataStr = exportPreferences();
    const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
    
    const exportFileDefaultName = `task-preferences-${new Date().toISOString().split('T')[0]}.json`;
    
    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileDefaultName);
    linkElement.click();
  };
  
  return {
    exportPreferences,
    importPreferences,
    downloadPreferences,
    resetPreferences,
  };
};