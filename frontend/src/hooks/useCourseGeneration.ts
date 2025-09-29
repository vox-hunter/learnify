import { useState, useCallback, useEffect } from 'react';
import { courseService } from '../services/courseService';
import type { CourseGenerationRequest, CourseData } from '../types/api';

interface CourseGenerationState {
  isGenerating: boolean;
  progress: number;
  courseId: string | null;
  course: CourseData | null;
  error: string | null;
  estimatedCompletion?: string;
}

interface UseCourseGenerationReturn extends CourseGenerationState {
  generateCourse: (request: CourseGenerationRequest) => Promise<void>;
  checkStatus: () => Promise<void>;
  resetState: () => void;
}

/**
 * Custom hook for managing course generation status and progress
 * Provides state management for document-to-course conversion process
 */
export const useCourseGeneration = (): UseCourseGenerationReturn => {
  const [state, setState] = useState<CourseGenerationState>({
    isGenerating: false,
    progress: 0,
    courseId: null,
    course: null,
    error: null,
    estimatedCompletion: undefined
  });

  const generateCourse = useCallback(async (request: CourseGenerationRequest) => {
    setState(prev => ({
      ...prev,
      isGenerating: true,
      progress: 0,
      error: null,
      courseId: null,
      course: null
    }));

    try {
      const response = await courseService.generateCourse(request.documentId, request.options);
      
      setState(prev => ({
        ...prev,
        courseId: response.courseId,
        progress: response.progress || 0,
        estimatedCompletion: response.estimatedCompletion
      }));
    } catch (error) {
      setState(prev => ({
        ...prev,
        isGenerating: false,
        error: error instanceof Error ? error.message : 'Failed to start course generation'
      }));
    }
  }, []);

  const checkStatus = useCallback(async () => {
    if (!state.courseId) return;

    try {
      const statusResponse = await courseService.getCourseStatus(state.courseId);
      
      setState(prev => ({
        ...prev,
        progress: statusResponse.progress,
        isGenerating: statusResponse.status === 'generating',
        course: statusResponse.course || null,
        error: statusResponse.error || null
      }));
    } catch (error) {
      setState(prev => ({
        ...prev,
        error: error instanceof Error ? error.message : 'Failed to check course status'
      }));
    }
  }, [state.courseId]);

  const resetState = useCallback(() => {
    setState({
      isGenerating: false,
      progress: 0,
      courseId: null,
      course: null,
      error: null,
      estimatedCompletion: undefined
    });
  }, []);

  // Auto-poll for status updates when generating
  useEffect(() => {
    if (!state.isGenerating || !state.courseId) return;

    const pollInterval = setInterval(() => {
      checkStatus();
    }, 2000); // Poll every 2 seconds

    return () => clearInterval(pollInterval);
  }, [state.isGenerating, state.courseId, checkStatus]);

  // Stop polling when course is complete
  useEffect(() => {
    if (state.course && state.isGenerating) {
      setState(prev => ({ ...prev, isGenerating: false }));
    }
  }, [state.course, state.isGenerating]);

  return {
    ...state,
    generateCourse,
    checkStatus,
    resetState
  };
};