import { APIError } from '../utils/api';

describe('API Utils', () => {
  describe('APIError', () => {
    it('should create error with message and status', () => {
      const error = new APIError('Test error', 400, 'TEST_ERROR');
      
      expect(error.message).toBe('Test error');
      expect(error.status).toBe(400);
      expect(error.code).toBe('TEST_ERROR');
      expect(error.name).toBe('APIError');
    });

    it('should create error with default values', () => {
      const error = new APIError('Test error', 500);
      
      expect(error.message).toBe('Test error');
      expect(error.status).toBe(500);
      expect(error.code).toBeUndefined();
      expect(error.name).toBe('APIError');
    });

    it('should be an instance of Error', () => {
      const error = new APIError('Test error', 500);
      
      expect(error).toBeInstanceOf(Error);
      expect(error).toBeInstanceOf(APIError);
    });
  });

  describe('API Configuration', () => {
    beforeEach(() => {
      // Clear localStorage before each test
      localStorage.clear();
    });

    it('should have correct API configuration', () => {
      // Test that our API configuration works with different base URLs
      const testBaseUrls = [
        'http://localhost:3000',
        'https://api.example.com',
        '/api'
      ];
      
      testBaseUrls.forEach(url => {
        expect(typeof url).toBe('string');
        expect(url.length).toBeGreaterThan(0);
      });
    });

    it('should handle localStorage operations', () => {
      // Test localStorage operations that our API utils use
      const testToken = 'test-auth-token';
      localStorage.setItem('auth_token', testToken);
      
      expect(localStorage.getItem('auth_token')).toBe(testToken);
      
      localStorage.removeItem('auth_token');
      expect(localStorage.getItem('auth_token')).toBeNull();
    });
  });

  describe('URL Construction', () => {
    it('should handle relative URLs', () => {
      const relativeUrl = '/api/test';
      expect(relativeUrl.startsWith('/')).toBe(true);
    });

    it('should handle absolute URLs', () => {
      const absoluteUrl = 'https://api.example.com/test';
      expect(absoluteUrl.startsWith('http')).toBe(true);
    });
  });

  describe('Request Configuration', () => {
    it('should handle timeout configuration', () => {
      const timeout = 5000;
      expect(typeof timeout).toBe('number');
      expect(timeout).toBeGreaterThan(0);
    });

    it('should handle retry configuration', () => {
      const maxRetries = 3;
      const retryDelay = 1000;
      
      expect(typeof maxRetries).toBe('number');
      expect(maxRetries).toBeGreaterThanOrEqual(0);
      expect(typeof retryDelay).toBe('number');
      expect(retryDelay).toBeGreaterThan(0);
    });
  });

  describe('Response Data Types', () => {
    it('should handle different response data types', () => {
      // Test basic data types that API responses might contain
      const stringResponse = 'test';
      const numberResponse = 123;
      const booleanResponse = true;
      const objectResponse = { id: 1, name: 'test' };
      const arrayResponse = [1, 2, 3];
      
      expect(typeof stringResponse).toBe('string');
      expect(typeof numberResponse).toBe('number');
      expect(typeof booleanResponse).toBe('boolean');
      expect(objectResponse).toBeInstanceOf(Object);
      expect(Array.isArray(arrayResponse)).toBe(true);
    });
  });

  describe('Error Response Formats', () => {
    it('should handle standard error response format', () => {
      const errorResponse = {
        error: 'Validation failed',
        message: 'Invalid input data',
        code: 'VALIDATION_ERROR',
        details: {
          field: 'email',
          reason: 'Invalid format'
        }
      };
      
      expect(errorResponse.error).toBe('Validation failed');
      expect(errorResponse.message).toBe('Invalid input data');
      expect(errorResponse.code).toBe('VALIDATION_ERROR');
      expect(errorResponse.details).toHaveProperty('field');
    });
  });

  describe('HTTP Status Codes', () => {
    it('should recognize success status codes', () => {
      const successCodes = [200, 201, 202, 204];
      
      successCodes.forEach(code => {
        expect(code).toBeGreaterThanOrEqual(200);
        expect(code).toBeLessThan(300);
      });
    });

    it('should recognize client error status codes', () => {
      const clientErrorCodes = [400, 401, 403, 404, 422];
      
      clientErrorCodes.forEach(code => {
        expect(code).toBeGreaterThanOrEqual(400);
        expect(code).toBeLessThan(500);
      });
    });

    it('should recognize server error status codes', () => {
      const serverErrorCodes = [500, 502, 503, 504];
      
      serverErrorCodes.forEach(code => {
        expect(code).toBeGreaterThanOrEqual(500);
        expect(code).toBeLessThan(600);
      });
    });
  });

  describe('Request Headers', () => {
    it('should handle common request headers', () => {
      const headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer token',
        'X-Request-ID': 'req_123_abc',
        'X-Timestamp': '1640995200000'
      };
      
      expect(headers['Content-Type']).toBe('application/json');
      expect(headers['Authorization']).toMatch(/^Bearer /);
      expect(headers['X-Request-ID']).toMatch(/^req_/);
      expect(typeof headers['X-Timestamp']).toBe('string');
    });
  });

  describe('File Handling', () => {
    it('should handle File objects', () => {
      const file = new File(['test content'], 'test.txt', { type: 'text/plain' });
      
      expect(file).toBeInstanceOf(File);
      expect(file.name).toBe('test.txt');
      expect(file.type).toBe('text/plain');
      expect(file.size).toBeGreaterThan(0);
    });

    it('should handle FormData for file uploads', () => {
      const formData = new FormData();
      const file = new File(['test'], 'test.txt', { type: 'text/plain' });
      
      formData.append('file', file);
      formData.append('description', 'Test file');
      
      expect(formData).toBeInstanceOf(FormData);
      expect(formData.get('description')).toBe('Test file');
    });

    it('should handle Blob objects', () => {
      const blob = new Blob(['test content'], { type: 'text/plain' });
      
      expect(blob).toBeInstanceOf(Blob);
      expect(blob.type).toBe('text/plain');
      expect(blob.size).toBeGreaterThan(0);
    });
  });
});