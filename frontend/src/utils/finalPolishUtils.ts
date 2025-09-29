/**
 * Final Polish and Optimization Utilities
 * Performance monitoring, code splitting, and production optimizations
 * Separated as .ts file to avoid TypeScript generic syntax issues in .tsx
 */

/**
 * Performance Monitoring
 */
export class PerformanceMonitor {
  private static instance: PerformanceMonitor;
  private metrics: Map<string, number[]> = new Map();
  private observers: PerformanceObserver[] = [];

  static getInstance(): PerformanceMonitor {
    if (!PerformanceMonitor.instance) {
      PerformanceMonitor.instance = new PerformanceMonitor();
    }
    return PerformanceMonitor.instance;
  }

  initialize(): void {
    if (typeof window === 'undefined' || !('PerformanceObserver' in window)) {
      return;
    }

    this.observeWebVitals();
    this.observeResourceTiming();
    this.observeNavigationTiming();
  }

  private observeWebVitals(): void {
    try {
      // Largest Contentful Paint (LCP)
      const lcpObserver = new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          if (entry.entryType === 'largest-contentful-paint') {
            this.recordMetric('LCP', entry.startTime);
          }
        }
      });
      lcpObserver.observe({ entryTypes: ['largest-contentful-paint'] });
      this.observers.push(lcpObserver);

      // First Input Delay (FID)
      const fidObserver = new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          if (entry.entryType === 'first-input') {
            const fidEntry = entry as PerformanceEventTiming;
            this.recordMetric('FID', fidEntry.processingStart - fidEntry.startTime);
          }
        }
      });
      fidObserver.observe({ entryTypes: ['first-input'] });
      this.observers.push(fidObserver);

      // Cumulative Layout Shift (CLS)
      const clsObserver = new PerformanceObserver((list) => {
        let clsScore = 0;
        for (const entry of list.getEntries()) {
          if (entry.entryType === 'layout-shift' && !(entry as LayoutShift).hadRecentInput) {
            clsScore += (entry as LayoutShift).value;
          }
        }
        if (clsScore > 0) {
          this.recordMetric('CLS', clsScore);
        }
      });
      clsObserver.observe({ entryTypes: ['layout-shift'] });
      this.observers.push(clsObserver);
    } catch (error) {
      console.warn('Web Vitals observation failed:', error);
    }
  }

  private observeResourceTiming(): void {
    try {
      const resourceObserver = new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          if (entry.entryType === 'resource') {
            const resourceEntry = entry as PerformanceResourceTiming;
            this.recordMetric('resource_load_time', resourceEntry.duration);
            
            // Monitor slow resources
            if (resourceEntry.duration > 1000) {
              console.warn('Slow resource detected:', {
                name: resourceEntry.name,
                duration: resourceEntry.duration,
                size: resourceEntry.transferSize
              });
            }
          }
        }
      });
      resourceObserver.observe({ entryTypes: ['resource'] });
      this.observers.push(resourceObserver);
    } catch (error) {
      console.warn('Resource timing observation failed:', error);
    }
  }

  private observeNavigationTiming(): void {
    try {
      const navigationObserver = new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          if (entry.entryType === 'navigation') {
            const navEntry = entry as PerformanceNavigationTiming;
            this.recordMetric('DOM_content_loaded', navEntry.domContentLoadedEventEnd - navEntry.domContentLoadedEventStart);
            this.recordMetric('page_load', navEntry.loadEventEnd - navEntry.loadEventStart);
          }
        }
      });
      navigationObserver.observe({ entryTypes: ['navigation'] });
      this.observers.push(navigationObserver);
    } catch (error) {
      console.warn('Navigation timing observation failed:', error);
    }
  }

  recordMetric(name: string, value: number): void {
    if (!this.metrics.has(name)) {
      this.metrics.set(name, []);
    }
    this.metrics.get(name)!.push(value);

    // Keep only last 100 measurements
    const values = this.metrics.get(name)!;
    if (values.length > 100) {
      values.shift();
    }
  }

  getMetrics(): Record<string, { avg: number; min: number; max: number; count: number }> {
    const result: Record<string, { avg: number; min: number; max: number; count: number }> = {};

    for (const [name, values] of this.metrics.entries()) {
      if (values.length > 0) {
        result[name] = {
          avg: values.reduce((sum, val) => sum + val, 0) / values.length,
          min: Math.min(...values),
          max: Math.max(...values),
          count: values.length
        };
      }
    }

    return result;
  }

  reportToAnalytics(): void {
    const metrics = this.getMetrics();
    
    // Report to console in development
    if (process.env.NODE_ENV === 'development') {
      console.table(metrics);
    }

    // Report to analytics service in production
    if (process.env.NODE_ENV === 'production' && (window as any).gtag) {
      for (const [name, data] of Object.entries(metrics)) {
        (window as any).gtag('event', 'performance_metric', {
          metric_name: name,
          metric_value: Math.round(data.avg),
          custom_parameter: data.count
        });
      }
    }
  }

  cleanup(): void {
    this.observers.forEach(observer => observer.disconnect());
    this.observers = [];
    this.metrics.clear();
  }
}

