import axios, { AxiosError } from 'axios';
import { describe, it, expect, beforeAll } from '@jest/globals';

describe('Document Upload API Integration Tests', () => {
  const API_BASE_URL = 'http://localhost:8000';
  const uploadEndpoint = `${API_BASE_URL}/api/documents/upload`;

  beforeAll(async () => {
    // Verify the backend is running
    try {
      await axios.get(`${API_BASE_URL}/health`);
    } catch {
      throw new Error('Backend server is not running. Please start the Python backend first.');
    }
  });

  describe('POST /api/documents/upload', () => {
    it('should successfully upload a valid PDF file', async () => {
      // Create a mock PDF file data
      const pdfContent = Buffer.from('%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n>>\nendobj\nxref\n0 4\n0000000000 65535 f \n0000000010 00000 n \n0000000079 00000 n \n0000000173 00000 n \ntrailer\n<<\n/Size 4\n/Root 1 0 R\n>>\nstartxref\n301\n%%EOF');
      
      const formData = new FormData();
      const file = new File([pdfContent], 'test.pdf', { type: 'application/pdf' });
      formData.append('file', file);

      const response = await axios.post(uploadEndpoint, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      expect(response.status).toBe(201);
      expect(response.data).toMatchObject({
        id: expect.stringMatching(/^doc_\w+$/),
        name: 'test.pdf',
        type: 'pdf',
        size: expect.any(Number),
        status: 'uploaded',
        uploadedAt: expect.stringMatching(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$/),
      });
    });

    it('should accept custom filename parameter', async () => {
      const pdfContent = Buffer.from('%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n>>\nendobj\nxref\n0 4\n0000000000 65535 f \n0000000010 00000 n \n0000000079 00000 n \n0000000173 00000 n \ntrailer\n<<\n/Size 4\n/Root 1 0 R\n>>\nstartxref\n301\n%%EOF');
      
      const formData = new FormData();
      const file = new File([pdfContent], 'original.pdf', { type: 'application/pdf' });
      formData.append('file', file);
      formData.append('filename', 'custom-name.pdf');

      const response = await axios.post(uploadEndpoint, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      expect(response.status).toBe(201);
      expect(response.data.name).toBe('custom-name.pdf');
    });

    it('should reject non-PDF files with 400 error', async () => {
      const textContent = 'This is not a PDF file';
      const formData = new FormData();
      const file = new File([textContent], 'test.txt', { type: 'text/plain' });
      formData.append('file', file);

      try {
        await axios.post(uploadEndpoint, formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });
        throw new Error('Expected request to fail with 400 error');
      } catch (error) {
        const axiosError = error as AxiosError;
        expect(axiosError.response?.status).toBe(400);
        expect(axiosError.response?.data).toMatchObject({
          error: 'invalid_file',
          message: 'File must be a valid PDF',
          details: {
            filename: 'test.txt',
            actualType: 'text/plain',
            expectedType: 'application/pdf',
          },
        });
      }
    });

    it('should reject files larger than 20MB with 413 error', async () => {
      // Create a large buffer (simulating >20MB file)
      const largeContent = Buffer.alloc(21 * 1024 * 1024); // 21MB
      const formData = new FormData();
      const file = new File([largeContent], 'large.pdf', { type: 'application/pdf' });
      formData.append('file', file);

      try {
        await axios.post(uploadEndpoint, formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });
        throw new Error('Expected request to fail with 413 error');
      } catch (error) {
        const axiosError = error as AxiosError;
        expect(axiosError.response?.status).toBe(413);
        expect(axiosError.response?.data).toMatchObject({
          error: 'file_too_large',
          message: 'File size exceeds 20MB limit',
          details: {
            fileSize: expect.any(Number),
            maxSize: 20971520,
          },
        });
      }
    });

    it('should reject corrupted PDF files with 422 error', async () => {
      const corruptedContent = Buffer.from('corrupted pdf content');
      const formData = new FormData();
      const file = new File([corruptedContent], 'corrupted.pdf', { type: 'application/pdf' });
      formData.append('file', file);

      try {
        await axios.post(uploadEndpoint, formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });
        throw new Error('Expected request to fail with 422 error');
      } catch (error) {
        const axiosError = error as AxiosError;
        expect(axiosError.response?.status).toBe(422);
        expect(axiosError.response?.data).toMatchObject({
          error: 'validation_failed',
          message: 'PDF file appears to be corrupted or empty',
          details: {
            validationErrors: expect.arrayContaining([
              expect.stringContaining('Invalid PDF header')
            ]),
          },
        });
      }
    });

    it('should validate filename length limits', async () => {
      const pdfContent = Buffer.from('%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n>>\nendobj\nxref\n0 4\n0000000000 65535 f \n0000000010 00000 n \n0000000079 00000 n \n0000000173 00000 n \ntrailer\n<<\n/Size 4\n/Root 1 0 R\n>>\nstartxref\n301\n%%EOF');
      
      const formData = new FormData();
      const file = new File([pdfContent], 'test.pdf', { type: 'application/pdf' });
      formData.append('file', file);
      
      // Create a filename longer than 255 characters
      const longFilename = 'a'.repeat(256) + '.pdf';
      formData.append('filename', longFilename);

      try {
        await axios.post(uploadEndpoint, formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });
        throw new Error('Expected request to fail with validation error');
      } catch (error) {
        const axiosError = error as AxiosError;
        expect(axiosError.response?.status).toBe(400);
        expect((axiosError.response?.data as { message: string }).message).toContain('filename too long');
      }
    });
  });
});