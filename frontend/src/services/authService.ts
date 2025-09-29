// T026: Authentication Service API Calls
// Handles all authentication-related API operations including login, logout, and session management

import type {
  LoginRequest,
  LoginResponse,
  UserProfile
} from '../types/api';
import { httpClient } from './httpClient';

/**
 * Authentication Service - Manages user authentication and session state
 */
export class AuthService {
  private static readonly ENDPOINTS = {
    LOGIN: '/api/auth/login',
    LOGOUT: '/api/auth/logout',
    REGISTER: '/api/auth/register',
    REFRESH: '/api/auth/refresh',
    PROFILE: '/api/auth/profile',
    UPDATE_PROFILE: '/api/auth/profile',
    CHANGE_PASSWORD: '/api/auth/password',
    FORGOT_PASSWORD: '/api/auth/forgot-password',
    RESET_PASSWORD: '/api/auth/reset-password',
    VERIFY_EMAIL: '/api/auth/verify-email'
  } as const;

  private static readonly STORAGE_KEYS = {
    TOKEN: 'auth_token',
    REFRESH_TOKEN: 'refresh_token',
    USER: 'user_profile',
    EXPIRES_AT: 'token_expires_at'
  } as const;

  /**
   * Login user with email and password
   * @param email - User email
   * @param password - User password
   * @param rememberMe - Whether to persist login
   * @returns Promise with login response
   */
  static async login(email: string, password: string, rememberMe: boolean = false): Promise<LoginResponse> {
    try {
      const request: LoginRequest = {
        email: email.toLowerCase().trim(),
        password,
        rememberMe
      };

      const response = await httpClient.post<LoginResponse>(
        this.ENDPOINTS.LOGIN,
        request
      );

      const loginData = response.data;

      if (loginData.success && loginData.token && loginData.user) {
        // Store authentication data
        this.storeAuthData(loginData, rememberMe);
        
        // Update HTTP client with new token
        this.setAuthToken(loginData.token);
      }

      return loginData;
    } catch (error) {
      console.error('Login failed:', error);
      throw this.handleApiError(error, 'Login failed. Please check your credentials.');
    }
  }

  /**
   * Register new user account
   * @param userData - User registration data
   * @returns Promise with registration response
   */
  static async register(userData: {
    name: string;
    email: string;
    password: string;
    confirmPassword: string;
  }): Promise<LoginResponse> {
    try {
      const request = {
        name: userData.name.trim(),
        email: userData.email.toLowerCase().trim(),
        password: userData.password,
        confirmPassword: userData.confirmPassword
      };

      const response = await httpClient.post<LoginResponse>(
        this.ENDPOINTS.REGISTER,
        request
      );

      const registrationData = response.data;

      if (registrationData.success && registrationData.token && registrationData.user) {
        // Store authentication data
        this.storeAuthData(registrationData, false);
        
        // Update HTTP client with new token
        this.setAuthToken(registrationData.token);
      }

      return registrationData;
    } catch (error) {
      console.error('Registration failed:', error);
      throw this.handleApiError(error, 'Registration failed. Please try again.');
    }
  }

  /**
   * Logout current user
   * @returns Promise with logout confirmation
   */
  static async logout(): Promise<{ success: boolean }> {
    try {
      const response = await httpClient.post<{ success: boolean }>(
        this.ENDPOINTS.LOGOUT
      );

      // Clear stored authentication data
      this.clearAuthData();
      
      // Remove token from HTTP client
      this.clearAuthToken();

      return response.data;
    } catch (error) {
      // Even if logout fails on server, clear local data
      this.clearAuthData();
      this.clearAuthToken();
      
      console.error('Logout error:', error);
      return { success: true }; // Consider logout successful locally
    }
  }

  /**
   * Refresh authentication token
   * @returns Promise with new token data
   */
  static async refreshToken(): Promise<LoginResponse> {
    try {
      const refreshToken = this.getStoredRefreshToken();
      if (!refreshToken) {
        throw new Error('No refresh token available');
      }

      const response = await httpClient.post<LoginResponse>(
        this.ENDPOINTS.REFRESH,
        { refreshToken }
      );

      const refreshData = response.data;

      if (refreshData.success && refreshData.token) {
        // Update stored token data
        this.updateStoredToken(refreshData.token, refreshData.expiresAt);
        
        // Update HTTP client with new token
        this.setAuthToken(refreshData.token);
      }

      return refreshData;
    } catch (error) {
      console.error('Token refresh failed:', error);
      // Clear invalid tokens
      this.clearAuthData();
      this.clearAuthToken();
      throw this.handleApiError(error, 'Session expired. Please login again.');
    }
  }

