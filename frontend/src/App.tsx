import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Layout } from './components/layout/Layout';
import { HomePage } from './pages/HomePage/HomePage';
import { CoursePage } from './pages/CoursePage/CoursePage';
import { LoginPage } from './pages/LoginPage/LoginPage';
import { PrivacyPage } from './pages/LegalPages/PrivacyPage';
import { TermsPage } from './pages/LegalPages/TermsPage';
import { useAuth } from './hooks/useAuth';
import './App.css';

// Protected Route Component
interface ProtectedRouteProps {
  children: React.ReactNode;
  requireAuth?: boolean;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children, requireAuth = true }) => {
  const { isAuthenticated } = useAuth();
  
  if (requireAuth && !isAuthenticated) {
    return <Navigate to="/login" state={{ returnTo: window.location.pathname }} replace />;
  }
  
  return <>{children}</>;
};

// Error Boundary Component
interface ErrorBoundaryState {
  hasError: boolean;
  error?: Error;
}

class ErrorBoundary extends React.Component<
  { children: React.ReactNode },
  ErrorBoundaryState
> {
  constructor(props: { children: React.ReactNode }) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('Application Error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <Layout>
          <div className="error-page">
            <div className="error-content">
              <h1>😱 Oops! Something went wrong</h1>
              <p>We're sorry, but something unexpected happened.</p>
              <button 
                onClick={() => window.location.reload()}
                className="error-reload-button"
              >
                Reload Page
              </button>
            </div>
          </div>
        </Layout>
      );
    }

    return this.props.children;
  }
}

// Main App Component
function App() {
  return (
    <ErrorBoundary>
      <Router>
        <div className="app">
          <Routes>
            {/* Public Routes */}
            <Route
              path="/"
              element={
                <Layout>
                  <HomePage />
                </Layout>
              }
            />
            
            <Route
              path="/login"
              element={
                <Layout showNavigation={false} showFooter={false}>
                  <LoginPage />
                </Layout>
              }
            />
            
            <Route
              path="/privacy"
              element={
                <Layout>
                  <PrivacyPage />
                </Layout>
              }
            />
            
            <Route
              path="/terms"
              element={
                <Layout>
                  <TermsPage />
                </Layout>
              }
            />

            {/* Protected Routes */}
            <Route
              path="/course/:courseId"
              element={
                <ProtectedRoute>
                  <Layout>
                    <CoursePage />
                  </Layout>
                </ProtectedRoute>
              }
            />

            {/* Catch-all Route */}
            <Route
              path="*"
              element={
                <Layout>
                  <div className="not-found-page">
                    <div className="not-found-content">
                      <h1>🔍 Page Not Found</h1>
                      <p>The page you're looking for doesn't exist.</p>
                      <a href="/" className="home-link">
                        Go back to Home
                      </a>
                    </div>
                  </div>
                </Layout>
              }
            />
          </Routes>
        </div>
      </Router>
    </ErrorBoundary>
  );
}

export default App;
