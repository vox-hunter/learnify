/**
 * API Helpers and Error Handling Utilities
 * Provides comprehensive API interaction and error management
 */

import axios, { AxiosError } from 'axios';
import type { AxiosRequestConfig } from 'axios';
import { getEnvVar } from './env';

declare module 'axios' {
  interface AxiosRequestConfig {
    skipAuth?: boolean;
  }
}

/**
 * API Error types
 */
export class APIError extends Error {
  public status: number;
  public code?: string;
  public details?: unknown;

  constructor(message: string, status: number, code?: string, details?: unknown) {
    super(message);
    this.name = 'APIError';
    this.status = status;
    this.code = code;
    this.details = details;
  }
}

export interface APIErrorResponse {
  message: string;
  code?: string;
  details?: unknown;
  errors?: Record<string, string[]>;
}

/**
 * HTTP Status Code Constants
 */
export const HTTP_STATUS = {
  OK: 200,
  CREATED: 201,
  NO_CONTENT: 204,
  BAD_REQUEST: 400,
  UNAUTHORIZED: 401,
  FORBIDDEN: 403,
  NOT_FOUND: 404,
  METHOD_NOT_ALLOWED: 405,
  CONFLICT: 409,
  UNPROCESSABLE_ENTITY: 422,
  TOO_MANY_REQUESTS: 429,
  INTERNAL_SERVER_ERROR: 500,
  BAD_GATEWAY: 502,
  SERVICE_UNAVAILABLE: 503,
  GATEWAY_TIMEOUT: 504,
} as const;

/**
 * Request/Response types
 */
export interface APIResponse<T = unknown> {
  data: T;
  message?: string;
  success: boolean;
}

export interface PaginatedResponse<T = unknown> {
  data: T[];
  pagination: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
    hasNext: boolean;
    hasPrev: boolean;
  };
}

export interface APIRequestConfig extends AxiosRequestConfig {
  skipAuth?: boolean;
  retries?: number;
  retryDelay?: number;
  timeout?: number;
}

/**
 * Create axios instance with base configuration
 */
const createAPIClient = () => {
  const client = axios.create({
    baseURL: getEnvVar('VITE_API_BASE_URL', 'http://localhost:8000/api'),
    timeout: 30000,
    headers: {
      'Content-Type': 'application/json',
    },
  });

  // Request interceptor for auth tokens
  client.interceptors.request.use(
    (config) => {
      const token = localStorage.getItem('authToken');
      if (token && !config.skipAuth) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    },
    (error) => Promise.reject(error)
  );

  // Response interceptor for error handling
  client.interceptors.response.use(
    (response) => response,
    async (error: AxiosError) => {
      if (error.response?.status === HTTP_STATUS.UNAUTHORIZED) {
        // Try to refresh token
        try {
          await refreshToken();
          // Retry original request
          return client.request(error.config!);
        } catch {
          // Redirect to login if refresh fails
          localStorage.removeItem('authToken');
          localStorage.removeItem('refreshToken');
          window.location.href = '/login';
          return Promise.reject(error);
        }
      }
      return Promise.reject(error);
    }
  );

  return client;
};

export const apiClient = createAPIClient();

/**
 * Refresh token helper
 */
const refreshToken = async (): Promise<string> => {
  const refreshToken = localStorage.getItem('refreshToken');
  if (!refreshToken) {
    throw new APIError('No refresh token available', HTTP_STATUS.UNAUTHORIZED);
  }

  const response = await axios.post(
    `${getEnvVar('VITE_API_BASE_URL')}/auth/refresh`,
    { refreshToken },
    { skipAuth: true } as APIRequestConfig
  );

  const { accessToken, refreshToken: newRefreshToken } = response.data;
  localStorage.setItem('authToken', accessToken);
  localStorage.setItem('refreshToken', newRefreshToken);

  return accessToken;
};

/**
 * Error parsing utility
 */
export const parseAPIError = (error: unknown): APIError => {
  if (error instanceof APIError) {
    return error;
  }

  if (axios.isAxiosError(error)) {
    const response = error.response;
    const status = response?.status || HTTP_STATUS.INTERNAL_SERVER_ERROR;
    
    if (response?.data) {
      const errorData = response.data as APIErrorResponse;
      return new APIError(
        errorData.message || error.message,
        status,
        errorData.code,
        errorData.details || errorData.errors
      );
    }

    return new APIError(error.message, status);
  }

  if (error instanceof Error) {
    return new APIError(error.message, HTTP_STATUS.INTERNAL_SERVER_ERROR);
  }

  return new APIError('Unknown error occurred', HTTP_STATUS.INTERNAL_SERVER_ERROR);
};