/**
 * Preload Utilities
 */
export const preloadUtils = {
  /**
   * Preload a lazy component
   */
  preloadComponent: <T>(factory: () => Promise<{ default: T }>) => {
    const componentImport = factory();
    // Cache the import promise
    return componentImport;
  },

  /**
   * Preload critical resources
   */
  preloadCriticalResources: () => {
    if (typeof document === 'undefined') return;

    // Preload critical CSS
    const criticalCSS = [
      '/assets/critical.css',
      '/assets/fonts.css'
    ];

    criticalCSS.forEach(href => {
      const link = document.createElement('link');
      link.rel = 'preload';
      link.as = 'style';
      link.href = href;
      document.head.appendChild(link);
    });

    // Preload critical images
    const criticalImages = [
      '/assets/logo.svg',
      '/assets/hero-image.webp'
    ];

    criticalImages.forEach(src => {
      const link = document.createElement('link');
      link.rel = 'preload';
      link.as = 'image';
      link.href = src;
      document.head.appendChild(link);
    });
  },

  /**
   * Preload routes on hover
   */
  preloadRoute: (routePath: string) => {
    if (typeof document === 'undefined') return;

    const link = document.createElement('link');
    link.rel = 'prefetch';
    link.href = routePath;
    document.head.appendChild(link);
  }
};

/**
 * Bundle Analysis Utilities
 */
export const bundleAnalysis = {
  /**
   * Analyze bundle size impact of imports
   */
  measureImportSize: async (importName: string, importFunction: () => Promise<unknown>) => {
    const startTime = performance.now();
    const startSize = (performance as any).memory?.usedJSHeapSize || 0;
    
    try {
      await importFunction();
      const endTime = performance.now();
      const endSize = (performance as any).memory?.usedJSHeapSize || 0;
      
      console.log(`Import "${importName}" metrics:`, {
        loadTime: `${(endTime - startTime).toFixed(2)}ms`,
        memoryIncrease: `${((endSize - startSize) / 1024 / 1024).toFixed(2)}MB`
      });
    } catch (error) {
      console.error(`Failed to load "${importName}":`, error);
    }
  },

  /**
   * Report largest bundles
   */
  reportLargestBundles: () => {
    if (typeof window === 'undefined' || !window.performance) return;

    const resources = performance.getEntriesByType('resource') as PerformanceResourceTiming[];
    const jsResources = resources
      .filter(resource => resource.name.includes('.js'))
      .sort((a, b) => (b.transferSize || 0) - (a.transferSize || 0))
      .slice(0, 10);

    console.table(jsResources.map(resource => ({
      name: resource.name.split('/').pop(),
      size: `${((resource.transferSize || 0) / 1024).toFixed(2)}KB`,
      loadTime: `${resource.duration.toFixed(2)}ms`
    })));
  }
};

/**
 * Production Optimizations
 */
