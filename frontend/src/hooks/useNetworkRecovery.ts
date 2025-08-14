import { useState, useEffect, useCallback } from 'react';
import { useLocalStorage } from './useLocalStorage';

interface QueuedOperation {
  id: string;
  operation: () => Promise<void>;
  description: string;
  timestamp: number;
  retryCount: number;
  maxRetries: number;
}

interface NetworkState {
  isOnline: boolean;
  isReconnecting: boolean;
  lastConnected: number | null;
  connectionType: 'online' | 'offline' | 'slow';
}

interface NavigatorWithConnection extends Navigator {
  connection?: {
    effectiveType?: string;
    addEventListener?: (event: string, handler: () => void) => void;
    removeEventListener?: (event: string, handler: () => void) => void;
  };
  mozConnection?: {
    effectiveType?: string;
    addEventListener?: (event: string, handler: () => void) => void;
    removeEventListener?: (event: string, handler: () => void) => void;
  };
  webkitConnection?: {
    effectiveType?: string;
    addEventListener?: (event: string, handler: () => void) => void;
    removeEventListener?: (event: string, handler: () => void) => void;
  };
}

/**
 * Hook for network recovery and offline support
 */
export const useNetworkRecovery = () => {
  const [networkState, setNetworkState] = useState<NetworkState>({
    isOnline: typeof navigator !== 'undefined' ? navigator.onLine : true,
    isReconnecting: false,
    lastConnected: Date.now(),
    connectionType: 'online',
  });
  
  const [retryQueue, setRetryQueue] = useLocalStorage<QueuedOperation[]>('network-retry-queue', []);
  const [offlineActions, setOfflineActions] = useLocalStorage<unknown[]>('offline-actions', []);
  
  // Monitor network status
  useEffect(() => {
    if (typeof window === 'undefined') return;
    
    const handleOnline = () => {
      setNetworkState(prev => ({
        ...prev,
        isOnline: true,
        lastConnected: Date.now(),
        connectionType: 'online',
      }));
      
      // Process retry queue when back online
      processRetryQueue();
    };
    
    const handleOffline = () => {
      setNetworkState(prev => ({
        ...prev,
        isOnline: false,
        connectionType: 'offline',
      }));
    };
    
    // Connection change detection
    const handleConnectionChange = () => {
      const nav = navigator as NavigatorWithConnection;
      const connection = nav.connection || nav.mozConnection || nav.webkitConnection;
      
      if (connection) {
        const effectiveType = connection.effectiveType;
        let connectionType: NetworkState['connectionType'] = 'online';
        
        if (!navigator.onLine) {
          connectionType = 'offline';
        } else if (effectiveType === 'slow-2g' || effectiveType === '2g') {
          connectionType = 'slow';
        }
        
        setNetworkState(prev => ({
          ...prev,
          connectionType,
          isOnline: navigator.onLine,
        }));
      }
    };
    
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);
    
    // Listen for connection changes if supported
    const nav = navigator as NavigatorWithConnection;
    const connection = nav.connection || nav.mozConnection || nav.webkitConnection;
    if (connection && connection.addEventListener) {
      connection.addEventListener('change', handleConnectionChange);
    }
    
    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
      
      if (connection && connection.removeEventListener) {
        connection.removeEventListener('change', handleConnectionChange);
      }
    };
  }, []);
  
  // Process retry queue
  const processRetryQueue = useCallback(async () => {
    if (!networkState.isOnline || retryQueue.length === 0) return;
    
    setNetworkState(prev => ({ ...prev, isReconnecting: true }));
    
    const updatedQueue = [...retryQueue];
    const successfulOperations: string[] = [];
    
    for (const operation of updatedQueue) {
      try {
        await operation.operation();
        successfulOperations.push(operation.id);
      } catch (error) {
        console.error(`Failed to retry operation ${operation.id}:`, error);
        
        // Increment retry count
        const operationIndex = updatedQueue.findIndex(op => op.id === operation.id);
        if (operationIndex !== -1) {
          updatedQueue[operationIndex].retryCount += 1;
          
          // Remove operation if max retries exceeded
          if (updatedQueue[operationIndex].retryCount >= operation.maxRetries) {
            console.warn(`Max retries exceeded for operation ${operation.id}, removing from queue`);
            successfulOperations.push(operation.id);
          }
        }
      }
    }
    
    // Remove successful operations from queue
    const newQueue = updatedQueue.filter(op => !successfulOperations.includes(op.id));
    setRetryQueue(newQueue);
    
    setNetworkState(prev => ({ ...prev, isReconnecting: false }));
  }, [networkState.isOnline, retryQueue, setRetryQueue]);
  
  // Add operation to retry queue
  const addToRetryQueue = useCallback((
    operation: () => Promise<void>,
    description: string,
    maxRetries: number = 3
  ) => {
    const queuedOperation: QueuedOperation = {
      id: `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      operation,
      description,
      timestamp: Date.now(),
      retryCount: 0,
      maxRetries,
    };
    
    setRetryQueue(prev => [...prev, queuedOperation]);
  }, [setRetryQueue]);
  
  // Add offline action for later sync
  const addOfflineAction = useCallback((action: unknown) => {
    setOfflineActions(prev => [...prev, { action, timestamp: Date.now() }]);
  }, [setOfflineActions]);
  
  // Clear offline actions (after successful sync)
  const clearOfflineActions = useCallback(() => {
    setOfflineActions([]);
  }, [setOfflineActions]);
  
  // Clear retry queue
  const clearRetryQueue = useCallback(() => {
    setRetryQueue([]);
  }, [setRetryQueue]);
  
  // Manual retry
  const retryFailedOperations = useCallback(async () => {
    if (networkState.isOnline) {
      await processRetryQueue();
    }
  }, [networkState.isOnline, processRetryQueue]);
  
  const getConnectionQuality = useCallback((): 'excellent' | 'good' | 'poor' | 'offline' => {
    if (!networkState.isOnline) return 'offline';
    
    if (typeof navigator !== 'undefined') {
      const nav = navigator as NavigatorWithConnection;
      const connection = nav.connection || nav.mozConnection || nav.webkitConnection;
      
      if (connection) {
        const effectiveType = connection.effectiveType;
        
        switch (effectiveType) {
          case '4g':
            return 'excellent';
          case '3g':
            return 'good';
          case '2g':
          case 'slow-2g':
            return 'poor';
          default:
            return 'good';
        }
      }
    }
    
    return 'good';
  }, [networkState.isOnline]);
  
  // Auto-retry with exponential backoff
  useEffect(() => {
    if (!networkState.isOnline || retryQueue.length === 0) return;
    
    const retryDelay = Math.min(1000 * Math.pow(2, retryQueue[0]?.retryCount || 0), 30000); // Max 30 seconds
    
    const timeoutId = setTimeout(() => {
      processRetryQueue();
    }, retryDelay);
    
    return () => clearTimeout(timeoutId);
  }, [networkState.isOnline, retryQueue.length, processRetryQueue]);
  
  return {
    networkState,
    retryQueue,
    offlineActions,
    addToRetryQueue,
    addOfflineAction,
    clearOfflineActions,
    clearRetryQueue,
    retryFailedOperations,
    getConnectionQuality,
    hasQueuedOperations: retryQueue.length > 0,
    hasOfflineActions: offlineActions.length > 0,
  };
};

/**
 * Hook for network-aware API calls
 */
export const useNetworkAwareAPI = () => {
  const { networkState, addToRetryQueue } = useNetworkRecovery();
  
  const makeNetworkCall = useCallback(async <T>(
    apiCall: () => Promise<T>,
    fallbackData?: T,
    options: {
      retryOnFailure?: boolean;
      maxRetries?: number;
      description?: string;
      fallbackOnOffline?: boolean;
    } = {}
  ): Promise<T> => {
    const {
      retryOnFailure = true,
      maxRetries = 3,
      description = 'API call',
      fallbackOnOffline = false,
    } = options;
    
    // If offline and fallback is provided, return fallback
    if (!networkState.isOnline && fallbackOnOffline && fallbackData !== undefined) {
      return fallbackData;
    }
    
    try {
      const result = await apiCall();
      return result;
    } catch (error) {
      // If online but failed, and retry is enabled, add to retry queue
      if (networkState.isOnline && retryOnFailure) {
        addToRetryQueue(
          async () => {
            await apiCall();
          },
          description,
          maxRetries
        );
      }
      
      // If offline or failed and fallback is available, return fallback
      if (fallbackData !== undefined) {
        return fallbackData;
      }
      
      throw error;
    }
  }, [networkState.isOnline, addToRetryQueue]);
  
  return {
    makeNetworkCall,
    isOnline: networkState.isOnline,
    connectionQuality: networkState.connectionType,
  };
};

/**
 * Hook for detecting slow connections
 */
export const useConnectionSpeed = () => {
  const [connectionSpeed, setConnectionSpeed] = useState<{
    downloadSpeed: number; // Mbps
    latency: number; // ms
    quality: 'fast' | 'medium' | 'slow';
  }>({
    downloadSpeed: 0,
    latency: 0,
    quality: 'medium',
  });
  
  const testConnectionSpeed = useCallback(async () => {
    if (typeof window === 'undefined' || !navigator.onLine) return;
    
    const startTime = performance.now();
    
    try {
      // Test with a small image (1x1 pixel)
      const testImage = new Image();
      const imageLoadPromise = new Promise<void>((resolve, reject) => {
        testImage.onload = () => resolve();
        testImage.onerror = () => reject(new Error('Failed to load test image'));
      });
      
      testImage.src = `data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7?t=${Date.now()}`;
      
      await imageLoadPromise;
      
      const endTime = performance.now();
      const latency = endTime - startTime;
      
      // Estimate quality based on latency
      let quality: 'fast' | 'medium' | 'slow' = 'medium';
      if (latency < 100) quality = 'fast';
      else if (latency > 500) quality = 'slow';
      
      setConnectionSpeed({
        downloadSpeed: 0, // Simplified - would need more complex test for actual speed
        latency,
        quality,
      });
    } catch (error) {
      console.error('Connection speed test failed:', error);
    }
  }, []);
  
  // Test connection speed on mount and network changes
  useEffect(() => {
    testConnectionSpeed();
    
    const handleNetworkChange = () => {
      setTimeout(testConnectionSpeed, 1000); // Delay to allow connection to stabilize
    };
    
    window.addEventListener('online', handleNetworkChange);
    
    return () => {
      window.removeEventListener('online', handleNetworkChange);
    };
  }, [testConnectionSpeed]);
  
  return {
    connectionSpeed,
    testConnectionSpeed,
  };
};