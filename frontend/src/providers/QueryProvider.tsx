import React from 'react';
import { QueryClientProvider } from '@tanstack/react-query';
import { queryClient } from './queryClient';

// Error handler for global query errors
queryClient.getQueryCache().config.onError = (error, query) => {
  console.error('Query error:', error, 'Query key:', query.queryKey);
  
  // Handle authentication errors globally
  if (error instanceof Error) {
    if (error.message.includes('401') || error.message.includes('Unauthorized')) {
      // Clear auth token and redirect to login
      localStorage.removeItem('auth_token');
      sessionStorage.removeItem('auth_token');
      window.location.href = '/login';
    }
    
    // Handle network errors
    if (error.message.includes('Failed to fetch') || error.message.includes('Network Error')) {
      console.warn('Network error detected, queries will retry automatically');
    }
  }
};

// Error handler for global mutation errors
queryClient.getMutationCache().config.onError = (error, _variables, _context, mutation) => {
  console.error('Mutation error:', error, 'Mutation key:', mutation.options.mutationKey);
  
  // Handle authentication errors globally
  if (error instanceof Error && (error.message.includes('401') || error.message.includes('Unauthorized'))) {
    localStorage.removeItem('auth_token');
    sessionStorage.removeItem('auth_token');
    window.location.href = '/login';
  }
};

// Success handler for mutations
queryClient.getMutationCache().config.onSuccess = (_data, _variables, _context, mutation) => {
  // Invalidate relevant queries on successful mutations
  const mutationKey = mutation.options.mutationKey;
  
  if (mutationKey) {
    const [resource] = mutationKey as string[];
    
    switch (resource) {
      case 'courses':
        // Invalidate all course-related queries
        queryClient.invalidateQueries({ queryKey: ['courses'] });
        queryClient.invalidateQueries({ queryKey: ['course-status'] });
        break;
      case 'auth':
        // Invalidate auth-related queries
        queryClient.invalidateQueries({ queryKey: ['user-profile'] });
        break;
      case 'documents':
        // Invalidate document-related queries
        queryClient.invalidateQueries({ queryKey: ['documents'] });
        break;
      default:
        break;
    }
  }
};

interface QueryProviderProps {
  children: React.ReactNode;
}

export const QueryProvider: React.FC<QueryProviderProps> = ({ children }) => {
  return (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
};

// Note: queryClient, useQuery, and useMutation are available through separate imports
// export { queryClient } from './QueryProvider';
// export { useQuery, useMutation } from '@tanstack/react-query';