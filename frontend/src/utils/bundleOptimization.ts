/**
 * Bundle Size Analysis and Optimization Utilities
 * Provides tools for analyzing and optimizing bundle size
 */

/**
 * Bundle analyzer configuration for Vite
 */
export const bundleAnalyzerConfig = {
  rollupOptions: {
    output: {
      manualChunks: {
        // Vendor chunk for React and related libraries
        vendor: ['react', 'react-dom', 'react-router-dom'],
        
        // UI components chunk
        ui: [
          '@tanstack/react-query',
          'axios'
        ],
        
        // Utility libraries chunk
        utils: [
          'date-fns',
          'lodash-es'
        ]
      }
    }
  },
  
  // Bundle analysis plugins
  plugins: [
    // Uncomment for bundle analysis
    // import('rollup-plugin-visualizer').then(({ visualizer }) =>
    //   visualizer({
    //     filename: 'dist/bundle-analysis.html',
    //     open: true,
    //     gzipSize: true,
    //     brotliSize: true
    //   })
    // )
  ]
};

/**
 * Code splitting strategies
 */
export const codeSplittingStrategies = {
  // Route-based splitting
  routeBased: {
    description: 'Split by route/page components',
    implementation: `
      const HomePage = lazy(() => import('../pages/HomePage'));
      const CoursePage = lazy(() => import('../pages/CoursePage'));
      const QuizPage = lazy(() => import('../pages/QuizPage'));
    `
  },
  
  // Feature-based splitting
  featureBased: {
    description: 'Split by feature modules',
    implementation: `
      const CourseManagement = lazy(() => import('../features/CourseManagement'));
      const QuizEngine = lazy(() => import('../features/QuizEngine'));
      const UserDashboard = lazy(() => import('../features/UserDashboard'));
    `
  },
  
  // Vendor splitting
  vendorBased: {
    description: 'Split vendor libraries from application code',
    implementation: `
      // Automatic via Vite's manualChunks configuration
      // See bundleAnalyzerConfig above
    `
  }
};

/**
 * Bundle optimization techniques
 */
export const optimizationTechniques = {
  treeShaking: {
    description: 'Remove unused code from bundles',
    implementation: {
      // Import only what you need
      correct: `import { debounce } from 'lodash-es';`,
      incorrect: `import _ from 'lodash';`,
      
      // Use ES modules for better tree shaking
      preferred: `import { format } from 'date-fns';`,
      avoid: `import * as dateFns from 'date-fns';`
    }
  },
  
  dynamicImports: {
    description: 'Load code only when needed',
    examples: [
      {
        name: 'Conditional imports',
        code: `
          const loadChartLibrary = async () => {
            if (needsChart) {
              const { Chart } = await import('chart.js');
              return Chart;
            }
          };
        `
      },
      {
        name: 'Feature flags',
        code: `
          const loadAdvancedFeatures = async () => {
            if (user.hasAdvancedFeatures) {
              return import('../features/AdvancedFeatures');
            }
          };
        `
      }
    ]
  },
  
  compression: {
    description: 'Compress assets for better network performance',
    techniques: ['gzip', 'brotli', 'webpack compression'],
    implementation: `
      // Vite automatically handles this in production
      // Additional compression can be configured in server
    `
  }
};

/**
 * Bundle size monitoring utilities
 */
export class BundleSizeMonitor {
  private static readonly SIZE_LIMITS = {
    total: 500 * 1024, // 500KB total
    initial: 200 * 1024, // 200KB initial load
    chunk: 100 * 1024 // 100KB per chunk
  };

  /**
   * Check if bundle sizes are within acceptable limits
   */
  static checkSizeLimits(bundleStats: {
    total: number;
    initial: number;
    chunks: { name: string; size: number }[];
  }): {
    passed: boolean;
    violations: string[];
    recommendations: string[];
  } {
    const violations: string[] = [];
    const recommendations: string[] = [];

    // Check total size
    if (bundleStats.total > this.SIZE_LIMITS.total) {
      violations.push(
        `Total bundle size (${this.formatSize(bundleStats.total)}) exceeds limit (${this.formatSize(this.SIZE_LIMITS.total)})`
      );
      recommendations.push('Consider code splitting and lazy loading');
    }

    // Check initial load size
    if (bundleStats.initial > this.SIZE_LIMITS.initial) {
      violations.push(
        `Initial load size (${this.formatSize(bundleStats.initial)}) exceeds limit (${this.formatSize(this.SIZE_LIMITS.initial)})`
      );
      recommendations.push('Move non-critical code to lazy-loaded chunks');
    }

    // Check individual chunk sizes
    bundleStats.chunks.forEach(chunk => {
      if (chunk.size > this.SIZE_LIMITS.chunk) {
        violations.push(
          `Chunk "${chunk.name}" (${this.formatSize(chunk.size)}) exceeds limit (${this.formatSize(this.SIZE_LIMITS.chunk)})`
        );
        recommendations.push(`Split "${chunk.name}" into smaller chunks`);
      }
    });

    return {
      passed: violations.length === 0,
      violations,
      recommendations
    };
  }

