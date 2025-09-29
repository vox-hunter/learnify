/**
 * Environment utilities for accessing Vite environment variables
 * Provides fallback for testing environments
 */

interface ImportMeta {
  env: Record<string, string | boolean | undefined>;
}

declare global {
  interface Window {
    'import.meta'?: ImportMeta;
  }
}

/**
 * Get environment variable with fallback for testing
 */
export const getEnvVar = (key: string, defaultValue?: string): string | undefined => {
  // Check for test environment mock first
  const testEnv = (globalThis as unknown as { 'import.meta'?: ImportMeta })['import.meta']?.env;
  if (testEnv && testEnv[key] !== undefined) {
    return String(testEnv[key]);
  }

  return defaultValue;
};

/**
 * Check if we're in development mode
 */
export const isDevelopment = (): boolean => {
  const mode = getEnvVar('MODE');
  const dev = getEnvVar('DEV');
  return mode === 'development' || dev === 'true' || Boolean(dev);
};

/**
 * Get API base URL
 */
export const getApiBaseUrl = (): string => {
  return getEnvVar('VITE_API_BASE_URL', 'http://localhost:8000') || 'http://localhost:8000';
};