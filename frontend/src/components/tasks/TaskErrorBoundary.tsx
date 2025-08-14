import React, { Component, ErrorInfo, ReactNode } from 'react';

interface TaskErrorBoundaryProps {
  children: ReactNode;
  fallback?: ReactNode;
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
}

interface TaskErrorBoundaryState {
  hasError: boolean;
  error?: Error;
  errorInfo?: ErrorInfo;
}

/**
 * Error boundary specifically for task-related components
 */
export class TaskErrorBoundary extends Component<TaskErrorBoundaryProps, TaskErrorBoundaryState> {
  constructor(props: TaskErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false };
  }
  
  static getDerivedStateFromError(error: Error): TaskErrorBoundaryState {
    return { hasError: true, error };
  }
  
  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    this.setState({ errorInfo });
    
    // Log error details
    console.error('Task component error:', error, errorInfo);
    
    // Call custom error handler if provided
    if (this.props.onError) {
      this.props.onError(error, errorInfo);
    }
    
    // Log to error reporting service (e.g., Sentry, LogRocket)
    if (typeof window !== 'undefined' && (window as unknown as { Sentry?: unknown }).Sentry) {
      ((window as unknown as { Sentry: { captureException: (error: Error, options?: unknown) => void } }).Sentry).captureException(error, {
        contexts: {
          errorBoundary: {
            componentStack: errorInfo.componentStack,
          },
        },
      });
    }
  }
  
  private handleRetry = () => {
    this.setState({ hasError: false, error: undefined, errorInfo: undefined });
  };
  
  private handleReload = () => {
    window.location.reload();
  };
  
  render() {
    if (this.state.hasError) {
      // Custom fallback UI
      if (this.props.fallback) {
        return this.props.fallback;
      }
      
      // Default error UI
      return (
        <div className="task-error-boundary bg-red-50 border border-red-200 rounded-lg p-6 mx-4 my-4">
          <div className="flex items-center mb-4">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.28 7.22a.75.75 0 00-1.06 1.06L8.94 10l-1.72 1.72a.75.75 0 101.06 1.06L10 11.06l1.72 1.72a.75.75 0 101.06-1.06L11.06 10l1.72-1.72a.75.75 0 00-1.06-1.06L10 8.94 8.28 7.22z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-red-800">
                Something went wrong with your tasks
              </h3>
            </div>
          </div>
          
          <div className="text-sm text-red-700 mb-4">
            <p>We encountered an error while loading your tasks. This might be a temporary issue.</p>
            {process.env.NODE_ENV === 'development' && this.state.error && (
              <details className="mt-4 p-4 bg-red-100 rounded border">
                <summary className="cursor-pointer font-semibold">Error Details (Development)</summary>
                <pre className="mt-2 text-xs overflow-auto">
                  {this.state.error.toString()}
                  {this.state.errorInfo?.componentStack}
                </pre>
              </details>
            )}
          </div>
          
          <div className="flex space-x-3">
            <button
              onClick={this.handleRetry}
              className="bg-red-600 text-white px-4 py-2 rounded text-sm font-medium hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2"
            >
              Try Again
            </button>
            <button
              onClick={this.handleReload}
              className="bg-gray-600 text-white px-4 py-2 rounded text-sm font-medium hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2"
            >
              Reload Page
            </button>
          </div>
        </div>
      );
    }
    
    return this.props.children;
  }
}

/**
 * Higher-order component to wrap components with error boundary
 */
export function withTaskErrorBoundary<P extends object>(
  Component: React.ComponentType<P>,
  errorBoundaryProps?: Omit<TaskErrorBoundaryProps, 'children'>
) {
  const WrappedComponent = (props: P) => (
    <TaskErrorBoundary {...errorBoundaryProps}>
      <Component {...props} />
    </TaskErrorBoundary>
  );
  
  WrappedComponent.displayName = `withTaskErrorBoundary(${Component.displayName || Component.name})`;
  
  return WrappedComponent;
}

/**
 * Hook for error handling in functional components
 */
export const useErrorHandler = () => {
  const [error, setError] = React.useState<Error | null>(null);
  
  const resetError = React.useCallback(() => {
    setError(null);
  }, []);
  
  const handleError = React.useCallback((error: Error) => {
    setError(error);
    console.error('Component error:', error);
    
    // Log to error reporting service
    if (typeof window !== 'undefined' && (window as unknown as { Sentry?: unknown }).Sentry) {
      ((window as unknown as { Sentry: { captureException: (error: Error) => void } }).Sentry).captureException(error);
    }
  }, []);
  
  // Throw error to be caught by error boundary
  React.useEffect(() => {
    if (error) {
      throw error;
    }
  }, [error]);
  
  return { handleError, resetError, error };
};

/**
 * Async error handler hook
 */
export const useAsyncError = () => {
  const [, setError] = React.useState();
  
  return React.useCallback(
    (error: Error) => {
      setError(() => {
        throw error;
      });
    },
    []
  );
};

/**
 * Safe async operation hook
 */
export const useSafeAsync = () => {
  const [state, setState] = React.useState<{
    loading: boolean;
    error: Error | null;
    data: unknown;
  }>({
    loading: false,
    error: null,
    data: null,
  });
  
  const executeAsync = React.useCallback(async (
    asyncFunction: () => Promise<unknown>,
    options: {
      onSuccess?: (data: unknown) => void;
      onError?: (error: Error) => void;
      throwOnError?: boolean;
    } = {}
  ): Promise<unknown | null> => {
    const { onSuccess, onError, throwOnError = false } = options;
    
    setState(prev => ({ ...prev, loading: true, error: null }));
    
    try {
      const result = await asyncFunction();
      setState(prev => ({ ...prev, loading: false, data: result }));
      
      if (onSuccess) {
        onSuccess(result);
      }
      
      return result;
    } catch (error) {
      const err = error instanceof Error ? error : new Error('Unknown error');
      setState(prev => ({ ...prev, loading: false, error: err }));
      
      if (onError) {
        onError(err);
      }
      
      if (throwOnError) {
        throw err;
      }
      
      return null;
    }
  }, []);
  
  const resetState = React.useCallback(() => {
    setState({ loading: false, error: null, data: null });
  }, []);
  
  return {
    ...state,
    executeAsync,
    resetState,
  };
};