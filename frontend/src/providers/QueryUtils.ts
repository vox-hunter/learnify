import { queryClient } from './queryClient';

// Custom hooks for common query patterns
export const useInvalidateQueries = () => {
  return {
    invalidateAll: () => queryClient.invalidateQueries(),
    invalidateCourses: () => queryClient.invalidateQueries({ queryKey: ['courses'] }),
    invalidateDocuments: () => queryClient.invalidateQueries({ queryKey: ['documents'] }),
    invalidateAuth: () => queryClient.invalidateQueries({ queryKey: ['auth'] }),
    refetchAll: () => queryClient.refetchQueries(),
    clear: () => queryClient.clear(),
  };
};

// Custom hook for optimistic updates
export const useOptimisticUpdate = () => {
  return {
    setQueryData: queryClient.setQueryData.bind(queryClient),
    getQueryData: queryClient.getQueryData.bind(queryClient),
    setQueriesData: queryClient.setQueriesData.bind(queryClient),
    cancelQueries: queryClient.cancelQueries.bind(queryClient),
  };
};

// Custom hook for manual cache management
export const useCacheManager = () => {
  return {
    // Remove specific query from cache
    removeQueries: (queryKey: unknown[]) => queryClient.removeQueries({ queryKey }),
    // Reset specific query
    resetQueries: (queryKey: unknown[]) => queryClient.resetQueries({ queryKey }),
    // Get cache size and stats
    getCacheStats: () => ({
      queryCount: queryClient.getQueryCache().getAll().length,
      mutationCount: queryClient.getMutationCache().getAll().length,
    }),
    // Prefetch data
    prefetchQuery: queryClient.prefetchQuery.bind(queryClient),
    // Ensure query data exists
    ensureQueryData: queryClient.ensureQueryData.bind(queryClient),
  };
};