import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { Navigation } from '../Navigation';
import { useAuth } from '../../../hooks/useAuth';
import type { UseAuthReturn } from '../../../hooks/useAuth';
import type { UserProfile } from '../../../types/api';
import '@testing-library/jest-dom';

// Mock the useAuth hook
jest.mock('../../../hooks/useAuth');
const mockUseAuth = useAuth as jest.MockedFunction<typeof useAuth>;

// Mock react-router-dom
const mockNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockNavigate,
  useLocation: () => ({ pathname: '/' })
}));

const renderWithRouter = (component: React.ReactElement) => {
  return render(
    <BrowserRouter>
      {component}
    </BrowserRouter>
  );
};

const createMockUser = (overrides: Partial<UserProfile> = {}): UserProfile => ({
  id: '1',
  name: 'John Doe',
  email: 'john@example.com',
  avatar: 'https://example.com/avatar.jpg',
  createdAt: '2024-01-01T00:00:00Z',
  preferences: {
    language: 'en',
    theme: 'light',
    notifications: true
  },
  ...overrides
});

const createMockAuthReturn = (overrides: Partial<UseAuthReturn> = {}): UseAuthReturn => ({
  user: null,
  isAuthenticated: false,
  login: jest.fn(),
  logout: jest.fn(),
  register: jest.fn(),
  refreshToken: jest.fn(),
  clearError: jest.fn(),
  updateProfile: jest.fn(),
  isLoading: false,
  error: null,
  token: null,
  ...overrides
});

describe('Navigation', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders navigation with brand logo and name', () => {
    mockUseAuth.mockReturnValue(createMockAuthReturn());

    renderWithRouter(<Navigation />);
    
    expect(screen.getByText('Learnify')).toBeInTheDocument();
    expect(screen.getByText('🤓')).toBeInTheDocument();
  });

  it('shows authentication buttons when user is not logged in', () => {
    mockUseAuth.mockReturnValue(createMockAuthReturn());

    renderWithRouter(<Navigation />);
    
    expect(screen.getByText('Sign In')).toBeInTheDocument();
    expect(screen.getByText('Sign Up')).toBeInTheDocument();
  });

  it('shows user menu when user is authenticated', () => {
    const mockUser = createMockUser();

    mockUseAuth.mockReturnValue(createMockAuthReturn({
      user: mockUser,
      isAuthenticated: true
    }));

    renderWithRouter(<Navigation />);
    
    expect(screen.getByText('Hi, John Doe')).toBeInTheDocument();
    expect(screen.getByText('Sign Out')).toBeInTheDocument();
    expect(screen.getByText('Dashboard')).toBeInTheDocument();
    expect(screen.getByText('My Courses')).toBeInTheDocument();
  });

  it('handles logout correctly', async () => {
    const mockLogout = jest.fn();
    const mockUser = createMockUser();

    mockUseAuth.mockReturnValue(createMockAuthReturn({
      user: mockUser,
      isAuthenticated: true,
      logout: mockLogout
    }));

    renderWithRouter(<Navigation />);
    
    const logoutButton = screen.getByText('Sign Out');
    fireEvent.click(logoutButton);

    await waitFor(() => {
      expect(mockLogout).toHaveBeenCalled();
      expect(mockNavigate).toHaveBeenCalledWith('/');
    });
  });

  it('toggles mobile menu correctly', () => {
    mockUseAuth.mockReturnValue(createMockAuthReturn());

    renderWithRouter(<Navigation />);
    
    const mobileMenuButton = screen.getByLabelText('Open menu');
    fireEvent.click(mobileMenuButton);

    expect(screen.getByLabelText('Close menu')).toBeInTheDocument();
  });

  it('navigates to login page when Sign In is clicked', () => {
    mockUseAuth.mockReturnValue(createMockAuthReturn());

    renderWithRouter(<Navigation />);
    
    const signInButton = screen.getByText('Sign In');
    fireEvent.click(signInButton);

    expect(mockNavigate).toHaveBeenCalledWith('/login');
  });

  it('navigates to register page when Sign Up is clicked', () => {
    mockUseAuth.mockReturnValue(createMockAuthReturn());

    renderWithRouter(<Navigation />);
    
    const signUpButton = screen.getByText('Sign Up');
    fireEvent.click(signUpButton);

    expect(mockNavigate).toHaveBeenCalledWith('/login?mode=register');
  });

  it('highlights active route correctly', () => {
    mockUseAuth.mockReturnValue(createMockAuthReturn());

    renderWithRouter(<Navigation />);
    
    const homeLink = screen.getByRole('link', { name: /home/i });
    expect(homeLink).toHaveClass('active');
  });
});