/**
 * Comprehensive Testing Suite - T067
 * Complete testing utilities, helpers, and configurations for Learnify
 */

import { render, screen, fireEvent, waitFor, within } from '@testing-library/react';
import { renderHook, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import React from 'react';
import { ToastProvider } from './errorHandling';

/**
 * Custom render function with all providers
 */
export const renderWithProviders = (
  ui: React.ReactElement,
  {
    route = '/',
    queryClient,
    ...renderOptions
  }: {
    route?: string;
    queryClient?: QueryClient;
    [key: string]: unknown;
  } = {}
) => {
  const testQueryClient = queryClient || new QueryClient({
    defaultOptions: {
      queries: { retry: false, cacheTime: 0 },
      mutations: { retry: false },
    },
  });

  window.history.pushState({}, 'Test page', route);

  const AllTheProviders: React.FC<{ children: React.ReactNode }> = ({ children }) => (
    <BrowserRouter>
      <QueryClientProvider client={testQueryClient}>
        <ToastProvider>
          {children}
        </ToastProvider>
      </QueryClientProvider>
    </BrowserRouter>
  );

  return {
    user: userEvent.setup(),
    queryClient: testQueryClient,
    ...render(ui, { wrapper: AllTheProviders, ...renderOptions }),
  };
};

/**
 * Mock Data Factories
 */
export const mockData = {
  createUser: (overrides = {}) => ({
    id: '1',
    name: 'Test User',
    email: 'test@example.com',
    role: 'student',
    ...overrides,
  }),

  createCourse: (overrides = {}) => ({
    id: '1',
    title: 'Test Course',
    description: 'A test course',
    instructor: 'Test Instructor',
    duration: 120,
    difficulty: 'beginner',
    enrolled: false,
    ...overrides,
  }),

  createQuiz: (overrides = {}) => ({
    id: '1',
    title: 'Test Quiz',
    questions: [{
      id: '1',
      question: 'What is 2 + 2?',
      type: 'multiple-choice',
      options: ['3', '4', '5', '6'],
      correct: 1,
    }],
    timeLimit: 300,
    attempts: 3,
    ...overrides,
  }),
};

/**
 * Test Utilities
 */
export const testUtils = {
  waitForElement: async (text: string | RegExp, options?: { timeout?: number }) => {
    return await waitFor(() => screen.getByText(text), options);
  },

  fillForm: async (user: ReturnType<typeof userEvent.setup>, fields: Record<string, string>) => {
    for (const [label, value] of Object.entries(fields)) {
      const field = screen.getByLabelText(new RegExp(label, 'i'));
      await user.clear(field);
      await user.type(field, value);
    }
  },

  submitForm: async (user: ReturnType<typeof userEvent.setup>, formTestId?: string) => {
    const submitButton = formTestId 
      ? within(screen.getByTestId(formTestId)).getByRole('button', { name: /submit/i })
      : screen.getByRole('button', { name: /submit/i });
    await user.click(submitButton);
  },

  expectLoadingState: () => {
    expect(screen.getByText(/loading/i)).toBeInTheDocument();
  },

  expectErrorState: (message?: string) => {
    if (message) {
      expect(screen.getByText(new RegExp(message, 'i'))).toBeInTheDocument();
    } else {
      expect(screen.getByText(/error/i)).toBeInTheDocument();
    }
  },
};

/**
 * Performance Testing
 */
export const performanceUtils = {
  measureRenderTime: (component: React.ReactElement) => {
    const start = performance.now();
    render(component);
    const end = performance.now();
    return end - start;
  },

  measureMemoryUsage: () => {
    const memory = (performance as { memory?: { usedJSHeapSize: number } }).memory;
    return memory?.usedJSHeapSize || null;
  },
};

/**
 * Integration Testing
 */
export const integrationUtils = {
  testUserFlow: async (
    steps: Array<{
      action: string;
      target?: string;
      value?: string;
      expected?: string;
    }>
  ) => {
    const user = userEvent.setup();
    
    for (const step of steps) {
      switch (step.action) {
        case 'click':
          if (step.target) {
            const element = screen.getByRole('button', { name: new RegExp(step.target, 'i') });
            await user.click(element);
          }
          break;
        case 'type':
          if (step.target && step.value) {
            const field = screen.getByLabelText(new RegExp(step.target, 'i'));
            await user.type(field, step.value);
          }
          break;
        case 'wait':
          if (step.expected) {
            await testUtils.waitForElement(new RegExp(step.expected, 'i'));
          }
          break;
        case 'expect':
          if (step.expected) {
            expect(screen.getByText(new RegExp(step.expected, 'i'))).toBeInTheDocument();
          }
          break;
      }
    }
  },
};

/**
 * Test Configuration
 */
export const testConfig = {
  timeout: 10000,

  setupTestEnvironment: () => {
    Object.defineProperty(window, 'matchMedia', {
      writable: true,
      value: (query: string) => ({
        matches: false,
        media: query,
        onchange: null,
        addEventListener: () => {},
        removeEventListener: () => {},
      }),
    });

    if (typeof global !== 'undefined') {
      global.IntersectionObserver = class {
        observe() {}
        unobserve() {}
        disconnect() {}
      };
    }
  },
};

// Re-export testing library utilities
export {
  render,
  screen,
  fireEvent,
  waitFor,
  within,
  renderHook,
  act,
  userEvent,
};