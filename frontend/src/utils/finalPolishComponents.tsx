/**
 * Final Polish and Optimization React Components
 * React components for performance monitoring and optimization
 */

import React, { memo } from 'react';
import { useToast } from './errorHandlingUtils';
import { initializeOptimizations } from './finalPolishUtils';

// createLazyComponent utility moved to finalPolishUtils.ts for Fast Refresh compatibility

/**
 * Performance Monitor Component
 */
export const PerformanceMonitorDisplay: React.FC<{ 
  className?: string;
  showDetails?: boolean;
}> = memo(({ className, showDetails = false }) => {
  const [metrics, setMetrics] = React.useState<Record<string, string>>({});
  const [isVisible, setIsVisible] = React.useState(false);

  React.useEffect(() => {
    // Only show in development
    if (import.meta.env.MODE !== 'development') return;

    setIsVisible(true);
    
    const updateMetrics = () => {
      // This would be connected to the PerformanceMonitor from utils
      setMetrics({
        pageLoad: '1.2s',
        lcp: '850ms',
        fid: '12ms',
        cls: '0.05'
      });
    };

    const interval = setInterval(updateMetrics, 5000);
    updateMetrics();

    return () => clearInterval(interval);
  }, []);

  if (!isVisible || import.meta.env.MODE !== 'development') {
    return null;
  }

  return (
    <div className={`performance-monitor ${className || ''}`}>
      <div className="monitor-header">
        <h4>⚡ Performance Metrics</h4>
        <button 
          onClick={() => setIsVisible(false)}
          aria-label="Close performance monitor"
        >
          ×
        </button>
      </div>
      
      <div className="metrics-grid">
        <div className="metric">
          <span className="metric-label">LCP</span>
          <span className="metric-value">{metrics.lcp || '-'}</span>
        </div>
        <div className="metric">
          <span className="metric-label">FID</span>
          <span className="metric-value">{metrics.fid || '-'}</span>
        </div>
        <div className="metric">
          <span className="metric-label">CLS</span>
          <span className="metric-value">{metrics.cls || '-'}</span>
        </div>
        <div className="metric">
          <span className="metric-label">Load</span>
          <span className="metric-value">{metrics.pageLoad || '-'}</span>
        </div>
      </div>

      {showDetails && (
        <div className="metrics-details">
          <small>Core Web Vitals - Updated every 5s</small>
        </div>
      )}
    </div>
  );
});

/**
 * Loading Component with Performance Optimization
 */
export const OptimizedLoader: React.FC<{
  message?: string;
  showProgress?: boolean;
  timeout?: number;
}> = memo(({ message = 'Loading...', showProgress = false, timeout = 10000 }) => {
  const [progress, setProgress] = React.useState(0);
  const [timedOut, setTimedOut] = React.useState(false);

  React.useEffect(() => {
    let progressInterval: number;
    let timeoutTimer: number;

    if (showProgress) {
      progressInterval = setInterval(() => {
        setProgress(prev => Math.min(prev + Math.random() * 15, 95));
      }, 200);
    }

    if (timeout > 0) {
      timeoutTimer = setTimeout(() => {
        setTimedOut(true);
      }, timeout);
    }

    return () => {
      if (progressInterval) clearInterval(progressInterval);
      if (timeoutTimer) clearTimeout(timeoutTimer);
    };
  }, [showProgress, timeout]);

  if (timedOut) {
    return (
      <div className="optimized-loader timeout">
        <div className="loader-content">
          <div className="loader-icon error">⚠️</div>
          <p>Loading is taking longer than expected...</p>
          <button onClick={() => window.location.reload()}>
            Reload Page
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="optimized-loader">
      <div className="loader-content">
        <div className="loader-spinner" role="status" aria-label={message}></div>
        <p>{message}</p>
        {showProgress && (
          <div className="progress-bar">
            <div 
              className="progress-fill" 
              style={{ width: `${progress}%` }}
            ></div>
          </div>
        )}
      </div>
    </div>
  );
});

/**
 * Image Component with Optimization
 */
export const OptimizedImage: React.FC<{
  src: string;
  alt: string;
  className?: string;
  lazy?: boolean;
  webpSrc?: string;
  placeholder?: string;
  onLoad?: () => void;
  onError?: () => void;
}> = memo(({ 
  src, 
  alt, 
  className, 
  lazy = true, 
  webpSrc, 
  placeholder,
  onLoad,
  onError 
}) => {
  const [isLoaded, setIsLoaded] = React.useState(false);
  const [hasError, setHasError] = React.useState(false);
  const [shouldLoad, setShouldLoad] = React.useState(!lazy);
  const imgRef = React.useRef<HTMLImageElement>(null);

  React.useEffect(() => {
    if (!lazy || shouldLoad) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setShouldLoad(true);
          observer.disconnect();
        }
      },
      { threshold: 0.1 }
    );

    if (imgRef.current) {
      observer.observe(imgRef.current);
    }

    return () => observer.disconnect();
  }, [lazy, shouldLoad]);

  const handleLoad = () => {
    setIsLoaded(true);
    onLoad?.();
  };

  const handleError = () => {
    setHasError(true);
    onError?.();
  };

  // Check WebP support
  const supportsWebP = React.useMemo(() => {
    const canvas = document.createElement('canvas');
    return canvas.toDataURL('image/webp').indexOf('data:image/webp') === 0;
  }, []);

  const imageSrc = supportsWebP && webpSrc ? webpSrc : src;

  return (
    <div className={`optimized-image ${className || ''}`} ref={imgRef}>
      {placeholder && !isLoaded && !hasError && (
        <div className="image-placeholder">
          <img src={placeholder} alt="" />
        </div>
      )}
      
      {shouldLoad && !hasError && (
        <img
          src={imageSrc}
          alt={alt}
          onLoad={handleLoad}
          onError={handleError}
          className={isLoaded ? 'loaded' : 'loading'}
          loading={lazy ? 'lazy' : 'eager'}
        />
      )}
      
      {hasError && (
        <div className="image-error">
          <span>Failed to load image</span>
        </div>
      )}
    </div>
  );
});

