/**
 * Date and Time Utilities
 * Provides comprehensive date/time formatting and manipulation
 */

/**
 * Date format types
 */
export type DateFormat = 
  | 'short'           // 1/1/23
  | 'medium'          // Jan 1, 2023
  | 'long'            // January 1, 2023
  | 'full'            // Sunday, January 1, 2023
  | 'iso'             // 2023-01-01
  | 'time'            // 3:30 PM
  | 'time24'          // 15:30
  | 'datetime'        // Jan 1, 2023 3:30 PM
  | 'datetime24'      // Jan 1, 2023 15:30
  | 'relative'        // 2 days ago
  | 'duration';       // 2h 30m

/**
 * Time zone handling
 */
export const getTimeZone = (): string => {
  return Intl.DateTimeFormat().resolvedOptions().timeZone;
};

export const convertToTimeZone = (date: Date, timeZone: string): Date => {
  const utc = date.getTime() + (date.getTimezoneOffset() * 60000);
  const targetOffset = new Intl.DateTimeFormat('en-US', {
    timeZone,
    timeZoneName: 'longOffset'
  }).formatToParts(date).find(part => part.type === 'timeZoneName')?.value || '+00:00';
  
  const offsetMatch = targetOffset.match(/([+-])(\d{2}):(\d{2})/);
  if (!offsetMatch) return new Date(utc);
  
  const sign = offsetMatch[1] === '+' ? 1 : -1;
  const hours = parseInt(offsetMatch[2], 10);
  const minutes = parseInt(offsetMatch[3], 10);
  const offset = sign * (hours * 60 + minutes) * 60000;
  
  return new Date(utc + offset);
};

/**
 * Date validation
 */
export const isValidDate = (date: unknown): date is Date => {
  return date instanceof Date && !isNaN(date.getTime());
};

export const parseDate = (input: string | number | Date): Date | null => {
  if (input instanceof Date) {
    return isValidDate(input) ? input : null;
  }
  
  const date = new Date(input);
  return isValidDate(date) ? date : null;
};

/**
 * Date formatting
 */
export const formatDate = (
  input: string | number | Date,
  format: DateFormat = 'medium',
  locale = 'en-US',
  timeZone?: string
): string => {
  const date = parseDate(input);
  if (!date) return 'Invalid Date';

  const options: Intl.DateTimeFormatOptions = { timeZone };

  switch (format) {
    case 'short':
      return new Intl.DateTimeFormat(locale, {
        ...options,
        year: '2-digit',
        month: 'numeric',
        day: 'numeric',
      }).format(date);

    case 'medium':
      return new Intl.DateTimeFormat(locale, {
        ...options,
        year: 'numeric',
        month: 'short',
        day: 'numeric',
      }).format(date);

    case 'long':
      return new Intl.DateTimeFormat(locale, {
        ...options,
        year: 'numeric',
        month: 'long',
        day: 'numeric',
      }).format(date);

    case 'full':
      return new Intl.DateTimeFormat(locale, {
        ...options,
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric',
      }).format(date);

    case 'iso':
      return date.toISOString().split('T')[0];

    case 'time':
      return new Intl.DateTimeFormat(locale, {
        ...options,
        hour: 'numeric',
        minute: '2-digit',
        hour12: true,
      }).format(date);

    case 'time24':
      return new Intl.DateTimeFormat(locale, {
        ...options,
        hour: '2-digit',
        minute: '2-digit',
        hour12: false,
      }).format(date);

    case 'datetime':
      return new Intl.DateTimeFormat(locale, {
        ...options,
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: 'numeric',
        minute: '2-digit',
        hour12: true,
      }).format(date);

    case 'datetime24':
      return new Intl.DateTimeFormat(locale, {
        ...options,
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        hour12: false,
      }).format(date);

    case 'relative':
      return formatRelativeTime(date);

    case 'duration':
      return formatDuration(Date.now() - date.getTime());

    default:
      return date.toLocaleDateString(locale);
  }
};

/**
 * Relative time formatting
 */
