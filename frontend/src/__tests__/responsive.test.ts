/**
 * @jest-environment jsdom
 */

import { describe, it, expect, jest } from '@jest/globals';
import {
  breakpoints,
  mediaQuery,
  getResponsiveValue,
  responsivePatterns,
} from '../utils/responsive';

describe('Responsive Utilities', () => {
  describe('breakpoints', () => {
    it('should have correct breakpoint values', () => {
      expect(breakpoints.xs).toBe(0);
      expect(breakpoints.sm).toBe(640);
      expect(breakpoints.md).toBe(768);
      expect(breakpoints.lg).toBe(1024);
      expect(breakpoints.xl).toBe(1280);
      expect(breakpoints['2xl']).toBe(1536);
    });
  });

  describe('mediaQuery', () => {
    it('should generate correct up media queries', () => {
      expect(mediaQuery.up('sm')).toBe('@media (min-width: 640px)');
      expect(mediaQuery.up('lg')).toBe('@media (min-width: 1024px)');
    });

    it('should generate correct down media queries', () => {
      expect(mediaQuery.down('xs')).toBe('');
      expect(mediaQuery.down('sm')).toBe('@media (max-width: 639px)');
      expect(mediaQuery.down('lg')).toBe('@media (max-width: 1023px)');
    });

    it('should generate correct between media queries', () => {
      expect(mediaQuery.between('sm', 'lg')).toBe('@media (min-width: 640px) and (max-width: 1023px)');
    });
  });

  describe('getResponsiveValue', () => {
    it('should return primitive values as-is', () => {
      expect(getResponsiveValue('test', 'md')).toBe('test');
      expect(getResponsiveValue(42, 'lg')).toBe(42);
    });

    it('should return responsive values correctly', () => {
      const responsiveValue = {
        xs: 'small',
        md: 'medium',
        lg: 'large',
      };

      expect(getResponsiveValue(responsiveValue, 'xs')).toBe('small');
      expect(getResponsiveValue(responsiveValue, 'sm')).toBe('small'); // fallback to xs
      expect(getResponsiveValue(responsiveValue, 'md')).toBe('medium');
      expect(getResponsiveValue(responsiveValue, 'lg')).toBe('large');
      expect(getResponsiveValue(responsiveValue, 'xl')).toBe('large'); // fallback to lg
    });
  });

  describe('responsivePatterns', () => {
    it('should generate hide/show patterns', () => {
      const hideBelow = responsivePatterns.hideBelow('md');
      expect(hideBelow).toHaveProperty('@media (max-width: 767px)');
      expect(hideBelow['@media (max-width: 767px)']).toEqual({ display: 'none' });
    });

    it('should generate stack pattern', () => {
      const stackBelow = responsivePatterns.stackBelow('lg');
      expect(stackBelow).toHaveProperty('@media (max-width: 1023px)');
      expect(stackBelow['@media (max-width: 1023px)']).toEqual({ flexDirection: 'column' });
    });
  });
});

// Mock window.matchMedia for useMediaQuery tests
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(), // deprecated
    removeListener: jest.fn(), // deprecated
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
});