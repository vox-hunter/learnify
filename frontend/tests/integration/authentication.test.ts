import axios, { AxiosError } from 'axios';
import { describe, it, expect, beforeAll, beforeEach } from '@jest/globals';

describe('Authentication API Integration Tests', () => {
  const API_BASE_URL = 'http://localhost:8000';
  const loginEndpoint = `${API_BASE_URL}/api/auth/login`;
  const logoutEndpoint = `${API_BASE_URL}/api/auth/logout`;
  const meEndpoint = `${API_BASE_URL}/api/auth/me`;

  // Test credentials - these should be set up in test environment
  const testUser = {
    email: 'test@example.com',
    password: 'testpassword123',
  };

  beforeAll(async () => {
    // Verify the backend is running
    try {
      await axios.get(`${API_BASE_URL}/health`);
    } catch {
      throw new Error('Backend server is not running. Please start the Python backend first.');
    }
  });

  describe('POST /api/auth/login', () => {
    it('should successfully authenticate valid user credentials', async () => {
      const requestData = {
        email: testUser.email,
        password: testUser.password,
      };

      const response = await axios.post(loginEndpoint, requestData, {
        headers: {
          'Content-Type': 'application/json',
        },
      });

      expect(response.status).toBe(200);
      expect(response.data).toMatchObject({
        user: {
          id: expect.stringMatching(/^user_\w+$/),
          email: testUser.email,
          name: expect.any(String),
          isGuest: false,
          createdAt: expect.stringMatching(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$/),
        },
        session: {
          id: expect.stringMatching(/^session_\w+$/),
          token: expect.any(String),
          expiresAt: expect.stringMatching(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$/),
        },
      });

      // Verify token is a JWT-like string
      expect(response.data.session.token).toMatch(/^[A-Za-z0-9\-_]+\.[A-Za-z0-9\-_]+\.[A-Za-z0-9\-_]+$/);
    });

    it('should reject missing email with 400 error', async () => {
      const requestData = {
        password: testUser.password,
        // Missing email
      };

      try {
        await axios.post(loginEndpoint, requestData, {
          headers: {
            'Content-Type': 'application/json',
          },
        });
        throw new Error('Expected request to fail with 400 error');
      } catch (error) {
        const axiosError = error as AxiosError;
        expect(axiosError.response?.status).toBe(400);
        expect(axiosError.response?.data).toMatchObject({
          error: 'missing_credentials',
          message: 'Email and password are required',
          details: {
            missingFields: expect.arrayContaining(['email']),
          },
        });
      }
    });

    it('should reject missing password with 400 error', async () => {
      const requestData = {
        email: testUser.email,
        // Missing password
      };

      try {
        await axios.post(loginEndpoint, requestData, {
          headers: {
            'Content-Type': 'application/json',
          },
        });
        throw new Error('Expected request to fail with 400 error');
      } catch (error) {
        const axiosError = error as AxiosError;
        expect(axiosError.response?.status).toBe(400);
        expect(axiosError.response?.data).toMatchObject({
          error: 'missing_credentials',
          message: 'Email and password are required',
          details: {
            missingFields: expect.arrayContaining(['password']),
          },
        });
      }
    });

    it('should reject invalid credentials with 401 error', async () => {
      const requestData = {
        email: 'nonexistent@example.com',
        password: 'wrongpassword',
      };

      try {
        await axios.post(loginEndpoint, requestData, {
          headers: {
            'Content-Type': 'application/json',
          },
        });
        throw new Error('Expected request to fail with 401 error');
      } catch (error) {
        const axiosError = error as AxiosError;
        expect(axiosError.response?.status).toBe(401);
        expect(axiosError.response?.data).toMatchObject({
          error: 'invalid_credentials',
          message: 'Invalid email or password',
          details: {
            attemptCount: expect.any(Number),
            maxAttempts: expect.any(Number),
          },
        });
      }
    });

    it('should validate email format', async () => {
      const requestData = {
        email: 'invalid-email-format',
        password: testUser.password,
      };

      try {
        await axios.post(loginEndpoint, requestData, {
          headers: {
            'Content-Type': 'application/json',
          },
        });
        throw new Error('Expected request to fail with validation error');
      } catch (error) {
        const axiosError = error as AxiosError;
        expect(axiosError.response?.status).toBe(400);
        expect((axiosError.response?.data as { message: string }).message).toContain('email');
      }
    });

    it('should validate password minimum length', async () => {
      const requestData = {
        email: testUser.email,
        password: 'short', // Less than 8 characters
      };

      try {
        await axios.post(loginEndpoint, requestData, {
          headers: {
            'Content-Type': 'application/json',
          },
        });
        throw new Error('Expected request to fail with validation error');
      } catch (error) {
        const axiosError = error as AxiosError;
        expect(axiosError.response?.status).toBe(400);
        expect((axiosError.response?.data as { message: string }).message).toContain('password');
      }
    });
  });

  describe('GET /api/auth/me', () => {
    let authToken: string;

    beforeAll(async () => {
      // Login to get auth token
      const loginResponse = await axios.post(loginEndpoint, testUser, {
        headers: {
          'Content-Type': 'application/json',
        },
      });
      authToken = loginResponse.data.session.token;
    });

    it('should return current user info with valid token', async () => {
      const response = await axios.get(meEndpoint, {
        headers: {
          Authorization: `Bearer ${authToken}`,
        },
      });

      expect(response.status).toBe(200);
      expect(response.data).toMatchObject({
        user: {
          id: expect.stringMatching(/^user_\w+$/),
          email: testUser.email,
          name: expect.any(String),
          isGuest: false,
          guestUsageCount: expect.any(Number),
          guestUsageLimit: expect.any(Number),
          lastLoginAt: expect.stringMatching(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$/),
          createdAt: expect.stringMatching(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$/),
        },
        session: {
          id: expect.stringMatching(/^session_\w+$/),
          expiresAt: expect.stringMatching(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$/),
        },
      });
    });

    it('should reject request without token with 401 error', async () => {
      try {
        await axios.get(meEndpoint);
        throw new Error('Expected request to fail with 401 error');
      } catch (error) {
        const axiosError = error as AxiosError;
        expect(axiosError.response?.status).toBe(401);
        expect(axiosError.response?.data).toMatchObject({
          error: 'unauthorized',
          message: 'Authentication required',
        });
      }
    });

    it('should reject request with invalid token with 401 error', async () => {
      try {
        await axios.get(meEndpoint, {
          headers: {
            Authorization: 'Bearer invalid_token_here',
          },
        });
        throw new Error('Expected request to fail with 401 error');
      } catch (error) {
        const axiosError = error as AxiosError;
        expect(axiosError.response?.status).toBe(401);
        expect(axiosError.response?.data).toMatchObject({
          error: 'invalid_token',
          message: 'Authentication token is invalid or expired',
        });
      }
    });
  });

  describe('POST /api/auth/logout', () => {
    let authToken: string;

    beforeEach(async () => {
      // Login to get fresh auth token for each test
      const loginResponse = await axios.post(loginEndpoint, testUser, {
        headers: {
          'Content-Type': 'application/json',
        },
      });
      authToken = loginResponse.data.session.token;
    });

    it('should successfully logout with valid token', async () => {
      const response = await axios.post(logoutEndpoint, {}, {
        headers: {
          Authorization: `Bearer ${authToken}`,
        },
      });

      expect(response.status).toBe(200);
      expect(response.data).toMatchObject({
        message: 'Successfully logged out',
      });

      // Verify token is now invalid
      try {
        await axios.get(meEndpoint, {
          headers: {
            Authorization: `Bearer ${authToken}`,
          },
        });
        throw new Error('Token should be invalid after logout');
      } catch (error) {
        const axiosError = error as AxiosError;
        expect(axiosError.response?.status).toBe(401);
      }
    });

    it('should reject logout without token with 401 error', async () => {
      try {
        await axios.post(logoutEndpoint, {});
        throw new Error('Expected request to fail with 401 error');
      } catch (error) {
        const axiosError = error as AxiosError;
        expect(axiosError.response?.status).toBe(401);
        expect(axiosError.response?.data).toMatchObject({
          error: 'unauthorized',
          message: 'Authentication required',
        });
      }
    });

    it('should reject logout with invalid token with 401 error', async () => {
      try {
        await axios.post(logoutEndpoint, {}, {
          headers: {
            Authorization: 'Bearer invalid_token_here',
          },
        });
        throw new Error('Expected request to fail with 401 error');
      } catch (error) {
        const axiosError = error as AxiosError;
        expect(axiosError.response?.status).toBe(401);
        expect(axiosError.response?.data).toMatchObject({
          error: 'invalid_token',
          message: 'Authentication token is invalid or expired',
        });
      }
    });
  });
});