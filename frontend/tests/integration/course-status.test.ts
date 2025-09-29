import axios, { AxiosError } from 'axios';
import { describe, it, expect, beforeAll } from '@jest/globals';

describe('Course Status API Integration Tests', () => {
  const API_BASE_URL = 'http://localhost:8000';
  const statusEndpoint = (jobId: string) => `${API_BASE_URL}/api/courses/status/${jobId}`;
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

  describe('GET /api/courses/status/{jobId}', () => {
    it('should return job status for valid job ID in processing state', async () => {
      // First, create a job by uploading a document and generating a course
      const pdfContent = Buffer.from('%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n>>\nendobj\nxref\n0 4\n0000000000 65535 f \n0000000010 00000 n \n0000000079 00000 n \n0000000173 00000 n \ntrailer\n<<\n/Size 4\n/Root 1 0 R\n>>\nstartxref\n301\n%%EOF');
      
      const formData = new FormData();
      const file = new File([pdfContent], 'status-test.pdf', { type: 'application/pdf' });
      formData.append('file', file);

      const uploadResponse = await axios.post(uploadEndpoint, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      
      const documentId = uploadResponse.data.id;
      
      const generateResponse = await axios.post(generateEndpoint, { documentId }, {
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      const jobId = generateResponse.data.jobId;

      // Check job status
      const response = await axios.get(statusEndpoint(jobId));

      expect(response.status).toBe(200);
      expect(response.data).toMatchObject({
        jobId,
        status: expect.stringMatching(/^(queued|processing|completed|error)$/),
        progress: expect.any(Number),
        message: expect.any(String),
      });

      // If processing, should have time remaining estimate
      if (response.data.status === 'processing') {
        expect(response.data).toHaveProperty('estimatedTimeRemaining');
        expect(response.data.estimatedTimeRemaining).toMatch(/\d+-\d+ seconds?/);
      }
    });

    it('should return completed job status with course details', async () => {
      // This test assumes we can create a job and wait for completion
      // In a real scenario, you might need to mock or wait for completion
      const pdfContent = Buffer.from('%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n>>\nendobj\nxref\n0 4\n0000000000 65535 f \n0000000010 00000 n \n0000000079 00000 n \n0000000173 00000 n \ntrailer\n<<\n/Size 4\n/Root 1 0 R\n>>\nstartxref\n301\n%%EOF');
      
      const formData = new FormData();
      const file = new File([pdfContent], 'completion-test.pdf', { type: 'application/pdf' });
      formData.append('file', file);

      const uploadResponse = await axios.post(uploadEndpoint, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      
      const documentId = uploadResponse.data.id;
      
      const generateResponse = await axios.post(generateEndpoint, { documentId }, {
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      const jobId = generateResponse.data.jobId;

      // Poll for completion (with timeout)
      let attempts = 0;
      const maxAttempts = 30; // 30 seconds timeout
      let lastResponse;

      while (attempts < maxAttempts) {
        lastResponse = await axios.get(statusEndpoint(jobId));
        
        if (lastResponse.data.status === 'completed') {
          expect(lastResponse.status).toBe(200);
          expect(lastResponse.data).toMatchObject({
            jobId,
            status: 'completed',
            progress: 100,
            message: expect.stringContaining('success'),
            result: {
              id: expect.stringMatching(/^course_\w+$/),
              title: expect.any(String),
              description: expect.any(String),
              sections: expect.arrayContaining([
                expect.objectContaining({
                  id: expect.stringMatching(/^section_\w+$/),
                  title: expect.any(String),
                  content: expect.any(String),
                  order: expect.any(Number),
                  quiz: expect.objectContaining({
                    id: expect.stringMatching(/^quiz_\w+$/),
                    questions: expect.any(Array),
                    totalPoints: expect.any(Number),
                    passingScore: expect.any(Number),
                  }),
                }),
              ]),
              totalQuestions: expect.any(Number),
              estimatedDuration: expect.any(Number),
              createdAt: expect.stringMatching(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$/),
            },
          });
          return;
        }

        if (lastResponse.data.status === 'error') {
          expect(lastResponse.status).toBe(200);
          expect(lastResponse.data).toMatchObject({
            jobId,
            status: 'error',
            progress: 100,
            message: expect.stringContaining('failed'),
            error: {
              code: expect.any(String),
              message: expect.any(String),
              details: expect.any(String),
            },
          });
          return;
        }

        // Wait 1 second before next attempt
        await new Promise(resolve => setTimeout(resolve, 1000));
        attempts++;
      }

      // If we reach here, job didn't complete in time - verify it's still processing
      expect(lastResponse?.data.status).toMatch(/^(queued|processing)$/);
    });

    it('should reject invalid job ID with 404 error', async () => {
      const invalidJobId = 'job_invalid123';

      try {
        await axios.get(statusEndpoint(invalidJobId));
        throw new Error('Expected request to fail with 404 error');
      } catch (error) {
        const axiosError = error as AxiosError;
        expect(axiosError.response?.status).toBe(404);
        expect(axiosError.response?.data).toMatchObject({
          error: 'job_not_found',
          message: 'Job with specified ID does not exist',
          details: {
            jobId: invalidJobId,
          },
        });
      }
    });

    it('should reject malformed job ID with 404 error', async () => {
      const malformedJobId = 'not-a-job-id';

      try {
        await axios.get(statusEndpoint(malformedJobId));
        throw new Error('Expected request to fail with 404 error');
      } catch (error) {
        const axiosError = error as AxiosError;
        expect(axiosError.response?.status).toBe(404);
        expect(axiosError.response?.data).toMatchObject({
          error: 'job_not_found',
          message: expect.stringContaining('Job'),
        });
      }
    });

    it('should validate progress is between 0 and 100', async () => {
      // Create a job to test
      const pdfContent = Buffer.from('%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n>>\nendobj\nxref\n0 4\n0000000000 65535 f \n0000000010 00000 n \n0000000079 00000 n \n0000000173 00000 n \ntrailer\n<<\n/Size 4\n/Root 1 0 R\n>>\nstartxref\n301\n%%EOF');
      
      const formData = new FormData();
      const file = new File([pdfContent], 'progress-test.pdf', { type: 'application/pdf' });
      formData.append('file', file);

      const uploadResponse = await axios.post(uploadEndpoint, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      
      const documentId = uploadResponse.data.id;
      
      const generateResponse = await axios.post(generateEndpoint, { documentId }, {
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      const jobId = generateResponse.data.jobId;

      const response = await axios.get(statusEndpoint(jobId));

      expect(response.status).toBe(200);
      expect(response.data.progress).toBeGreaterThanOrEqual(0);
      expect(response.data.progress).toBeLessThanOrEqual(100);
      expect(typeof response.data.progress).toBe('number');
    });
  });
});