/**
 * Image Optimization and Asset Management Utilities
 * Provides comprehensive image optimization and asset loading strategies
 */

import React from 'react';

/**
 * Image format detection and optimization
 */
export class ImageOptimizer {
  public static readonly QUALITY_SETTINGS = {
    high: 90,
    medium: 75,
    low: 60
  } as const;

  /**
   * Check browser support for modern image formats
   */
  static checkFormatSupport(): Promise<{
    webp: boolean;
    avif: boolean;
  }> {
    return Promise.all([
      this.canUseWebP(),
      this.canUseAVIF()
    ]).then(([webp, avif]) => ({ webp, avif }));
  }

  /**
   * Check WebP support
   */
  private static canUseWebP(): Promise<boolean> {
    return new Promise(resolve => {
      const webP = new Image();
      webP.onload = webP.onerror = () => {
        resolve(webP.height === 2);
      };
      webP.src = 'data:image/webp;base64,UklGRjoAAABXRUJQVlA4IC4AAACyAgCdASoCAAIALmk0mk0iIiIiIgBoSygABc6WWgAA/veff/0PP8bA//LwYAAA';
    });
  }

  /**
   * Check AVIF support
   */
  private static canUseAVIF(): Promise<boolean> {
    return new Promise(resolve => {
      const avif = new Image();
      avif.onload = avif.onerror = () => {
        resolve(avif.height === 2);
      };
      avif.src = 'data:image/avif;base64,AAAAIGZ0eXBhdmlmAAAAAGF2aWZtaWYxbWlhZk1BMUIAAADybWV0YQAAAAAAAAAoaGRscgAAAAAAAAAAcGljdAAAAAAAAAAAAAAAAGxpYmF2aWYAAAAADnBpdG0AAAAAAAEAAAAeaWxvYwAAAABEAAABAAEAAAABAAABGgAAAB0AAAAoaWluZgAAAAAAAQAAABppbmZlAgAAAAABAABhdjAxQ29sb3IAAAAAamlwcnAAAABLaXBjbwAAABRpc3BlAAAAAAAAAAIAAAACAAAAEHBpeGkAAAAAAwgICAAAAAxhdjFDgS0AAAAAABNjb2xybmNseAACAAIAAYAAAAAXaXBtYQAAAAAAAAABAAEEAQKDBAAAACVtZGF0EgAKCBgABogQEAwgMg8f8D///8WfhwB8+ErK42A=';
    });
  }

  /**
   * Generate optimized image URLs with fallbacks
   */
  static getOptimizedImageUrl(
    baseUrl: string,
    options: {
      width?: number;
      height?: number;
      quality?: keyof typeof ImageOptimizer.QUALITY_SETTINGS;
      format?: 'auto' | 'webp' | 'avif' | 'jpeg' | 'png';
    } = {}
  ): string {
    const { width, height, quality = 'medium', format = 'auto' } = options;
    const params = new URLSearchParams();

    if (width) params.append('w', width.toString());
    if (height) params.append('h', height.toString());
    if (quality !== 'medium') params.append('q', this.QUALITY_SETTINGS[quality].toString());
    if (format !== 'auto') params.append('f', format);

    return `${baseUrl}${params.toString() ? `?${params.toString()}` : ''}`;
  }

  /**
   * Generate responsive image sources
   */
  static generateResponsiveSrcs(
    baseUrl: string,
    breakpoints: number[] = [320, 640, 768, 1024, 1280, 1536]
  ): string {
    return breakpoints
      .map(width => `${this.getOptimizedImageUrl(baseUrl, { width })} ${width}w`)
      .join(', ');
  }
}

/**
 * Optimized Image Component with lazy loading and format detection
 */
export const OptimizedImage: React.FC<{
  src: string;
  alt: string;
  width?: number;
  height?: number;
  quality?: keyof typeof ImageOptimizer.QUALITY_SETTINGS;
  lazy?: boolean;
  placeholder?: string;
  className?: string;
  onLoad?: () => void;
  onError?: () => void;
}> = ({
  src,
  alt,
  width,
  height,
  quality = 'medium',
  lazy = true,
  placeholder,
  className = '',
  onLoad,
  onError
}) => {
  const [isLoaded, setIsLoaded] = React.useState(false);
  const [hasError, setHasError] = React.useState(false);
  const [formatSupport, setFormatSupport] = React.useState<{
    webp: boolean;
    avif: boolean;
  } | null>(null);
  const imgRef = React.useRef<HTMLImageElement>(null);

  // Check format support on mount
  React.useEffect(() => {
    ImageOptimizer.checkFormatSupport().then(setFormatSupport);
  }, []);

  // Handle image load
  const handleLoad = React.useCallback(() => {
    setIsLoaded(true);
    onLoad?.();
  }, [onLoad]);

  // Handle image error
  const handleError = React.useCallback(() => {
    setHasError(true);
    onError?.();
  }, [onError]);

  // Generate optimized source URLs
  const getOptimizedSrc = React.useCallback((format?: 'webp' | 'avif') => {
    return ImageOptimizer.getOptimizedImageUrl(src, {
      width,
      height,
      quality,
      format
    });
  }, [src, width, height, quality]);

  // Generate responsive sizes
  const responsiveSrcs = React.useMemo(() => {
    if (!width) return undefined;
    return ImageOptimizer.generateResponsiveSrcs(src);
  }, [src, width]);

  if (hasError) {
    return (
      <div 
        className={`image-error ${className}`}
        style={{ width, height }}
      >
        <span>Failed to load image</span>
      </div>
    );
  }

  return (
    <picture className={className}>
      {formatSupport?.avif && (
        <source
          srcSet={responsiveSrcs ? 
            ImageOptimizer.generateResponsiveSrcs(getOptimizedSrc('avif')) :
            getOptimizedSrc('avif')
          }
          type="image/avif"
        />
      )}
      {formatSupport?.webp && (
        <source
          srcSet={responsiveSrcs ? 
            ImageOptimizer.generateResponsiveSrcs(getOptimizedSrc('webp')) :
            getOptimizedSrc('webp')
          }
          type="image/webp"
        />
      )}
      <img
        ref={imgRef}
        src={isLoaded ? getOptimizedSrc() : placeholder || getOptimizedSrc()}
        srcSet={responsiveSrcs}
        alt={alt}
        width={width}
        height={height}
        loading={lazy ? 'lazy' : 'eager'}
        onLoad={handleLoad}
        onError={handleError}
        style={{
          opacity: isLoaded ? 1 : 0.7,
          transition: 'opacity 0.3s ease'
        }}
      />
    </picture>
  );
};

