/**
 * Error Handling and User Feedback Systems
 * Comprehensive error handling, notifications, and user feedback components
 */

import React from 'react';
import { useToast, ToastContext, type Toast } from './errorHandlingUtils';

/**
 * Toast Notification System
 * Types and context imported from errorHandlingUtils.ts
 */
export type ToastType = 'success' | 'error' | 'warning' | 'info';

// useToast hook moved to errorHandlingUtils.ts for Fast Refresh compatibility

/**
 * Toast Provider Component
 */
export const ToastProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [toasts, setToasts] = React.useState<Toast[]>([]);

  const removeToast = React.useCallback((id: string) => {
    setToasts(prev => prev.filter(toast => toast.id !== id));
  }, []);

  const addToast = React.useCallback((toast: Omit<Toast, 'id'>) => {
    const id = Math.random().toString(36).substr(2, 9);
    const newToast: Toast = {
      ...toast,
      id,
      duration: toast.duration ?? 5000
    };

    setToasts(prev => [...prev, newToast]);

    // Auto-remove toast after duration
    if (!newToast.persistent) {
      setTimeout(() => {
        removeToast(id);
      }, newToast.duration);
    }
  }, [removeToast]);

  const clearAllToasts = React.useCallback(() => {
    setToasts([]);
  }, []);

  return (
    <ToastContext.Provider value={{ toasts, addToast, removeToast, clearAllToasts }}>
      {children}
    </ToastContext.Provider>
  );
};

/**
 * Toast Container Component
 */
export const ToastContainer: React.FC = () => {
  const toasts = React.useContext(ToastContext)?.toasts || [];
  const removeToast = React.useContext(ToastContext)?.removeToast || (() => {});

  return (
    <div className="toast-container" aria-live="polite" aria-label="Notifications">
      {toasts.map(toast => (
        <ToastItem key={toast.id} toast={toast} onRemove={removeToast} />
      ))}
    </div>
  );
};

/**
 * Individual Toast Item Component
 */
const ToastItem: React.FC<{
  toast: Toast;
  onRemove: (id: string) => void;
}> = ({ toast, onRemove }) => {
  const [isVisible, setIsVisible] = React.useState(false);
  const [isRemoving, setIsRemoving] = React.useState(false);

  React.useEffect(() => {
    // Trigger entrance animation
    const timer = setTimeout(() => setIsVisible(true), 50);
    return () => clearTimeout(timer);
  }, []);

  const handleRemove = () => {
    setIsRemoving(true);
    setTimeout(() => onRemove(toast.id), 300);
  };

  const getIcon = () => {
    switch (toast.type) {
      case 'success': return '✅';
      case 'error': return '❌';
      case 'warning': return '⚠️';
      case 'info': return 'ℹ️';
      default: return 'ℹ️';
    }
  };

  return (
    <div
      className={`toast toast--${toast.type} ${isVisible ? 'toast--visible' : ''} ${isRemoving ? 'toast--removing' : ''}`}
      role="alert"
      aria-atomic="true"
    >
      <div className="toast-content">
        <div className="toast-icon" aria-hidden="true">
          {getIcon()}
        </div>
        <div className="toast-body">
          <div className="toast-title">{toast.title}</div>
          {toast.message && (
            <div className="toast-message">{toast.message}</div>
          )}
          {toast.action && (
            <button
              className="toast-action"
              onClick={toast.action.onClick}
              aria-label={toast.action.label}
            >
              {toast.action.label}
            </button>
          )}
        </div>
        <button
          className="toast-close"
          onClick={handleRemove}
          aria-label="Close notification"
        >
          ✕
        </button>
      </div>
    </div>
  );
};

/**
 * Error Boundary with User Feedback
 */
interface ErrorBoundaryState {
  hasError: boolean;
  error?: Error;
  errorInfo?: React.ErrorInfo;
  eventId?: string;
}

export class ErrorBoundaryWithFeedback extends React.Component<
  React.PropsWithChildren<{
    fallback?: React.ComponentType<{ error: Error; resetError: () => void }>;
    onError?: (error: Error, errorInfo: React.ErrorInfo) => void;
  }>,
  ErrorBoundaryState
