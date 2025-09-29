/**
 * Error Handling Utilities
 * Utility functions separated from components for Fast Refresh compatibility
 */

import React from 'react';

/**
 * Toast Context Type (re-export for utility functions)
 */
export interface Toast {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message?: string;
  duration?: number;
  persistent?: boolean;
  action?: {
    label: string;
    onClick: () => void;
  };
}

interface ToastContextType {
  toasts: Toast[];
  addToast: (toast: Omit<Toast, 'id'>) => void;
  removeToast: (id: string) => void;
  clearAllToasts: () => void;
}

/**
 * Create Toast Context (for export)
 */
export const ToastContext = React.createContext<ToastContextType | undefined>(undefined);

/**
 * Toast Hook
 */
export const useToast = () => {
  const context = React.useContext(ToastContext);
  if (context === undefined) {
    throw new Error('useToast must be used within a ToastProvider');
  }
  return context;
};

/**
 * Error reporting utilities
 */
export const errorUtils = {
  /**
   * Log error to console with enhanced information
   */
  logError: (error: Error, context?: Record<string, unknown>) => {
    console.group('🚨 Error Report');
    console.error('Message:', error.message);
    console.error('Stack:', error.stack);
    if (context) {
      console.table(context);
    }
    console.error('Timestamp:', new Date().toISOString());
    console.error('User Agent:', navigator.userAgent);
    console.error('URL:', window.location.href);
    console.groupEnd();
  },

  /**
   * Send error to external service
   */
  reportError: async (
    error: Error, 
    context?: Record<string, unknown>
  ): Promise<boolean> => {
    try {
      const errorReport = {
        message: error.message,
        stack: error.stack,
        context,
        timestamp: new Date().toISOString(),
        userAgent: navigator.userAgent,
        url: window.location.href,
        userId: localStorage.getItem('userId'),
        sessionId: sessionStorage.getItem('sessionId')
      };

      const response = await fetch('/api/errors', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(errorReport)
      });

      return response.ok;
    } catch (reportError) {
      console.error('Failed to report error:', reportError);
      return false;
    }
  },

  /**
   * Create user-friendly error message
   */
  getUserFriendlyMessage: (error: Error | string): string => {
    const errorMessage = typeof error === 'string' ? error : error.message;
    
    // Common error patterns and their user-friendly messages
    const errorPatterns = [
      { pattern: /network/i, message: 'Network connection problem. Please check your internet connection.' },
      { pattern: /timeout/i, message: 'The request took too long. Please try again.' },
      { pattern: /unauthorized|401/i, message: 'You need to log in to access this feature.' },
      { pattern: /forbidden|403/i, message: 'You don\'t have permission to perform this action.' },
      { pattern: /not found|404/i, message: 'The requested resource was not found.' },
      { pattern: /server error|500/i, message: 'Server error. Our team has been notified.' },
      { pattern: /validation/i, message: 'Please check your input and try again.' }
    ];

    for (const { pattern, message } of errorPatterns) {
      if (pattern.test(errorMessage)) {
        return message;
      }
    }

    return 'An unexpected error occurred. Please try again.';
  },

  /**
   * Retry function with exponential backoff
   */
  retryWithBackoff: async <T>(
    fn: () => Promise<T>,
    maxRetries: number = 3,
    baseDelay: number = 1000
  ): Promise<T> => {
    let lastError: Error;

    for (let attempt = 0; attempt <= maxRetries; attempt++) {
      try {
        return await fn();
      } catch (error) {
        lastError = error as Error;
        
        if (attempt === maxRetries) {
          throw lastError;
        }

        // Exponential backoff with jitter
        const delay = baseDelay * Math.pow(2, attempt) + Math.random() * 1000;
        await new Promise(resolve => setTimeout(resolve, delay));
      }
    }

    throw lastError!;
  }
};

/**
 * Form validation utilities
 */
export const validationUtils = {
  /**
   * Validate email format
   */
  isValidEmail: (email: string): boolean => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  },

  /**
   * Validate password strength
   */
  validatePassword: (password: string): {
    isValid: boolean;
    errors: string[];
  } => {
    const errors: string[] = [];

    if (password.length < 8) {
      errors.push('Password must be at least 8 characters long');
    }
    if (!/[A-Z]/.test(password)) {
      errors.push('Password must contain at least one uppercase letter');
    }
    if (!/[a-z]/.test(password)) {
      errors.push('Password must contain at least one lowercase letter');
    }
    if (!/\d/.test(password)) {
      errors.push('Password must contain at least one number');
    }
    if (!/[!@#$%^&*(),.?":{}|<>]/.test(password)) {
      errors.push('Password must contain at least one special character');
    }

    return {
      isValid: errors.length === 0,
      errors
    };
  },

  /**
   * Validate required fields
   */
  validateRequired: <T extends Record<string, unknown>>(
    data: T,
    requiredFields: (keyof T)[]
  ): Record<string, string> => {
    const errors: Record<string, string> = {};

    requiredFields.forEach(field => {
      const value = data[field];
      if (!value || (typeof value === 'string' && !value.trim())) {
        errors[field as string] = `${String(field)} is required`;
      }
    });

    return errors;
  }
};

/**
 * Toast helper functions
 */
export const toastHelpers = {
  /**
   * Create success toast
   */
  success: (title: string, message?: string, duration?: number) => ({
    type: 'success' as const,
    title,
    message,
    duration
  }),

  /**
   * Create error toast
   */
  error: (title: string, message?: string, persistent = true) => ({
    type: 'error' as const,
    title,
    message,
    persistent
  }),

  /**
   * Create warning toast
   */
  warning: (title: string, message?: string, duration?: number) => ({
    type: 'warning' as const,
    title,
    message,
    duration
  }),

  /**
   * Create info toast
   */
  info: (title: string, message?: string, duration?: number) => ({
    type: 'info' as const,
    title,
    message,
    duration
  })
};

export default {
  useToast,
  errorUtils,
  validationUtils,
  toastHelpers,
  ToastContext
};