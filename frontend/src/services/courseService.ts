// T025: Course Service API Calls
// Handles all course-related API operations including generation and management

import type {
  CourseGenerationRequest,
  CourseGenerationResponse,
  CourseStatusResponse,
  CourseData
} from '../types/api';
import { httpClient } from './httpClient';

/**
 * Course Service - Manages course generation, retrieval, and quiz operations
 */
export class CourseService {
  private static readonly ENDPOINTS = {
    GENERATE: '/api/courses/generate',
    GET_COURSE: '/api/courses',
    GET_STATUS: '/api/courses/status',
    UPDATE_COURSE: '/api/courses',
    DELETE_COURSE: '/api/courses',
    SUBMIT_QUIZ: '/api/courses/quiz/submit',
    GET_RESULTS: '/api/courses/quiz/results'
  } as const;

  /**
   * Generate a new course from a document
   * @param documentId - Source document ID
   * @param options - Course generation options
   * @returns Promise with generation response
   */
  static async generateCourse(documentId: string, options: CourseGenerationRequest['options']): Promise<CourseGenerationResponse> {
    try {
      const request: CourseGenerationRequest = {
        documentId,
        options: {
          courseType: options.courseType || 'mixed',
          difficulty: options.difficulty || 'medium',
          questionCount: options.questionCount || 10,
          topics: options.topics || []
        }
      };

      const response = await httpClient.post<CourseGenerationResponse>(
        this.ENDPOINTS.GENERATE,
        request,
        {
          timeout: 180000 // 3 minute timeout for course generation
        }
      );

      return response.data;
    } catch (error) {
      console.error('Course generation failed:', error);
      throw this.handleApiError(error, 'Failed to generate course');
    }
  }

  /**
   * Get course generation status
   * @param courseId - Course identifier
   * @returns Promise with status response
   */
  static async getCourseStatus(courseId: string): Promise<CourseStatusResponse> {
    try {
      const response = await httpClient.get<CourseStatusResponse>(
        `${this.ENDPOINTS.GET_STATUS}/${courseId}`
      );

      return response.data;
    } catch (error) {
      console.error('Failed to get course status:', error);
      throw this.handleApiError(error, 'Failed to check course status');
    }
  }

  /**
   * Get course by ID
   * @param courseId - Course identifier
   * @returns Promise with course data
   */
  static async getCourse(courseId: string): Promise<CourseData> {
    try {
      const response = await httpClient.get<CourseData>(
        `${this.ENDPOINTS.GET_COURSE}/${courseId}`
      );

      return response.data;
    } catch (error) {
      console.error('Failed to get course:', error);
      throw this.handleApiError(error, 'Failed to retrieve course');
    }
  }

  /**
   * Get all courses for current user
   * @param filters - Optional filters
   * @returns Promise with courses array
   */
  static async getCourses(filters?: {
    type?: 'quiz' | 'flashcards' | 'summary' | 'mixed';
    difficulty?: 'easy' | 'medium' | 'hard';
    limit?: number;
    offset?: number;
  }): Promise<{ courses: CourseData[]; total: number }> {
    try {
      const params = new URLSearchParams();
      
      if (filters?.type) params.append('type', filters.type);
      if (filters?.difficulty) params.append('difficulty', filters.difficulty);
      if (filters?.limit) params.append('limit', filters.limit.toString());
      if (filters?.offset) params.append('offset', filters.offset.toString());

      const queryString = params.toString();
      const url = queryString ? `${this.ENDPOINTS.GET_COURSE}?${queryString}` : this.ENDPOINTS.GET_COURSE;

      const response = await httpClient.get<{ courses: CourseData[]; total: number }>(url);

      return response.data;
    } catch (error) {
      console.error('Failed to get courses:', error);
      throw this.handleApiError(error, 'Failed to retrieve courses');
    }
  }

  /**
   * Update course metadata
   * @param courseId - Course identifier
   * @param updates - Course updates
   * @returns Promise with updated course
   */
  static async updateCourse(courseId: string, updates: Partial<CourseData>): Promise<CourseData> {
    try {
      const response = await httpClient.put<CourseData>(
        `${this.ENDPOINTS.UPDATE_COURSE}/${courseId}`,
        updates
      );

      return response.data;
    } catch (error) {
      console.error('Failed to update course:', error);
      throw this.handleApiError(error, 'Failed to update course');
    }
  }

  /**
   * Delete a course
   * @param courseId - Course identifier
   * @returns Promise with deletion confirmation
   */
  static async deleteCourse(courseId: string): Promise<{ success: boolean }> {
    try {
      const response = await httpClient.delete<{ success: boolean }>(
        `${this.ENDPOINTS.DELETE_COURSE}/${courseId}`
      );

      return response.data;
    } catch (error) {
      console.error('Failed to delete course:', error);
      throw this.handleApiError(error, 'Failed to delete course');
    }
  }