> {
  constructor(props: React.PropsWithChildren<{
    fallback?: React.ComponentType<{ error: Error; resetError: () => void }>;
    onError?: (error: Error, errorInfo: React.ErrorInfo) => void;
  }>) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return {
      hasError: true,
      error,
      eventId: `error_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
    };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    this.setState({ errorInfo });
    this.props.onError?.(error, errorInfo);
  }

  resetError = () => {
    this.setState({ hasError: false, error: undefined, errorInfo: undefined });
  };

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return <this.props.fallback error={this.state.error!} resetError={this.resetError} />;
      }

      return (
        <ErrorFallback
          error={this.state.error!}
          resetError={this.resetError}
          eventId={this.state.eventId}
        />
      );
    }

    return this.props.children;
  }
}

/**
 * Default Error Fallback Component
 */
const ErrorFallback: React.FC<{
  error: Error;
  resetError: () => void;
  eventId?: string;
}> = ({ error, resetError, eventId }) => {
  const [feedbackSent, setFeedbackSent] = React.useState(false);
  const [feedback, setFeedback] = React.useState('');

  const handleSendFeedback = async () => {
    try {
      // Send feedback to error reporting service
      await fetch('/api/error-feedback', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          eventId,
          feedback,
          error: error.message,
          stack: error.stack,
          userAgent: navigator.userAgent,
          timestamp: new Date().toISOString()
        })
      });
      setFeedbackSent(true);
    } catch (err) {
      console.error('Failed to send feedback:', err);
    }
  };

  return (
    <div className="error-fallback" role="alert">
      <div className="error-fallback-content">
        <div className="error-fallback-icon">😵</div>
        <h1 className="error-fallback-title">Something went wrong</h1>
        <p className="error-fallback-message">
          We're sorry, but something unexpected happened. Our team has been notified.
        </p>
        
        {eventId && (
          <div className="error-fallback-id">
            <strong>Error ID:</strong> {eventId}
          </div>
        )}

        <div className="error-fallback-actions">
          <button
            className="button button--primary"
            onClick={resetError}
          >
            Try Again
          </button>
          <button
            className="button button--secondary"
            onClick={() => window.location.reload()}
          >
            Reload Page
          </button>
        </div>

        <details className="error-fallback-details">
          <summary>Technical Details</summary>
          <pre className="error-fallback-stack">
            {error.message}
            {'\n\n'}
            {error.stack}
          </pre>
        </details>

        <div className="error-fallback-feedback">
          <h3>Help us improve</h3>
          <p>What were you trying to do when this error occurred?</p>
          <textarea
            className="error-fallback-textarea"
            value={feedback}
            onChange={(e) => setFeedback(e.target.value)}
            placeholder="Describe what you were doing..."
            rows={3}
          />
          <div className="error-fallback-feedback-actions">
            <button
              className="button button--ghost"
              onClick={handleSendFeedback}
              disabled={feedbackSent || !feedback.trim()}
            >
              {feedbackSent ? 'Feedback Sent!' : 'Send Feedback'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

/**
 * Loading State Component with Error Handling
 */
export const LoadingWithError: React.FC<{
  loading: boolean;
  error?: Error | string;
  onRetry?: () => void;
  children: React.ReactNode;
  loadingText?: string;
}> = ({ loading, error, onRetry, children, loadingText = 'Loading...' }) => {
  if (loading) {
    return (
      <div className="loading-state" role="status" aria-live="polite">
        <div className="loading-spinner" aria-hidden="true"></div>
        <span className="loading-text">{loadingText}</span>
      </div>
    );
  }

  if (error) {
    const errorMessage = typeof error === 'string' ? error : error.message;
    return (
      <div className="error-state" role="alert">
        <div className="error-state-icon">⚠️</div>
        <h3 className="error-state-title">Something went wrong</h3>
        <p className="error-state-message">{errorMessage}</p>
        {onRetry && (
          <button
            className="button button--primary"
            onClick={onRetry}
          >
            Try Again
          </button>
        )}
      </div>
    );
  }

  return <>{children}</>;
};

/**
 * Form Error Summary Component
 */
export const FormErrorSummary: React.FC<{
  errors: Record<string, string>;
  title?: string;
}> = ({ errors, title = 'Please correct the following errors:' }) => {
  const errorEntries = Object.entries(errors).filter(([, message]) => message);

  if (errorEntries.length === 0) return null;

  return (
    <div className="form-error-summary" role="alert" aria-labelledby="error-summary-title">
      <h3 id="error-summary-title" className="form-error-summary-title">
        {title}
      </h3>
      <ul className="form-error-summary-list">
        {errorEntries.map(([field, message]) => (
          <li key={field}>
            <a href={`#${field}`} className="form-error-summary-link">
              {message}
            </a>
          </li>
        ))}
      </ul>
    </div>
  );
};

/**
 * Feedback Modal Component
 */
export const FeedbackModal: React.FC<{
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (feedback: { rating: number; comment: string; category: string }) => void;
}> = ({ isOpen, onClose, onSubmit }) => {
  const [rating, setRating] = React.useState(0);
  const [comment, setComment] = React.useState('');
  const [category, setCategory] = React.useState('general');
  const [isSubmitting, setIsSubmitting] = React.useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    
    try {
      await onSubmit({ rating, comment, category });
      onClose();
      setRating(0);
      setComment('');
      setCategory('general');
    } catch (error) {
      console.error('Failed to submit feedback:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-dialog" onClick={(e) => e.stopPropagation()}>
        <form onSubmit={handleSubmit}>
          <div className="modal-header">
            <h2>Share Your Feedback</h2>
            <button type="button" onClick={onClose} aria-label="Close">✕</button>
          </div>
          
          <div className="modal-content">
            <div className="form-field">
              <label htmlFor="feedback-category">Category</label>
              <select
                id="feedback-category"
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                required
              >
                <option value="general">General</option>
                <option value="bug">Bug Report</option>
                <option value="feature">Feature Request</option>
                <option value="ui">User Interface</option>
              </select>
            </div>

            <div className="form-field">
              <label>Rating</label>
              <div className="star-rating">
                {[1, 2, 3, 4, 5].map((star) => (
                  <button
                    key={star}
                    type="button"
                    className={`star ${star <= rating ? 'star--filled' : ''}`}
                    onClick={() => setRating(star)}
                    aria-label={`Rate ${star} stars`}
                  >
                    ⭐
                  </button>
                ))}
              </div>
            </div>

            <div className="form-field">
              <label htmlFor="feedback-comment">Comments</label>
              <textarea
                id="feedback-comment"
                value={comment}
                onChange={(e) => setComment(e.target.value)}
                placeholder="Tell us about your experience..."
                rows={4}
                required
              />
            </div>
          </div>

          <div className="modal-footer">
            <button
              type="button"
              className="button button--secondary"
              onClick={onClose}
              disabled={isSubmitting}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="button button--primary"
              disabled={isSubmitting || rating === 0 || !comment.trim()}
            >
              {isSubmitting ? 'Submitting...' : 'Submit Feedback'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default {
  ToastProvider,
  ToastContainer,
  ErrorBoundaryWithFeedback,
  LoadingWithError,
  FormErrorSummary,
  FeedbackModal
};