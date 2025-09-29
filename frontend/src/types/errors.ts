// T023: Error Handling Types
// Defines TypeScript interfaces for comprehensive error handling

// Base Error Types
export interface BaseError {
  message: string;
  code?: string;
  timestamp: number;
  context?: string;
  stack?: string;
}

export interface AppError extends BaseError {
  type: ErrorType;
  severity: ErrorSeverity;
  retryable: boolean;
  metadata?: Record<string, unknown>;
}

// Error Classification
export type ErrorType = 
  | 'NETWORK_ERROR'
  | 'API_ERROR'
  | 'VALIDATION_ERROR'
  | 'AUTHENTICATION_ERROR'
  | 'AUTHORIZATION_ERROR'
  | 'FILE_ERROR'
  | 'STORAGE_ERROR'
  | 'PARSING_ERROR'
  | 'TIMEOUT_ERROR'
  | 'UNKNOWN_ERROR';

export type ErrorSeverity = 'low' | 'medium' | 'high' | 'critical';

// Specific Error Types
export interface NetworkError extends AppError {
  type: 'NETWORK_ERROR';
  status?: number;
  statusText?: string;
  url?: string;
  method?: string;
}

export interface APIError extends AppError {
  type: 'API_ERROR';
  endpoint: string;
  method: string;
  status: number;
  response?: unknown;
  requestId?: string;
}

export interface ValidationError extends AppError {
  type: 'VALIDATION_ERROR';
  field: string;
  value: unknown;
  constraints: string[];
  children?: ValidationError[];
}

export interface AuthenticationError extends AppError {
  type: 'AUTHENTICATION_ERROR';
  reason: 'invalid_credentials' | 'token_expired' | 'token_invalid' | 'session_expired';
  redirectTo?: string;
}

export interface AuthorizationError extends AppError {
  type: 'AUTHORIZATION_ERROR';
  resource: string;
  action: string;
  requiredPermissions: string[];
  userPermissions: string[];
}

export interface FileError extends AppError {
  type: 'FILE_ERROR';
  fileName: string;
  fileSize?: number;
  fileType?: string;
  reason: 'invalid_type' | 'too_large' | 'corrupted' | 'not_found' | 'permission_denied';
}

export interface StorageError extends AppError {
  type: 'STORAGE_ERROR';
  operation: 'read' | 'write' | 'delete' | 'clear';
  key?: string;
  storage: 'localStorage' | 'sessionStorage' | 'indexedDB' | 'memory';
}

export interface ParsingError extends AppError {
  type: 'PARSING_ERROR';
  input: string;
  format: 'json' | 'xml' | 'csv' | 'yaml' | 'html' | 'markdown';
  line?: number;
  column?: number;
}

export interface TimeoutError extends AppError {
  type: 'TIMEOUT_ERROR';
  operation: string;
  timeout: number;
  elapsed: number;
}

// Error Context Types
export interface ErrorContext {
  userId?: string;
  sessionId?: string;
  route?: string;
  component?: string;
  action?: string;
  userAgent?: string;
  timestamp: number;
  environment: 'development' | 'staging' | 'production';
}

export interface ErrorBoundaryState {
  hasError: boolean;
  error?: Error;
  errorInfo?: Record<string, unknown>;
  errorId?: string;
}

export interface ErrorBoundaryProps {
  fallback?: (error: Error, errorInfo: Record<string, unknown>, retry: () => void) => React.ReactElement;
  onError?: (error: Error, errorInfo: Record<string, unknown>) => void;
  enableRetry?: boolean;
  maxRetries?: number;
  children: React.ReactNode;
}

// Error Handler Types
export type ErrorHandler = (error: AppError, context?: ErrorContext) => void;
export type AsyncErrorHandler = (error: AppError, context?: ErrorContext) => Promise<void>;

export interface ErrorHandlerOptions {
  shouldReport: boolean;
  shouldNotifyUser: boolean;
  shouldRetry: boolean;
  maxRetries: number;
  retryDelay: number;
  fallbackAction?: () => void;
}

export interface ErrorReporter {
  report: (error: AppError, context?: ErrorContext) => Promise<void>;
  configure: (options: ErrorReporterConfig) => void;
}

export interface ErrorReporterConfig {
  apiEndpoint: string;
  apiKey: string;
  environment: string;
  userId?: string;
  sessionId?: string;
  enableConsoleLogging: boolean;
  enableRemoteLogging: boolean;
  samplingRate: number;
}

// Error Recovery Types
export interface ErrorRecoveryStrategy {
  canRecover: (error: AppError) => boolean;
  recover: (error: AppError, context?: ErrorContext) => Promise<boolean>;
  getRecoveryMessage: (error: AppError) => string;
}

