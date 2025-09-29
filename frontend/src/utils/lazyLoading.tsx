/**
 * Lazy Loading Components
 * Provides React components for code splitting and dynamic loading
 */

import React, { Suspense } from 'react';
import type { ComponentType, LazyExoticComponent } from 'react';
import ErrorBoundary from '../components/common/ErrorBoundary';
import { preloadLazyComponent } from './lazyLoadingUtils';

/**
 * Loading component for Suspense fallback
 */
export const LazyLoadingSpinner: React.FC<{ message?: string }> = ({ 
  message = 'Loading...' 
}) => {
  return (
    <div className="lazy-loading-container">
      <div className="lazy-loading-spinner" />
      <p className="lazy-loading-message">{message}</p>
    </div>
  );
};

/**
 * Error fallback for lazy loading failures
 */
export const LazyLoadingError: React.FC<{ 
  error?: Error;
  retry?: () => void;
}> = ({ error, retry }) => {
  return (
    <div className="lazy-loading-error">
      <h3>Failed to load content</h3>
      <p>{error?.message || 'Something went wrong while loading this component.'}</p>
      {retry && (
        <button onClick={retry} className="retry-button">
          Try Again
        </button>
      )}
    </div>
  );
};

/**
 * Higher-order component for lazy loading with error handling
 */
export const withLazyLoading = <P extends object>(
  LazyComponent: LazyExoticComponent<ComponentType<P>>,
  options: {
    fallback?: React.ComponentType;
    loadingMessage?: string;
  } = {}
) => {
  const WithLazyLoadingComponent: React.FC<P> = (props: P) => {
    const { fallback: CustomFallback, loadingMessage } = options;

    const fallbackComponent = CustomFallback ? (
      <CustomFallback />
    ) : (
      <LazyLoadingSpinner message={loadingMessage} />
    );

    return (
      <ErrorBoundary>
        <Suspense fallback={fallbackComponent}>
          <LazyComponent {...props} />
        </Suspense>
      </ErrorBoundary>
    );
  };

  return WithLazyLoadingComponent;
};

/**
 * Route-based lazy loading component
 */
export const LazyRoute: React.FC<{
  component: LazyExoticComponent<ComponentType<Record<string, unknown>>>;
  fallback?: React.ComponentType;
  loadingMessage?: string;
  preload?: boolean;
  children?: never;
}> = ({ 
  component: Component, 
  fallback: FallbackComponent, 
  loadingMessage = 'Loading page...',
  preload = false
}) => {
  // Preload on mount if requested
  React.useEffect(() => {
    if (preload) {
      preloadLazyComponent(Component).catch(() => {
        // Ignore preload errors - component will load normally when needed
      });
    }
  }, [Component, preload]);

  const fallbackComponent = FallbackComponent ? (
    <FallbackComponent />
  ) : (
    <LazyLoadingSpinner message={loadingMessage} />
  );

  return (
    <ErrorBoundary>
      <Suspense fallback={fallbackComponent}>
        <Component />
      </Suspense>
    </ErrorBoundary>
  );
};

export default {
  LazyLoadingSpinner,
  LazyLoadingError,
  withLazyLoading,
  LazyRoute
};