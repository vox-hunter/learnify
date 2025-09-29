/**
 * Testing Documentation and Configuration - T067
 * Complete testing guide and setup for the Learnify application
 */

# Comprehensive Testing Suite Documentation

## Overview
This document outlines the complete testing strategy for the Learnify React application, including unit tests, integration tests, and end-to-end testing approaches.

## Testing Stack
- **Jest**: Test runner and assertion library
- **React Testing Library**: Component testing utilities
- **User Event**: User interaction simulation
- **MSW (Mock Service Worker)**: API mocking
- **React Query**: Data fetching and caching tests

## Test Structure

### Unit Tests
```typescript
// Example: Component unit test
import { renderWithProviders } from '../utils/testingUtils';
import { CourseCard } from '../components/CourseCard';

describe('CourseCard', () => {
  const mockCourse = {
    id: '1',
    title: 'Test Course',
    description: 'Test Description',
    instructor: 'Test Instructor',
    duration: 120,
    difficulty: 'beginner'
  };

  it('renders course information correctly', () => {
    const { screen } = renderWithProviders(<CourseCard course={mockCourse} />);
    
    expect(screen.getByText('Test Course')).toBeInTheDocument();
    expect(screen.getByText('Test Instructor')).toBeInTheDocument();
    expect(screen.getByText(/beginner/i)).toBeInTheDocument();
  });
});
```

### Integration Tests
```typescript
// Example: User flow integration test
import { renderWithProviders } from '../utils/testingUtils';
import { App } from '../App';

describe('Course Enrollment Flow', () => {
  it('allows user to enroll in a course', async () => {
    const { user, screen } = renderWithProviders(<App />, { route: '/courses' });
    
    // Navigate to course
    await user.click(screen.getByText('JavaScript Fundamentals'));
    
    // Enroll in course
    await user.click(screen.getByRole('button', { name: /enroll/i }));
    
    // Verify enrollment
    expect(screen.getByText(/enrolled successfully/i)).toBeInTheDocument();
  });
});
```

### Hook Testing
```typescript
// Example: Custom hook test
import { renderHookWithProviders } from '../utils/testingUtils';
import { useCourses } from '../hooks/useCourses';

describe('useCourses', () => {
  it('fetches and returns course data', async () => {
    const { result, waitFor } = renderHookWithProviders(() => useCourses());
    
    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });
    
    expect(result.current.data).toHaveLength(2);
  });
});
```

## Mock Data Factories

### User Mock
```typescript
export const createMockUser = (overrides = {}) => ({
  id: '1',
  name: 'Test User',
  email: 'test@example.com',
  role: 'student',
  avatar: '/avatars/default.jpg',
  preferences: {
    theme: 'light',
    language: 'en'
  },
  ...overrides
});
```

### Course Mock
```typescript
export const createMockCourse = (overrides = {}) => ({
  id: '1',
  title: 'Test Course',
  description: 'A comprehensive test course',
  instructor: 'Test Instructor',
  duration: 120,
  difficulty: 'beginner',
  topics: ['javascript', 'react'],
  enrolled: false,
  progress: 0,
  ...overrides
});
```

### Quiz Mock
```typescript
export const createMockQuiz = (overrides = {}) => ({
  id: '1',
  title: 'Test Quiz',
  courseId: '1',
  questions: [
    {
      id: '1',
      question: 'What is React?',
      type: 'multiple-choice',
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
  attempts: 3,
  ...overrides
});
```

## API Mocking

### Mock Service Worker Setup
```typescript
// mocks/handlers.ts
import { rest } from 'msw';
import { createMockUser, createMockCourse } from './mockData';

export const handlers = [
  rest.get('/api/auth/me', (req, res, ctx) => {
    return res(ctx.json(createMockUser()));
  }),

  rest.get('/api/courses', (req, res, ctx) => {
    return res(ctx.json([
      createMockCourse({ id: '1', title: 'JavaScript Fundamentals' }),
      createMockCourse({ id: '2', title: 'React Basics' })
    ]));
  }),

  rest.post('/api/courses/:id/enroll', (req, res, ctx) => {
    return res(ctx.json({ success: true, message: 'Enrolled successfully' }));
  })
];
```

## Test Utilities

