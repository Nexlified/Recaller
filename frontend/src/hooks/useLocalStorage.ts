import { useState, useEffect } from 'react';

/**
 * Hook for persistent local storage state
 */
export const useLocalStorage = <T>(key: string, defaultValue: T) => {
  const [value, setValue] = useState<T>(() => {
    if (typeof window === 'undefined') {
      return defaultValue;
    }
    
    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : defaultValue;
    } catch (error) {
      console.warn(`Error reading localStorage key "${key}":`, error);
      return defaultValue;
    }
  });
  
  const setStoredValue = (newValue: T | ((val: T) => T)) => {
    try {
      const valueToStore = newValue instanceof Function ? newValue(value) : newValue;
      setValue(valueToStore);
      
      if (typeof window !== 'undefined') {
        window.localStorage.setItem(key, JSON.stringify(valueToStore));
      }
    } catch (error) {
      console.warn(`Error setting localStorage key "${key}":`, error);
    }
  };
  
  // Listen for changes in other tabs
  useEffect(() => {
    if (typeof window === 'undefined') return;
    
    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === key && e.newValue !== null) {
        try {
          setValue(JSON.parse(e.newValue));
        } catch (error) {
          console.warn(`Error parsing localStorage value for key "${key}":`, error);
        }
      }
    };
    
    window.addEventListener('storage', handleStorageChange);
    return () => window.removeEventListener('storage', handleStorageChange);
  }, [key]);
  
  return [value, setStoredValue] as const;
};

/**
 * Hook for session storage (temporary storage)
 */
export const useSessionStorage = <T>(key: string, defaultValue: T) => {
  const [value, setValue] = useState<T>(() => {
    if (typeof window === 'undefined') {
      return defaultValue;
    }
    
    try {
      const item = window.sessionStorage.getItem(key);
      return item ? JSON.parse(item) : defaultValue;
    } catch (error) {
      console.warn(`Error reading sessionStorage key "${key}":`, error);
      return defaultValue;
    }
  });
  
  const setStoredValue = (newValue: T | ((val: T) => T)) => {
    try {
      const valueToStore = newValue instanceof Function ? newValue(value) : newValue;
      setValue(valueToStore);
      
      if (typeof window !== 'undefined') {
        window.sessionStorage.setItem(key, JSON.stringify(valueToStore));
      }
    } catch (error) {
      console.warn(`Error setting sessionStorage key "${key}":`, error);
    }
  };
  
  return [value, setStoredValue] as const;
};

/**
 * Hook for managing localStorage with expiration
 */
export const useLocalStorageWithExpiry = <T>(
  key: string, 
  defaultValue: T, 
  expiryInMs: number
) => {
  const [value, setValue] = useState<T>(() => {
    if (typeof window === 'undefined') {
      return defaultValue;
    }
    
    try {
      const item = window.localStorage.getItem(key);
      if (!item) return defaultValue;
      
      const parsed = JSON.parse(item);
      const now = Date.now();
      
      if (parsed.expiry && now > parsed.expiry) {
        window.localStorage.removeItem(key);
        return defaultValue;
      }
      
      return parsed.value ?? defaultValue;
    } catch (error) {
      console.warn(`Error reading localStorage key "${key}":`, error);
      return defaultValue;
    }
  });
  
  const setStoredValue = (newValue: T | ((val: T) => T)) => {
    try {
      const valueToStore = newValue instanceof Function ? newValue(value) : newValue;
      setValue(valueToStore);
      
      if (typeof window !== 'undefined') {
        const now = Date.now();
        const item = {
          value: valueToStore,
          expiry: now + expiryInMs,
        };
        window.localStorage.setItem(key, JSON.stringify(item));
      }
    } catch (error) {
      console.warn(`Error setting localStorage key "${key}":`, error);
    }
  };
  
  const clearValue = () => {
    setValue(defaultValue);
    if (typeof window !== 'undefined') {
      window.localStorage.removeItem(key);
    }
  };
  
  return [value, setStoredValue, clearValue] as const;
};

/**
 * Hook for debounced localStorage updates
 */
export const useDebouncedLocalStorage = <T>(
  key: string, 
  defaultValue: T, 
  delay: number = 500
) => {
  const [value, setValue] = useState<T>(() => {
    if (typeof window === 'undefined') {
      return defaultValue;
    }
    
    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : defaultValue;
    } catch (error) {
      console.warn(`Error reading localStorage key "${key}":`, error);
      return defaultValue;
    }
  });
  
  const [pendingValue, setPendingValue] = useState<T>(value);
  
  useEffect(() => {
    const timeoutId = setTimeout(() => {
      if (typeof window !== 'undefined') {
        try {
          window.localStorage.setItem(key, JSON.stringify(pendingValue));
          setValue(pendingValue);
        } catch (error) {
          console.warn(`Error setting localStorage key "${key}":`, error);
        }
      }
    }, delay);
    
    return () => clearTimeout(timeoutId);
  }, [key, pendingValue, delay]);
  
  return [value, setPendingValue] as const;
};

/**
 * Utility functions for localStorage operations
 */
export const localStorageUtils = {
  /**
   * Get all localStorage keys with a specific prefix
   */
  getKeysWithPrefix: (prefix: string): string[] => {
    if (typeof window === 'undefined') return [];
    
    const keys: string[] = [];
    for (let i = 0; i < window.localStorage.length; i++) {
      const key = window.localStorage.key(i);
      if (key && key.startsWith(prefix)) {
        keys.push(key);
      }
    }
    return keys;
  },
  
  /**
   * Remove all localStorage items with a specific prefix
   */
  clearKeysWithPrefix: (prefix: string): void => {
    if (typeof window === 'undefined') return;
    
    const keys = localStorageUtils.getKeysWithPrefix(prefix);
    keys.forEach(key => window.localStorage.removeItem(key));
  },
  
  /**
   * Get localStorage usage in bytes
   */
  getStorageSize: (): number => {
    if (typeof window === 'undefined') return 0;
    
    let total = 0;
    for (const key in window.localStorage) {
      if (window.localStorage.hasOwnProperty(key)) {
        total += window.localStorage[key].length + key.length;
      }
    }
    return total;
  },
  
  /**
   * Check if localStorage is available
   */
  isAvailable: (): boolean => {
    if (typeof window === 'undefined') return false;
    
    try {
      const test = '__localStorage_test__';
      window.localStorage.setItem(test, 'test');
      window.localStorage.removeItem(test);
      return true;
    } catch (error) {
      return false;
    }
  },
  
  /**
   * Export all localStorage data
   */
  exportData: (): Record<string, unknown> => {
    if (typeof window === 'undefined') return {};
    
    const data: Record<string, unknown> = {};
    for (let i = 0; i < window.localStorage.length; i++) {
      const key = window.localStorage.key(i);
      if (key) {
        try {
          data[key] = JSON.parse(window.localStorage.getItem(key) || '');
        } catch {
          data[key] = window.localStorage.getItem(key);
        }
      }
    }
    return data;
  },
  
  /**
   * Import localStorage data
   */
  importData: (data: Record<string, unknown>): void => {
    if (typeof window === 'undefined') return;
    
    Object.entries(data).forEach(([key, value]) => {
      try {
        window.localStorage.setItem(key, typeof value === 'string' ? value : JSON.stringify(value));
      } catch {
        console.warn(`Error importing localStorage key "${key}"`);
      }
    });
  },
};