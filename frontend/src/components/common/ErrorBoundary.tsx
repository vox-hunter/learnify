import { Component } from 'react';
import type { ErrorInfo, ReactNode } from 'react';
import { Button } from '../ui/Button';
import { isDevelopment } from '../../utils/env';

interface ErrorBoundaryProps {
  children: ReactNode;
  fallback?: ReactNode;
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
  resetOnPropsChange?: boolean;
  resetKeys?: Array<string | number>;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
  eventId: string | null;
}

class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  private resetTimeoutId: number | null = null;

  constructor(props: ErrorBoundaryProps) {
    super(props);
    
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
      eventId: null,
    };

    // Store initial reset keys for comparison
    // this.previousResetKeys = props.resetKeys || [];
  }

  static getDerivedStateFromError(error: Error): Partial<ErrorBoundaryState> {
    // Update state so the next render will show the fallback UI
    return {
      hasError: true,
      error,
    };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    const eventId = this.generateEventId();
    
    // Log error details
    console.error('ErrorBoundary caught an error:', error, errorInfo);
    
    // Update state with error details
    this.setState({
      error,
      errorInfo,
      eventId,
    });

    // Call custom error handler if provided
    if (this.props.onError) {
      this.props.onError(error, errorInfo);
    }

    // Send error to monitoring service (if available)
    this.reportErrorToService(error, errorInfo, eventId);
  }

  componentDidUpdate(prevProps: ErrorBoundaryProps) {
    const { resetKeys, resetOnPropsChange } = this.props;
    const { hasError } = this.state;

    // Reset error boundary when resetKeys change
    if (hasError && resetKeys && prevProps.resetKeys) {
      const hasResetKeyChanged = resetKeys.some(
        (key, index) => prevProps.resetKeys![index] !== key
      );
      
      if (hasResetKeyChanged) {
        this.resetErrorBoundary();
      }
    }

    // Reset error boundary when any props change (if enabled)
    if (hasError && resetOnPropsChange && prevProps !== this.props) {
      this.resetErrorBoundary();
    }
  }

  componentWillUnmount() {
    if (this.resetTimeoutId) {
      clearTimeout(this.resetTimeoutId);
    }
  }

  private generateEventId(): string {
    return `error_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  private reportErrorToService(error: Error, errorInfo: ErrorInfo, eventId: string) {
    // Here you would typically send the error to a monitoring service
    // like Sentry, LogRocket, or a custom error reporting endpoint
    
    try {
      const errorReport = {
        eventId,
        error: {
          name: error.name,
          message: error.message,
          stack: error.stack,
        },
        errorInfo,
        userAgent: navigator.userAgent,
        url: window.location.href,
        timestamp: new Date().toISOString(),
        userId: this.getUserId(),
      };

      // Send to error reporting service
      // fetch('/api/errors', {
      //   method: 'POST',
      //   headers: { 'Content-Type': 'application/json' },
      //   body: JSON.stringify(errorReport),
      // }).catch(reportingError => {
      //   console.error('Failed to report error:', reportingError);
      // });

      // Store in localStorage as fallback
      const storedErrors = JSON.parse(localStorage.getItem('error_reports') || '[]');
      storedErrors.push(errorReport);
      // Keep only last 10 errors
      if (storedErrors.length > 10) {
        storedErrors.splice(0, storedErrors.length - 10);
      }
      localStorage.setItem('error_reports', JSON.stringify(storedErrors));
    } catch (reportingError) {
      console.error('Failed to report error:', reportingError);
    }
  }

  private getUserId(): string | null {
    try {
      const userProfile = localStorage.getItem('user_profile') || sessionStorage.getItem('user_profile');
      if (userProfile) {
        const user = JSON.parse(userProfile);
        return user.id || null;
      }
    } catch {
      // Ignore errors when getting user ID
    }
    return null;
  }

  private resetErrorBoundary = () => {
    // Clear any existing timeout
    if (this.resetTimeoutId) {
      clearTimeout(this.resetTimeoutId);
    }

    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
      eventId: null,
    });
  };

  private handleRetry = () => {
    this.resetErrorBoundary();
  };

  private handleReload = () => {
    window.location.reload();
  };

  private handleGoHome = () => {
    window.location.href = '/';
  };

  private copyErrorToClipboard = async () => {
    const { error, errorInfo, eventId } = this.state;
    
    const errorText = [
      `Event ID: ${eventId}`,
      `Error: ${error?.name} - ${error?.message}`,
      `Stack: ${error?.stack}`,
      `Component Stack: ${errorInfo?.componentStack}`,
      `URL: ${window.location.href}`,
      `User Agent: ${navigator.userAgent}`,
      `Timestamp: ${new Date().toISOString()}`,
    ].join('\n\n');

    try {
      await navigator.clipboard.writeText(errorText);
      alert('Error details copied to clipboard');
    } catch {
      // Fallback for older browsers
      const textarea = document.createElement('textarea');
      textarea.value = errorText;
      document.body.appendChild(textarea);
      textarea.select();
      document.execCommand('copy');
      document.body.removeChild(textarea);
      alert('Error details copied to clipboard');
    }
  };

  render() {
    const { hasError, error, errorInfo, eventId } = this.state;
    const { children, fallback } = this.props;

    if (hasError) {
      // Custom fallback UI
      if (fallback) {
        return fallback;
      }

      // Default error UI
      return (
        <div className="error-boundary">
          <div className="error-boundary-container">
            <div className="error-boundary-content">
              {/* Error Icon */}
              <div className="error-boundary-icon">
                😱
              </div>

              {/* Error Message */}
              <h1 className="error-boundary-title">
                Oops! Something went wrong
              </h1>
              
              <p className="error-boundary-description">
                We're sorry, but something unexpected happened. Our team has been notified.
              </p>

              {/* Error Details (Development Only) */}
              {isDevelopment() && (
                <details className="error-boundary-details">
                  <summary>Error Details (Development)</summary>
                  <div className="error-boundary-error-info">
                    <p><strong>Event ID:</strong> {eventId}</p>
                    <p><strong>Error:</strong> {error?.name} - {error?.message}</p>
                    {error?.stack && (
                      <pre className="error-boundary-stack">
                        <code>{error.stack}</code>
                      </pre>
                    )}
                    {errorInfo?.componentStack && (
                      <pre className="error-boundary-component-stack">
                        <code>{errorInfo.componentStack}</code>
                      </pre>
                    )}
                  </div>
                </details>
              )}

              {/* Action Buttons */}
              <div className="error-boundary-actions">
                <Button
                  onClick={this.handleRetry}
                  variant="primary"
                  className="error-boundary-button"
                >
                  Try Again
                </Button>
                
                <Button
                  onClick={this.handleGoHome}
                  variant="secondary"
                  className="error-boundary-button"
                >
                  Go to Home
                </Button>
                
                <Button
                  onClick={this.handleReload}
                  variant="ghost"
                  className="error-boundary-button"
                >
                  Reload Page
                </Button>
              </div>

              {/* Support Info */}
              <div className="error-boundary-support">
                <p className="error-boundary-support-text">
                  If this problem persists, please contact support.
                </p>
                
                <div className="error-boundary-support-actions">
                  <button
                    onClick={this.copyErrorToClipboard}
                    className="error-boundary-copy-button"
                    type="button"
                  >
                    📋 Copy Error Details
                  </button>
                  
                  {eventId && (
                    <p className="error-boundary-event-id">
                      <strong>Reference ID:</strong> {eventId}
                    </p>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      );
    }

    return children;
  }
}

export default ErrorBoundary;