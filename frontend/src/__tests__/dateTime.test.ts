/**
 * @jest-environment jsdom
 */

import { describe, it, expect } from '@jest/globals';
import { 
  formatDate, 
  formatRelativeTime, 
  parseDate, 
  isValidDate,
  addTime,
  isSameDay,
  isBefore,
  isAfter,
  getDateRange,
  calculateAge,
} from '../utils/dateTime';

describe('DateTime Utilities', () => {
  const testDate = new Date('2023-06-15T14:30:00Z');

  describe('isValidDate', () => {
    it('should return true for valid dates', () => {
      expect(isValidDate(new Date())).toBe(true);
      expect(isValidDate(new Date('2023-01-01'))).toBe(true);
    });

    it('should return false for invalid dates', () => {
      expect(isValidDate(new Date('invalid'))).toBe(false);
      expect(isValidDate('not a date' as unknown as Date)).toBe(false);
      expect(isValidDate(null as unknown as Date)).toBe(false);
    });
  });

  describe('parseDate', () => {
    it('should parse valid date strings', () => {
      const result = parseDate('2023-06-15');
      expect(result).toBeInstanceOf(Date);
      expect(result?.getFullYear()).toBe(2023);
    });

    it('should parse Date objects', () => {
      const result = parseDate(testDate);
      expect(result).toBe(testDate);
    });

    it('should return null for invalid dates', () => {
      expect(parseDate('invalid-date')).toBeNull();
      expect(parseDate('')).toBeNull();
    });
  });

  describe('formatDate', () => {
    it('should format dates in different formats', () => {
      expect(formatDate(testDate, 'iso')).toBe('2023-06-15');
      expect(formatDate(testDate, 'short')).toMatch(/\d{1,2}\/\d{1,2}\/\d{2}/);
      expect(formatDate(testDate, 'medium')).toMatch(/Jun \d{1,2}, 2023/);
    });

    it('should handle invalid dates', () => {
      expect(formatDate('invalid-date')).toBe('Invalid Date');
    });
  });

  describe('formatRelativeTime', () => {
    const now = new Date('2023-06-15T15:00:00Z');

    it('should format recent times', () => {
      const thirtyMinutesAgo = new Date('2023-06-15T14:30:00Z');
      const result = formatRelativeTime(thirtyMinutesAgo, now);
      expect(result).toContain('30 minutes');
    });

    it('should format future times', () => {
      const futureDate = new Date('2023-06-16T15:00:00Z');
      const result = formatRelativeTime(futureDate, now);
      expect(result).toMatch(/tomorrow|in 1 day/);
    });
  });

  describe('addTime', () => {
    it('should add different time units', () => {
      const result = addTime(testDate, 1, 'days');
      expect(result.getDate()).toBe(testDate.getDate() + 1);

      const hourResult = addTime(testDate, 2, 'hours');
      expect(hourResult.getHours()).toBe(testDate.getHours() + 2);
    });

    it('should handle month and year additions', () => {
      const monthResult = addTime(testDate, 1, 'months');
      expect(monthResult.getMonth()).toBe(testDate.getMonth() + 1);

      const yearResult = addTime(testDate, 1, 'years');
      expect(yearResult.getFullYear()).toBe(testDate.getFullYear() + 1);
    });
  });

  describe('date comparison functions', () => {
    const date1 = new Date('2023-06-15');
    const date2 = new Date('2023-06-15');
    const date3 = new Date('2023-06-16');

    it('should check if dates are the same day', () => {
      expect(isSameDay(date1, date2)).toBe(true);
      expect(isSameDay(date1, date3)).toBe(false);
    });

    it('should check if date is before another', () => {
      expect(isBefore(date1, date3)).toBe(true);
      expect(isBefore(date3, date1)).toBe(false);
    });

    it('should check if date is after another', () => {
      expect(isAfter(date3, date1)).toBe(true);
      expect(isAfter(date1, date3)).toBe(false);
    });
  });

  describe('getDateRange', () => {
    it('should generate date range', () => {
      const start = new Date('2023-06-15');
      const end = new Date('2023-06-17');
      const range = getDateRange(start, end);
      
      expect(range).toHaveLength(3);
      expect(range[0]).toEqual(start);
      expect(range[2]).toEqual(end);
    });

    it('should handle same start and end date', () => {
      const date = new Date('2023-06-15');
      const range = getDateRange(date, date);
      
      expect(range).toHaveLength(1);
      expect(range[0]).toEqual(date);
    });
  });

  describe('calculateAge', () => {
    it('should calculate age correctly', () => {
      const birthDate = new Date('1990-06-15');
      const referenceDate = new Date('2023-06-15');
      
      expect(calculateAge(birthDate, referenceDate)).toBe(33);
    });

    it('should handle birthday not yet reached this year', () => {
      const birthDate = new Date('1990-12-25');
      const referenceDate = new Date('2023-06-15');
      
      expect(calculateAge(birthDate, referenceDate)).toBe(32);
    });

    it('should handle birthday already passed this year', () => {
      const birthDate = new Date('1990-01-15');
      const referenceDate = new Date('2023-06-15');
      
      expect(calculateAge(birthDate, referenceDate)).toBe(33);
    });
  });
});