import { useState, useEffect, useMemo, useCallback, useRef } from 'react';
import { Task } from '../types/Task';

interface VirtualizedTasksConfig {
  itemHeight: number;
  overscan: number; // Number of items to render outside visible area
  containerHeight?: number;
}

interface VirtualizedTasksReturn {
  visibleTasks: Task[];
  totalHeight: number;
  offsetY: number;
  setContainerHeight: (height: number) => void;
  setScrollTop: (scrollTop: number) => void;
  containerRef: React.RefObject<HTMLDivElement>;
  scrollToTask: (taskId: number) => void;
  scrollToIndex: (index: number) => void;
}

/**
 * Hook for virtualizing large task lists for performance
 */
export const useVirtualizedTasks = (
  tasks: Task[],
  config: VirtualizedTasksConfig = { itemHeight: 60, overscan: 5 }
): VirtualizedTasksReturn => {
  const { itemHeight, overscan, containerHeight: initialHeight } = config;
  
  const [containerHeight, setContainerHeight] = useState(initialHeight || 600);
  const [scrollTop, setScrollTop] = useState(0);
  const containerRef = useRef<HTMLDivElement>(null);
  
  // Auto-detect container height
  useEffect(() => {
    if (containerRef.current && !initialHeight) {
      const resizeObserver = new ResizeObserver(entries => {
        for (const entry of entries) {
          setContainerHeight(entry.contentRect.height);
        }
      });
      
      resizeObserver.observe(containerRef.current);
      setContainerHeight(containerRef.current.clientHeight);
      
      return () => resizeObserver.disconnect();
    }
  }, [initialHeight]);
  
  // Calculate visible range
  const visibleRange = useMemo(() => {
    const startIndex = Math.max(0, Math.floor(scrollTop / itemHeight) - overscan);
    const endIndex = Math.min(
      tasks.length,
      Math.ceil((scrollTop + containerHeight) / itemHeight) + overscan
    );
    
    return { startIndex, endIndex };
  }, [scrollTop, containerHeight, itemHeight, overscan, tasks.length]);
  
  // Get visible tasks
  const visibleTasks = useMemo(
    () => tasks.slice(visibleRange.startIndex, visibleRange.endIndex),
    [tasks, visibleRange]
  );
  
  // Calculate total height and offset
  const totalHeight = tasks.length * itemHeight;
  const offsetY = visibleRange.startIndex * itemHeight;
  
  // Scroll to specific task
  const scrollToTask = useCallback((taskId: number) => {
    const index = tasks.findIndex(task => task.id === taskId);
    if (index !== -1) {
      const scrollPosition = index * itemHeight;
      setScrollTop(scrollPosition);
      
      if (containerRef.current) {
        containerRef.current.scrollTop = scrollPosition;
      }
    }
  }, [tasks, itemHeight]);
  
  // Scroll to specific index
  const scrollToIndex = useCallback((index: number) => {
    if (index >= 0 && index < tasks.length) {
      const scrollPosition = index * itemHeight;
      setScrollTop(scrollPosition);
      
      if (containerRef.current) {
        containerRef.current.scrollTop = scrollPosition;
      }
    }
  }, [tasks.length, itemHeight]);
  
  return {
    visibleTasks,
    totalHeight,
    offsetY,
    setContainerHeight,
    setScrollTop,
    containerRef,
    scrollToTask,
    scrollToIndex,
  };
};

/**
 * Hook for performance monitoring
 */
export const usePerformanceMonitor = () => {
  const [metrics, setMetrics] = useState({
    renderTime: 0,
    updateCount: 0,
    lastUpdate: Date.now(),
  });
  
  const startTime = useRef<number>(0);
  const frameRef = useRef<number>(0);
  
  const startRender = useCallback(() => {
    startTime.current = performance.now();
  }, []);
  
  const endRender = useCallback(() => {
    const endTime = performance.now();
    const renderTime = endTime - startTime.current;
    
    setMetrics(prev => ({
      renderTime,
      updateCount: prev.updateCount + 1,
      lastUpdate: Date.now(),
    }));
    
    // Log performance warning if render time is too high
    if (renderTime > 16) { // 60fps = 16.67ms per frame
      console.warn(`Slow render detected: ${renderTime.toFixed(2)}ms`);
    }
  }, []);
  
  const measureFrameRate = useCallback(() => {
    let frames = 0;
    let startTime = performance.now();
    
    const countFrames = () => {
      frames++;
      const currentTime = performance.now();
      
      if (currentTime - startTime >= 1000) {
        const fps = Math.round((frames * 1000) / (currentTime - startTime));
        console.log(`FPS: ${fps}`);
        
        frames = 0;
        startTime = currentTime;
      }
      
      frameRef.current = requestAnimationFrame(countFrames);
    };
    
    frameRef.current = requestAnimationFrame(countFrames);
    
    return () => {
      if (frameRef.current) {
        cancelAnimationFrame(frameRef.current);
      }
    };
  }, []);
  
  return {
    metrics,
    startRender,
    endRender,
    measureFrameRate,
  };
};