  /**
   * Get current user profile
   * @returns Promise with user profile
   */
  static async getProfile(): Promise<UserProfile> {
    try {
      const response = await httpClient.get<UserProfile>(
        this.ENDPOINTS.PROFILE
      );

      const profile = response.data;
      
      // Update stored user data
      this.updateStoredUser(profile);

      return profile;
    } catch (error) {
      console.error('Failed to get profile:', error);
      throw this.handleApiError(error, 'Failed to load user profile');
    }
  }

  /**
   * Update user profile
   * @param updates - Profile updates
   * @returns Promise with updated profile
   */
  static async updateProfile(updates: Partial<UserProfile>): Promise<UserProfile> {
    try {
      const response = await httpClient.put<UserProfile>(
        this.ENDPOINTS.UPDATE_PROFILE,
        updates
      );

      const updatedProfile = response.data;
      
      // Update stored user data
      this.updateStoredUser(updatedProfile);

      return updatedProfile;
    } catch (error) {
      console.error('Failed to update profile:', error);
      throw this.handleApiError(error, 'Failed to update profile');
    }
  }

  /**
   * Change user password
   * @param currentPassword - Current password
   * @param newPassword - New password
   * @returns Promise with change confirmation
   */
  static async changePassword(currentPassword: string, newPassword: string): Promise<{ success: boolean }> {
    try {
      const response = await httpClient.post<{ success: boolean }>(
        this.ENDPOINTS.CHANGE_PASSWORD,
        {
          currentPassword,
          newPassword
        }
      );

      return response.data;
    } catch (error) {
      console.error('Failed to change password:', error);
      throw this.handleApiError(error, 'Failed to change password');
    }
  }

  /**
   * Request password reset email
   * @param email - User email
   * @returns Promise with reset confirmation
   */
  static async forgotPassword(email: string): Promise<{ success: boolean; message: string }> {
    try {
      const response = await httpClient.post<{ success: boolean; message: string }>(
        this.ENDPOINTS.FORGOT_PASSWORD,
        { email: email.toLowerCase().trim() }
      );

      return response.data;
    } catch (error) {
      console.error('Failed to request password reset:', error);
      throw this.handleApiError(error, 'Failed to send password reset email');
    }
  }

  /**
   * Reset password with token
   * @param token - Reset token
   * @param newPassword - New password
   * @returns Promise with reset confirmation
   */
  static async resetPassword(token: string, newPassword: string): Promise<{ success: boolean }> {
    try {
      const response = await httpClient.post<{ success: boolean }>(
        this.ENDPOINTS.RESET_PASSWORD,
        {
          token,
          newPassword
        }
      );

      return response.data;
    } catch (error) {
      console.error('Failed to reset password:', error);
      throw this.handleApiError(error, 'Failed to reset password');
    }
  }

  /**
   * Check if user is currently authenticated
   * @returns Boolean indicating authentication status
   */
  static isAuthenticated(): boolean {
    const token = this.getStoredToken();
    const expiresAt = this.getStoredTokenExpiry();
    
    if (!token || !expiresAt) {
      return false;
    }

    // Check if token is expired
    if (Date.now() > new Date(expiresAt).getTime()) {
      this.clearAuthData();
      return false;
    }

    return true;
  }

  /**
   * Get stored user profile
   * @returns User profile or null
   */
  static getStoredUser(): UserProfile | null {
    try {
      const userJson = localStorage.getItem(this.STORAGE_KEYS.USER) ||
                      sessionStorage.getItem(this.STORAGE_KEYS.USER);
      return userJson ? JSON.parse(userJson) : null;
    } catch {
      return null;
    }
  }

  /**
   * Get stored authentication token
   * @returns Token string or null
   */
  static getStoredToken(): string | null {
    return localStorage.getItem(this.STORAGE_KEYS.TOKEN) ||
           sessionStorage.getItem(this.STORAGE_KEYS.TOKEN);
  }

  /**
   * Get stored refresh token
   * @returns Refresh token string or null
   */
  private static getStoredRefreshToken(): string | null {
    return localStorage.getItem(this.STORAGE_KEYS.REFRESH_TOKEN) ||
           sessionStorage.getItem(this.STORAGE_KEYS.REFRESH_TOKEN);
  }

