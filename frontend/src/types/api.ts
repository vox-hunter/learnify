// T019: API Response Types
// Defines TypeScript interfaces for all backend API responses

// Document Upload API Types
export interface DocumentUploadRequest {
  file: File;
  metadata?: {
    title?: string;
    description?: string;
  };
}

export interface DocumentUploadResponse {
  success: boolean;
  documentId: string;
  filename: string;
  size: number;
  uploadedAt: string;
  processingStatus: 'pending' | 'processing' | 'completed' | 'failed';
  error?: string;
}

// URL Document Processing API Types
export interface URLDocumentRequest {
  url: string;
  options?: {
    includeImages?: boolean;
    maxPages?: number;
  };
}

export interface URLDocumentResponse {
  success: boolean;
  documentId: string;
  url: string;
  title?: string;
  contentLength: number;
  processingStatus: 'pending' | 'processing' | 'completed' | 'failed';
  extractedAt: string;
  error?: string;
}

// Course Generation API Types
export interface CourseGenerationRequest {
  documentId: string;
  options: {
    courseType: 'quiz' | 'flashcards' | 'summary' | 'mixed';
    difficulty: 'easy' | 'medium' | 'hard';
    questionCount?: number;
    topics?: string[];
  };
}

export interface CourseGenerationResponse {
  success: boolean;
  courseId: string;
  documentId: string;
  generationStatus: 'pending' | 'generating' | 'completed' | 'failed';
  estimatedCompletion?: string;
  progress?: number;
  error?: string;
}

// Course Status API Types
export interface CourseStatusResponse {
  success: boolean;
  courseId: string;
  status: 'pending' | 'generating' | 'completed' | 'failed';
  progress: number;
  course?: CourseData;
  error?: string;
}

// Authentication API Types
export interface LoginRequest {
  email: string;
  password: string;
  rememberMe?: boolean;
}

export interface LoginResponse {
  success: boolean;
  user?: UserProfile;
  token?: string;
  refreshToken?: string;
  expiresAt?: string;
  error?: string;
}

export interface UserProfile {
  id: string;
  email: string;
  name: string;
  avatar?: string;
  createdAt: string;
  lastLoginAt?: string;
  preferences: {
    language: string;
    theme: 'light' | 'dark' | 'auto';
    notifications: boolean;
  };
}

// Generic API Error Response
export interface APIError {
  success: false;
  error: string;
  code?: string;
  details?: Record<string, unknown>;
  timestamp: string;
}

// API Response Wrapper
export type APIResponse<T> = T | APIError;

// Course Data Structure
export interface CourseData {
  id: string;
  title: string;
  description?: string;
  type: 'quiz' | 'flashcards' | 'summary' | 'mixed';
  difficulty: 'easy' | 'medium' | 'hard';
  createdAt: string;
  updatedAt: string;
  questions: Question[];
  metadata: {
    documentId: string;
    questionCount: number;
    estimatedDuration: number;
    topics: string[];
  };
}

export interface Question {
  id: string;
  type: 'multiple_choice' | 'true_false' | 'fill_in_blank' | 'short_answer';
  question: string;
  options?: string[];
  correctAnswer: string | string[];
  explanation?: string;
  difficulty: 'easy' | 'medium' | 'hard';
  topic?: string;
}