  /**
   * Format byte size to human readable format
   */
  private static formatSize(bytes: number): string {
    const units = ['B', 'KB', 'MB', 'GB'];
    let size = bytes;
    let unitIndex = 0;

    while (size >= 1024 && unitIndex < units.length - 1) {
      size /= 1024;
      unitIndex++;
    }

    return `${size.toFixed(1)} ${units[unitIndex]}`;
  }

  /**
   * Generate bundle size report
   */
  static generateReport(bundleStats: {
    total: number;
    initial: number;
    chunks: { name: string; size: number }[];
  }): string {
    const { passed, violations, recommendations } = this.checkSizeLimits(bundleStats);
    
    let report = '# Bundle Size Analysis Report\n\n';
    
    report += `## Summary\n`;
    report += `- **Status**: ${passed ? '✅ PASSED' : '❌ FAILED'}\n`;
    report += `- **Total Size**: ${this.formatSize(bundleStats.total)}\n`;
    report += `- **Initial Load**: ${this.formatSize(bundleStats.initial)}\n`;
    report += `- **Chunks**: ${bundleStats.chunks.length}\n\n`;
    
    if (violations.length > 0) {
      report += `## Violations\n`;
      violations.forEach(violation => {
        report += `- ❌ ${violation}\n`;
      });
      report += '\n';
    }
    
    if (recommendations.length > 0) {
      report += `## Recommendations\n`;
      recommendations.forEach(recommendation => {
        report += `- 💡 ${recommendation}\n`;
      });
      report += '\n';
    }
    
    report += `## Chunk Details\n`;
    bundleStats.chunks
      .sort((a, b) => b.size - a.size)
      .forEach(chunk => {
        const status = chunk.size > this.SIZE_LIMITS.chunk ? '❌' : '✅';
        report += `- ${status} **${chunk.name}**: ${this.formatSize(chunk.size)}\n`;
      });
    
    return report;
  }
}

/**
 * Performance budget configuration
 */
export const performanceBudget = {
  // Size budgets
  sizes: {
    total: '500KB',
    initial: '200KB',
    perChunk: '100KB'
  },
  
  // Performance metrics budgets
  metrics: {
    firstContentfulPaint: 1500, // ms
    largestContentfulPaint: 2500, // ms
    cumulativeLayoutShift: 0.1,
    firstInputDelay: 100 // ms
  },
  
  // Resource count budgets
  resources: {
    scripts: 10,
    stylesheets: 5,
    images: 20,
    fonts: 4
  }
};

/**
 * Bundle optimization recommendations
 */
export const optimizationRecommendations = [
  {
    category: 'Code Splitting',
    items: [
      'Implement route-based code splitting',
      'Split vendor libraries into separate chunks',
      'Use dynamic imports for conditional features',
      'Implement component-level lazy loading'
    ]
  },
  {
    category: 'Tree Shaking',
    items: [
      'Use ES6 imports instead of CommonJS requires',
      'Import only needed functions from libraries',
      'Avoid importing entire libraries when possible',
      'Use babel-plugin-import for selective imports'
    ]
  },
  {
    category: 'Asset Optimization',
    items: [
      'Optimize images with proper formats (WebP, AVIF)',
      'Use responsive images with srcset',
      'Implement image lazy loading',
      'Minimize and compress CSS/JS files'
    ]
  },
  {
    category: 'Network Optimization',
    items: [
      'Enable gzip/brotli compression',
      'Use HTTP/2 server push for critical resources',
      'Implement proper caching strategies',
      'Use CDN for static assets'
    ]
  }
];

export default {
  bundleAnalyzerConfig,
  codeSplittingStrategies,
  optimizationTechniques,
  BundleSizeMonitor,
  performanceBudget,
  optimizationRecommendations
};