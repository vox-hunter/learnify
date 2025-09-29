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
      <div className="hero-section">
        <div className="hero-content">
          <h1 className="hero-title">
            Transform Your Documents into Interactive Learning
          </h1>
          <p className="hero-description">
            Upload any document or provide a URL, and we'll create personalized quizzes 
            and learning materials powered by AI.
          </p>
        </div>
      </div>

      <div className="upload-section">
        <div className="upload-container">
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
                <h3>🎯 Generating Your Course</h3>
                <p>We're analyzing your document and creating personalized learning content...</p>
                <div className="progress-info">
                  <span>Progress: {Math.round(progress)}%</span>
                </div>
              </div>
            </div>
          )}

          {courseError && (
            <div className="error-message">
              <p>❌ {courseError}</p>
            </div>
          )}

          {courseId && !isGenerating && (
            <div className="success-section">
              <div className="success-content">
                <h3>✅ Course Ready!</h3>
                <p>Your personalized learning course has been generated successfully.</p>
                <Button
                  onClick={handleViewCourse}
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

      <div className="features-section">
        <div className="features-grid">
          <div className="feature-card">
            <div className="feature-icon">🤖</div>
            <h3>AI-Powered</h3>
            <p>Advanced AI analyzes your content to create relevant questions and explanations.</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">📊</div>
            <h3>Progress Tracking</h3>
            <p>Monitor your learning progress with detailed analytics and performance insights.</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">🎯</div>
            <h3>Adaptive Learning</h3>
            <p>Questions adapt to your skill level for optimal learning experience.</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">⚡</div>
            <h3>Instant Results</h3>
            <p>Get immediate feedback and explanations to reinforce your understanding.</p>
          </div>
        </div>
      </div>

      {!isAuthenticated && (
        <div className="auth-prompt">
          <div className="auth-content">
            <h3>Ready to Get Started?</h3>
            <p>Create an account to save your progress and access advanced features.</p>
            <div className="auth-buttons">
              <Button
                onClick={() => navigate('/login')}
                variant="primary"
                size="lg"
              >
                Sign In
              </Button>
              <Button
                onClick={() => navigate('/login?mode=register')}
                variant="secondary"
                size="lg"
              >
                Create Account
              </Button>
            </div>
          </div>
        </div>
      )}

      {isAuthenticated && user && (
        <div className="welcome-back">
          <p>Welcome back, {user.name}! 👋</p>
        </div>
      )}
    </div>
  );
};