import axios, { AxiosError } from 'axios';
import { describe, it, expect, beforeAll } from '@jest/globals';

describe('URL Document API Integration Tests', () => {
  const API_BASE_URL = 'http://localhost:8000';
  const urlEndpoint = `${API_BASE_URL}/api/documents/url`;

  beforeAll(async () => {
    // Verify the backend is running
    try {
      await axios.get(`${API_BASE_URL}/health`);
    } catch {
      throw new Error('Backend server is not running. Please start the Python backend first.');
    }
  });

  describe('POST /api/documents/url', () => {
    it('should successfully process a valid PDF URL', async () => {
      const requestData = {
        url: 'https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf',
      };

      const response = await axios.post(urlEndpoint, requestData, {
        headers: {
          'Content-Type': 'application/json',
        },
      });

      expect(response.status).toBe(201);
      expect(response.data).toMatchObject({
        id: expect.stringMatching(/^doc_\w+$/),
        name: expect.stringContaining('.pdf'),
        type: 'url',
        content: requestData.url,
        status: 'processing',
        uploadedAt: expect.stringMatching(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$/),
      });
    });

    it('should accept custom filename parameter', async () => {
      const requestData = {
        url: 'https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf',
        filename: 'custom-document.pdf',
      };

      const response = await axios.post(urlEndpoint, requestData, {
        headers: {
          'Content-Type': 'application/json',
        },
      });

      expect(response.status).toBe(201);
      expect(response.data.name).toBe('custom-document.pdf');
    });

    it('should reject invalid URL protocols with 400 error', async () => {
      const requestData = {
        url: 'ftp://example.com/document.pdf',
      };

      try {
        await axios.post(urlEndpoint, requestData, {
          headers: {
            'Content-Type': 'application/json',
          },
        });
        throw new Error('Expected request to fail with 400 error');
      } catch (error) {
        const axiosError = error as AxiosError;
        expect(axiosError.response?.status).toBe(400);
        expect(axiosError.response?.data).toMatchObject({
          error: 'invalid_url',
          message: 'URL must start with http:// or https://',
          details: {
            providedUrl: 'ftp://example.com/document.pdf',
            validFormats: ['http://', 'https://'],
          },
        });
      }
    });

    it('should reject malformed URLs with 400 error', async () => {
      const requestData = {
        url: 'not-a-valid-url',
      };

      try {
        await axios.post(urlEndpoint, requestData, {
          headers: {
            'Content-Type': 'application/json',
          },
        });
        throw new Error('Expected request to fail with 400 error');
      } catch (error) {
        const axiosError = error as AxiosError;
        expect(axiosError.response?.status).toBe(400);
        expect(axiosError.response?.data).toMatchObject({
          error: 'invalid_url',
          message: expect.stringContaining('URL'),
        });
      }
    });

    it('should handle inaccessible URLs with 404 error', async () => {
      const requestData = {
        url: 'https://example.com/nonexistent-document.pdf',
      };

      try {
        await axios.post(urlEndpoint, requestData, {
          headers: {
            'Content-Type': 'application/json',
          },
        });
        throw new Error('Expected request to fail with 404 error');
      } catch (error) {
        const axiosError = error as AxiosError;
        expect(axiosError.response?.status).toBe(404);
        expect(axiosError.response?.data).toMatchObject({
          error: 'url_not_found',
          message: 'Unable to access the provided URL',
          details: {
            url: 'https://example.com/nonexistent-document.pdf',
            httpStatus: expect.any(Number),
          },
        });
      }
    });

    it('should reject non-PDF content with 422 error', async () => {
      const requestData = {
        url: 'https://www.google.com', // Returns HTML, not PDF
      };

      try {
        await axios.post(urlEndpoint, requestData, {
          headers: {
            'Content-Type': 'application/json',
          },
        });
        throw new Error('Expected request to fail with 422 error');
      } catch (error) {
        const axiosError = error as AxiosError;
        expect(axiosError.response?.status).toBe(422);
        expect(axiosError.response?.data).toMatchObject({
          error: 'invalid_content_type',
          message: 'URL does not point to a PDF file',
          details: {
            detectedType: expect.stringContaining('text/html'),
            expectedType: 'application/pdf',
          },
        });
      }
    });

    it('should validate filename length limits', async () => {
      const requestData = {
        url: 'https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf',
        filename: 'a'.repeat(256) + '.pdf', // Exceeds 255 character limit
      };

      try {
        await axios.post(urlEndpoint, requestData, {
          headers: {
            'Content-Type': 'application/json',
          },
        });
        throw new Error('Expected request to fail with validation error');
      } catch (error) {
        const axiosError = error as AxiosError;
        expect(axiosError.response?.status).toBe(400);
        expect((axiosError.response?.data as { message: string }).message).toContain('filename too long');
      }
    });

    it('should require URL parameter', async () => {
      const requestData = {
        filename: 'test.pdf',
        // Missing required 'url' parameter
      };

      try {
        await axios.post(urlEndpoint, requestData, {
          headers: {
            'Content-Type': 'application/json',
          },
        });
        throw new Error('Expected request to fail with validation error');
      } catch (error) {
        const axiosError = error as AxiosError;
        expect(axiosError.response?.status).toBe(400);
        expect((axiosError.response?.data as { message: string }).message).toContain('url is required');
      }
    });
  });
});