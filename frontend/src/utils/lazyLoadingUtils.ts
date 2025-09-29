/**
 * Lazy Loading Utility Functions
 */

import React from 'react';
import type { ComponentType, LazyExoticComponent } from 'react';

/**
 * Lazy loading hook for dynamic imports
 */
export function useLazyImport<T>(
  importFn: () => Promise<{ default: T }>
) {
  const [state, setState] = React.useState<{
    component: T | null;
    loading: boolean;
    error: Error | null;
  }>({
    component: null,
    loading: false,
    error: null
  });

  const load = React.useCallback(async () => {
    setState(prev => ({ ...prev, loading: true, error: null }));
    
    try {
      const module = await importFn();
      setState({
        component: module.default,
        loading: false,
        error: null
      });
    } catch (error) {
      setState({
        component: null,
        loading: false,
        error: error instanceof Error ? error : new Error('Failed to load component')
      });
    }
  }, [importFn]);

  React.useEffect(() => {
    load();
  }, [load]);

  return {
    ...state,
    retry: load
  };
}

/**
 * Preload function for warming up lazy components
 */
export function preloadLazyComponent<T>(
  lazyComponent: LazyExoticComponent<ComponentType<T>>
): Promise<{ default: ComponentType<T> }> {
  // Access the internal React.lazy properties
  const lazyInternal = lazyComponent as {
    _payload?: { _result?: ComponentType<T> };
    _init?: (payload: unknown) => ComponentType<T>;
  };
  
  if (lazyInternal._payload && typeof lazyInternal._payload._result !== 'undefined') {
    // Already loaded
    return Promise.resolve({ default: lazyInternal._payload._result });
  }
  
  // Trigger the lazy loading
  if (lazyInternal._init && lazyInternal._payload) {
    try {
      const result = lazyInternal._init(lazyInternal._payload);
      return Promise.resolve({ default: result });
    } catch (error) {
      return Promise.reject(error);
    }
  }
  
  return Promise.reject(new Error('Unable to preload component'));
}

/**
 * Intersection Observer based lazy loading for components
 */
export function useIntersectionLazyLoad<T extends HTMLElement = HTMLDivElement>(
  callback: () => void,
  options: IntersectionObserverInit = {}
) {
  const [ref, setRef] = React.useState<T | null>(null);
  const [isIntersecting, setIsIntersecting] = React.useState(false);

  React.useEffect(() => {
    if (!ref) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting && !isIntersecting) {
          setIsIntersecting(true);
          callback();
        }
      },
      {
        rootMargin: '50px', // Load 50px before entering viewport
        threshold: 0.1,
        ...options
      }
    );

    observer.observe(ref);

    return () => {
      observer.disconnect();
    };
  }, [ref, callback, isIntersecting, options]);

  return {
    ref: setRef,
    isIntersecting
  };
}

/**
 * Lazy component factory with built-in optimizations
 */
export function createLazyComponent<P extends object>(
  importFn: () => Promise<{ default: ComponentType<P> }>,
  displayName?: string
) {
  const LazyComponent = React.lazy(importFn);
  
  if (displayName) {
    // Set display name on the internal component reference
    Object.defineProperty(LazyComponent, 'displayName', {
      value: `Lazy(${displayName})`,
      writable: false
    });
  }

  // Add preload method
  const enhancedComponent = LazyComponent as LazyExoticComponent<ComponentType<P>> & {
    preload: () => Promise<{ default: ComponentType<P> }>;
  };
  
  enhancedComponent.preload = () => preloadLazyComponent(LazyComponent);

  return enhancedComponent;
}

/**
 * Batch lazy loading for multiple components
 */
export function batchPreloadComponents(
  components: LazyExoticComponent<ComponentType<Record<string, unknown>>>[]
): Promise<void> {
  return Promise.all(
    components.map(component => 
      preloadLazyComponent(component).catch(() => {
        // Ignore individual failures
      })
    )
  ).then(() => {});
}

/**
 * Lazy loading based on user interaction
 */
export function useInteractionLazyLoad(
  callback: () => void,
  interactions: ('mouseenter' | 'focus' | 'click')[] = ['mouseenter', 'focus']
) {
  const [loaded, setLoaded] = React.useState(false);
  const ref = React.useRef<HTMLElement>(null);

  React.useEffect(() => {
    const element = ref.current;
    if (!element || loaded) return;

    const handleInteraction = () => {
      if (!loaded) {
        setLoaded(true);
        callback();
      }
    };

    interactions.forEach(event => {
      element.addEventListener(event, handleInteraction, { once: true });
    });

    return () => {
      interactions.forEach(event => {
        element.removeEventListener(event, handleInteraction);
      });
    };
  }, [callback, loaded, interactions]);

  return { ref, loaded };
}

/**
 * Performance monitoring for lazy loading
 */
export function useLazyLoadingMetrics() {
  const [metrics, setMetrics] = React.useState<{
    loadTime: number | null;
    loadStart: number | null;
    failed: boolean;
  }>({
    loadTime: null,
    loadStart: null,
    failed: false
  });

  const startLoading = React.useCallback(() => {
    setMetrics({
      loadTime: null,
      loadStart: performance.now(),
      failed: false
    });
  }, []);

  const finishLoading = React.useCallback(() => {
    setMetrics(prev => ({
      ...prev,
      loadTime: prev.loadStart ? performance.now() - prev.loadStart : null
    }));
  }, []);

  const failLoading = React.useCallback(() => {
    setMetrics(prev => ({
      ...prev,
      failed: true,
      loadTime: prev.loadStart ? performance.now() - prev.loadStart : null
    }));
  }, []);

  return {
    metrics,
    startLoading,
    finishLoading,
    failLoading
  };
}