/**
 * Polish Provider Component
 * High-level component that applies all optimizations
 */
export const PolishProvider: React.FC<{ 
  children: React.ReactNode;
  showPerformanceMonitor?: boolean;
}> = memo(({ children, showPerformanceMonitor = false }) => {
  const { addToast } = useToast();

  React.useEffect(() => {
    try {
      initializeOptimizations();
      
      if (import.meta.env.MODE === 'development') {
        addToast({
          type: 'info',
          title: 'Optimizations Active',
          message: 'Performance monitoring and dev tools are enabled.',
          duration: 3000
        });
      }
    } catch (error) {
      console.error('Failed to initialize optimizations:', error);
      addToast({
        type: 'warning',
        title: 'Optimization Warning',
        message: 'Some optimizations failed to initialize.',
        duration: 5000
      });
    }
  }, [addToast]);

  return (
    <>
      {children}
      {showPerformanceMonitor && <PerformanceMonitorDisplay />}
    </>
  );
});

/**
 * Preloader Component for Route Optimization
 */
export const RoutePreloader: React.FC<{
  routes: string[];
  onHover?: boolean;
}> = memo(({ routes, onHover = true }) => {
  const preloadedRoutes = React.useRef(new Set<string>());

  const preloadRoute = React.useCallback((route: string) => {
    if (preloadedRoutes.current.has(route)) return;
    
    const link = document.createElement('link');
    link.rel = 'prefetch';
    link.href = route;
    document.head.appendChild(link);
    
    preloadedRoutes.current.add(route);
  }, []);

  React.useEffect(() => {
    if (!onHover) {
      // Preload all routes immediately
      routes.forEach(preloadRoute);
    }
  }, [routes, onHover, preloadRoute]);

  const handleMouseEnter = React.useCallback((route: string) => {
    if (onHover) {
      preloadRoute(route);
    }
  }, [onHover, preloadRoute]);

  // This component doesn't render anything visible
  // It just sets up the preloading behavior
  React.useEffect(() => {
    if (!onHover) return;

    const links = document.querySelectorAll('a[href]');
    
    const handleLinkHover = (event: Event) => {
      const link = event.target as HTMLAnchorElement;
      const href = link.getAttribute('href');
      
      if (href && routes.includes(href)) {
        handleMouseEnter(href);
      }
    };

    links.forEach(link => {
      link.addEventListener('mouseenter', handleLinkHover);
    });

    return () => {
      links.forEach(link => {
        link.removeEventListener('mouseenter', handleLinkHover);
      });
    };
  }, [routes, onHover, handleMouseEnter]);

  return null;
});

/**
 * Memory Monitor Component (Development Only)
 */
export const MemoryMonitor: React.FC = memo(() => {
  const [memoryInfo, setMemoryInfo] = React.useState<{
    used: number;
    limit: number;
    percentage: number;
  } | null>(null);

  React.useEffect(() => {
    if (import.meta.env.MODE !== 'development') return;

    const updateMemoryInfo = () => {
      const memory = (performance as { memory?: { usedJSHeapSize: number; jsHeapSizeLimit: number } }).memory;
      if (memory) {
        const used = memory.usedJSHeapSize / 1024 / 1024;
        const limit = memory.jsHeapSizeLimit / 1024 / 1024;
        const percentage = (used / limit) * 100;
        
        setMemoryInfo({ used, limit, percentage });
      }
    };

    updateMemoryInfo();
    const interval = setInterval(updateMemoryInfo, 5000);

    return () => clearInterval(interval);
  }, []);

  if (import.meta.env.MODE !== 'development' || !memoryInfo) {
    return null;
  }

  return (
    <div className="memory-monitor">
      <div className="memory-info">
        <span>Memory: {memoryInfo.used.toFixed(1)}MB / {memoryInfo.limit.toFixed(1)}MB</span>
        <div className="memory-bar">
          <div 
            className="memory-fill"
            style={{ 
              width: `${memoryInfo.percentage}%`,
              backgroundColor: memoryInfo.percentage > 80 ? '#ff4444' : '#4444ff'
            }}
          ></div>
        </div>
      </div>
    </div>
  );
});

export default {
  PerformanceMonitorDisplay,
  OptimizedLoader,
  OptimizedImage,
  PolishProvider,
  RoutePreloader,
  MemoryMonitor
};