export const productionOptimizations = {
  /**
   * Initialize all production optimizations
   */
  initialize: () => {
    if (process.env.NODE_ENV !== 'production') return;

    // Initialize performance monitoring
    PerformanceMonitor.getInstance().initialize();

    // Preload critical resources
    preloadUtils.preloadCriticalResources();

    // Set up error reporting
    window.addEventListener('error', (event) => {
      console.error('Global error:', event.error);
      // Report to error tracking service
    });

    window.addEventListener('unhandledrejection', (event) => {
      console.error('Unhandled promise rejection:', event.reason);
      // Report to error tracking service
    });

    // Set up performance reporting
    setTimeout(() => {
      PerformanceMonitor.getInstance().reportToAnalytics();
    }, 5000);
  },

  /**
   * Optimize images with lazy loading and WebP support
   */
  optimizeImages: () => {
    if (typeof document === 'undefined') return;

    const images = document.querySelectorAll('img[data-src]');
    
    const imageObserver = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const img = entry.target as HTMLImageElement;
          const src = img.dataset.src;
          
          if (src) {
            // Check WebP support
            const supportsWebP = document.createElement('canvas')
              .toDataURL('image/webp')
              .indexOf('data:image/webp') === 0;
            
            if (supportsWebP && src.includes('.jpg')) {
              img.src = src.replace('.jpg', '.webp');
            } else {
              img.src = src;
            }
            
            img.removeAttribute('data-src');
            imageObserver.unobserve(img);
          }
        }
      });
    });

    images.forEach(img => imageObserver.observe(img));
  },

  /**
   * Enable service worker for caching
   */
  enableServiceWorker: async () => {
    if ('serviceWorker' in navigator && process.env.NODE_ENV === 'production') {
      try {
        await navigator.serviceWorker.register('/sw.js');
        console.log('Service Worker registered successfully');
      } catch (error) {
        console.error('Service Worker registration failed:', error);
      }
    }
  }
};

/**
 * Development Tools
 */
export const devTools = {
  /**
   * Show performance metrics in development
   */
  showPerformanceMetrics: () => {
    if (process.env.NODE_ENV !== 'development') return;

    const monitor = PerformanceMonitor.getInstance();
    monitor.initialize();

    // Show metrics every 10 seconds
    setInterval(() => {
      const metrics = monitor.getMetrics();
      if (Object.keys(metrics).length > 0) {
        console.group('🚀 Performance Metrics');
        console.table(metrics);
        console.groupEnd();
      }
    }, 10000);
  },

  /**
   * Analyze bundle sizes
   */
  analyzeBundles: () => {
    if (process.env.NODE_ENV !== 'development') return;

    setTimeout(() => {
      bundleAnalysis.reportLargestBundles();
    }, 2000);
  },

  /**
   * Enable React DevTools profiling
   */
  enableProfiling: () => {
    if (process.env.NODE_ENV !== 'development' || typeof window === 'undefined') return;

    // Enable React DevTools Profiler
    (window as any).__REACT_DEVTOOLS_GLOBAL_HOOK__?.onCommitFiberRoot = (
      id: number,
      root: any,
      priorityLevel: any,
      actualDuration: number,
      baseDuration: number,
      startTime: number,
      commitTime: number
    ) => {
      if (actualDuration > 16) { // > 16ms indicates potential performance issue
        console.warn('Slow component render detected:', {
          actualDuration: `${actualDuration.toFixed(2)}ms`,
          baseDuration: `${baseDuration.toFixed(2)}ms`,
          startTime,
          commitTime
        });
      }
    };
  }
};

/**
 * Memory Management
 */
export const memoryUtils = {
  /**
   * Monitor memory usage
   */
  monitorMemory: () => {
    if (typeof window === 'undefined' || !(performance as any).memory) return;

    const checkMemory = () => {
      const memory = (performance as any).memory;
      const used = memory.usedJSHeapSize / 1024 / 1024;
      const limit = memory.jsHeapSizeLimit / 1024 / 1024;
      
      console.log(`Memory usage: ${used.toFixed(2)}MB / ${limit.toFixed(2)}MB (${((used / limit) * 100).toFixed(1)}%)`);
      
      // Warn if memory usage is high
      if (used / limit > 0.8) {
        console.warn('High memory usage detected. Consider optimizing component state and cleaning up event listeners.');
      }
    };

    // Check memory every 30 seconds in development
    if (process.env.NODE_ENV === 'development') {
      setInterval(checkMemory, 30000);
    }
  },

  /**
   * Force garbage collection (development only)
   */
  forceGC: () => {
    if (process.env.NODE_ENV === 'development' && (window as any).gc) {
      (window as any).gc();
      console.log('Garbage collection forced');
    }
  }
};

