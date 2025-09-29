// T027: HTTP Client Configuration with Axios
// Centralized HTTP client with interceptors, error handling, and request/response management

import axios, { type AxiosInstance, type AxiosRequestConfig, type AxiosResponse, type AxiosError } from 'axios';
import type { APIError } from '../types/api';
import { getApiBaseUrl, isDevelopment } from '../utils/env';

/**
 * HTTP Client Configuration
 * Provides a configured Axios instance with interceptors and error handling
 */
class HttpClient {
  private client: AxiosInstance;
  private readonly baseURL: string;
  private refreshPromise: Promise<string | null> | null = null;

  constructor() {
    this.baseURL = getApiBaseUrl();
    
    this.client = axios.create({
      baseURL: this.baseURL,
      timeout: 30000, // 30 second default timeout
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      // Enable cookies for session management
      withCredentials: true
    });

    this.setupInterceptors();
  }

  /**
   * Setup request and response interceptors
   * @private
   */
  private setupInterceptors(): void {
    // Request interceptor
    this.client.interceptors.request.use(
      (config) => {
        // Add request timestamp
        config.metadata = { startTime: Date.now() };
        
        // Log requests in development
        if (isDevelopment()) {
          console.log(`🚀 ${config.method?.toUpperCase()} ${config.url}`, {
            data: config.data,
            params: config.params,
            headers: config.headers
          });
        }

        return config;
      },
      (error) => {
        console.error('Request interceptor error:', error);
        return Promise.reject(this.handleRequestError(error));
      }
    );

    // Response interceptor
    this.client.interceptors.response.use(
      (response) => {
        // Log response time in development
        if (isDevelopment() && response.config.metadata) {
          const duration = Date.now() - response.config.metadata.startTime;
          console.log(`✅ ${response.config.method?.toUpperCase()} ${response.config.url} (${duration}ms)`, {
            status: response.status,
            data: response.data
          });
        }

        return response;
      },
      async (error: AxiosError) => {
        const originalRequest = error.config as AxiosRequestConfig & { _retry?: boolean };

        // Log errors in development
        if (isDevelopment()) {
          console.error(`❌ ${originalRequest?.method?.toUpperCase()} ${originalRequest?.url}`, {
            status: error.response?.status,
            data: error.response?.data,
            message: error.message
          });
        }

        // Handle 401 Unauthorized - attempt token refresh
        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;

          try {
            const newToken = await this.refreshAuthToken();
            if (newToken && originalRequest.headers) {
              originalRequest.headers['Authorization'] = `Bearer ${newToken}`;
              return this.client(originalRequest);
            }
          } catch {
            // Refresh failed - redirect to login
            this.handleAuthFailure();
            return Promise.reject(this.handleResponseError(error));
          }
        }

        return Promise.reject(this.handleResponseError(error));
      }
    );
  }

  /**
   * Refresh authentication token
   * @private
   */
  private async refreshAuthToken(): Promise<string | null> {
    // Prevent multiple simultaneous refresh attempts
    if (this.refreshPromise) {
      return this.refreshPromise;
    }

    this.refreshPromise = new Promise((resolve) => {
      const doRefresh = async () => {
        try {
          const refreshToken = localStorage.getItem('refresh_token') || sessionStorage.getItem('refresh_token');
          if (!refreshToken) {
            resolve(null);
            return;
          }

          const response = await axios.post(`${this.baseURL}/api/auth/refresh`, {
            refreshToken
          });

          const { token, expiresAt } = response.data;
          
          if (token) {
            // Update stored token
            const storage = localStorage.getItem('refresh_token') ? localStorage : sessionStorage;
            storage.setItem('auth_token', token);
            if (expiresAt) {
              storage.setItem('token_expires_at', expiresAt);
            }
            
            // Update default headers
            this.client.defaults.headers.common['Authorization'] = `Bearer ${token}`;
            
            resolve(token);
          } else {
            resolve(null);
          }
        } catch (error) {
          console.error('Token refresh failed:', error);
          resolve(null);
        } finally {
          this.refreshPromise = null;
        }
      };
      doRefresh();
    });

    return this.refreshPromise;
  }

  /**
   * Handle authentication failure
   * @private
   */
  private handleAuthFailure(): void {
    // Clear stored auth data
    ['auth_token', 'refresh_token', 'user_profile', 'token_expires_at'].forEach(key => {
      localStorage.removeItem(key);
      sessionStorage.removeItem(key);
    });

    // Remove auth header
    delete this.client.defaults.headers.common['Authorization'];

    // Emit auth failure event for app to handle
    window.dispatchEvent(new CustomEvent('auth-failure'));
  }

  /**
   * Handle request errors
   * @private
   */
  private handleRequestError(error: unknown): Error {
    if (error instanceof Error) {
      return new Error(`Request failed: ${error.message}`);
    }
    return new Error('Request failed: Unknown error');
  }

  /**
   * Handle response errors
   * @private
   */
  private handleResponseError(error: AxiosError): Error {
    // Network error
    if (!error.response) {
      if (error.code === 'ECONNABORTED') {
        return new Error('Request timeout. Please check your connection and try again.');
      }
      if (error.message.includes('Network Error')) {
        return new Error('Network error. Please check your internet connection.');
      }
      return new Error('Network error. Please try again.');
    }

    // HTTP error responses
    const status = error.response.status;
    const data = error.response.data as APIError | { error?: string; message?: string };

    // Use server-provided error message if available
    const serverMessage = (data as APIError)?.error || 
                         (data as { error?: string })?.error ||
                         (data as { message?: string })?.message;

    if (serverMessage) {
      return new Error(serverMessage);
    }

    // Default error messages based on status code
    switch (status) {
      case 400:
        return new Error('Bad request. Please check your input and try again.');
      case 401:
        return new Error('Authentication required. Please login.');
      case 403:
        return new Error('Access denied. You do not have permission for this action.');
      case 404:
        return new Error('Resource not found.');
      case 409:
        return new Error('Conflict. The resource already exists or has been modified.');
      case 422:
        return new Error('Validation error. Please check your input.');
      case 429:
        return new Error('Too many requests. Please wait a moment and try again.');
      case 500:
        return new Error('Server error. Please try again later.');
      case 502:
        return new Error('Service temporarily unavailable. Please try again later.');
      case 503:
        return new Error('Service unavailable. Please try again later.');
      default:
        return new Error(`Request failed with status ${status}`);
    }
  }

  /**
   * Set authentication token
   * @param token - JWT token
   */
  setAuthToken(token: string): void {
    this.client.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  }

  /**
   * Clear authentication token
   */
  clearAuthToken(): void {
    delete this.client.defaults.headers.common['Authorization'];
  }

  /**
   * Get current base URL
   */
  getBaseURL(): string {
    return this.baseURL;
  }

  /**
   * Update request timeout
   * @param timeout - Timeout in milliseconds
   */
  setTimeout(timeout: number): void {
    this.client.defaults.timeout = timeout;
  }

  /**
   * Add custom header
   * @param key - Header key
   * @param value - Header value
   */
  setHeader(key: string, value: string): void {
    this.client.defaults.headers.common[key] = value;
  }

  /**
   * Remove custom header
   * @param key - Header key
   */
  removeHeader(key: string): void {
    delete this.client.defaults.headers.common[key];
  }

  /**
   * GET request
   */
  async get<T = unknown>(url: string, config?: AxiosRequestConfig): Promise<AxiosResponse<T>> {
    return this.client.get<T>(url, config);
  }

  /**
   * POST request
   */
  async post<T = unknown>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<AxiosResponse<T>> {
    return this.client.post<T>(url, data, config);
  }

  /**
   * PUT request
   */
  async put<T = unknown>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<AxiosResponse<T>> {
    return this.client.put<T>(url, data, config);
  }

  /**
   * PATCH request
   */
  async patch<T = unknown>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<AxiosResponse<T>> {
    return this.client.patch<T>(url, data, config);
  }

  /**
   * DELETE request
   */
  async delete<T = unknown>(url: string, config?: AxiosRequestConfig): Promise<AxiosResponse<T>> {
    return this.client.delete<T>(url, config);
  }

  /**
   * Upload file with progress tracking
   */
  async uploadFile<T = unknown>(
    url: string, 
    file: File, 
    onProgress?: (progress: number) => void,
    additionalData?: Record<string, string>
  ): Promise<AxiosResponse<T>> {
    const formData = new FormData();
    formData.append('file', file);
    
    if (additionalData) {
      Object.entries(additionalData).forEach(([key, value]) => {
        formData.append(key, value);
      });
    }

    return this.client.post<T>(url, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      onUploadProgress: (progressEvent) => {
        if (onProgress && progressEvent.total) {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          onProgress(progress);
        }
      }
    });
  }

  /**
   * Download file
   */
  async downloadFile(url: string, filename?: string): Promise<void> {
    try {
      const response = await this.client.get(url, {
        responseType: 'blob'
      });

      // Create blob URL
      const blob = new Blob([response.data]);
      const blobUrl = window.URL.createObjectURL(blob);

      // Create download link
      const link = document.createElement('a');
      link.href = blobUrl;
      link.download = filename || 'download';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);

      // Clean up
      window.URL.revokeObjectURL(blobUrl);
    } catch (downloadError) {
      console.error('File download failed:', downloadError);
      throw new Error('Failed to download file');
    }
  }

  /**
   * Health check endpoint
   */
  async healthCheck(): Promise<{ status: string; timestamp: string }> {
    try {
      const response = await this.client.get<{ status: string; timestamp: string }>('/health');
      return response.data;
    } catch {
      throw new Error('Health check failed');
    }
  }
}

// Create singleton instance
const httpClient = new HttpClient();

// Export the singleton instance
export { httpClient };

// Export class for testing purposes
export { HttpClient };

// Export types
export type { AxiosRequestConfig, AxiosResponse, AxiosError };

// Extend axios request config to include metadata
declare module 'axios' {
  interface AxiosRequestConfig {
    metadata?: {
      startTime: number;
    };
  }
}