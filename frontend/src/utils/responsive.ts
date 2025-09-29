/**
 * Responsive Design System
 * Provides breakpoints, media queries, and responsive utilities
 */

export const breakpoints = {
  xs: 0,
  sm: 640,
  md: 768,
  lg: 1024,
  xl: 1280,
  '2xl': 1536,
} as const;

export type Breakpoint = keyof typeof breakpoints;

/**
 * Generate media query string for a breakpoint
 */
export const mediaQuery = {
  up: (breakpoint: Breakpoint) => `@media (min-width: ${breakpoints[breakpoint]}px)`,
  down: (breakpoint: Breakpoint) => {
    const bpValue = breakpoints[breakpoint];
    return bpValue === 0 ? '' : `@media (max-width: ${bpValue - 1}px)`;
  },
  between: (minBreakpoint: Breakpoint, maxBreakpoint: Breakpoint) => {
    const minValue = breakpoints[minBreakpoint];
    const maxValue = breakpoints[maxBreakpoint];
    return `@media (min-width: ${minValue}px) and (max-width: ${maxValue - 1}px)`;
  },
  only: (breakpoint: Breakpoint) => {
    const keys = Object.keys(breakpoints) as Breakpoint[];
    const currentIndex = keys.indexOf(breakpoint);
    const nextBreakpoint = keys[currentIndex + 1];
    
    if (!nextBreakpoint) {
      return mediaQuery.up(breakpoint);
    }
    
    return mediaQuery.between(breakpoint, nextBreakpoint);
  },
} as const;

/**
 * Hook to get current breakpoint
 */
export const useBreakpoint = () => {
  const [currentBreakpoint, setCurrentBreakpoint] = React.useState<Breakpoint>('xs');

  React.useEffect(() => {
    const updateBreakpoint = () => {
      const width = window.innerWidth;
      const breakpointEntries = Object.entries(breakpoints) as [Breakpoint, number][];
      
      // Find the largest breakpoint that fits the current width
      const matchingBreakpoint = breakpointEntries
        .reverse()
        .find(([, value]) => width >= value);
      
      if (matchingBreakpoint) {
        setCurrentBreakpoint(matchingBreakpoint[0]);
      }
    };

    updateBreakpoint();
    window.addEventListener('resize', updateBreakpoint);
    return () => window.removeEventListener('resize', updateBreakpoint);
  }, []);

  return currentBreakpoint;
};

/**
 * Hook to check if screen is at least a certain breakpoint
 */
export const useMediaQuery = (query: string) => {
  const [matches, setMatches] = React.useState(false);

  React.useEffect(() => {
    const mediaQueryList = window.matchMedia(query);
    const updateMatches = () => setMatches(mediaQueryList.matches);
    
    updateMatches();
    mediaQueryList.addEventListener('change', updateMatches);
    return () => mediaQueryList.removeEventListener('change', updateMatches);
  }, [query]);

  return matches;
};

/**
 * Responsive value utility
 */
export type ResponsiveValue<T> = T | Partial<Record<Breakpoint, T>>;

export const getResponsiveValue = <T>(
  value: ResponsiveValue<T>,
  breakpoint: Breakpoint
): T => {
  if (typeof value === 'object' && value !== null && !Array.isArray(value)) {
    const responsiveValue = value as Partial<Record<Breakpoint, T>>;
    const breakpointOrder: Breakpoint[] = ['xs', 'sm', 'md', 'lg', 'xl', '2xl'];
    const currentIndex = breakpointOrder.indexOf(breakpoint);
    
    // Find the closest defined value at or below current breakpoint
    for (let i = currentIndex; i >= 0; i--) {
      const bp = breakpointOrder[i];
      if (bp in responsiveValue && responsiveValue[bp] !== undefined) {
        return responsiveValue[bp] as T;
      }
    }
    
    // Fallback to the first defined value
    const firstDefinedValue = Object.values(responsiveValue).find(v => v !== undefined);
    return firstDefinedValue as T;
  }
  
  return value as T;
};

/**
 * Container max-width utilities
 */
export const containerMaxWidths = {
  sm: '640px',
  md: '768px',
  lg: '1024px',
  xl: '1280px',
  '2xl': '1536px',
} as const;

/**
 * Grid system utilities
 */
export const gridCols = {
  1: '8.333333%',
  2: '16.666667%',
  3: '25%',
  4: '33.333333%',
  5: '41.666667%',
  6: '50%',
  7: '58.333333%',
  8: '66.666667%',
  9: '75%',
  10: '83.333333%',
  11: '91.666667%',
  12: '100%',
} as const;

/**
 * Spacing scale for consistent responsive spacing
 */
export const spacing = {
  0: '0',
  1: '0.25rem',    // 4px
  2: '0.5rem',     // 8px
  3: '0.75rem',    // 12px
  4: '1rem',       // 16px
  5: '1.25rem',    // 20px
  6: '1.5rem',     // 24px
  8: '2rem',       // 32px
  10: '2.5rem',    // 40px
  12: '3rem',      // 48px
  16: '4rem',      // 64px
  20: '5rem',      // 80px
  24: '6rem',      // 96px
  32: '8rem',      // 128px
} as const;

