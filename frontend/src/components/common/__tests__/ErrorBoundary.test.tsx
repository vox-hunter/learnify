import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import ErrorBoundary from '../ErrorBoundary';
import { ErrorBoundaryWrapper } from '../ErrorBoundaryUtils';
import { withErrorBoundary } from '../withErrorBoundary';
import '@testing-library/jest-dom';

// Mock console.error to avoid noise in tests
const originalConsoleError = console.error;
beforeAll(() => {
  console.error = jest.fn();
});

afterAll(() => {
  console.error = originalConsoleError;
});

// Mock clipboard API
Object.assign(navigator, {
  clipboard: {
    writeText: jest.fn(() => Promise.resolve()),
  },
});

// Mock localStorage
const mockLocalStorage = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
};
Object.defineProperty(window, 'localStorage', { value: mockLocalStorage });

// Component that throws an error
const ThrowErrorComponent: React.FC<{ shouldThrow?: boolean }> = ({ shouldThrow = true }) => {
  if (shouldThrow) {
    throw new Error('Test error message');
  }
  return <div data-testid="no-error">No error occurred</div>;
};

// Component that works normally
const WorkingComponent: React.FC = () => {
  return <div data-testid="working">Working component</div>;
};

describe('ErrorBoundary', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockLocalStorage.getItem.mockReturnValue('[]');
  });

  it('renders children when there is no error', () => {
    render(
      <ErrorBoundary>
        <WorkingComponent />
      </ErrorBoundary>
    );

    expect(screen.getByTestId('working')).toBeInTheDocument();
  });

  it('renders error UI when child component throws', () => {
    render(
      <ErrorBoundary>
        <ThrowErrorComponent />
      </ErrorBoundary>
    );

    expect(screen.getByText('Oops! Something went wrong')).toBeInTheDocument();
    expect(screen.getByText('Try Again')).toBeInTheDocument();
    expect(screen.getByText('Go to Home')).toBeInTheDocument();
    expect(screen.getByText('Reload Page')).toBeInTheDocument();
  });

  it('displays custom fallback UI when provided', () => {
    const CustomFallback = <div data-testid="custom-fallback">Custom error UI</div>;

    render(
      <ErrorBoundary fallback={CustomFallback}>
        <ThrowErrorComponent />
      </ErrorBoundary>
    );

    expect(screen.getByTestId('custom-fallback')).toBeInTheDocument();
    expect(screen.queryByText('Oops! Something went wrong')).not.toBeInTheDocument();
  });

  it('calls onError callback when error occurs', () => {
    const onErrorMock = jest.fn();

    render(
      <ErrorBoundary onError={onErrorMock}>
        <ThrowErrorComponent />
      </ErrorBoundary>
    );

    expect(onErrorMock).toHaveBeenCalledTimes(1);
    expect(onErrorMock).toHaveBeenCalledWith(
      expect.any(Error),
      expect.objectContaining({
        componentStack: expect.any(String),
      })
    );
  });

  it('resets error state when Try Again is clicked', () => {
    const { rerender } = render(
      <ErrorBoundary>
        <ThrowErrorComponent shouldThrow={true} />
      </ErrorBoundary>
    );

    expect(screen.getByText('Oops! Something went wrong')).toBeInTheDocument();

    const tryAgainButton = screen.getByText('Try Again');
    fireEvent.click(tryAgainButton);

    // Re-render with a non-throwing component
    rerender(
      <ErrorBoundary>
        <ThrowErrorComponent shouldThrow={false} />
      </ErrorBoundary>
    );

    expect(screen.getByTestId('no-error')).toBeInTheDocument();
  });

  it('shows error details in development mode', () => {
    // Mock import.meta.env for Vite
    const mockEnv = { DEV: true };
    (globalThis as unknown as { 'import.meta': { env: Record<string, boolean> } })['import.meta'] = { env: mockEnv };

    render(
      <ErrorBoundary>
        <ThrowErrorComponent />
      </ErrorBoundary>
    );

    expect(screen.getByText('Error Details (Development)')).toBeInTheDocument();
  });

  it('hides error details in production mode', () => {
    // Mock import.meta.env for Vite production
    const mockEnv = { DEV: false };
    (globalThis as unknown as { 'import.meta': { env: Record<string, boolean> } })['import.meta'] = { env: mockEnv };

    render(
      <ErrorBoundary>
        <ThrowErrorComponent />
      </ErrorBoundary>
    );

    expect(screen.queryByText('Error Details (Development)')).not.toBeInTheDocument();
  });

  it('copies error details to clipboard', async () => {
    render(
      <ErrorBoundary>
        <ThrowErrorComponent />
      </ErrorBoundary>
    );

    const copyButton = screen.getByText('📋 Copy Error Details');
    fireEvent.click(copyButton);

    expect(navigator.clipboard.writeText).toHaveBeenCalledWith(
      expect.stringContaining('Event ID:')
    );
  });

  it('stores error reports in localStorage', () => {
    render(
      <ErrorBoundary>
        <ThrowErrorComponent />
      </ErrorBoundary>
    );

    expect(mockLocalStorage.setItem).toHaveBeenCalledWith(
      'error_reports',
      expect.stringContaining('Test error message')
    );
  });

  it('resets when resetKeys change', () => {
    let resetKey = 'key1';
    
    const { rerender } = render(
      <ErrorBoundary resetKeys={[resetKey]}>
        <ThrowErrorComponent />
      </ErrorBoundary>
    );

    expect(screen.getByText('Oops! Something went wrong')).toBeInTheDocument();

    // Change reset key
    resetKey = 'key2';
    rerender(
      <ErrorBoundary resetKeys={[resetKey]}>
        <WorkingComponent />
      </ErrorBoundary>
    );

    expect(screen.getByTestId('working')).toBeInTheDocument();
  });

  it('resets when resetOnPropsChange is true and props change', () => {
    let propValue = 'value1';
    
    const { rerender } = render(
      <ErrorBoundary resetOnPropsChange resetKeys={[propValue]}>
        <ThrowErrorComponent />
      </ErrorBoundary>
    );

    expect(screen.getByText('Oops! Something went wrong')).toBeInTheDocument();

    // Change props
    propValue = 'value2';
    rerender(
      <ErrorBoundary resetOnPropsChange resetKeys={[propValue]}>
        <WorkingComponent />
      </ErrorBoundary>
    );

    expect(screen.getByTestId('working')).toBeInTheDocument();
  });
});

describe('ErrorBoundaryWrapper', () => {
  it('wraps components with error boundary functionality', () => {
    render(
      <ErrorBoundaryWrapper>
        <ThrowErrorComponent />
      </ErrorBoundaryWrapper>
    );

    expect(screen.getByText('Oops! Something went wrong')).toBeInTheDocument();
  });
});

describe('withErrorBoundary HOC', () => {
  it('wraps component with error boundary', () => {
    const WrappedComponent = withErrorBoundary(ThrowErrorComponent);
    
    render(<WrappedComponent />);

    expect(screen.getByText('Oops! Something went wrong')).toBeInTheDocument();
  });

  it('passes props to wrapped component', () => {
    const WrappedComponent = withErrorBoundary(ThrowErrorComponent);
    
    render(<WrappedComponent shouldThrow={false} />);

    expect(screen.getByTestId('no-error')).toBeInTheDocument();
  });

  it('sets proper display name', () => {
    const WrappedComponent = withErrorBoundary(ThrowErrorComponent);
    
    expect(WrappedComponent.displayName).toBe('withErrorBoundary(ThrowErrorComponent)');
  });
});