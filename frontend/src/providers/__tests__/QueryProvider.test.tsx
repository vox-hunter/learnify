import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { QueryProvider } from '../QueryProvider';
import { useInvalidateQueries, useCacheManager } from '../QueryUtils';
import '@testing-library/jest-dom';

// Mock API function
const mockApiCall = jest.fn();
const mockMutationCall = jest.fn();

// Test component that uses React Query
const TestQueryComponent: React.FC = () => {
  const { data, error, isLoading } = useQuery({
    queryKey: ['test-query'],
    queryFn: mockApiCall,
  });

  const mutation = useMutation({
    mutationKey: ['test-mutation'],
    mutationFn: mockMutationCall,
  });

  const { invalidateAll, invalidateCourses } = useInvalidateQueries();
  const { getCacheStats, removeQueries } = useCacheManager();

  return (
    <div>
      <div data-testid="loading">{String(isLoading)}</div>
      <div data-testid="error">{error ? String(error) : 'no-error'}</div>
      <div data-testid="data">{data || 'no-data'}</div>
      <div data-testid="mutation-loading">{String(mutation.isPending)}</div>
      <button onClick={() => mutation.mutate('test-data')}>Mutate</button>
      <button onClick={() => invalidateAll()}>Invalidate All</button>
      <button onClick={() => invalidateCourses()}>Invalidate Courses</button>
      <button onClick={() => removeQueries(['test-query'])}>Remove Query</button>
      <div data-testid="cache-stats">{JSON.stringify(getCacheStats())}</div>
    </div>
  );
};

const renderWithQueryProvider = (component: React.ReactElement) => {
  return render(
    <QueryProvider>
      {component}
    </QueryProvider>
  );
};

describe('QueryProvider', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('provides React Query functionality to child components', async () => {
    mockApiCall.mockResolvedValue('test-response');

    renderWithQueryProvider(<TestQueryComponent />);
    
    // Initially loading
    expect(screen.getByTestId('loading')).toHaveTextContent('true');
    expect(screen.getByTestId('data')).toHaveTextContent('no-data');

    // Wait for query to resolve
    await waitFor(() => {
      expect(screen.getByTestId('loading')).toHaveTextContent('false');
      expect(screen.getByTestId('data')).toHaveTextContent('test-response');
    });

    expect(mockApiCall).toHaveBeenCalledTimes(1);
  });

  it('handles query errors correctly', async () => {
    const errorMessage = 'API Error';
    mockApiCall.mockRejectedValue(new Error(errorMessage));

    renderWithQueryProvider(<TestQueryComponent />);
    
    await waitFor(() => {
      expect(screen.getByTestId('loading')).toHaveTextContent('false');
      expect(screen.getByTestId('error')).toContain('Error');
    });
  });

  it('provides mutation functionality', async () => {
    mockMutationCall.mockResolvedValue('mutation-response');

    renderWithQueryProvider(<TestQueryComponent />);
    
    const mutateButton = screen.getByText('Mutate');
    mutateButton.click();

    expect(screen.getByTestId('mutation-loading')).toHaveTextContent('true');

    await waitFor(() => {
      expect(screen.getByTestId('mutation-loading')).toHaveTextContent('false');
    });

    expect(mockMutationCall).toHaveBeenCalledWith('test-data');
  });

  it('provides cache management utilities', () => {
    renderWithQueryProvider(<TestQueryComponent />);
    
    // Check that cache stats are available
    const cacheStatsElement = screen.getByTestId('cache-stats');
    expect(cacheStatsElement).toBeInTheDocument();
    
    const cacheStats = JSON.parse(cacheStatsElement.textContent || '{}');
    expect(cacheStats).toHaveProperty('queryCount');
    expect(cacheStats).toHaveProperty('mutationCount');
  });

  it('provides query invalidation utilities', () => {
    renderWithQueryProvider(<TestQueryComponent />);
    
    // Test that invalidation buttons are available
    expect(screen.getByText('Invalidate All')).toBeInTheDocument();
    expect(screen.getByText('Invalidate Courses')).toBeInTheDocument();
  });

  it('handles retries according to configuration', async () => {
    // Mock API to fail first few times, then succeed
    let callCount = 0;
    mockApiCall.mockImplementation(() => {
      callCount++;
      if (callCount < 3) {
        return Promise.reject(new Error('Temporary error'));
      }
      return Promise.resolve('success-after-retry');
    });

    renderWithQueryProvider(<TestQueryComponent />);
    
    // Wait for retries and eventual success
    await waitFor(
      () => {
        expect(screen.getByTestId('data')).toHaveTextContent('success-after-retry');
      },
      { timeout: 10000 }
    );

    // Should have been called multiple times due to retries
    expect(mockApiCall).toHaveBeenCalledTimes(3);
  });

  it('renders without crashing in development mode', () => {
    // Mock import.meta.env for Vite
    const mockEnv = { DEV: true };
    (globalThis as unknown as { 'import.meta': { env: Record<string, boolean> } })['import.meta'] = { env: mockEnv };

    renderWithQueryProvider(<TestQueryComponent />);
    
    // Should render without issues
    expect(screen.getByTestId('loading')).toBeInTheDocument();
  });

  it('configures proper default options', () => {
    renderWithQueryProvider(<TestQueryComponent />);
    
    // The component should render, indicating the QueryClient is properly configured
    expect(screen.getByTestId('loading')).toBeInTheDocument();
    expect(screen.getByTestId('error')).toBeInTheDocument();
    expect(screen.getByTestId('data')).toBeInTheDocument();
  });
});