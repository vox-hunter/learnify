import { useState, useCallback, useEffect, useMemo } from 'react';
import { courseService } from '../services/courseService';
import type { Question } from '../types/api';

export interface QuizAnswer {
  questionId: string;
  type: string;
  value: string | boolean | string[];
  isCorrect?: boolean;
}

interface QuizProgressState {
  currentQuestionIndex: number;
  answers: Record<string, QuizAnswer>;
  isSubmitted: boolean;
  score: number;
  totalQuestions: number;
  timeSpent: number;
  startTime: number | null;
  isLoading: boolean;
  error: string | null;
}

interface UseQuizProgressReturn extends QuizProgressState {
  // Navigation
  goToNext: () => void;
  goToPrevious: () => void;
  goToQuestion: (index: number) => void;
  
  // Answer management
  setAnswer: (questionId: string, answer: QuizAnswer) => void;
  getAnswer: (questionId: string) => QuizAnswer | null;
  
  // Quiz control
  startQuiz: () => void;
  submitQuiz: (courseId: string) => Promise<void>;
  resetQuiz: () => void;
  
  // Progress calculations
  progress: number;
  isComplete: boolean;
  canGoNext: boolean;
  canGoPrevious: boolean;
  answeredCount: number;
  unansweredQuestions: number[];
}

/**
 * Custom hook for tracking quiz completion and scoring
 * Manages quiz state, progress, and submission logic
 */
export const useQuizProgress = (questions: Question[] = []): UseQuizProgressReturn => {
  const [state, setState] = useState<QuizProgressState>({
    currentQuestionIndex: 0,
    answers: {},
    isSubmitted: false,
    score: 0,
    totalQuestions: questions.length,
    timeSpent: 0,
    startTime: null,
    isLoading: false,
    error: null
  });

  // Update total questions when questions prop changes
  useEffect(() => {
    setState(prev => ({ ...prev, totalQuestions: questions.length }));
  }, [questions.length]);

  // Timer for tracking time spent
  useEffect(() => {
    if (!state.startTime || state.isSubmitted) return;

    const timer = setInterval(() => {
      setState(prev => ({
        ...prev,
        timeSpent: Date.now() - prev.startTime!
      }));
    }, 1000);

    return () => clearInterval(timer);
  }, [state.startTime, state.isSubmitted]);

  const startQuiz = useCallback(() => {
    setState(prev => ({
      ...prev,
      startTime: Date.now(),
      timeSpent: 0,
      currentQuestionIndex: 0,
      answers: {},
      isSubmitted: false,
      score: 0,
      error: null
    }));
  }, []);

  const goToNext = useCallback(() => {
    setState(prev => ({
      ...prev,
      currentQuestionIndex: Math.min(prev.currentQuestionIndex + 1, prev.totalQuestions - 1)
    }));
  }, []);

  const goToPrevious = useCallback(() => {
    setState(prev => ({
      ...prev,
      currentQuestionIndex: Math.max(prev.currentQuestionIndex - 1, 0)
    }));
  }, []);

  const goToQuestion = useCallback((index: number) => {
    if (index >= 0 && index < state.totalQuestions) {
      setState(prev => ({ ...prev, currentQuestionIndex: index }));
    }
  }, [state.totalQuestions]);

  const setAnswer = useCallback((questionId: string, answer: QuizAnswer) => {
    setState(prev => ({
      ...prev,
      answers: {
        ...prev.answers,
        [questionId]: answer
      }
    }));
  }, []);

  const getAnswer = useCallback((questionId: string): QuizAnswer | null => {
    return state.answers[questionId] || null;
  }, [state.answers]);

  const submitQuiz = useCallback(async (courseId: string) => {
    setState(prev => ({ ...prev, isLoading: true, error: null }));

    try {
      // Calculate score based on correct answers
      const answeredQuestions = Object.values(state.answers);
      const correctAnswers = answeredQuestions.filter(answer => answer.isCorrect === true);
      const calculatedScore = (correctAnswers.length / state.totalQuestions) * 100;

      // Submit to backend - convert answers to required format
      const answersRecord: Record<string, string | string[]> = {};
      Object.values(state.answers).forEach(answer => {
        answersRecord[answer.questionId] = Array.isArray(answer.value) 
          ? answer.value 
          : String(answer.value);
      });

      await courseService.submitQuiz(courseId, answersRecord);

      setState(prev => ({
        ...prev,
        isSubmitted: true,
        score: calculatedScore,
        isLoading: false
      }));
    } catch (error) {
      setState(prev => ({
        ...prev,
        isLoading: false,
        error: error instanceof Error ? error.message : 'Failed to submit quiz'
      }));
    }
  }, [state.answers, state.totalQuestions]);

  const resetQuiz = useCallback(() => {
    setState({
      currentQuestionIndex: 0,
      answers: {},
      isSubmitted: false,
      score: 0,
      totalQuestions: questions.length,
      timeSpent: 0,
      startTime: null,
      isLoading: false,
      error: null
    });
  }, [questions.length]);

  // Computed values
  const progress = useMemo(() => {
    if (state.totalQuestions === 0) return 0;
    return (Object.keys(state.answers).length / state.totalQuestions) * 100;
  }, [state.answers, state.totalQuestions]);

  const isComplete = useMemo(() => {
    return Object.keys(state.answers).length === state.totalQuestions;
  }, [state.answers, state.totalQuestions]);

  const canGoNext = useMemo(() => {
    return state.currentQuestionIndex < state.totalQuestions - 1;
  }, [state.currentQuestionIndex, state.totalQuestions]);

  const canGoPrevious = useMemo(() => {
    return state.currentQuestionIndex > 0;
  }, [state.currentQuestionIndex]);

  const answeredCount = useMemo(() => {
    return Object.keys(state.answers).length;
  }, [state.answers]);

  const unansweredQuestions = useMemo(() => {
    const answered = new Set(Object.keys(state.answers));
    return questions
      .map((_, index) => index)
      .filter(index => !answered.has(questions[index]?.id));
  }, [state.answers, questions]);

  return {
    ...state,
    goToNext,
    goToPrevious,
    goToQuestion,
    setAnswer,
    getAnswer,
    startQuiz,
    submitQuiz,
    resetQuiz,
    progress,
    isComplete,
    canGoNext,
    canGoPrevious,
    answeredCount,
    unansweredQuestions
  };
};