export const formatRelativeTime = (
  input: string | number | Date,
  baseDate: Date = new Date(),
  locale = 'en-US'
): string => {
  const date = parseDate(input);
  if (!date) return 'Invalid Date';

  const diffMs = baseDate.getTime() - date.getTime();
  const diffSeconds = Math.floor(diffMs / 1000);
  const diffMinutes = Math.floor(diffSeconds / 60);
  const diffHours = Math.floor(diffMinutes / 60);
  const diffDays = Math.floor(diffHours / 24);
  const diffWeeks = Math.floor(diffDays / 7);
  const diffMonths = Math.floor(diffDays / 30);
  const diffYears = Math.floor(diffDays / 365);

  const rtf = new Intl.RelativeTimeFormat(locale, { numeric: 'auto' });

  if (Math.abs(diffSeconds) < 60) {
    return rtf.format(-diffSeconds, 'second');
  } else if (Math.abs(diffMinutes) < 60) {
    return rtf.format(-diffMinutes, 'minute');
  } else if (Math.abs(diffHours) < 24) {
    return rtf.format(-diffHours, 'hour');
  } else if (Math.abs(diffDays) < 7) {
    return rtf.format(-diffDays, 'day');
  } else if (Math.abs(diffWeeks) < 4) {
    return rtf.format(-diffWeeks, 'week');
  } else if (Math.abs(diffMonths) < 12) {
    return rtf.format(-diffMonths, 'month');
  } else {
    return rtf.format(-diffYears, 'year');
  }
};

/**
 * Duration formatting
 */
export const formatDuration = (
  milliseconds: number,
  options: {
    units?: ('years' | 'months' | 'days' | 'hours' | 'minutes' | 'seconds')[];
    precision?: number;
    format?: 'long' | 'short' | 'narrow';
  } = {}
): string => {
  const {
    units = ['hours', 'minutes', 'seconds'],
    precision = 2,
    format = 'short',
  } = options;

  const ms = Math.abs(milliseconds);
  const seconds = Math.floor(ms / 1000);
  const minutes = Math.floor(seconds / 60);
  const hours = Math.floor(minutes / 60);
  const days = Math.floor(hours / 24);
  const months = Math.floor(days / 30);
  const years = Math.floor(days / 365);

  const values = {
    years: years,
    months: months % 12,
    days: days % 30,
    hours: hours % 24,
    minutes: minutes % 60,
    seconds: seconds % 60,
  };

  const parts: string[] = [];
  let count = 0;

  for (const unit of units) {
    if (count >= precision) break;
    const value = values[unit];
    if (value > 0) {
      parts.push(formatDurationUnit(value, unit, format));
      count++;
    }
  }

  if (parts.length === 0) {
    return formatDurationUnit(0, units[units.length - 1], format);
  }

  return parts.join(' ');
};

const formatDurationUnit = (
  value: number,
  unit: string,
  format: 'long' | 'short' | 'narrow'
): string => {
  const formatMap = {
    long: {
      years: value === 1 ? 'year' : 'years',
      months: value === 1 ? 'month' : 'months',
      days: value === 1 ? 'day' : 'days',
      hours: value === 1 ? 'hour' : 'hours',
      minutes: value === 1 ? 'minute' : 'minutes',
      seconds: value === 1 ? 'second' : 'seconds',
    },
    short: {
      years: 'y',
      months: 'mo',
      days: 'd',
      hours: 'h',
      minutes: 'm',
      seconds: 's',
    },
    narrow: {
      years: 'y',
      months: 'M',
      days: 'd',
      hours: 'h',
      minutes: 'm',
      seconds: 's',
    },
  };

  const unitText = formatMap[format][unit as keyof typeof formatMap[typeof format]];
  return format === 'long' ? `${value} ${unitText}` : `${value}${unitText}`;
};

/**
 * Date manipulation
 */
