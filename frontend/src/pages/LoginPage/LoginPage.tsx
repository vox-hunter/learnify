import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation, useSearchParams } from 'react-router-dom';
import { Button } from '../../components/ui/Button';
import { Input } from '../../components/ui/Input';
import { useAuth } from '../../hooks/useAuth';

type AuthMode = 'login' | 'register';

interface LocationState {
  returnTo?: string;
  message?: string;
}

export const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [searchParams] = useSearchParams();
  const { login, register, isLoading, error, isAuthenticated, clearError } = useAuth();
  
  const [mode, setMode] = useState<AuthMode>(
    (searchParams.get('mode') as AuthMode) || 'login'
  );
  
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    name: '',
    rememberMe: false
  });
  
  const [validationErrors, setValidationErrors] = useState<Record<string, string>>({});
  
  const state = location.state as LocationState;
  const returnTo = state?.returnTo || '/';
  const message = state?.message;

  useEffect(() => {
    if (isAuthenticated) {
      navigate(returnTo, { replace: true });
    }
  }, [isAuthenticated, navigate, returnTo]);

  useEffect(() => {
    clearError();
    setValidationErrors({});
  }, [mode, clearError]);

  const validateForm = (): boolean => {
    const errors: Record<string, string> = {};

    if (!formData.email) {
      errors.email = 'Email is required';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      errors.email = 'Please enter a valid email address';
    }

    if (!formData.password) {
      errors.password = 'Password is required';
    } else if (formData.password.length < 6) {
      errors.password = 'Password must be at least 6 characters';
    }

    if (mode === 'register') {
      if (!formData.name) {
        errors.name = 'Name is required';
      }
      
      if (!formData.confirmPassword) {
        errors.confirmPassword = 'Please confirm your password';
      } else if (formData.password !== formData.confirmPassword) {
        errors.confirmPassword = 'Passwords do not match';
      }
    }

    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) return;

    try {
      if (mode === 'login') {
        await login({
          email: formData.email,
          password: formData.password,
          rememberMe: formData.rememberMe
        });
      } else {
        await register({
          name: formData.name,
          email: formData.email,
          password: formData.password,
          confirmPassword: formData.confirmPassword
        });
      }
    } catch (err) {
      // Error handling is managed by the useAuth hook
      console.error('Authentication error:', err);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
    
    // Clear validation error when user starts typing
    if (validationErrors[name]) {
      setValidationErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[name];
        return newErrors;
      });
    }
  };

  const switchMode = () => {
    const newMode = mode === 'login' ? 'register' : 'login';
    setMode(newMode);
    setFormData({
      email: formData.email, // Keep email when switching
      password: '',
      confirmPassword: '',
      name: '',
      rememberMe: false
    });
    setValidationErrors({});
    navigate(`/login?mode=${newMode}`, { replace: true });
  };

  return (
    <div className="login-page">
      <div className="login-container">
        <div className="login-header">
          <h1 className="login-title">
            {mode === 'login' ? 'Welcome Back!' : 'Create Account'}
          </h1>
          <p className="login-subtitle">
            {mode === 'login' 
              ? 'Sign in to continue your learning journey'
              : 'Join thousands of learners transforming documents into knowledge'
            }
          </p>
          
          {message && (
            <div className="auth-message">
              <p>{message}</p>
            </div>
          )}
        </div>

        <form onSubmit={handleSubmit} className="login-form">
          {mode === 'register' && (
            <Input
              type="text"
              name="name"
              label="Full Name"
              value={formData.name}
              onChange={handleInputChange}
              error={validationErrors.name}
              placeholder="Enter your full name"
              disabled={isLoading}
              leftIcon="👤"
            />
          )}

          <Input
            type="email"
            name="email"
            label="Email Address"
            value={formData.email}
            onChange={handleInputChange}
            error={validationErrors.email}
            placeholder="Enter your email"
            disabled={isLoading}
            leftIcon="📧"
          />

          <Input
            type="password"
            name="password"
            label="Password"
            value={formData.password}
            onChange={handleInputChange}
            error={validationErrors.password}
            placeholder={mode === 'login' ? 'Enter your password' : 'Create a password (min. 6 characters)'}
            disabled={isLoading}
            leftIcon="🔒"
          />

          {mode === 'register' && (
            <Input
              type="password"
              name="confirmPassword"
              label="Confirm Password"
              value={formData.confirmPassword}
              onChange={handleInputChange}
              error={validationErrors.confirmPassword}
              placeholder="Confirm your password"
              disabled={isLoading}
              leftIcon="🔒"
            />
          )}

          {mode === 'login' && (
            <div className="form-options">
              <label className="remember-me">
                <input
                  type="checkbox"
                  name="rememberMe"
                  checked={formData.rememberMe}
                  onChange={handleInputChange}
                  disabled={isLoading}
                />
                <span>Remember me</span>
              </label>
            </div>
          )}

          {error && (
            <div className="error-message">
              <p>❌ {error}</p>
            </div>
          )}

          <Button
            type="submit"
            variant="primary"
            size="lg"
            fullWidth
            isLoading={isLoading}
            disabled={isLoading}
            className="submit-button"
          >
            {mode === 'login' ? 'Sign In' : 'Create Account'}
          </Button>
        </form>

        <div className="login-footer">
          <p className="switch-mode">
            {mode === 'login' ? "Don't have an account? " : 'Already have an account? '}
            <button
              type="button"
              onClick={switchMode}
              className="switch-button"
              disabled={isLoading}
            >
              {mode === 'login' ? 'Sign up' : 'Sign in'}
            </button>
          </p>

          {mode === 'login' && (
            <div className="forgot-password">
              <button type="button" className="forgot-link">
                Forgot your password?
              </button>
            </div>
          )}
        </div>
      </div>

      <div className="login-features">
        <div className="features-content">
          <h3>Why join Learnify?</h3>
          <ul className="features-list">
            <li>🚀 Transform any document into interactive learning</li>
            <li>📊 Track your progress with detailed analytics</li>
            <li>🎯 AI-powered personalized questions</li>
            <li>⚡ Instant feedback and explanations</li>
            <li>📱 Learn anywhere, anytime</li>
          </ul>
        </div>
      </div>
    </div>
  );
};