  /**
   * Submit quiz answers
   * @param courseId - Course identifier
   * @param answers - Quiz answers
   * @returns Promise with quiz results
   */
  static async submitQuiz(courseId: string, answers: Record<string, string | string[]>): Promise<{
    score: number;
    totalQuestions: number;
    correctAnswers: number;
    results: Array<{
      questionId: string;
      correct: boolean;
      userAnswer: string | string[];
      correctAnswer: string | string[];
      explanation?: string;
    }>;
  }> {
    try {
      const response = await httpClient.post<{
        score: number;
        totalQuestions: number;
        correctAnswers: number;
        results: Array<{
          questionId: string;
          correct: boolean;
          userAnswer: string | string[];
          correctAnswer: string | string[];
          explanation?: string;
        }>;
      }>(
        `${this.ENDPOINTS.SUBMIT_QUIZ}/${courseId}`,
        { answers }
      );

      return response.data;
    } catch (error) {
      console.error('Failed to submit quiz:', error);
      throw this.handleApiError(error, 'Failed to submit quiz answers');
    }
  }

  /**
   * Get quiz results for a course
   * @param courseId - Course identifier
   * @param attemptId - Optional specific attempt ID
   * @returns Promise with quiz results
   */
  static async getQuizResults(courseId: string, attemptId?: string): Promise<{
    attempts: Array<{
      id: string;
      score: number;
      totalQuestions: number;
      completedAt: string;
      timeSpent: number;
    }>;
    bestScore: number;
    averageScore: number;
    totalAttempts: number;
  }> {
    try {
      const url = attemptId 
        ? `${this.ENDPOINTS.GET_RESULTS}/${courseId}/${attemptId}`
        : `${this.ENDPOINTS.GET_RESULTS}/${courseId}`;

      const response = await httpClient.get<{
        attempts: Array<{
          id: string;
          score: number;
          totalQuestions: number;
          completedAt: string;
          timeSpent: number;
        }>;
        bestScore: number;
        averageScore: number;
        totalAttempts: number;
      }>(url);

      return response.data;
    } catch (error) {
      console.error('Failed to get quiz results:', error);
      throw this.handleApiError(error, 'Failed to retrieve quiz results');
    }
  }

  /**
   * Search courses by title or content
   * @param query - Search query
   * @param filters - Optional filters
   * @returns Promise with search results
   */
  static async searchCourses(query: string, filters?: {
    type?: 'quiz' | 'flashcards' | 'summary' | 'mixed';
    difficulty?: 'easy' | 'medium' | 'hard';
    limit?: number;
  }): Promise<{ courses: CourseData[]; total: number }> {
    try {
      const params = new URLSearchParams({ q: query });
      
      if (filters?.type) params.append('type', filters.type);
      if (filters?.difficulty) params.append('difficulty', filters.difficulty);
      if (filters?.limit) params.append('limit', filters.limit.toString());

      const response = await httpClient.get<{ courses: CourseData[]; total: number }>(
        `${this.ENDPOINTS.GET_COURSE}/search?${params.toString()}`
      );

      return response.data;
    } catch (error) {
      console.error('Failed to search courses:', error);
      throw this.handleApiError(error, 'Failed to search courses');
    }
  }

  /**
   * Get course analytics and progress
   * @param courseId - Course identifier
   * @returns Promise with analytics data
   */
  static async getCourseAnalytics(courseId: string): Promise<{
    totalAttempts: number;
    averageScore: number;
    averageTimeSpent: number;
    questionAnalytics: Array<{
      questionId: string;
      correctRate: number;
      averageTime: number;
      commonMistakes: string[];
    }>;
    learningProgress: {
      conceptsMastered: number;
      conceptsInProgress: number;
      conceptsNotStarted: number;
    };
  }> {
    try {
      const response = await httpClient.get<{
        totalAttempts: number;
        averageScore: number;
        averageTimeSpent: number;
        questionAnalytics: Array<{
          questionId: string;
          correctRate: number;
          averageTime: number;
          commonMistakes: string[];
        }>;
        learningProgress: {
          conceptsMastered: number;
          conceptsInProgress: number;
          conceptsNotStarted: number;
        };
      }>(`${this.ENDPOINTS.GET_COURSE}/${courseId}/analytics`);

      return response.data;
    } catch (error) {
      console.error('Failed to get course analytics:', error);
      throw this.handleApiError(error, 'Failed to retrieve course analytics');
    }
  }

  /**
   * Validate course generation options
   * @param options - Options to validate
   * @returns Validation result
   */
  static validateGenerationOptions(options: CourseGenerationRequest['options']): { isValid: boolean; error?: string } {
    if (!options.courseType || !['quiz', 'flashcards', 'summary', 'mixed'].includes(options.courseType)) {
      return {
        isValid: false,
        error: 'Course type must be one of: quiz, flashcards, summary, mixed'
      };
    }

    if (!options.difficulty || !['easy', 'medium', 'hard'].includes(options.difficulty)) {
      return {
        isValid: false,
        error: 'Difficulty must be one of: easy, medium, hard'
      };
    }

    if (options.questionCount && (options.questionCount < 1 || options.questionCount > 50)) {
      return {
        isValid: false,
        error: 'Question count must be between 1 and 50'
      };
    }

    return { isValid: true };
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
export const courseService = CourseService;

// Export types for external use
export type { CourseGenerationRequest, CourseGenerationResponse, CourseStatusResponse, CourseData };