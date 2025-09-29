import React from 'react';
import ErrorBoundary from './ErrorBoundary';
import type { ErrorInfo, ReactNode } from 'react';

// Functional wrapper with hooks support
interface ErrorBoundaryWrapperProps {
  children: ReactNode;
  fallback?: ReactNode;
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
  resetOnPropsChange?: boolean;
  resetKeys?: Array<string | number>;
}

export const ErrorBoundaryWrapper: React.FC<ErrorBoundaryWrapperProps> = (props) => {
  return <ErrorBoundary {...props} />;
};

