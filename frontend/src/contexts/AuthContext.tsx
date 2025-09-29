import React, { createContext, useEffect, useState, useCallback } from 'react';
import { authService } from '../services/authService';
import type { UserProfile, LoginRequest } from '../types/api';

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

const AuthContext = createContext<UseAuthReturn | undefined>(undefined);

interface AuthProviderProps {
  children: React.ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
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

  const logout = useCallback(() => {
    // Clear all stored data
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user_profile');
    sessionStorage.removeItem('auth_token');
    sessionStorage.removeItem('user_profile');

    setState({
      user: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,
      token: null
    });

    // Optional: Call backend to invalidate token
    authService.logout().catch(error => {
      console.error('Logout service call failed:', error);
    });
  }, []);

  const refreshToken = useCallback(async () => {
    const currentToken = state.token || localStorage.getItem('auth_token') || sessionStorage.getItem('auth_token');
    
    if (!currentToken) {
      throw new Error('No token available for refresh');
    }

    try {
      const response = await authService.refreshToken();
      
      if (response.success && response.token && response.user) {
        // Update stored token
        const isRemembered = localStorage.getItem('auth_token');
        if (isRemembered) {
          localStorage.setItem('auth_token', response.token);
          localStorage.setItem('user_profile', JSON.stringify(response.user));
        } else {
          sessionStorage.setItem('auth_token', response.token);
          sessionStorage.setItem('user_profile', JSON.stringify(response.user));
        }

        setState(prev => ({
          ...prev,
          user: response.user || null,
          token: response.token || null,
          error: null
        }));
      } else {
        throw new Error(response.error || 'Token refresh failed');
      }
    } catch (error) {
      console.error('Token refresh failed:', error);
      logout();
      throw error;
    }
  }, [state.token, logout]);

  const login = useCallback(async (credentials: LoginRequest) => {
    setState(prev => ({ ...prev, isLoading: true, error: null }));

    try {
      const response = await authService.login(credentials.email, credentials.password, credentials.rememberMe);
      
      if (response.success && response.user && response.token) {
        // Store in localStorage if "remember me" is checked
        if (credentials.rememberMe) {
          localStorage.setItem('auth_token', response.token);
          localStorage.setItem('user_profile', JSON.stringify(response.user));
        } else {
          // Store in sessionStorage for session-only persistence
          sessionStorage.setItem('auth_token', response.token);
          sessionStorage.setItem('user_profile', JSON.stringify(response.user));
        }

        setState({
          user: response.user,
          isAuthenticated: true,
          isLoading: false,
          error: null,
          token: response.token
        });
      } else {
        throw new Error(response.error || 'Login failed');
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Login failed';
      setState(prev => ({
        ...prev,
        isLoading: false,
        error: errorMessage
      }));
      throw error;
    }
  }, []);

  const register = useCallback(async (userData: { email: string; password: string; name: string; confirmPassword: string }) => {
    setState(prev => ({ ...prev, isLoading: true, error: null }));

    try {
      // Validate passwords match
      if (userData.password !== userData.confirmPassword) {
        throw new Error('Passwords do not match');
      }

      const response = await authService.register({ 
        email: userData.email, 
        password: userData.password, 
        name: userData.name,
        confirmPassword: userData.confirmPassword
      });
      
      if (response.success && response.user && response.token) {
        // Auto-login after successful registration
        localStorage.setItem('auth_token', response.token);
        localStorage.setItem('user_profile', JSON.stringify(response.user));

        setState({
          user: response.user,
          isAuthenticated: true,
          isLoading: false,
          error: null,
          token: response.token
        });
      } else {
        throw new Error(response.error || 'Registration failed');
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Registration failed';
      setState(prev => ({
        ...prev,
        isLoading: false,
        error: errorMessage
      }));
      throw error;
    }
  }, []);

  const clearError = useCallback(() => {
    setState(prev => ({ ...prev, error: null }));
  }, []);

  const updateProfile = useCallback(async (updates: Partial<UserProfile>) => {
    if (!state.user) {
      throw new Error('No user logged in');
    }

    setState(prev => ({ ...prev, isLoading: true, error: null }));

    try {
      const updatedUser = await authService.updateProfile(updates);
      
      if (updatedUser) {
        // Update stored user profile
        const userJson = JSON.stringify(updatedUser);
        if (localStorage.getItem('user_profile')) {
          localStorage.setItem('user_profile', userJson);
        }
        if (sessionStorage.getItem('user_profile')) {
          sessionStorage.setItem('user_profile', userJson);
        }

        setState(prev => ({
          ...prev,
          user: updatedUser,
          isLoading: false,
          error: null
        }));
      } else {
        throw new Error('Profile update failed');
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Profile update failed';
      setState(prev => ({
        ...prev,
        isLoading: false,
        error: errorMessage
      }));
      throw error;
    }
  }, [state.user]);

  // Auto-refresh token on app load
  useEffect(() => {
    const initializeAuth = async () => {
      const token = localStorage.getItem('auth_token');
      if (token) {
        try {
          setState(prev => ({ ...prev, isLoading: true }));
          await refreshToken();
        } catch (error) {
          console.error('Failed to refresh token on initialization:', error);
          logout();
        } finally {
          setState(prev => ({ ...prev, isLoading: false }));
        }
      }
    };

    initializeAuth();
  }, [refreshToken, logout]);

  // Set up token refresh interval
  useEffect(() => {
    if (state.isAuthenticated && state.token) {
      // Refresh token every 55 minutes (tokens typically expire in 1 hour)
      const refreshInterval = setInterval(() => {
        refreshToken().catch(error => {
          console.error('Automatic token refresh failed:', error);
          logout();
        });
      }, 55 * 60 * 1000);

      return () => clearInterval(refreshInterval);
    }
  }, [state.isAuthenticated, state.token, refreshToken, logout]);

  const contextValue: UseAuthReturn = {
    ...state,
    login,
    logout,
    register,
    refreshToken,
    clearError,
    updateProfile
  };

  return (
    <AuthContext.Provider value={contextValue}>
      {children}
    </AuthContext.Provider>
  );
};

// Export the context for testing purposes
export { AuthContext };

