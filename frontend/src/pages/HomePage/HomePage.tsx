import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { FileUpload } from '../../components/forms/FileUpload';
import { URLInput } from '../../components/forms/URLInput';
import { Button } from '../../components/ui/Button';
import { useCourseGeneration } from '../../hooks/useCourseGeneration';
import { useAuth } from '../../hooks/useAuth';
import type { DocumentUploadResponse, URLDocumentResponse, APIError } from '../../types/api';

type InputMode = 'file' | 'url';

export const HomePage: React.FC = () => {
  const navigate = useNavigate();
  const [inputMode, setInputMode] = useState<InputMode>('file');
  const { user, isAuthenticated } = useAuth();
  const { generateCourse, isGenerating, progress, courseId, error: courseError } = useCourseGeneration();

  const handleDocumentSuccess = async (response: DocumentUploadResponse | URLDocumentResponse) => {
    if (!isAuthenticated) {
      navigate('/login', { 
        state: { 
          returnTo: '/', 
          message: 'Please log in to generate a course from your document.' 
        } 
      });
      return;
    }

    try {
      await generateCourse({
        documentId: response.documentId,
        options: {
          courseType: 'quiz',
          difficulty: 'medium',
          questionCount: 10
        }
      });
    } catch (error) {
      console.error('Failed to start course generation:', error);
    }
  };

  const handleDocumentError = (error: APIError) => {
    console.error('Document processing failed:', error);
  };

  const handleViewCourse = () => {
    if (courseId) {
      navigate(`/course/${courseId}`);
    }
  };

  return (
    <div className="home-page">
      {/* Enhanced Hero Section */}
      <div className="hero-section">
        <div className="hero-content">
          <h1 className="hero-title">
            Transform Your Notes Into Knowledge
          </h1>
          <p className="hero-description">
            Experience the future of learning with AI Loom - where your documents become interactive, 
            adaptive courses powered by cutting-edge artificial intelligence.
          </p>
          <div className="hero-features">
            <div className="hero-feature">
              <span className="hero-feature-icon">⚡</span>
              <span>Instant Generation</span>
            </div>
            <div className="hero-feature">
              <span className="hero-feature-icon">🧠</span>
              <span>AI-Powered</span>
            </div>
            <div className="hero-feature">
              <span className="hero-feature-icon">📈</span>
              <span>Adaptive Learning</span>
            </div>
          </div>
        </div>
      </div>

      {/* Upload Section with Enhanced Styling */}
      <div className="upload-section">
        <div className="upload-container">
          <div className="upload-header">
            <h2>Get Started</h2>
            <p>Upload your study materials and let AI create your personalized learning experience</p>
          </div>

          <div className="mode-selector">
            <Button
              variant={inputMode === 'file' ? 'primary' : 'secondary'}
              onClick={() => setInputMode('file')}
              className="mode-button"
            >
              📄 Upload File
            </Button>
            <Button
              variant={inputMode === 'url' ? 'primary' : 'secondary'}
              onClick={() => setInputMode('url')}
              className="mode-button"
            >
              🔗 From URL
            </Button>
          </div>

          <div className="input-area">
            {inputMode === 'file' ? (
              <FileUpload
                onSuccess={handleDocumentSuccess}
                onError={handleDocumentError}
                className="upload-component"
              />
            ) : (
              <URLInput
                onSuccess={handleDocumentSuccess}
                onError={handleDocumentError}
                className="url-component"
              />
            )}
          </div>

          {isGenerating && (
            <div className="generation-status">
              <div className="status-content">
                <div className="status-icon">🎯</div>
                <h3>Generating Your Course</h3>
                <p>Our AI is analyzing your content and creating personalized learning materials...</p>
                <div className="progress-container">
                  <div className="progress-bar">
                    <div 
                      className="progress-fill" 
                      style={{ width: `${progress}%` }}
                    ></div>
                  </div>
                  <span className="progress-text">{Math.round(progress)}%</span>
                </div>
              </div>
            </div>
          )}

          {courseError && (
            <div className="error-message">
              <div className="error-icon">❌</div>
              <p>{courseError}</p>
            </div>
          )}

          {courseId && !isGenerating && (
            <div className="success-section">
              <div className="success-content">
                <div className="success-icon">✨</div>
                <h3>Course Ready!</h3>
                <p>Your personalized learning course has been generated successfully.</p>
                <Button
                  onClick={handleViewCourse}
                  variant="gradient"
                  size="lg"
                  className="view-course-button"
                >
                  Start Learning 🚀
                </Button>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Enhanced Features Section */}
      <div className="features-section">
        <div className="features-header">
          <h2>Why Choose AI Loom?</h2>
          <p>Experience the next generation of personalized learning</p>
        </div>
        <div className="features-grid">
          <div className="feature-card">
            <div className="feature-icon">🤖</div>
            <h3>AI-Powered Analysis</h3>
            <p>Advanced machine learning algorithms analyze your content to create relevant, targeted questions and comprehensive explanations.</p>
            <div className="feature-highlight">Smart Content Processing</div>
          </div>
          <div className="feature-card">
            <div className="feature-icon">📊</div>
            <h3>Progress Tracking</h3>
            <p>Monitor your learning journey with detailed analytics, performance insights, and visual progress indicators.</p>
            <div className="feature-highlight">Real-time Analytics</div>
          </div>
          <div className="feature-card">
            <div className="feature-icon">🎯</div>
            <h3>Adaptive Learning</h3>
            <p>Questions dynamically adapt to your skill level and learning pace for an optimal educational experience.</p>
            <div className="feature-highlight">Personalized Experience</div>
          </div>
          <div className="feature-card">
            <div className="feature-icon">⚡</div>
            <h3>Instant Results</h3>
            <p>Get immediate feedback and detailed explanations to reinforce your understanding and accelerate learning.</p>
            <div className="feature-highlight">Immediate Feedback</div>
          </div>
        </div>
      </div>

      {/* Enhanced Auth Prompt */}
      {!isAuthenticated && (
        <div className="auth-prompt">
          <div className="auth-content">
            <div className="auth-icon">🚀</div>
            <h3>Ready to Transform Your Learning?</h3>
            <p>Join thousands of learners who have revolutionized their study experience with AI-powered courses.</p>
            <div className="auth-benefits">
              <div className="auth-benefit">
                <span className="benefit-check">✓</span>
                <span>Save your progress</span>
              </div>
              <div className="auth-benefit">
                <span className="benefit-check">✓</span>
                <span>Access advanced features</span>
              </div>
              <div className="auth-benefit">
                <span className="benefit-check">✓</span>
                <span>Track your learning analytics</span>
              </div>
            </div>
            <div className="auth-buttons">
              <Button
                onClick={() => navigate('/login?mode=register')}
                variant="gradient"
                size="lg"
              >
                Get Started Free
              </Button>
              <Button
                onClick={() => navigate('/login')}
                variant="ghost"
                size="lg"
              >
                Sign In
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* Welcome Back Section */}
      {isAuthenticated && user && (
        <div className="welcome-back">
          <div className="welcome-content">
            <span className="welcome-emoji">👋</span>
            <div className="welcome-text">
              <h3>Welcome back, {user.name}!</h3>
              <p>Ready to continue your learning journey?</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};