/**
 * Typography scale
 */
export const fontSize = {
  xs: '0.75rem',     // 12px
  sm: '0.875rem',    // 14px
  base: '1rem',      // 16px
  lg: '1.125rem',    // 18px
  xl: '1.25rem',     // 20px
  '2xl': '1.5rem',   // 24px
  '3xl': '1.875rem', // 30px
  '4xl': '2.25rem',  // 36px
  '5xl': '3rem',     // 48px
} as const;

/**
 * Responsive font sizes
 */
export const responsiveFontSize = {
  xs: { xs: fontSize.xs, sm: fontSize.xs },
  sm: { xs: fontSize.xs, sm: fontSize.sm },
  base: { xs: fontSize.sm, sm: fontSize.base },
  lg: { xs: fontSize.base, sm: fontSize.lg },
  xl: { xs: fontSize.lg, sm: fontSize.xl },
  '2xl': { xs: fontSize.xl, sm: fontSize['2xl'] },
  '3xl': { xs: fontSize['2xl'], sm: fontSize['3xl'] },
  '4xl': { xs: fontSize['3xl'], sm: fontSize['4xl'] },
  '5xl': { xs: fontSize['4xl'], sm: fontSize['5xl'] },
} as const;

/**
 * Responsive spacing scale
 */
export const responsiveSpacing = {
  xs: { xs: spacing[1], sm: spacing[2] },
  sm: { xs: spacing[2], sm: spacing[3] },
  md: { xs: spacing[3], sm: spacing[4] },
  lg: { xs: spacing[4], sm: spacing[6] },
  xl: { xs: spacing[6], sm: spacing[8] },
  '2xl': { xs: spacing[8], sm: spacing[10] },
  '3xl': { xs: spacing[10], sm: spacing[12] },
  '4xl': { xs: spacing[12], sm: spacing[16] },
} as const;

/**
 * CSS custom properties for responsive design
 */
export const cssVariables = {
  // Container
  '--container-max-width': 'var(--max-width, 100%)',
  '--container-padding': 'var(--padding, 1rem)',
  
  // Grid
  '--grid-columns': 'var(--columns, 12)',
  '--grid-gap': 'var(--gap, 1rem)',
  
  // Breakpoints (for CSS calc functions)
  '--breakpoint-xs': `${breakpoints.xs}px`,
  '--breakpoint-sm': `${breakpoints.sm}px`,
  '--breakpoint-md': `${breakpoints.md}px`,
  '--breakpoint-lg': `${breakpoints.lg}px`,
  '--breakpoint-xl': `${breakpoints.xl}px`,
  '--breakpoint-2xl': `${breakpoints['2xl']}px`,
} as const;

/**
 * Common responsive patterns
 */
export const responsivePatterns = {
  // Hide/show at breakpoints
  hideBelow: (breakpoint: Breakpoint) => ({
    [mediaQuery.down(breakpoint)]: {
      display: 'none',
    },
  }),
  
  hideAbove: (breakpoint: Breakpoint) => ({
    [mediaQuery.up(breakpoint)]: {
      display: 'none',
    },
  }),
  
  showOnly: (breakpoint: Breakpoint) => ({
    display: 'none',
    [mediaQuery.only(breakpoint)]: {
      display: 'block',
    },
  }),
  
  // Stack on mobile
  stackBelow: (breakpoint: Breakpoint) => ({
    [mediaQuery.down(breakpoint)]: {
      flexDirection: 'column',
    },
  }),
  
  // Responsive grid
  responsiveGrid: (cols: Partial<Record<Breakpoint, number>>) => {
    const styles: Record<string, string | Record<string, string>> = {
      display: 'grid',
      gap: 'var(--grid-gap)',
    };
    
    Object.entries(cols).forEach(([bp, colCount]) => {
      const breakpoint = bp as Breakpoint;
      const query = breakpoint === 'xs' ? '' : mediaQuery.up(breakpoint);
      
      if (query) {
        styles[query] = {
          gridTemplateColumns: `repeat(${colCount}, 1fr)`,
        };
      } else {
        styles.gridTemplateColumns = `repeat(${colCount}, 1fr)`;
      }
    });
    
    return styles;
  },
  
  // Responsive spacing
  responsivePadding: (values: Partial<Record<Breakpoint, number>>) => {
    const styles: Record<string, string | Record<string, string>> = {};
    
    Object.entries(values).forEach(([bp, value]) => {
      const breakpoint = bp as Breakpoint;
      const query = breakpoint === 'xs' ? '' : mediaQuery.up(breakpoint);
      const spacingValue = spacing[value as keyof typeof spacing];
      
      if (query) {
        styles[query] = { padding: spacingValue };
      } else {
        styles.padding = spacingValue;
      }
    });
    
    return styles;
  },
} as const;

import React from 'react';