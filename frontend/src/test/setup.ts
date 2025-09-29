import '@testing-library/jest-dom';

// Mock import.meta for testing environment
(globalThis as unknown as { 'import.meta': { env: Record<string, string> } })['import.meta'] = {
  env: {
    MODE: 'test',
    VITE_API_BASE_URL: 'http://localhost:8000'
  }
};

// Mock TextEncoder/TextDecoder for testing environment
if (typeof globalThis.TextEncoder === 'undefined') {
  (globalThis as unknown as { TextEncoder: unknown; TextDecoder: unknown }).TextEncoder = class {
    encode(input: string) {
      return new Uint8Array(Array.from(input).map(char => char.charCodeAt(0)));
    }
  };
  (globalThis as unknown as { TextEncoder: unknown; TextDecoder: unknown }).TextDecoder = class {
    decode(input: Uint8Array) {
      return String.fromCharCode(...Array.from(input));
    }
  };
}

// Global test setup
(globalThis as unknown as { ResizeObserver: unknown }).ResizeObserver = class ResizeObserver {
  observe() {}
  unobserve() {}
  disconnect() {}
};

// Mock matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(), // deprecated
    removeListener: jest.fn(), // deprecated
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
});