/**
 * Hook for memoizing expensive computations
 */
export const useTaskMemo = <T>(
  computeValue: () => T,
  dependencies: Task[]
): T => {
  const useTaskMemo = useMemo(() => {
    const start = performance.now();
    const value = computeValue();
    const end = performance.now();
    
    if (end - start > 10) {
      console.warn(`Expensive computation detected: ${(end - start).toFixed(2)}ms`);
    }
    
    return value;
  }, [dependencies, computeValue]);
  
  return useTaskMemo;
};

/**
 * Hook for debouncing expensive operations
 */
export const useTaskDebounce = <T extends (...args: unknown[]) => unknown>(
  callback: T,
  delay: number
): T => {
  const timeoutRef = useRef<NodeJS.Timeout>();
  
  const debouncedCallback = useCallback((...args: Parameters<T>) => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }
    
    timeoutRef.current = setTimeout(() => {
      callback(...args);
    }, delay);
  }, [callback, delay]) as T;
  
  useEffect(() => {
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, []);
  
  return debouncedCallback;
};

/**
 * Hook for throttling rapid operations
 */
export const useTaskThrottle = <T extends (...args: unknown[]) => unknown>(
  callback: T,
  limit: number
): T => {
  const inThrottle = useRef(false);
  
  const throttledCallback = useCallback((...args: Parameters<T>) => {
    if (!inThrottle.current) {
      callback(...args);
      inThrottle.current = true;
      
      setTimeout(() => {
        inThrottle.current = false;
      }, limit);
    }
  }, [callback, limit]) as T;
  
  return throttledCallback;
};

/**
 * Hook for intersection observer (lazy loading)
 */
export const useIntersectionObserver = (
  options: IntersectionObserverInit = {}
) => {
  const [isIntersecting, setIsIntersecting] = useState(false);
  const [entry, setEntry] = useState<IntersectionObserverEntry | null>(null);
  const elementRef = useRef<HTMLElement>(null);
  
  useEffect(() => {
    const element = elementRef.current;
    if (!element) return;
    
    const observer = new IntersectionObserver(([entry]) => {
      setIsIntersecting(entry.isIntersecting);
      setEntry(entry);
    }, options);
    
    observer.observe(element);
    
    return () => observer.disconnect();
  }, [options]);
  
  return { elementRef, isIntersecting, entry };
};

/**
 * Hook for image lazy loading
 */
export const useLazyImage = (src: string, placeholder?: string) => {
  const [imageSrc, setImageSrc] = useState(placeholder || '');
  const [isLoaded, setIsLoaded] = useState(false);
  const [isError, setIsError] = useState(false);
  const { elementRef, isIntersecting } = useIntersectionObserver({
    threshold: 0.1,
    rootMargin: '50px',
  });
  
  useEffect(() => {
    if (isIntersecting && src && !isLoaded) {
      const img = new Image();
      
      img.onload = () => {
        setImageSrc(src);
        setIsLoaded(true);
      };
      
      img.onerror = () => {
        setIsError(true);
      };
      
      img.src = src;
    }
  }, [isIntersecting, src, isLoaded]);
  
  return {
    elementRef,
    imageSrc,
    isLoaded,
    isError,
  };
};

/**
 * Hook for optimizing re-renders
 */
export const useStableCallback = <T extends (...args: unknown[]) => unknown>(
  callback: T
): T => {
  const callbackRef = useRef(callback);
  
  useEffect(() => {
    callbackRef.current = callback;
  });
  
  return useCallback((...args: Parameters<T>) => {
    return callbackRef.current(...args);
  }, []) as T;
};

/**
 * Hook for batching state updates
 */
export const useBatchedUpdates = <T>() => {
  const [pendingUpdates, setPendingUpdates] = useState<Array<(prev: T) => T>>([]);
  const [state, setState] = useState<T | undefined>();
  
  const batchUpdate = useCallback((updater: (prev: T) => T) => {
    setPendingUpdates(prev => [...prev, updater]);
  }, []);
  
  const flushUpdates = useCallback(() => {
    if (pendingUpdates.length > 0 && state !== undefined) {
      const finalState = pendingUpdates.reduce((acc, updater) => updater(acc), state);
      setState(finalState);
      setPendingUpdates([]);
    }
  }, [pendingUpdates, state]);
  
  // Auto-flush updates on next tick
  useEffect(() => {
    if (pendingUpdates.length > 0) {
      const timeoutId = setTimeout(flushUpdates, 0);
      return () => clearTimeout(timeoutId);
    }
  }, [pendingUpdates, flushUpdates]);
  
  return {
    state,
    setState,
    batchUpdate,
    flushUpdates,
    hasPendingUpdates: pendingUpdates.length > 0,
  };
};