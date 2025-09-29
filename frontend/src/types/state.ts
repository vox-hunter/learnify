// T021: State Management Types
// Defines TypeScript interfaces for application state management

import type { CourseData, UserProfile, Question } from './api';
import type { FileUploadError } from './components';

// Application State
export interface AppState {
  auth: AuthState;
  courses: CoursesState;
  quiz: QuizState;
  ui: UIState;
  upload: UploadState;
}

// Authentication State
export interface AuthState {
  isAuthenticated: boolean;
  user: UserProfile | null;
  token: string | null;
  refreshToken: string | null;
  loading: boolean;
  error: string | null;
  lastActivity: string | null;
}

export interface AuthActions {
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  refreshAuth: () => Promise<void>;
  updateProfile: (updates: Partial<UserProfile>) => Promise<void>;
  clearError: () => void;
}

// Courses State
export interface CoursesState {
  courses: CourseData[];
  currentCourse: CourseData | null;
  loading: boolean;
  error: string | null;
  searchQuery: string;
  filters: CourseFilters;
  viewMode: 'grid' | 'list';
  pagination: {
    page: number;
    limit: number;
    total: number;
    hasMore: boolean;
  };
}

export interface CourseFilters {
  type?: 'quiz' | 'flashcards' | 'summary' | 'mixed';
  difficulty?: 'easy' | 'medium' | 'hard';
  topics: string[];
  dateRange?: {
    start: string;
    end: string;
  };
}

export interface CoursesActions {
  fetchCourses: (page?: number) => Promise<void>;
  searchCourses: (query: string) => Promise<void>;
  filterCourses: (filters: Partial<CourseFilters>) => void;
  selectCourse: (courseId: string) => Promise<void>;
  createCourse: (documentId: string, options: CourseGenerationOptions) => Promise<string>;
}

export interface CourseGenerationOptions {
  courseType: 'quiz' | 'flashcards' | 'summary' | 'mixed';
  difficulty: 'easy' | 'medium' | 'hard';
  questionCount?: number;
  topics?: string[];
  deleteCourse: (courseId: string) => Promise<void>;
  setViewMode: (mode: 'grid' | 'list') => void;
  clearError: () => void;
}

// Quiz State
export interface QuizState {
  currentQuiz: QuizSession | null;
  questions: Question[];
  currentQuestionIndex: number;
  answers: Record<string, string | string[]>;
  timeStarted: string | null;
  timeSpent: number;
  isCompleted: boolean;
  score: number | null;
  loading: boolean;
  error: string | null;
}

export interface QuizSession {
  id: string;
  courseId: string;
  userId: string;
  startedAt: string;
  completedAt?: string;
  answers: Record<string, string | string[]>;
  score?: number;
  timeSpent: number;
  status: 'in_progress' | 'completed' | 'abandoned';
}

export interface QuizActions {
  startQuiz: (courseId: string) => Promise<void>;
  answerQuestion: (questionId: string, answer: string | string[]) => void;
  nextQuestion: () => void;
  previousQuestion: () => void;
  submitQuiz: () => Promise<void>;
  pauseQuiz: () => void;
  resumeQuiz: () => void;
  restartQuiz: () => void;
  clearQuiz: () => void;
}

// UI State
export interface UIState {
  theme: 'light' | 'dark' | 'auto';
  sidebarOpen: boolean;
  notifications: Notification[];
  modals: ModalState[];
  loading: LoadingState[];
  toasts: Toast[];
}

export interface Notification {
  id: string;
  type: 'info' | 'success' | 'warning' | 'error';
  title: string;
  message: string;
  timestamp: string;
  read: boolean;
  actions?: NotificationAction[];
}

export interface NotificationAction {
  label: string;
  action: () => void;
  variant?: 'primary' | 'secondary';
}

export interface ModalState {
  id: string;
  type: string;
  isOpen: boolean;
  data?: Record<string, unknown>;
}

export interface LoadingState {
  id: string;
  message?: string;
  progress?: number;
}

export interface Toast {
  id: string;
  type: 'info' | 'success' | 'warning' | 'error';
  message: string;
  duration?: number;
  actions?: ToastAction[];
}

export interface ToastAction {
  label: string;
  action: () => void;
}

export interface UIActions {
  setTheme: (theme: 'light' | 'dark' | 'auto') => void;
  toggleSidebar: () => void;
  addNotification: (notification: Omit<Notification, 'id' | 'timestamp' | 'read'>) => void;
  markNotificationRead: (id: string) => void;
  clearNotifications: () => void;
  openModal: (type: string, data?: Record<string, unknown>) => void;
  closeModal: (id: string) => void;
  startLoading: (id: string, message?: string) => void;
  updateLoading: (id: string, progress: number) => void;
  stopLoading: (id: string) => void;
  showToast: (toast: Omit<Toast, 'id'>) => void;
  dismissToast: (id: string) => void;
}

// Upload State
export interface UploadState {
  uploads: UploadSession[];
  currentUpload: UploadSession | null;
  dragActive: boolean;
}

export interface UploadSession {
  id: string;
  file: File;
  status: 'pending' | 'uploading' | 'processing' | 'completed' | 'failed';
  progress: number;
  documentId?: string;
  error?: FileUploadError;
  startedAt: string;
  completedAt?: string;
}

export interface UploadActions {
  startUpload: (file: File) => Promise<string>;
  startURLUpload: (url: string) => Promise<string>;
  cancelUpload: (id: string) => void;
  retryUpload: (id: string) => void;
  clearUploads: () => void;
  setDragActive: (active: boolean) => void;
}

// Hook Types
export type StateSelector<T> = (state: AppState) => T;

export interface StateAction<T = unknown> {
  type: string;
  payload?: T;
}

export type StateDispatch = (action: StateAction) => void;
export type StateSubscriber = (state: AppState) => void;

// Context Types
export interface StateContextValue {
  state: AppState;
  dispatch: StateDispatch;
  subscribe: (subscriber: StateSubscriber) => () => void;
}

// Reducer Types
export type StateReducer<S, A> = (state: S, action: A) => S;
export type ActionCreator<T = unknown> = (...args: unknown[]) => StateAction<T>;

// Middleware Types
export type StateMiddleware = (store: StateContextValue) => (next: StateDispatch) => StateDispatch;