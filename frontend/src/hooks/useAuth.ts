import { useState, useCallback, useEffect } from 'react';
import { authService } from '../services/authService';
import type { LoginRequest, UserProfile } from '../types/api';

interface AuthState {
  user: UserProfile | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  token: string | null;
}

export interface UseAuthReturn extends AuthState {
  login: (credentials: LoginRequest) => Promise<void>;
  logout: () => void;
  register: (userData: { email: string; password: string; name: string; confirmPassword: string }) => Promise<void>;
  refreshToken: () => Promise<void>;
  clearError: () => void;
  updateProfile: (updates: Partial<UserProfile>) => Promise<void>;
}

/**
 * Custom hook for managing authentication state and user sessions
 * Provides centralized auth logic with automatic token refresh
 */
export const useAuth = (): UseAuthReturn => {
  const [state, setState] = useState<AuthState>(() => {
    // Initialize from localStorage if available
    const token = localStorage.getItem('auth_token');
    const userJson = localStorage.getItem('user_profile');
    
    return {
      user: userJson ? JSON.parse(userJson) : null,
      isAuthenticated: !!token,
      isLoading: false,
      error: null,
      token
    };
  });

  const login = useCallback(async (credentials: LoginRequest) => {
    setState(prev => ({ ...prev, isLoading: true, error: null }));

    try {
      const response = await authService.login(credentials.email, credentials.password, credentials.rememberMe);
      
      if (response.success && response.user && response.token) {
        // Store in localStorage if "remember me" is checked
        if (credentials.rememberMe) {
          localStorage.setItem('auth_token', response.token);
          localStorage.setItem('user_profile', JSON.stringify(response.user));
          if (response.refreshToken) {
            localStorage.setItem('refresh_token', response.refreshToken);
          }
        } else {
          // Store in sessionStorage for session-only auth
          sessionStorage.setItem('auth_token', response.token);
          sessionStorage.setItem('user_profile', JSON.stringify(response.user));
          if (response.refreshToken) {
            sessionStorage.setItem('refresh_token', response.refreshToken);
          }
        }

        setState({
          user: response.user,
          isAuthenticated: true,
          isLoading: false,
          error: null,
          token: response.token
        });
      } else {
        setState(prev => ({
          ...prev,
          isLoading: false,
          error: response.error || 'Login failed'
        }));
      }
    } catch (error) {
      setState(prev => ({
        ...prev,
        isLoading: false,
        error: error instanceof Error ? error.message : 'Login failed'
      }));
    }
  }, []);

  const logout = useCallback(() => {
    // Clear all stored auth data
    localStorage.removeItem('auth_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user_profile');
    sessionStorage.removeItem('auth_token');
    sessionStorage.removeItem('refresh_token');
    sessionStorage.removeItem('user_profile');

    setState({
      user: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,
      token: null
    });
  }, []);

  const register = useCallback(async (userData: { email: string; password: string; name: string; confirmPassword: string }) => {
    setState(prev => ({ ...prev, isLoading: true, error: null }));

    try {
      const response = await authService.register(userData);
      
      if (response.success && response.user && response.token) {
        // Auto-login after successful registration
        sessionStorage.setItem('auth_token', response.token);
        sessionStorage.setItem('user_profile', JSON.stringify(response.user));
        
        setState({
          user: response.user,
          isAuthenticated: true,
          isLoading: false,
          error: null,
          token: response.token
        });
      } else {
        setState(prev => ({
          ...prev,
          isLoading: false,
          error: response.error || 'Registration failed'
        }));
      }
    } catch (error) {
      setState(prev => ({
        ...prev,
        isLoading: false,
        error: error instanceof Error ? error.message : 'Registration failed'
      }));
    }
  }, []);

  const refreshToken = useCallback(async () => {
    const refreshToken = localStorage.getItem('refresh_token') || sessionStorage.getItem('refresh_token');
    
    if (!refreshToken) {
      logout();
      return;
    }

    try {
      const response = await authService.refreshToken();
      
      if (response.success && response.token) {
        const isRemembered = !!localStorage.getItem('auth_token');
        const storage = isRemembered ? localStorage : sessionStorage;
        
        storage.setItem('auth_token', response.token);
        
        setState(prev => ({
          ...prev,
          token: response.token || null,
          error: null
        }));
      } else {
        logout();
      }
    } catch {
      logout();
    }
  }, [logout]);

  const updateProfile = useCallback(async (updates: Partial<UserProfile>) => {
    if (!state.user) return;

    setState(prev => ({ ...prev, isLoading: true, error: null }));

    try {
      const updatedUser = await authService.updateProfile(updates);
      
      const isRemembered = !!localStorage.getItem('auth_token');
      const storage = isRemembered ? localStorage : sessionStorage;
      
      storage.setItem('user_profile', JSON.stringify(updatedUser));
      
      setState(prev => ({
        ...prev,
        user: updatedUser,
        isLoading: false
      }));
    } catch (error) {
      setState(prev => ({
        ...prev,
        isLoading: false,
        error: error instanceof Error ? error.message : 'Profile update failed'
      }));
    }
  }, [state.user]);

  const clearError = useCallback(() => {
    setState(prev => ({ ...prev, error: null }));
  }, []);

  // Auto-refresh token when it's close to expiring
  useEffect(() => {
    if (!state.isAuthenticated || !state.token) return;

    const refreshInterval = setInterval(() => {
      refreshToken();
    }, 15 * 60 * 1000); // Refresh every 15 minutes

    return () => clearInterval(refreshInterval);
  }, [state.isAuthenticated, state.token, refreshToken]);

  return {
    ...state,
    login,
    logout,
    register,
    refreshToken,
    clearError,
    updateProfile
  };
};