export interface RetryStrategy {
  shouldRetry: (error: AppError, attemptCount: number) => boolean;
  getDelay: (attemptCount: number) => number;
  maxAttempts: number;
}

export interface FallbackStrategy {
  canFallback: (error: AppError) => boolean;
  fallback: (error: AppError, context?: ErrorContext) => unknown;
  getFallbackMessage: (error: AppError) => string;
}

// Error Notification Types
export interface ErrorNotification {
  id: string;
  error: AppError;
  title: string;
  message: string;
  actions: ErrorNotificationAction[];
  dismissible: boolean;
  autoHide: boolean;
  duration?: number;
}

export interface ErrorNotificationAction {
  label: string;
  action: () => void;
  style: 'primary' | 'secondary' | 'danger';
}

// Error Analytics Types
export interface ErrorMetrics {
  totalErrors: number;
  errorsByType: Record<ErrorType, number>;
  errorsBySeverity: Record<ErrorSeverity, number>;
  errorRate: number;
  averageResolutionTime: number;
  topErrors: ErrorStatistic[];
}

export interface ErrorStatistic {
  error: string;
  count: number;
  percentage: number;
  lastOccurrence: number;
  firstOccurrence: number;
}

export interface ErrorTracking {
  track: (error: AppError, context?: ErrorContext) => void;
  getMetrics: (timeRange?: DateRange) => Promise<ErrorMetrics>;
  getErrorHistory: (errorType?: ErrorType) => Promise<ErrorHistoryItem[]>;
}

export interface ErrorHistoryItem {
  id: string;
  error: AppError;
  context: ErrorContext;
  resolved: boolean;
  resolvedAt?: number;
  resolution?: string;
}

export interface DateRange {
  start: Date;
  end: Date;
}

// Error Debugging Types
export interface DebugInfo {
  errorId: string;
  error: AppError;
  context: ErrorContext;
  stackTrace: string;
  breadcrumbs: Breadcrumb[];
  userActions: UserAction[];
  systemInfo: SystemInfo;
}

export interface Breadcrumb {
  timestamp: number;
  category: 'navigation' | 'user' | 'http' | 'error' | 'info';
  message: string;
  data?: Record<string, unknown>;
  level: 'debug' | 'info' | 'warning' | 'error';
}

export interface UserAction {
  timestamp: number;
  type: 'click' | 'input' | 'navigation' | 'api_call';
  target: string;
  data?: Record<string, unknown>;
}

export interface SystemInfo {
  userAgent: string;
  platform: string;
  language: string;
  screenResolution: string;
  availableMemory?: number;
  connectionType?: string;
  timestamp: number;
}

// Error Testing Types
export interface ErrorSimulator {
  simulateNetworkError: (status?: number) => void;
  simulateAPIError: (endpoint: string, error: unknown) => void;
  simulateValidationError: (field: string, message: string) => void;
  simulateFileError: (fileName: string, reason: string) => void;
  simulateTimeout: (operation: string, delay: number) => void;
  reset: () => void;
}

export interface MockErrorHandler {
  errors: AppError[];
  handleError: ErrorHandler;
  getLastError: () => AppError | undefined;
  getErrorCount: () => number;
  clearErrors: () => void;
}

// Utility Types
export type ErrorFactory<T extends AppError> = (message: string, options?: Partial<T>) => T;
export type ErrorMatcher = (error: AppError) => boolean;
export type ErrorTransformer = (error: unknown) => AppError;
export type ErrorFilter = (error: AppError) => boolean;

// Constants
export const ERROR_CODES = {
  // Network Errors
  NETWORK_UNREACHABLE: 'NETWORK_001',
  CONNECTION_TIMEOUT: 'NETWORK_002',
  REQUEST_FAILED: 'NETWORK_003',
  
  // API Errors
  BAD_REQUEST: 'API_001',
  UNAUTHORIZED: 'API_002',
  FORBIDDEN: 'API_003',
  NOT_FOUND: 'API_004',
  INTERNAL_SERVER_ERROR: 'API_005',
  
  // Validation Errors
  REQUIRED_FIELD: 'VALIDATION_001',
  INVALID_FORMAT: 'VALIDATION_002',
  OUT_OF_RANGE: 'VALIDATION_003',
  
  // File Errors
  INVALID_FILE_TYPE: 'FILE_001',
  FILE_TOO_LARGE: 'FILE_002',
  FILE_CORRUPTED: 'FILE_003',
  
  // Storage Errors
  STORAGE_FULL: 'STORAGE_001',
  STORAGE_UNAVAILABLE: 'STORAGE_002',
  STORAGE_QUOTA_EXCEEDED: 'STORAGE_003',
} as const;

export type ErrorCode = typeof ERROR_CODES[keyof typeof ERROR_CODES];