/**
 * Retry mechanism for failed requests
 */
export const withRetry = async <T>(
  fn: () => Promise<T>,
  maxRetries = 3,
  delayMs = 1000,
  backoffMultiplier = 2
): Promise<T> => {
  let lastError: unknown;

  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error;
      
      if (attempt === maxRetries) {
        break;
      }

      // Don't retry on client errors (4xx)
      if (axios.isAxiosError(error) && error.response?.status && error.response.status < 500) {
        break;
      }

      // Wait before retry with exponential backoff
      await new Promise(resolve => 
        setTimeout(resolve, delayMs * Math.pow(backoffMultiplier, attempt))
      );
    }
  }

  throw parseAPIError(lastError);
};

/**
 * Generic API methods
 */
export const apiMethods = {
  get: async <T>(url: string, config?: APIRequestConfig): Promise<T> => {
    try {
      const response = await apiClient.get<APIResponse<T>>(url, config);
      return response.data.data;
    } catch (error) {
      throw parseAPIError(error);
    }
  },

  post: async <T, D = unknown>(url: string, data?: D, config?: APIRequestConfig): Promise<T> => {
    try {
      const response = await apiClient.post<APIResponse<T>>(url, data, config);
      return response.data.data;
    } catch (error) {
      throw parseAPIError(error);
    }
  },

  put: async <T, D = unknown>(url: string, data?: D, config?: APIRequestConfig): Promise<T> => {
    try {
      const response = await apiClient.put<APIResponse<T>>(url, data, config);
      return response.data.data;
    } catch (error) {
      throw parseAPIError(error);
    }
  },

  patch: async <T, D = unknown>(url: string, data?: D, config?: APIRequestConfig): Promise<T> => {
    try {
      const response = await apiClient.patch<APIResponse<T>>(url, data, config);
      return response.data.data;
    } catch (error) {
      throw parseAPIError(error);
    }
  },

  delete: async <T>(url: string, config?: APIRequestConfig): Promise<T> => {
    try {
      const response = await apiClient.delete<APIResponse<T>>(url, config);
      return response.data.data;
    } catch (error) {
      throw parseAPIError(error);
    }
  },

  upload: async <T>(
    url: string, 
    file: File, 
    onProgress?: (progress: number) => void,
    config?: APIRequestConfig
  ): Promise<T> => {
    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await apiClient.post<APIResponse<T>>(url, formData, {
        ...config,
        headers: {
          ...config?.headers,
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          if (onProgress && progressEvent.total) {
            const progress = Math.round((progressEvent.loaded / progressEvent.total) * 100);
            onProgress(progress);
          }
        },
      });

      return response.data.data;
    } catch (error) {
      throw parseAPIError(error);
    }
  },

  download: async (url: string, filename?: string, config?: APIRequestConfig): Promise<void> => {
    try {
      const response = await apiClient.get(url, {
        ...config,
        responseType: 'blob',
      });

      const blob = new Blob([response.data]);
      const downloadUrl = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = downloadUrl;
      link.download = filename || 'download';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(downloadUrl);
    } catch (error) {
      throw parseAPIError(error);
    }
  },
};

/**
 * Pagination helper
 */
export const getPaginatedData = async <T>(
  url: string,
  page = 1,
  limit = 10,
  config?: APIRequestConfig
): Promise<PaginatedResponse<T>> => {
  try {
    const response = await apiClient.get<PaginatedResponse<T>>(url, {
      ...config,
      params: {
        ...config?.params,
        page,
        limit,
      },
    });
    return response.data;
  } catch (error) {
    throw parseAPIError(error);
  }
};

/**
 * Query parameter builder
 */
export const buildQueryParams = (params: Record<string, unknown>): string => {
  const searchParams = new URLSearchParams();
  
  Object.entries(params).forEach(([key, value]) => {
    if (value !== null && value !== undefined && value !== '') {
      if (Array.isArray(value)) {
        value.forEach(item => searchParams.append(key, String(item)));
      } else {
        searchParams.append(key, String(value));
      }
    }
  });

  return searchParams.toString();
};