export const addTime = (
  date: Date,
  amount: number,
  unit: 'years' | 'months' | 'days' | 'hours' | 'minutes' | 'seconds' | 'milliseconds'
): Date => {
  const newDate = new Date(date);

  switch (unit) {
    case 'years':
      newDate.setFullYear(newDate.getFullYear() + amount);
      break;
    case 'months':
      newDate.setMonth(newDate.getMonth() + amount);
      break;
    case 'days':
      newDate.setDate(newDate.getDate() + amount);
      break;
    case 'hours':
      newDate.setHours(newDate.getHours() + amount);
      break;
    case 'minutes':
      newDate.setMinutes(newDate.getMinutes() + amount);
      break;
    case 'seconds':
      newDate.setSeconds(newDate.getSeconds() + amount);
      break;
    case 'milliseconds':
      newDate.setMilliseconds(newDate.getMilliseconds() + amount);
      break;
  }

  return newDate;
};

export const subtractTime = (
  date: Date,
  amount: number,
  unit: 'years' | 'months' | 'days' | 'hours' | 'minutes' | 'seconds' | 'milliseconds'
): Date => {
  return addTime(date, -amount, unit);
};

export const startOfDay = (date: Date): Date => {
  const newDate = new Date(date);
  newDate.setHours(0, 0, 0, 0);
  return newDate;
};

export const endOfDay = (date: Date): Date => {
  const newDate = new Date(date);
  newDate.setHours(23, 59, 59, 999);
  return newDate;
};

export const startOfWeek = (date: Date, firstDayOfWeek = 0): Date => {
  const newDate = new Date(date);
  const day = newDate.getDay();
  const diff = (day < firstDayOfWeek ? 7 : 0) + day - firstDayOfWeek;
  newDate.setDate(newDate.getDate() - diff);
  return startOfDay(newDate);
};

export const endOfWeek = (date: Date, firstDayOfWeek = 0): Date => {
  const start = startOfWeek(date, firstDayOfWeek);
  return endOfDay(addTime(start, 6, 'days'));
};

export const startOfMonth = (date: Date): Date => {
  const newDate = new Date(date);
  newDate.setDate(1);
  return startOfDay(newDate);
};

export const endOfMonth = (date: Date): Date => {
  const newDate = new Date(date);
  newDate.setMonth(newDate.getMonth() + 1, 0);
  return endOfDay(newDate);
};

export const startOfYear = (date: Date): Date => {
  const newDate = new Date(date);
  newDate.setMonth(0, 1);
  return startOfDay(newDate);
};

export const endOfYear = (date: Date): Date => {
  const newDate = new Date(date);
  newDate.setMonth(11, 31);
  return endOfDay(newDate);
};

/**
 * Date comparison
 */
export const isSameDay = (date1: Date, date2: Date): boolean => {
  return (
    date1.getFullYear() === date2.getFullYear() &&
    date1.getMonth() === date2.getMonth() &&
    date1.getDate() === date2.getDate()
  );
};

export const isSameWeek = (date1: Date, date2: Date, firstDayOfWeek = 0): boolean => {
  const start1 = startOfWeek(date1, firstDayOfWeek);
  const start2 = startOfWeek(date2, firstDayOfWeek);
  return isSameDay(start1, start2);
};

export const isSameMonth = (date1: Date, date2: Date): boolean => {
  return (
    date1.getFullYear() === date2.getFullYear() &&
    date1.getMonth() === date2.getMonth()
  );
};

export const isSameYear = (date1: Date, date2: Date): boolean => {
  return date1.getFullYear() === date2.getFullYear();
};

export const isBefore = (date1: Date, date2: Date): boolean => {
  return date1.getTime() < date2.getTime();
};

export const isAfter = (date1: Date, date2: Date): boolean => {
  return date1.getTime() > date2.getTime();
};

export const isBetween = (date: Date, start: Date, end: Date, inclusive = true): boolean => {
  const dateTime = date.getTime();
  const startTime = start.getTime();
  const endTime = end.getTime();
  
  if (inclusive) {
    return dateTime >= startTime && dateTime <= endTime;
  } else {
    return dateTime > startTime && dateTime < endTime;
  }
};

