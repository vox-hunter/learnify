import { render } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

// Simple testing utility without JSX components
export const createTestQueryClient = () => {
  return new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false }
    }
  });
};

export const mockUser = {
  id: '1',
  name: 'Test User',
  email: 'test@example.com',
  role: 'student' as const,
  avatar: '/avatars/default.jpg',
  preferences: {
    theme: 'light' as const,
    language: 'en'
  }
};

export const mockCourse = {
  id: '1',
  title: 'Test Course',
  description: 'A comprehensive test course',
  instructor: 'Test Instructor',
  duration: 120,
  difficulty: 'beginner' as const,
  topics: ['javascript', 'react'],
  enrolled: false,
  progress: 0
};

export const mockQuiz = {
  id: '1',
  title: 'Test Quiz',
  courseId: '1',
  questions: [
    {
      id: '1',
      question: 'What is React?',
      type: 'multiple-choice' as const,
      options: [
        'A JavaScript library',
        'A database',
        'A web server',
        'A CSS framework'
      ],
      correct: 0
    }
  ],
  timeLimit: 300,
  attempts: 3
};

export const createMockUser = (overrides: Partial<typeof mockUser> = {}) => ({
  ...mockUser,
  ...overrides
});

export const createMockCourse = (overrides: Partial<typeof mockCourse> = {}) => ({
  ...mockCourse,
  ...overrides
});

export const createMockQuiz = (overrides: Partial<typeof mockQuiz> = {}) => ({
  ...mockQuiz,
  ...overrides
});

// Test utilities
export const testUtils = {
  delay: (ms: number) => new Promise(resolve => setTimeout(resolve, ms)),
  
  mockLocalStorage: () => {
    const store: Record<string, string> = {};
    return {
      getItem: (key: string) => store[key] || null,
      setItem: (key: string, value: string) => {
        store[key] = value;
      },
      removeItem: (key: string) => {
        delete store[key];
      },
      clear: () => {
        Object.keys(store).forEach(key => delete store[key]);
      }
    };
  },
  
  mockSessionStorage: () => {
    const store: Record<string, string> = {};
    return {
      getItem: (key: string) => store[key] || null,
      setItem: (key: string, value: string) => {
        store[key] = value;
      },
      removeItem: (key: string) => {
        delete store[key];
      },
      clear: () => {
        Object.keys(store).forEach(key => delete store[key]);
      }
    };
  }
};

// Performance testing utilities
export const performanceUtils = {
  measureRenderTime: (renderFn: () => void) => {
    const start = performance.now();
    renderFn();
    const end = performance.now();
    return end - start;
  },
  
  measureAsyncOperation: async (operation: () => Promise<void>) => {
    const start = performance.now();
    await operation();
    const end = performance.now();
    return end - start;
  },
  
  createLargeDataset: (size: number, factory: (index: number) => any) => {
    return Array.from({ length: size }, (_, i) => factory(i));
  }
};

// API mocking helpers
export const mockApiResponse = <T>(data: T, delay: number = 0) => {
  return new Promise<T>(resolve => {
    setTimeout(() => resolve(data), delay);
  });
};

export const mockApiError = (message: string, status: number = 500, delay: number = 0) => {
  return new Promise((_, reject) => {
    setTimeout(() => reject(new Error(`${status}: ${message}`)), delay);
  });
};

// Test configuration
export const testConfig = {
  defaultTimeout: 5000,
  renderTimeout: 100,
  apiTimeout: 1000,
  queryRetries: 0,
  mutationRetries: 0
};

export default {
  createTestQueryClient,
  mockUser,
  mockCourse,
  mockQuiz,
  createMockUser,
  createMockCourse,
  createMockQuiz,
  testUtils,
  performanceUtils,
  mockApiResponse,
  mockApiError,
  testConfig
};