  /**
   * Get stored token expiry
   * @returns Expiry date string or null
   */
  private static getStoredTokenExpiry(): string | null {
    return localStorage.getItem(this.STORAGE_KEYS.EXPIRES_AT) ||
           sessionStorage.getItem(this.STORAGE_KEYS.EXPIRES_AT);
  }

  /**
   * Store authentication data
   * @private
   */
  private static storeAuthData(data: LoginResponse, persistent: boolean): void {
    const storage = persistent ? localStorage : sessionStorage;

    if (data.token) {
      storage.setItem(this.STORAGE_KEYS.TOKEN, data.token);
    }
    
    if (data.refreshToken) {
      storage.setItem(this.STORAGE_KEYS.REFRESH_TOKEN, data.refreshToken);
    }
    
    if (data.user) {
      storage.setItem(this.STORAGE_KEYS.USER, JSON.stringify(data.user));
    }
    
    if (data.expiresAt) {
      storage.setItem(this.STORAGE_KEYS.EXPIRES_AT, data.expiresAt);
    }
  }

  /**
   * Update stored token data
   * @private
   */
  private static updateStoredToken(token: string, expiresAt?: string): void {
    const hasLocalStorage = localStorage.getItem(this.STORAGE_KEYS.TOKEN);
    const storage = hasLocalStorage ? localStorage : sessionStorage;

    storage.setItem(this.STORAGE_KEYS.TOKEN, token);
    if (expiresAt) {
      storage.setItem(this.STORAGE_KEYS.EXPIRES_AT, expiresAt);
    }
  }

  /**
   * Update stored user data
   * @private
   */
  private static updateStoredUser(user: UserProfile): void {
    const hasLocalStorage = localStorage.getItem(this.STORAGE_KEYS.USER);
    const storage = hasLocalStorage ? localStorage : sessionStorage;

    storage.setItem(this.STORAGE_KEYS.USER, JSON.stringify(user));
  }

  /**
   * Clear all stored authentication data
   * @private
   */
  private static clearAuthData(): void {
    // Clear from both storages
    Object.values(this.STORAGE_KEYS).forEach(key => {
      localStorage.removeItem(key);
      sessionStorage.removeItem(key);
    });
  }

  /**
   * Set authentication token in HTTP client
   * @private
   */
  private static setAuthToken(token: string): void {
    httpClient.setAuthToken(token);
  }

  /**
   * Clear authentication token from HTTP client
   * @private
   */
  private static clearAuthToken(): void {
    httpClient.clearAuthToken();
  }

  /**
   * Initialize authentication from stored data
   * Call this on app startup
   */
  static initializeAuth(): void {
    const token = this.getStoredToken();
    if (token && this.isAuthenticated()) {
      this.setAuthToken(token);
    } else {
      this.clearAuthData();
    }
  }

  /**
   * Validate email format
   * @param email - Email to validate
   * @returns Validation result
   */
  static validateEmail(email: string): { isValid: boolean; error?: string } {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    
    if (!email.trim()) {
      return { isValid: false, error: 'Email is required' };
    }
    
    if (!emailRegex.test(email.trim())) {
      return { isValid: false, error: 'Please enter a valid email address' };
    }
    
    return { isValid: true };
  }

  /**
   * Validate password strength
   * @param password - Password to validate
   * @returns Validation result
   */
  static validatePassword(password: string): { isValid: boolean; error?: string } {
    if (!password) {
      return { isValid: false, error: 'Password is required' };
    }
    
    if (password.length < 8) {
      return { isValid: false, error: 'Password must be at least 8 characters long' };
    }
    
    if (!/(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/.test(password)) {
      return { isValid: false, error: 'Password must contain at least one uppercase letter, one lowercase letter, and one number' };
    }
    
    return { isValid: true };
  }

  /**
   * Handle API errors with user-friendly messages
   * @private
   */
  private static handleApiError(error: unknown, defaultMessage: string): Error {
    if (error instanceof Error) {
      return error;
    }
    
    // Handle Axios errors
    if (typeof error === 'object' && error !== null && 'response' in error) {
      const axiosError = error as { response?: { data?: { error?: string; message?: string } } };
      const serverMessage = axiosError.response?.data?.error || axiosError.response?.data?.message;
      if (serverMessage) {
        return new Error(serverMessage);
      }
    }

    return new Error(defaultMessage);
  }
}

// Export singleton instance for convenience
export const authService = AuthService;

// Export types for external use
export type { LoginRequest, LoginResponse, UserProfile };