/**
 * Asset preloading utilities
 */
export class AssetPreloader {
  private static preloadedAssets = new Set<string>();

  /**
   * Preload critical images
   */
  static preloadImages(urls: string[]): Promise<void[]> {
    return Promise.all(
      urls.map(url => this.preloadImage(url))
    );
  }

  /**
   * Preload a single image
   */
  static preloadImage(url: string): Promise<void> {
    if (this.preloadedAssets.has(url)) {
      return Promise.resolve();
    }

    return new Promise((resolve, reject) => {
      const img = new Image();
      img.onload = () => {
        this.preloadedAssets.add(url);
        resolve();
      };
      img.onerror = reject;
      img.src = url;
    });
  }

  /**
   * Preload fonts
   */
  static preloadFonts(fontUrls: string[]): void {
    fontUrls.forEach(url => {
      if (!this.preloadedAssets.has(url)) {
        const link = document.createElement('link');
        link.rel = 'preload';
        link.as = 'font';
        link.type = 'font/woff2';
        link.crossOrigin = 'anonymous';
        link.href = url;
        document.head.appendChild(link);
        this.preloadedAssets.add(url);
      }
    });
  }

  /**
   * Preload critical CSS
   */
  static preloadCSS(cssUrls: string[]): void {
    cssUrls.forEach(url => {
      if (!this.preloadedAssets.has(url)) {
        const link = document.createElement('link');
        link.rel = 'preload';
        link.as = 'style';
        link.href = url;
        document.head.appendChild(link);
        this.preloadedAssets.add(url);
      }
    });
  }
}

// Hook moved to imageOptimizationUtils.ts for Fast Refresh compatibility

/**
 * Image dimension utilities
 */
export class ImageDimensions {
  /**
   * Get image dimensions without loading the full image
   */
  static getDimensions(url: string): Promise<{ width: number; height: number }> {
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
  }

  /**
   * Calculate aspect ratio
   */
  static getAspectRatio(width: number, height: number): number {
    return width / height;
  }

  /**
   * Calculate dimensions maintaining aspect ratio
   */
  static calculateDimensions(
    originalWidth: number,
    originalHeight: number,
    constraints: { maxWidth?: number; maxHeight?: number }
  ): { width: number; height: number } {
    const aspectRatio = this.getAspectRatio(originalWidth, originalHeight);
    const { maxWidth, maxHeight } = constraints;

    let width = originalWidth;
    let height = originalHeight;

    if (maxWidth && width > maxWidth) {
      width = maxWidth;
      height = width / aspectRatio;
    }

    if (maxHeight && height > maxHeight) {
      height = maxHeight;
      width = height * aspectRatio;
    }

    return { width: Math.round(width), height: Math.round(height) };
  }
}

/**
 * Asset monitoring and performance tracking
 */
export class AssetPerformanceMonitor {
  private static metrics = new Map<string, {
    loadTime: number;
    size: number;
    type: string;
  }>();

  /**
   * Track asset loading performance
   */
  static trackAsset(url: string, type: string): {
    start: () => void;
    end: (size?: number) => void;
  } {
    let startTime = 0;

    return {
      start: () => {
        startTime = performance.now();
      },
      end: (size = 0) => {
        const loadTime = performance.now() - startTime;
        this.metrics.set(url, { loadTime, size, type });
      }
    };
  }

  /**
   * Get performance report
   */
  static getPerformanceReport(): {
    totalAssets: number;
    totalSize: number;
    averageLoadTime: number;
    slowestAssets: Array<{ url: string; loadTime: number; type: string }>;
  } {
    const assets = Array.from(this.metrics.entries());
    const totalAssets = assets.length;
    const totalSize = assets.reduce((sum, [, metrics]) => sum + metrics.size, 0);
    const averageLoadTime = assets.reduce((sum, [, metrics]) => sum + metrics.loadTime, 0) / totalAssets;
    
    const slowestAssets = assets
      .sort(([, a], [, b]) => b.loadTime - a.loadTime)
      .slice(0, 5)
      .map(([url, metrics]) => ({
        url,
        loadTime: metrics.loadTime,
        type: metrics.type
      }));

    return {
      totalAssets,
      totalSize,
      averageLoadTime,
      slowestAssets
    };
  }
}

export default {
  ImageOptimizer,
  OptimizedImage,
  AssetPreloader,
  ImageDimensions,
  AssetPerformanceMonitor
};