/**
 * Response caching utility
 */
const cache = new Map<string, { data: unknown; timestamp: number; ttl: number }>();

export const getCachedResponse = <T>(key: string): T | null => {
  const cached = cache.get(key);
  if (!cached) return null;

  const now = Date.now();
  if (now - cached.timestamp > cached.ttl) {
    cache.delete(key);
    return null;
  }

  return cached.data as T;
};

export const setCachedResponse = <T>(key: string, data: T, ttlMs = 300000): void => {
  cache.set(key, {
    data,
    timestamp: Date.now(),
    ttl: ttlMs,
  });
};

export const clearCache = (pattern?: string): void => {
  if (pattern) {
    const regex = new RegExp(pattern);
    for (const key of cache.keys()) {
      if (regex.test(key)) {
        cache.delete(key);
      }
    }
  } else {
    cache.clear();
  }
};

/**
 * Request cancellation utility
 */
export const createCancelToken = () => {
  const controller = new AbortController();
  return {
    token: controller.signal,
    cancel: (reason?: string) => controller.abort(reason),
  };
};

/**
 * API status checker
 */
export const checkAPIHealth = async (): Promise<boolean> => {
  try {
    await apiClient.get('/health', { 
      timeout: 5000,
      skipAuth: true,
    } as APIRequestConfig);
    return true;
  } catch {
    return false;
  }
};

/**
 * Error message helpers
 */
export const getErrorMessage = (error: unknown): string => {
  const apiError = parseAPIError(error);
  
  switch (apiError.status) {
    case HTTP_STATUS.BAD_REQUEST:
      return 'Invalid request. Please check your input.';
    case HTTP_STATUS.UNAUTHORIZED:
      return 'You are not authorized to perform this action.';
    case HTTP_STATUS.FORBIDDEN:
      return 'Access denied.';
    case HTTP_STATUS.NOT_FOUND:
      return 'The requested resource was not found.';
    case HTTP_STATUS.CONFLICT:
      return 'A conflict occurred. The resource may already exist.';
    case HTTP_STATUS.UNPROCESSABLE_ENTITY:
      return 'Validation failed. Please check your input.';
    case HTTP_STATUS.TOO_MANY_REQUESTS:
      return 'Too many requests. Please try again later.';
    case HTTP_STATUS.INTERNAL_SERVER_ERROR:
      return 'Internal server error. Please try again later.';
    case HTTP_STATUS.SERVICE_UNAVAILABLE:
      return 'Service temporarily unavailable. Please try again later.';
    default:
      return apiError.message || 'An unexpected error occurred.';
  }
};

export const getValidationErrors = (error: unknown): Record<string, string[]> => {
  const apiError = parseAPIError(error);
  
  if (apiError.status === HTTP_STATUS.UNPROCESSABLE_ENTITY && apiError.details) {
    return apiError.details as Record<string, string[]>;
  }
  
  return {};
};

/**
 * Network status utilities
 */
export const isOnline = (): boolean => navigator.onLine;

export const waitForConnection = (): Promise<void> => {
  return new Promise((resolve) => {
    if (isOnline()) {
      resolve();
      return;
    }

    const handleOnline = () => {
      window.removeEventListener('online', handleOnline);
      resolve();
    };

    window.addEventListener('online', handleOnline);
  });
};

/**
 * API method with automatic retry and caching
 */
export const createAPIMethod = <T, P extends unknown[] = []>(
  method: (...args: P) => Promise<T>,
  options: {
    retries?: number;
    cacheKey?: (...args: P) => string;
    cacheTTL?: number;
  } = {}
) => {
  const { retries = 3, cacheKey, cacheTTL = 300000 } = options;

  return async (...args: P): Promise<T> => {
    // Check cache first
    if (cacheKey) {
      const key = cacheKey(...args);
      const cached = getCachedResponse<T>(key);
      if (cached) return cached;
    }

    // Execute with retry
    const result = await withRetry(() => method(...args), retries);

    // Cache result
    if (cacheKey) {
      const key = cacheKey(...args);
      setCachedResponse(key, result, cacheTTL);
    }

    return result;
  };
};