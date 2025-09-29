import React from 'react';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import { AuthProvider } from '../AuthContext';
import { useAuthContext } from '../../hooks/useAuthContext';
import { authService } from '../../services/authService';
import type { UserProfile } from '../../types/api';
import '@testing-library/jest-dom';

// Mock authService
jest.mock('../../services/authService');
const mockAuthService = authService as jest.Mocked<typeof authService>;

// Mock localStorage and sessionStorage
const mockLocalStorage = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};

const mockSessionStorage = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};

Object.defineProperty(window, 'localStorage', { value: mockLocalStorage });
Object.defineProperty(window, 'sessionStorage', { value: mockSessionStorage });

// Test component that uses the auth context
const TestComponent: React.FC = () => {
  const auth = useAuthContext();
  
  return (
    <div>
      <div data-testid="isAuthenticated">{String(auth.isAuthenticated)}</div>
      <div data-testid="isLoading">{String(auth.isLoading)}</div>
      <div data-testid="error">{auth.error || 'no-error'}</div>
      <div data-testid="user">{auth.user ? auth.user.name : 'no-user'}</div>
      <button onClick={() => auth.login({ email: 'test@example.com', password: 'password', rememberMe: true })}>
        Login
      </button>
      <button onClick={() => auth.logout()}>
        Logout
      </button>
      <button onClick={() => auth.register({ email: 'new@example.com', password: 'password', name: 'New User', confirmPassword: 'password' })}>
        Register
      </button>
      <button onClick={() => auth.clearError()}>
        Clear Error
      </button>
    </div>
  );
};

const renderWithAuthProvider = (component: React.ReactElement) => {
  return render(
    <AuthProvider>
      {component}
    </AuthProvider>
  );
};

const mockUser: UserProfile = {
  id: '1',
  name: 'Test User',
  email: 'test@example.com',
  createdAt: '2024-01-01T00:00:00Z',
  preferences: {
    language: 'en',
    theme: 'light',
    notifications: true
  }
};

describe('AuthContext', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockLocalStorage.getItem.mockReturnValue(null);
    mockSessionStorage.getItem.mockReturnValue(null);
  });

  it('initializes with no user when no token in storage', () => {
    renderWithAuthProvider(<TestComponent />);
    
    expect(screen.getByTestId('isAuthenticated')).toHaveTextContent('false');
    expect(screen.getByTestId('user')).toHaveTextContent('no-user');
    expect(screen.getByTestId('error')).toHaveTextContent('no-error');
  });

  it('initializes with user when token exists in localStorage', () => {
    mockLocalStorage.getItem.mockImplementation((key) => {
      if (key === 'auth_token') return 'mock-token';
      if (key === 'user_profile') return JSON.stringify(mockUser);
      return null;
    });

    renderWithAuthProvider(<TestComponent />);
    
    expect(screen.getByTestId('isAuthenticated')).toHaveTextContent('true');
    expect(screen.getByTestId('user')).toHaveTextContent('Test User');
  });

  it('handles successful login', async () => {
    mockAuthService.login.mockResolvedValue({
      success: true,
      user: mockUser,
      token: 'new-token'
    });

    renderWithAuthProvider(<TestComponent />);
    
    const loginButton = screen.getByText('Login');
    fireEvent.click(loginButton);

    await waitFor(() => {
      expect(screen.getByTestId('isAuthenticated')).toHaveTextContent('true');
      expect(screen.getByTestId('user')).toHaveTextContent('Test User');
    });

    expect(mockLocalStorage.setItem).toHaveBeenCalledWith('auth_token', 'new-token');
    expect(mockLocalStorage.setItem).toHaveBeenCalledWith('user_profile', JSON.stringify(mockUser));
  });

  it('handles login failure', async () => {
    mockAuthService.login.mockResolvedValue({
      success: false,
      error: 'Invalid credentials'
    });

    renderWithAuthProvider(<TestComponent />);
    
    const loginButton = screen.getByText('Login');
    fireEvent.click(loginButton);

    await waitFor(() => {
      expect(screen.getByTestId('error')).toHaveTextContent('Invalid credentials');
      expect(screen.getByTestId('isAuthenticated')).toHaveTextContent('false');
    });
  });

  it('handles successful registration', async () => {
    mockAuthService.register.mockResolvedValue({
      success: true,
      user: mockUser,
      token: 'registration-token'
    });

    renderWithAuthProvider(<TestComponent />);
    
    const registerButton = screen.getByText('Register');
    fireEvent.click(registerButton);

    await waitFor(() => {
      expect(screen.getByTestId('isAuthenticated')).toHaveTextContent('true');
      expect(screen.getByTestId('user')).toHaveTextContent('Test User');
    });

    expect(mockLocalStorage.setItem).toHaveBeenCalledWith('auth_token', 'registration-token');
  });

  it('handles logout correctly', async () => {
    mockAuthService.logout.mockResolvedValue({ success: true });
    
    // Start with authenticated state
    mockLocalStorage.getItem.mockImplementation((key) => {
      if (key === 'auth_token') return 'mock-token';
      if (key === 'user_profile') return JSON.stringify(mockUser);
      return null;
    });

    renderWithAuthProvider(<TestComponent />);
    
    const logoutButton = screen.getByText('Logout');
    fireEvent.click(logoutButton);

    await waitFor(() => {
      expect(screen.getByTestId('isAuthenticated')).toHaveTextContent('false');
      expect(screen.getByTestId('user')).toHaveTextContent('no-user');
    });

    expect(mockLocalStorage.removeItem).toHaveBeenCalledWith('auth_token');
    expect(mockLocalStorage.removeItem).toHaveBeenCalledWith('user_profile');
    expect(mockSessionStorage.removeItem).toHaveBeenCalledWith('auth_token');
    expect(mockSessionStorage.removeItem).toHaveBeenCalledWith('user_profile');
  });

  it('clears error when clearError is called', async () => {
    mockAuthService.login.mockResolvedValue({
      success: false,
      error: 'Test error'
    });

    renderWithAuthProvider(<TestComponent />);
    
    // Trigger an error
    const loginButton = screen.getByText('Login');
    fireEvent.click(loginButton);

    await waitFor(() => {
      expect(screen.getByTestId('error')).toHaveTextContent('Test error');
    });

    // Clear the error
    const clearErrorButton = screen.getByText('Clear Error');
    fireEvent.click(clearErrorButton);

    expect(screen.getByTestId('error')).toHaveTextContent('no-error');
  });

  it('throws error when useAuthContext is used outside provider', () => {
    // Suppress console.error for this test
    const consoleSpy = jest.spyOn(console, 'error').mockImplementation();
    
    expect(() => {
      render(<TestComponent />);
    }).toThrow('useAuthContext must be used within an AuthProvider');
    
    consoleSpy.mockRestore();
  });

  it('handles password mismatch during registration', async () => {
    renderWithAuthProvider(<TestComponent />);
    
    // Mock register with mismatched passwords
    const auth = useAuthContext();
    
    await act(async () => {
      try {
        await auth.register({ 
          email: 'test@example.com', 
          password: 'password1', 
          name: 'Test', 
          confirmPassword: 'password2' 
        });
      } catch {
        // Expected to throw
      }
    });

    await waitFor(() => {
      expect(screen.getByTestId('error')).toHaveTextContent('Passwords do not match');
    });
  });
});