### Custom Render Function
```typescript
import { render } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ToastProvider } from '../utils/errorHandling';

export const renderWithProviders = (ui, options = {}) => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false }
    }
  });

  const AllProviders = ({ children }) => (
    <BrowserRouter>
      <QueryClientProvider client={queryClient}>
        <ToastProvider>
          {children}
        </ToastProvider>
      </QueryClientProvider>
    </BrowserRouter>
  );

  return render(ui, { wrapper: AllProviders, ...options });
};
```

### Form Testing Utilities
```typescript
export const fillAndSubmitForm = async (user, formData) => {
  for (const [field, value] of Object.entries(formData)) {
    const input = screen.getByLabelText(new RegExp(field, 'i'));
    await user.clear(input);
    await user.type(input, value);
  }
  
  const submitButton = screen.getByRole('button', { name: /submit/i });
  await user.click(submitButton);
};
```

## Accessibility Testing

### Basic A11y Tests
```typescript
import { axe, toHaveNoViolations } from 'jest-axe';

expect.extend(toHaveNoViolations);

describe('Accessibility', () => {
  it('should not have accessibility violations', async () => {
    const { container } = renderWithProviders(<CourseCard course={mockCourse} />);
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });
});
```

### Keyboard Navigation Tests
```typescript
describe('Keyboard Navigation', () => {
  it('supports tab navigation', async () => {
    const { user } = renderWithProviders(<CourseCard course={mockCourse} />);
    
    await user.tab();
    expect(screen.getByRole('button', { name: /enroll/i })).toHaveFocus();
    
    await user.keyboard('{Enter}');
    expect(screen.getByText(/enrolled/i)).toBeInTheDocument();
  });
});
```

## Performance Testing

### Render Performance
```typescript
describe('Performance', () => {
  it('renders quickly with large datasets', () => {
    const largeCourseList = Array.from({ length: 1000 }, (_, i) => 
      createMockCourse({ id: i.toString(), title: `Course ${i}` })
    );
    
    const start = performance.now();
    renderWithProviders(<CourseList courses={largeCourseList} />);
    const end = performance.now();
    
    expect(end - start).toBeLessThan(100); // Should render in under 100ms
  });
});
```

## Test Configuration

### Jest Configuration (jest.config.js)
```javascript
module.exports = {
  testEnvironment: 'jsdom',
  setupFilesAfterEnv: ['<rootDir>/src/setupTests.ts'],
  moduleNameMapping: {
    '\\.(css|less|scss|sass)$': 'identity-obj-proxy',
    '^@/(.*)$': '<rootDir>/src/$1'
  },
  collectCoverageFrom: [
    'src/**/*.{ts,tsx}',
    '!src/**/*.d.ts',
    '!src/main.tsx',
    '!src/vite-env.d.ts'
  ],
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80
    }
  }
};
```

### Setup File (setupTests.ts)
```typescript
import '@testing-library/jest-dom';
import { server } from './mocks/server';

// Start MSW server
beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

// Mock window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(),
    removeListener: jest.fn(),
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
});

// Mock IntersectionObserver
global.IntersectionObserver = jest.fn().mockImplementation(() => ({
  observe: jest.fn(),
  unobserve: jest.fn(),
  disconnect: jest.fn(),
}));
```

## Running Tests

### NPM Scripts
```json
{
  "scripts": {
    "test": "jest",
    "test:watch": "jest --watch",
    "test:coverage": "jest --coverage",
    "test:ci": "jest --ci --coverage --watchAll=false"
  }
}
```

### Test Commands
- `npm test` - Run all tests
- `npm run test:watch` - Run tests in watch mode
- `npm run test:coverage` - Generate coverage report
- `npm run test:ci` - Run tests for CI/CD

## Best Practices

1. **Write descriptive test names** that explain what is being tested
2. **Use the AAA pattern** (Arrange, Act, Assert)
3. **Test user behavior**, not implementation details
4. **Mock external dependencies** to isolate units under test
5. **Use semantic queries** (getByRole, getByLabelText) over test IDs
6. **Test error states** and edge cases
7. **Keep tests focused** - one concept per test
8. **Use async/await** for asynchronous operations
9. **Clean up** after tests (clear mocks, reset state)
10. **Maintain good test coverage** without obsessing over 100%

This comprehensive testing suite ensures robust, maintainable, and reliable code for the Learnify application.