/**
 * Accessibility Enhancements
 */
export const a11yEnhancements = {
  /**
   * Auto-focus management
   */
  manageFocus: () => {
    // Skip to main content link
    const skipLink = document.createElement('a');
    skipLink.href = '#main-content';
    skipLink.textContent = 'Skip to main content';
    skipLink.className = 'skip-link';
    skipLink.style.cssText = `
      position: absolute;
      top: -40px;
      left: 6px;
      background: var(--primary-color);
      color: white;
      padding: 8px;
      z-index: 1000;
      text-decoration: none;
      border-radius: 4px;
      transition: top 0.3s;
    `;
    
    skipLink.addEventListener('focus', () => {
      skipLink.style.top = '6px';
    });
    
    skipLink.addEventListener('blur', () => {
      skipLink.style.top = '-40px';
    });
    
    document.body.insertBefore(skipLink, document.body.firstChild);
  },

  /**
   * Keyboard navigation enhancements
   */
  enhanceKeyboardNav: () => {
    document.addEventListener('keydown', (event) => {
      // Alt + M: Go to main content
      if (event.altKey && event.key === 'm') {
        const mainContent = document.getElementById('main-content');
        if (mainContent) {
          mainContent.focus();
          event.preventDefault();
        }
      }
      
      // Alt + N: Go to navigation
      if (event.altKey && event.key === 'n') {
        const navigation = document.querySelector('nav');
        if (navigation) {
          navigation.focus();
          event.preventDefault();
        }
      }
    });
  }
};

/**
 * SEO Optimizations
 */
export const seoOptimizations = {
  /**
   * Update meta tags dynamically
   */
  updateMetaTags: (data: {
    title?: string;
    description?: string;
    keywords?: string;
    image?: string;
    url?: string;
  }) => {
    if (typeof document === 'undefined') return;

    // Update title
    if (data.title) {
      document.title = data.title;
    }

    // Update meta description
    if (data.description) {
      let metaDesc = document.querySelector('meta[name="description"]') as HTMLMetaElement;
      if (!metaDesc) {
        metaDesc = document.createElement('meta');
        metaDesc.name = 'description';
        document.head.appendChild(metaDesc);
      }
      metaDesc.content = data.description;
    }

    // Update Open Graph tags
    const ogTags = [
      { property: 'og:title', content: data.title },
      { property: 'og:description', content: data.description },
      { property: 'og:image', content: data.image },
      { property: 'og:url', content: data.url }
    ];

    ogTags.forEach(({ property, content }) => {
      if (content) {
        let metaTag = document.querySelector(`meta[property="${property}"]`) as HTMLMetaElement;
        if (!metaTag) {
          metaTag = document.createElement('meta');
          metaTag.setAttribute('property', property);
          document.head.appendChild(metaTag);
        }
        metaTag.content = content;
      }
    });
  },

  /**
   * Generate structured data
   */
  addStructuredData: (data: Record<string, unknown>) => {
    if (typeof document === 'undefined') return;

    const script = document.createElement('script');
    script.type = 'application/ld+json';
    script.textContent = JSON.stringify(data);
    document.head.appendChild(script);
  }
};

/**
 * Main initialization function
 */
export const initializeOptimizations = () => {
  // Production optimizations
  productionOptimizations.initialize();
  
  // Development tools
  devTools.showPerformanceMetrics();
  devTools.analyzeBundles();
  devTools.enableProfiling();
  
  // Memory monitoring
  memoryUtils.monitorMemory();
  
  // Accessibility enhancements
  a11yEnhancements.manageFocus();
  a11yEnhancements.enhanceKeyboardNav();
  
  // Image optimization
  setTimeout(() => {
    productionOptimizations.optimizeImages();
  }, 1000);
};

export default {
  PerformanceMonitor,
  preloadUtils,
  bundleAnalysis,
  productionOptimizations,
  devTools,
  memoryUtils,
  a11yEnhancements,
  seoOptimizations,
  initializeOptimizations
};