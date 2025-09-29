// T020: Component Prop Interfaces
// Defines TypeScript interfaces for all React component props

import type { ReactNode } from 'react';
import type { Question, CourseData, UserProfile } from './api';

// Form Component Props
export interface FileUploadProps {
  onUpload: (file: File) => void;
  onError?: (error: FileUploadError) => void;
  accept?: string;
  maxSize?: number;
  disabled?: boolean;
  uploading?: boolean;
  progress?: number;
  error?: string;
  className?: string;
}

export interface FileUploadError {
  type: 'invalid_file_type' | 'file_too_large' | 'empty_file' | 'upload_failed';
  message: string;
  details?: Record<string, unknown>;
}

export interface URLInputProps {
  value: string;
  onChange: (value: string) => void;
  onSubmit?: (url: string) => void;
  placeholder?: string;
  disabled?: boolean;
  loading?: boolean;
  error?: string;
  className?: string;
  autoFocus?: boolean;
}

// UI Component Props
export interface ProgressBarProps {
  value: number;
  max?: number;
  showLabel?: boolean;
  label?: string;
  color?: 'primary' | 'success' | 'warning' | 'error';
  size?: 'small' | 'medium' | 'large';
  animated?: boolean;
  indeterminate?: boolean;
  onComplete?: () => void;
  className?: string;
}

export interface ButtonProps {
  children: ReactNode;
  onClick?: () => void;
  type?: 'button' | 'submit' | 'reset';
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger';
  size?: 'small' | 'medium' | 'large';
  disabled?: boolean;
  loading?: boolean;
  fullWidth?: boolean;
  className?: string;
}

export interface LoadingSpinnerProps {
  size?: 'small' | 'medium' | 'large';
  color?: string;
  className?: string;
}

// Quiz Component Props
export interface QuizQuestionProps {
  question: Question;
  questionNumber: number;
  totalQuestions: number;
  selectedAnswer?: string | string[];
  onAnswerChange: (answer: string | string[]) => void;
  showFeedback?: boolean;
  disabled?: boolean;
  className?: string;
}

export interface FillInBlanksProps {
  text: string;
  blanks: BlankField[];
  answers: Record<string, string>;
  onAnswerChange: (blankId: string, answer: string) => void;
  showFeedback?: boolean;
  disabled?: boolean;
  className?: string;
}

export interface BlankField {
  id: string;
  position: number;
  correctAnswers: string[];
  caseSensitive?: boolean;
  placeholder?: string;
}

export interface QuizResultsProps {
  course: CourseData;
  answers: Record<string, string | string[]>;
  score: number;
  totalQuestions: number;
  timeSpent: number;
  onRetake?: () => void;
  onShare?: () => void;
  onContinue?: () => void;
  className?: string;
}

// Page Component Props
export interface CourseListProps {
  courses: CourseData[];
  loading?: boolean;
  error?: string;
  onCourseSelect: (courseId: string) => void;
  onRefresh?: () => void;
  searchQuery?: string;
  onSearchChange?: (query: string) => void;
  viewMode?: 'grid' | 'list';
  onViewModeChange?: (mode: 'grid' | 'list') => void;
  className?: string;
}

export interface DashboardProps {
  user: UserProfile;
  recentCourses: CourseData[];
  statistics: DashboardStats;
  loading?: boolean;
  onCreateCourse?: () => void;
  onTakeQuiz?: () => void;
  onViewCourse?: (courseId: string) => void;
  className?: string;
}

export interface DashboardStats {
  totalCourses: number;
  totalQuizzes: number;
  averageScore: number;
  timeSpent: number;
  achievements: Achievement[];
  recentActivity: Activity[];
}

export interface Achievement {
  id: string;
  title: string;
  description: string;
  icon: string;
  unlockedAt: string;
  rarity: 'common' | 'rare' | 'epic' | 'legendary';
}

export interface Activity {
  id: string;
  type: 'course_created' | 'quiz_completed' | 'achievement_unlocked';
  title: string;
  description: string;
  timestamp: string;
  metadata?: Record<string, unknown>;
}

// Layout Component Props
export interface LayoutProps {
  children: ReactNode;
  title?: string;
  showNavigation?: boolean;
  showSidebar?: boolean;
  className?: string;
}

export interface NavigationProps {
  user?: UserProfile;
  currentPath: string;
  onNavigate: (path: string) => void;
  onLogout?: () => void;
  className?: string;
}

export interface SidebarProps {
  isOpen: boolean;
  onToggle: () => void;
  navigation: NavigationItem[];
  className?: string;
}

export interface NavigationItem {
  id: string;
  label: string;
  path: string;
  icon?: string;
  badge?: string | number;
  children?: NavigationItem[];
}