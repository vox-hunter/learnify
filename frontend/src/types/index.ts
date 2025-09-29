// Type Definitions Index
// Central export for all TypeScript type definitions

// API Types
export * from './api';

// Component Types
export * from './components';

// State Management Types
export * from './state';

// Utility Types
export * from './utils';

// Error Handling Types
export * from './errors';

// Re-export commonly used types for convenience
export type {
  // API
  DocumentUploadResponse,
  CourseGenerationRequest,
  CourseData,
  Question,
  UserProfile,
} from './api';

export type {
  // Components
  FileUploadProps,
  URLInputProps,
  ProgressBarProps,
  QuizQuestionProps,
  CourseListProps,
} from './components';

export type {
  // State
  AppState,
  AuthState,
  CoursesState,
  QuizState,
} from './state';

export type {
  // Utils
  Optional,
  Nullable,
  ValidationResult,
  FormState,
} from './utils';

export type {
  // Errors
  AppError,
  ErrorHandler,
  ErrorContext,
} from './errors';

// Type guards
export const isAPIError = (error: unknown): error is import('./api').APIError => {
  return error !== null && typeof error === 'object' && 'success' in error && (error as { success: boolean }).success === false;
};

export const isAppError = (error: unknown): error is import('./errors').AppError => {
  return error !== null && typeof error === 'object' && 'type' in error && 'severity' in error;
};

export const isValidationError = (error: unknown): error is import('./errors').ValidationError => {
  return isAppError(error) && error.type === 'VALIDATION_ERROR';
};

export const isNetworkError = (error: unknown): error is import('./errors').NetworkError => {
  return isAppError(error) && error.type === 'NETWORK_ERROR';
};

// Utility functions
export const createFormState = <T extends Record<string, unknown>>(
  initialValues: T
): import('./utils').FormState<T> => {
  const formState = {} as import('./utils').FormState<T>;
  
  for (const key in initialValues) {
    formState[key] = {
      value: initialValues[key],
      error: undefined,
      touched: false,
      dirty: false,
      valid: true,
    };
  }
  
  return formState;
};

export const createValidationResult = (
  isValid: boolean,
  errors: import('./utils').ValidationError[] = []
): import('./utils').ValidationResult => ({
  isValid,
  errors,
  warnings: [],
});

// Default configurations
export const DEFAULT_APP_CONFIG: import('./utils').AppConfig = {
  apiBaseURL: import.meta.env?.VITE_API_BASE_URL || 'http://localhost:8000',
  apiTimeout: 30000,
  maxFileSize: 20 * 1024 * 1024, // 20MB
  supportedFileTypes: ['.pdf', '.doc', '.docx', '.txt'],
  features: {
    enableAnalytics: false,
    enablePWA: false,
    enableOfflineMode: false,
    enableNotifications: true,
    maxUploadSize: 20 * 1024 * 1024,
    debugMode: import.meta.env?.MODE === 'development',
  },
  theme: {
    primaryColor: '#3b82f6',
    secondaryColor: '#64748b',
    backgroundColor: '#ffffff',
    textColor: '#1f2937',
    borderRadius: '8px',
    fontFamily: 'Inter, system-ui, sans-serif',
  },
  analytics: {
    trackingId: import.meta.env?.VITE_ANALYTICS_ID || '',
    enableAutoTracking: true,
    enableErrorTracking: true,
    sampleRate: 1.0,
  },
};

export const DEFAULT_ERROR_HANDLER_OPTIONS: import('./errors').ErrorHandlerOptions = {
  shouldReport: true,
  shouldNotifyUser: true,
  shouldRetry: false,
  maxRetries: 3,
  retryDelay: 1000,
};