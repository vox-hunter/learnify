// T022: Utility Type Definitions
// Defines reusable TypeScript utility types and helper types

// Generic Utility Types
export type Optional<T, K extends keyof T> = Omit<T, K> & Partial<Pick<T, K>>;
export type RequiredBy<T, K extends keyof T> = Omit<T, K> & Required<Pick<T, K>>;
export type Nullable<T> = T | null;
export type Undefinable<T> = T | undefined;
export type Maybe<T> = T | null | undefined;

// Deep utility types
export type DeepPartial<T> = {
  [P in keyof T]?: T[P] extends object ? DeepPartial<T[P]> : T[P];
};

export type DeepRequired<T> = {
  [P in keyof T]-?: T[P] extends object ? DeepRequired<T[P]> : T[P];
};

export type DeepReadonly<T> = {
  readonly [P in keyof T]: T[P] extends object ? DeepReadonly<T[P]> : T[P];
};

// Function utility types
export type AsyncFunction<T extends unknown[] = unknown[], R = unknown> = (...args: T) => Promise<R>;
export type SyncFunction<T extends unknown[] = unknown[], R = unknown> = (...args: T) => R;
export type EventHandler<T = Event> = (event: T) => void;
export type ValueCallback<T> = (value: T) => void;
export type ErrorCallback = (error: Error) => void;

// Object utility types
export type KeysOfType<T, U> = {
  [K in keyof T]: T[K] extends U ? K : never;
}[keyof T];

export type PickByType<T, U> = Pick<T, KeysOfType<T, U>>;
export type OmitByType<T, U> = Omit<T, KeysOfType<T, U>>;

// Array utility types
export type ArrayElement<ArrayType extends readonly unknown[]> = 
  ArrayType extends readonly (infer ElementType)[] ? ElementType : never;

export type NonEmptyArray<T> = [T, ...T[]];
export type ReadonlyNonEmptyArray<T> = readonly [T, ...readonly T[]];

// String utility types
export type StringKeys<T> = Extract<keyof T, string>;
export type NumberKeys<T> = Extract<keyof T, number>;
export type SymbolKeys<T> = Extract<keyof T, symbol>;

// Validation Types
export interface ValidationResult {
  isValid: boolean;
  errors: ValidationError[];
  warnings?: ValidationWarning[];
}

export interface ValidationError {
  field: string;
  message: string;
  code?: string;
  severity: 'error' | 'warning';
}

export interface ValidationWarning {
  field: string;
  message: string;
  code?: string;
}

export type Validator<T> = (value: T) => ValidationResult;
export type AsyncValidator<T> = (value: T) => Promise<ValidationResult>;

// Form Types
export interface FormField<T = unknown> {
  value: T;
  error?: string;
  touched: boolean;
  dirty: boolean;
  valid: boolean;
}

export type FormState<T extends Record<string, unknown>> = {
  [K in keyof T]: FormField<T[K]>;
};

export interface FormMeta {
  isSubmitting: boolean;
  isValidating: boolean;
  isValid: boolean;
  isDirty: boolean;
  submitCount: number;
  errors: Record<string, string>;
}

// Event Types
export interface CustomEvent<T = unknown> {
  type: string;
  payload: T;
  timestamp: number;
  source?: string;
}

export type EventListener<T = unknown> = (event: CustomEvent<T>) => void;
export type EventMap = Record<string, unknown>;

// Storage Types
export interface StorageItem<T = unknown> {
  value: T;
  timestamp: number;
  expires?: number;
}

export type StorageKey = string;
export type StorageSerializer<T> = {
  serialize: (value: T) => string;
  deserialize: (value: string) => T;
};

// HTTP Types
export type HTTPMethod = 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH' | 'HEAD' | 'OPTIONS';
export type HTTPStatus = number;
export type HTTPHeaders = Record<string, string>;

export interface HTTPRequest {
  url: string;
  method: HTTPMethod;
  headers?: HTTPHeaders;
  body?: unknown;
  timeout?: number;
  retries?: number;
}

export interface HTTPResponse<T = unknown> {
  data: T;
  status: HTTPStatus;
  headers: HTTPHeaders;
  request: HTTPRequest;
}

// Error Types
export interface AppError extends Error {
  code?: string;
  status?: number;
  details?: Record<string, unknown>;
  timestamp: number;
  context?: string;
}

export type ErrorHandler = (error: AppError) => void;
export type ErrorBoundaryFallback = (error: Error, errorInfo: Record<string, unknown>) => React.ReactElement;

// Configuration Types
export interface AppConfig {
  apiBaseURL: string;
  apiTimeout: number;
  maxFileSize: number;
  supportedFileTypes: string[];
  features: FeatureFlags;
  theme: ThemeConfig;
  analytics: AnalyticsConfig;
}

export interface FeatureFlags {
  enableAnalytics: boolean;
  enablePWA: boolean;
  enableOfflineMode: boolean;
  enableNotifications: boolean;
  maxUploadSize: number;
  debugMode: boolean;
}

export interface ThemeConfig {
  primaryColor: string;
  secondaryColor: string;
  backgroundColor: string;
  textColor: string;
  borderRadius: string;
  fontFamily: string;
}

export interface AnalyticsConfig {
  trackingId: string;
  enableAutoTracking: boolean;
  enableErrorTracking: boolean;
  sampleRate: number;
}

// Performance Types
export interface PerformanceMetrics {
  loadTime: number;
  renderTime: number;
  interactionTime: number;
  memoryUsage: number;
  networkLatency: number;
}

export type PerformanceObserver = (metrics: PerformanceMetrics) => void;

// Test Types
export interface TestContext {
  describe: string;
  test: string;
  beforeEach?: () => void;
  afterEach?: () => void;
  cleanup: () => void;
}

export type MockFunction<T extends (...args: unknown[]) => unknown> = 
  T & {
    mockImplementation: (fn: T) => MockFunction<T>;
    mockReturnValue: (value: ReturnType<T>) => MockFunction<T>;
    mockResolvedValue: (value: ReturnType<T>) => MockFunction<T>;
    mockRejectedValue: (error: unknown) => MockFunction<T>;
    mockClear: () => void;
    mockReset: () => void;
    mockRestore: () => void;
  };

// Brand Types (for type safety)
export type Brand<T, B> = T & { __brand: B };
export type UserId = Brand<string, 'UserId'>;
export type CourseId = Brand<string, 'CourseId'>;
export type DocumentId = Brand<string, 'DocumentId'>;
export type QuestionId = Brand<string, 'QuestionId'>;
export type SessionId = Brand<string, 'SessionId'>;

// Conditional Types
export type If<C extends boolean, T, F> = C extends true ? T : F;
export type IsArray<T> = T extends readonly unknown[] ? true : false;
export type IsFunction<T> = T extends (...args: unknown[]) => unknown ? true : false;
export type IsObject<T> = T extends object ? (T extends unknown[] ? false : true) : false;

// Template Literal Types
export type CSSUnit = `${number}${'px' | 'em' | 'rem' | '%' | 'vh' | 'vw'}`;
export type ColorHex = `#${string}`;
export type EmailAddress = `${string}@${string}.${string}`;
export type URLString = `${'http' | 'https'}://${string}`;