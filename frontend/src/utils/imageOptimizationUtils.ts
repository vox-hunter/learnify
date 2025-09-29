/**
 * Image Optimization Utility Functions and Hooks
 * Separated from components for Fast Refresh compatibility
 */

import React from 'react';

/**
 * Lazy loading hook for images with Intersection Observer
 */
export function useImageLazyLoad(options: IntersectionObserverInit = {}) {
  const [isIntersecting, setIsIntersecting] = React.useState(false);
  const [isLoaded, setIsLoaded] = React.useState(false);
  const imgRef = React.useRef<HTMLImageElement>(null);

  React.useEffect(() => {
    const img = imgRef.current;
    if (!img) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsIntersecting(true);
          observer.disconnect();
        }
      },
      {
        rootMargin: '50px',
        threshold: 0.1,
        ...options
      }
    );

    observer.observe(img);

    return () => observer.disconnect();
  }, [options]);

  const handleLoad = React.useCallback(() => {
    setIsLoaded(true);
  }, []);

  return {
    ref: imgRef,
    shouldLoad: isIntersecting,
    isLoaded,
    handleLoad
  };
}

/**
 * Hook for progressive image loading with blur effect
 */
export function useProgressiveImage(src: string, placeholder?: string) {
  const [currentSrc, setCurrentSrc] = React.useState(placeholder || '');
  const [isLoading, setIsLoading] = React.useState(true);
  const [isError, setIsError] = React.useState(false);

  React.useEffect(() => {
    const img = new Image();
    
    img.onload = () => {
      setCurrentSrc(src);
      setIsLoading(false);
    };
    
    img.onerror = () => {
      setIsError(true);
      setIsLoading(false);
    };
    
    img.src = src;
  }, [src]);

  return {
    src: currentSrc,
    isLoading,
    isError
  };
}

/**
 * Hook for image format support detection
 */
export function useImageFormatSupport() {
  const [support, setSupport] = React.useState<{
    webp: boolean;
    avif: boolean;
  } | null>(null);

  React.useEffect(() => {
    const checkWebP = (): Promise<boolean> => {
      return new Promise(resolve => {
        const webP = new Image();
        webP.onload = webP.onerror = () => {
          resolve(webP.height === 2);
        };
        webP.src = 'data:image/webp;base64,UklGRjoAAABXRUJQVlA4IC4AAACyAgCdASoCAAIALmk0mk0iIiIiIgBoSygABc6WWgAA/veff/0PP8bA//LwYAAA';
      });
    };

    const checkAVIF = (): Promise<boolean> => {
      return new Promise(resolve => {
        const avif = new Image();
        avif.onload = avif.onerror = () => {
          resolve(avif.height === 2);
        };
        avif.src = 'data:image/avif;base64,AAAAIGZ0eXBhdmlmAAAAAGF2aWZtaWYxbWlhZk1BMUIAAADybWV0YQAAAAAAAAAoaGRscgAAAAAAAAAAcGljdAAAAAAAAAAAAAAAAGxpYmF2aWYAAAAADnBpdG0AAAAAAAEAAAAeaWxvYwAAAABEAAABAAEAAAABAAABGgAAAB0AAAAoaWluZgAAAAAAAQAAABppbmZlAgAAAAABAABhdjAxQ29sb3IAAAAAamlwcnAAAABLaXBjbwAAABRpc3BlAAAAAAAAAAIAAAACAAAAEHBpeGkAAAAAAwgICAAAAAxhdjFDgS0AAAAAABNjb2xybmNseAACAAIAAYAAAAAXaXBtYQAAAAAAAAABAAEEAQKDBAAAACVtZGF0EgAKCBgABogQEAwgMg8f8D///8WfhwB8+ErK42A=';
      });
    };

    Promise.all([checkWebP(), checkAVIF()]).then(([webp, avif]) => {
      setSupport({ webp, avif });
    });
  }, []);

  return support;
}

/**
 * Hook for responsive image sizing
 */
export function useResponsiveImage(
  breakpoints: Record<string, number> = {
    sm: 640,
    md: 768,
    lg: 1024,
    xl: 1280
  }
) {
  const [currentBreakpoint, setCurrentBreakpoint] = React.useState<string>('sm');

  React.useEffect(() => {
    const updateBreakpoint = () => {
      const width = window.innerWidth;
      let newBreakpoint = 'sm';

      for (const [bp, minWidth] of Object.entries(breakpoints).reverse()) {
        if (width >= minWidth) {
          newBreakpoint = bp;
          break;
        }
      }

      setCurrentBreakpoint(newBreakpoint);
    };

    updateBreakpoint();
    window.addEventListener('resize', updateBreakpoint);

    return () => window.removeEventListener('resize', updateBreakpoint);
  }, [breakpoints]);

  return currentBreakpoint;
}

/**
 * Asset loading utilities
 */
export const assetUtils = {
  /**
   * Preload multiple images
   */
  preloadImages: (urls: string[]): Promise<HTMLImageElement[]> => {
    return Promise.all(
      urls.map(url => {
        return new Promise<HTMLImageElement>((resolve, reject) => {
          const img = new Image();
          img.onload = () => resolve(img);
          img.onerror = reject;
          img.src = url;
        });
      })
    );
  },

  /**
   * Get image natural dimensions
   */
  getImageDimensions: (url: string): Promise<{ width: number; height: number }> => {
    return new Promise((resolve, reject) => {
      const img = new Image();
      img.onload = () => {
        resolve({
          width: img.naturalWidth,
          height: img.naturalHeight
        });
      };
      img.onerror = reject;
      img.src = url;
    });
  },

  /**
   * Create optimized image URL with parameters
   */
  createOptimizedUrl: (
    baseUrl: string,
    params: {
      width?: number;
      height?: number;
      quality?: number;
      format?: string;
    }
  ): string => {
    const urlParams = new URLSearchParams();
    
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined) {
        urlParams.append(key.charAt(0), value.toString());
      }
    });

    return `${baseUrl}${urlParams.toString() ? `?${urlParams.toString()}` : ''}`;
  }
};

export default {
  useImageLazyLoad,
  useProgressiveImage,
  useImageFormatSupport,
  useResponsiveImage,
  assetUtils
};