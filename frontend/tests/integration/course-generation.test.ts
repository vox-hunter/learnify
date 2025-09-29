import axios, { AxiosError } from 'axios';
import { describe, it, expect, beforeAll } from '@jest/globals';

describe('Course Generation API Integration Tests', () => {
  const API_BASE_URL = 'http://localhost:8000';
  const generateEndpoint = `${API_BASE_URL}/api/courses/generate`;
  const uploadEndpoint = `${API_BASE_URL}/api/documents/upload`;

  beforeAll(async () => {
    // Verify the backend is running
    try {
      await axios.get(`${API_BASE_URL}/health`);
    } catch {
      throw new Error('Backend server is not running. Please start the Python backend first.');
    }
  });

  describe('POST /api/courses/generate', () => {
    it('should successfully initiate course generation for valid document', async () => {
      // First, upload a document to get a valid document ID
      const pdfContent = Buffer.from('%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n>>\nendobj\nxref\n0 4\n0000000000 65535 f \n0000000010 00000 n \n0000000079 00000 n \n0000000173 00000 n \ntrailer\n<<\n/Size 4\n/Root 1 0 R\n>>\nstartxref\n301\n%%EOF');
      
      const formData = new FormData();
      const file = new File([pdfContent], 'test.pdf', { type: 'application/pdf' });
      formData.append('file', file);

      const uploadResponse = await axios.post(uploadEndpoint, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      
      const documentId = uploadResponse.data.id;

      // Now test course generation
      const requestData = {
        documentId,
      };

      const response = await axios.post(generateEndpoint, requestData, {
        headers: {
          'Content-Type': 'application/json',
        },
      });

      expect(response.status).toBe(202);
      expect(response.data).toMatchObject({
        jobId: expect.stringMatching(/^job_\w+$/),
        status: 'queued',
        message: 'Course generation started',
        estimatedDuration: expect.stringContaining('seconds'),
      });
    });

    it('should reject missing document ID with 400 error', async () => {
      const requestData = {
        // Missing required documentId
      };

      try {
        await axios.post(generateEndpoint, requestData, {
          headers: {
            'Content-Type': 'application/json',
          },
        });
        throw new Error('Expected request to fail with 400 error');
      } catch (error) {
        const axiosError = error as AxiosError;
        expect(axiosError.response?.status).toBe(400);
        expect(axiosError.response?.data).toMatchObject({
          error: 'invalid_document_id',
          message: 'Document ID is required',
          details: {
            field: 'documentId',
            issue: 'missing_required_field',
          },
        });
      }
    });

    it('should reject empty document ID with 400 error', async () => {
      const requestData = {
        documentId: '',
      };

      try {
        await axios.post(generateEndpoint, requestData, {
          headers: {
            'Content-Type': 'application/json',
          },
        });
        throw new Error('Expected request to fail with 400 error');
      } catch (error) {
        const axiosError = error as AxiosError;
        expect(axiosError.response?.status).toBe(400);
        expect(axiosError.response?.data).toMatchObject({
          error: 'invalid_document_id',
          message: expect.stringContaining('Document ID'),
        });
      }
    });

    it('should reject invalid document ID with 404 error', async () => {
      const requestData = {
        documentId: 'doc_invalid123',
      };

      try {
        await axios.post(generateEndpoint, requestData, {
          headers: {
            'Content-Type': 'application/json',
          },
        });
        throw new Error('Expected request to fail with 404 error');
      } catch (error) {
        const axiosError = error as AxiosError;
        expect(axiosError.response?.status).toBe(404);
        expect(axiosError.response?.data).toMatchObject({
          error: 'document_not_found',
          message: 'Document with specified ID does not exist',
          details: {
            documentId: 'doc_invalid123',
          },
        });
      }
    });

    it('should handle duplicate generation requests with 409 error', async () => {
      // First, upload a document
      const pdfContent = Buffer.from('%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n>>\nendobj\nxref\n0 4\n0000000000 65535 f \n0000000010 00000 n \n0000000079 00000 n \n0000000173 00000 n \ntrailer\n<<\n/Size 4\n/Root 1 0 R\n>>\nstartxref\n301\n%%EOF');
      
      const formData = new FormData();
      const file = new File([pdfContent], 'duplicate-test.pdf', { type: 'application/pdf' });
      formData.append('file', file);

      const uploadResponse = await axios.post(uploadEndpoint, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      
      const documentId = uploadResponse.data.id;
      const requestData = { documentId };

      // First generation request should succeed
      const firstResponse = await axios.post(generateEndpoint, requestData, {
        headers: {
          'Content-Type': 'application/json',
        },
      });
      expect(firstResponse.status).toBe(202);

      // Second generation request should fail with 409
      try {
        await axios.post(generateEndpoint, requestData, {
          headers: {
            'Content-Type': 'application/json',
          },
        });
        throw new Error('Expected second request to fail with 409 error');
      } catch (error) {
        const axiosError = error as AxiosError;
        expect(axiosError.response?.status).toBe(409);
        expect(axiosError.response?.data).toMatchObject({
          error: 'document_processing',
          message: 'Course generation already in progress for this document',
          details: {
            documentId,
            existingJobId: expect.stringMatching(/^job_\w+$/),
            status: 'processing',
          },
        });
      }
    });

    it('should handle corrupted document with 422 error', async () => {
      // Upload a corrupted document first
      const corruptedContent = Buffer.from('corrupted pdf content');
      const formData = new FormData();
      const file = new File([corruptedContent], 'corrupted.pdf', { type: 'application/pdf' });
      formData.append('file', file);

      // This should still create a document record, but mark it as invalid
      let documentId: string;
      try {
        const uploadResponse = await axios.post(uploadEndpoint, formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });
        documentId = uploadResponse.data.id;
      } catch {
        // If upload fails due to validation, skip this test
        return;
      }

      const requestData = { documentId };

      try {
        await axios.post(generateEndpoint, requestData, {
          headers: {
            'Content-Type': 'application/json',
          },
        });
        throw new Error('Expected request to fail with 422 error');
      } catch (error) {
        const axiosError = error as AxiosError;
        expect(axiosError.response?.status).toBe(422);
        expect(axiosError.response?.data).toMatchObject({
          error: 'document_invalid',
          message: 'Document failed validation and cannot be processed',
          details: {
            documentId,
            validationErrors: expect.arrayContaining([
              expect.stringContaining('corrupted'),
            ]),
          },
        });
      }
    });
  });
});