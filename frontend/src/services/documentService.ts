// T024: Document Service API Calls
// Handles all document-related API operations including upload and URL processing

import type {
  DocumentUploadRequest,
  DocumentUploadResponse,
  URLDocumentRequest,
  URLDocumentResponse
} from '../types/api';
import { httpClient } from './httpClient';

// Define Document interface for service use
interface Document {
  id: string;
  name: string;
  type: 'pdf' | 'url';
  content: string;
  status: 'uploading' | 'processing' | 'completed' | 'error';
  uploadedAt: string;
  size?: number;
}

/**
 * Document Service - Manages document upload and processing operations
 */
export class DocumentService {
  private static readonly ENDPOINTS = {
    UPLOAD: '/api/documents/upload',
    URL_PROCESS: '/api/documents/url',
    GET_DOCUMENT: '/api/documents',
    DELETE_DOCUMENT: '/api/documents'
  } as const;

  /**
   * Upload a file document to the server
   * @param file - File to upload
   * @param metadata - Optional metadata
   * @returns Promise with upload response
   */
  static async uploadDocument(file: File, metadata?: DocumentUploadRequest['metadata']): Promise<DocumentUploadResponse> {
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      if (metadata) {
        formData.append('metadata', JSON.stringify(metadata));
      }

      const response = await httpClient.post<DocumentUploadResponse>(
        this.ENDPOINTS.UPLOAD,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data'
          },
          timeout: 60000, // 60 second timeout for large files
          onUploadProgress: (progressEvent) => {
            const progress = progressEvent.total 
              ? Math.round((progressEvent.loaded * 100) / progressEvent.total)
              : 0;
            // Emit progress event for UI updates
            this.emitUploadProgress(file.name, progress);
          }
        }
      );

      return response.data;
    } catch (error) {
      console.error('Document upload failed:', error);
      throw this.handleApiError(error, 'Failed to upload document');
    }
  }

  /**
   * Process a document from URL
   * @param url - URL to process
   * @param options - Processing options
   * @returns Promise with URL processing response
   */
  static async processUrlDocument(url: string, options?: URLDocumentRequest['options']): Promise<URLDocumentResponse> {
    try {
      const request: URLDocumentRequest = {
        url,
        options: {
          includeImages: options?.includeImages ?? true,
          maxPages: options?.maxPages ?? 100,
          ...options
        }
      };

      const response = await httpClient.post<URLDocumentResponse>(
        this.ENDPOINTS.URL_PROCESS,
        request,
        {
          timeout: 120000 // 2 minute timeout for URL processing
        }
      );

      return response.data;
    } catch (error) {
      console.error('URL document processing failed:', error);
      throw this.handleApiError(error, 'Failed to process URL document');
    }
  }

  /**
   * Get document by ID
   * @param documentId - Document identifier
   * @returns Promise with document data
   */
  static async getDocument(documentId: string): Promise<Document> {
    try {
      const response = await httpClient.get<Document>(
        `${this.ENDPOINTS.GET_DOCUMENT}/${documentId}`
      );

      return response.data;
    } catch (error) {
      console.error('Failed to get document:', error);
      throw this.handleApiError(error, 'Failed to retrieve document');
    }
  }

  /**
   * Get all documents for current user
   * @returns Promise with documents array
   */
  static async getDocuments(): Promise<Document[]> {
    try {
      const response = await httpClient.get<{ documents: Document[] }>(
        this.ENDPOINTS.GET_DOCUMENT
      );

      return response.data.documents || [];
    } catch (error) {
      console.error('Failed to get documents:', error);
      throw this.handleApiError(error, 'Failed to retrieve documents');
    }
  }

  /**
   * Delete a document
   * @param documentId - Document identifier
   * @returns Promise with deletion confirmation
   */
  static async deleteDocument(documentId: string): Promise<{ success: boolean }> {
    try {
      const response = await httpClient.delete<{ success: boolean }>(
        `${this.ENDPOINTS.DELETE_DOCUMENT}/${documentId}`
      );

      return response.data;
    } catch (error) {
      console.error('Failed to delete document:', error);
      throw this.handleApiError(error, 'Failed to delete document');
    }
  }

  /**
   * Check document processing status
   * @param documentId - Document identifier
   * @returns Promise with processing status
   */
  static async getProcessingStatus(documentId: string): Promise<{ status: string; progress?: number }> {
    try {
      const response = await httpClient.get<{ status: string; progress?: number }>(
        `${this.ENDPOINTS.GET_DOCUMENT}/${documentId}/status`
      );

      return response.data;
    } catch (error) {
      console.error('Failed to get processing status:', error);
      throw this.handleApiError(error, 'Failed to check processing status');
    }
  }

  /**
   * Validate file before upload
   * @param file - File to validate
   * @returns Validation result
   */
  static validateFile(file: File): { isValid: boolean; error?: string } {
    // Check file type
    const allowedTypes = ['application/pdf', 'text/plain', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
    if (!allowedTypes.includes(file.type)) {
      return {
        isValid: false,
        error: 'File type not supported. Please upload PDF, TXT, DOC, or DOCX files.'
      };
    }

    // Check file size (20MB limit)
    const maxSizeBytes = 20 * 1024 * 1024;
    if (file.size > maxSizeBytes) {
      return {
        isValid: false,
        error: 'File size exceeds 20MB limit. Please choose a smaller file.'
      };
    }

    // Check for empty file
    if (file.size === 0) {
      return {
        isValid: false,
        error: 'File is empty. Please choose a valid file.'
      };
    }

    return { isValid: true };
  }

  /**
   * Validate URL before processing
   * @param url - URL to validate
   * @returns Validation result
   */
  static validateUrl(url: string): { isValid: boolean; error?: string } {
    try {
      const urlObject = new URL(url);
      
      // Check protocol
      if (!['http:', 'https:'].includes(urlObject.protocol)) {
        return {
          isValid: false,
          error: 'URL must use HTTP or HTTPS protocol.'
        };
      }

      // Check for localhost in production
      if (import.meta.env.PROD && urlObject.hostname === 'localhost') {
        return {
          isValid: false,
          error: 'Localhost URLs are not allowed in production.'
        };
      }

      return { isValid: true };
    } catch {
      return {
        isValid: false,
        error: 'Invalid URL format. Please enter a valid HTTP or HTTPS URL.'
      };
    }
  }

  /**
   * Emit upload progress event for UI updates
   * @private
   */
  private static emitUploadProgress(fileName: string, progress: number): void {
    const event = new CustomEvent('document-upload-progress', {
      detail: { fileName, progress }
    });
    window.dispatchEvent(event);
  }

  /**
   * Handle API errors with user-friendly messages
   * @private
   */
  private static handleApiError(error: unknown, defaultMessage: string): Error {
    if (error instanceof Error) {
      return error;
    }
    
    // Handle Axios errors
    if (typeof error === 'object' && error !== null && 'response' in error) {
      const axiosError = error as { response?: { data?: { error?: string; message?: string } } };
      const serverMessage = axiosError.response?.data?.error || axiosError.response?.data?.message;
      if (serverMessage) {
        return new Error(serverMessage);
      }
    }

    return new Error(defaultMessage);
  }
}

// Export singleton instance for convenience
export const documentService = DocumentService;

// Export types for external use
export type { DocumentUploadRequest, DocumentUploadResponse, URLDocumentRequest, URLDocumentResponse };