/**
 * Date ranges
 */
export const getDaysInMonth = (year: number, month: number): number => {
  return new Date(year, month + 1, 0).getDate();
};

export const getWeeksInMonth = (year: number, month: number, firstDayOfWeek = 0): number => {
  const firstDay = new Date(year, month, 1);
  const lastDay = new Date(year, month + 1, 0);
  const firstWeekStart = startOfWeek(firstDay, firstDayOfWeek);
  const lastWeekStart = startOfWeek(lastDay, firstDayOfWeek);
  
  return Math.ceil((lastWeekStart.getTime() - firstWeekStart.getTime()) / (7 * 24 * 60 * 60 * 1000)) + 1;
};

export const getDateRange = (start: Date, end: Date): Date[] => {
  const dates: Date[] = [];
  const current = new Date(start);
  
  while (current <= end) {
    dates.push(new Date(current));
    current.setDate(current.getDate() + 1);
  }
  
  return dates;
};

export const getBusinessDays = (start: Date, end: Date): Date[] => {
  return getDateRange(start, end).filter(date => {
    const day = date.getDay();
    return day !== 0 && day !== 6; // Exclude Sunday (0) and Saturday (6)
  });
};

/**
 * Formatting presets
 */
export const dateFormats = {
  // Common formats
  short: (date: Date) => formatDate(date, 'short'),
  medium: (date: Date) => formatDate(date, 'medium'),
  long: (date: Date) => formatDate(date, 'long'),
  full: (date: Date) => formatDate(date, 'full'),
  
  // Time formats
  time: (date: Date) => formatDate(date, 'time'),
  time24: (date: Date) => formatDate(date, 'time24'),
  
  // Combined formats
  datetime: (date: Date) => formatDate(date, 'datetime'),
  datetime24: (date: Date) => formatDate(date, 'datetime24'),
  
  // Special formats
  iso: (date: Date) => formatDate(date, 'iso'),
  relative: (date: Date) => formatDate(date, 'relative'),
  
  // Custom formats
  monthYear: (date: Date) => formatDate(date, 'medium').replace(/^\w+\s+/, ''),
  dayMonth: (date: Date) => new Intl.DateTimeFormat('en-US', {
    month: 'short',
    day: 'numeric',
  }).format(date),
  weekday: (date: Date) => new Intl.DateTimeFormat('en-US', {
    weekday: 'long',
  }).format(date),
} as const;

/**
 * Utility constants
 */
export const TIME_CONSTANTS = {
  MILLISECONDS_IN_SECOND: 1000,
  SECONDS_IN_MINUTE: 60,
  MINUTES_IN_HOUR: 60,
  HOURS_IN_DAY: 24,
  DAYS_IN_WEEK: 7,
  DAYS_IN_YEAR: 365,
  MILLISECONDS_IN_MINUTE: 60 * 1000,
  MILLISECONDS_IN_HOUR: 60 * 60 * 1000,
  MILLISECONDS_IN_DAY: 24 * 60 * 60 * 1000,
} as const;

/**
 * Age calculation
 */
export const calculateAge = (birthDate: Date, referenceDate: Date = new Date()): number => {
  let age = referenceDate.getFullYear() - birthDate.getFullYear();
  const monthDiff = referenceDate.getMonth() - birthDate.getMonth();
  
  if (monthDiff < 0 || (monthDiff === 0 && referenceDate.getDate() < birthDate.getDate())) {
    age--;
  }
  
  return age;
};

/**
 * Working days calculation
 */
export const addBusinessDays = (date: Date, days: number): Date => {
  const result = new Date(date);
  let addedDays = 0;
  
  while (addedDays < days) {
    result.setDate(result.getDate() + 1);
    const dayOfWeek = result.getDay();
    if (dayOfWeek !== 0 && dayOfWeek !== 6) {
      addedDays++;
    }
  }
  
  return result;
};

export const getBusinessDaysBetween = (start: Date, end: Date): number => {
  return getBusinessDays(start, end).length;
};