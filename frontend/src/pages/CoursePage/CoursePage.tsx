import React, { useEffect, useState, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { QuizQuestion } from '../../components/quiz/QuizQuestion';
import { Button } from '../../components/ui/Button';
import { ProgressBar } from '../../components/ui/ProgressBar';
import { useQuizProgress } from '../../hooks/useQuizProgress';
import { useAuth } from '../../hooks/useAuth';
import { courseService } from '../../services/courseService';
import type { CourseData } from '../../types/api';

export const CoursePage: React.FC = () => {
  const { courseId } = useParams<{ courseId: string }>();
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();
  const [course, setCourse] = useState<CourseData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const {
    currentQuestionIndex,
    answers,
    isSubmitted,
    score,
    progress,
    isComplete,
    canGoNext,
    canGoPrevious,
    answeredCount,
    goToNext,
    goToPrevious,
    goToQuestion,
    setAnswer,
    getAnswer,
    startQuiz,
    submitQuiz,
    resetQuiz
  } = useQuizProgress(course?.questions || []);

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login', { 
        state: { 
          returnTo: `/course/${courseId}`,
          message: 'Please log in to access your course.'
        }
      });
      return;
    }

    if (!courseId) {
      navigate('/');
      return;
    }

    loadCourse();
  }, [courseId, isAuthenticated, navigate, loadCourse]);

  const loadCourse = useCallback(async () => {
    if (!courseId) return;

    try {
      setIsLoading(true);
      const response = await courseService.getCourseStatus(courseId);
      
      if (response.success && response.course) {
        setCourse(response.course);
        startQuiz();
      } else {
        setError(response.error || 'Course not found');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load course');
    } finally {
      setIsLoading(false);
    }
  }, [courseId, startQuiz]);

  const handleSubmitQuiz = async () => {
    if (!courseId || !course) return;

    try {
      await submitQuiz(courseId);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to submit quiz');
    }
  };

  const handleRestartQuiz = () => {
    resetQuiz();
    startQuiz();
  };

  if (isLoading) {
    return (
      <div className="course-page loading">
        <div className="loading-content">
          <div className="loading-spinner">⏳</div>
          <h2>Loading your course...</h2>
          <p>Please wait while we prepare your learning materials.</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="course-page error">
        <div className="error-content">
          <div className="error-icon">❌</div>
          <h2>Oops! Something went wrong</h2>
          <p>{error}</p>
          <div className="error-actions">
            <Button onClick={() => navigate('/')} variant="primary">
              Back to Home
            </Button>
            <Button onClick={loadCourse} variant="secondary">
              Try Again
            </Button>
          </div>
        </div>
      </div>
    );
  }

  if (!course) {
    return (
      <div className="course-page not-found">
        <div className="not-found-content">
          <div className="not-found-icon">🔍</div>
          <h2>Course Not Found</h2>
          <p>The course you're looking for doesn't exist or has been removed.</p>
          <Button onClick={() => navigate('/')} variant="primary">
            Back to Home
          </Button>
        </div>
      </div>
    );
  }

  const currentQuestion = course.questions[currentQuestionIndex];

  if (isSubmitted) {
    return (
      <div className="course-page results">
        <div className="results-content">
          <div className="results-header">
            <div className="score-circle">
              <span className="score-value">{Math.round(score)}%</span>
            </div>
            <h2>Quiz Complete! 🎉</h2>
            <p className="score-text">
              You scored {Math.round(score)}% ({answeredCount} out of {course.questions.length} questions)
            </p>
          </div>

          <div className="results-summary">
            <div className="summary-stats">
              <div className="stat-item">
                <span className="stat-label">Correct Answers</span>
                <span className="stat-value">
                  {Object.values(answers).filter(a => a.isCorrect).length}
                </span>
              </div>
              <div className="stat-item">
                <span className="stat-label">Total Questions</span>
                <span className="stat-value">{course.questions.length}</span>
              </div>
              <div className="stat-item">
                <span className="stat-label">Course</span>
                <span className="stat-value">{course.title}</span>
              </div>
            </div>
          </div>

          <div className="results-actions">
            <Button onClick={handleRestartQuiz} variant="primary" size="lg">
              Retake Quiz
            </Button>
            <Button onClick={() => navigate('/')} variant="secondary" size="lg">
              New Course
            </Button>
          </div>

          <div className="question-review">
            <h3>Review Your Answers</h3>
            <div className="question-list">
              {course.questions.map((question, index) => (
                <div key={question.id} className="question-item">
                  <div className="question-header">
                    <span className="question-number">Q{index + 1}</span>
                    <span className={`question-status ${
                      answers[question.id]?.isCorrect ? 'correct' : 'incorrect'
                    }`}>
                      {answers[question.id]?.isCorrect ? '✓' : '✗'}
                    </span>
                  </div>
                  <p className="question-text">{question.question}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="course-page quiz">
      <div className="quiz-header">
        <div className="course-info">
          <h1 className="course-title">{course.title}</h1>
          {course.description && (
            <p className="course-description">{course.description}</p>
          )}
        </div>
        
        <div className="quiz-progress">
          <div className="progress-info">
            <span className="progress-text">
              Question {currentQuestionIndex + 1} of {course.questions.length}
            </span>
            <span className="answered-count">
              {answeredCount} answered
            </span>
          </div>
          <ProgressBar
            value={((currentQuestionIndex + 1) / course.questions.length) * 100}
            className="question-progress"
          />
          <ProgressBar
            value={progress}
            className="completion-progress"
            variant="success"
          />
        </div>
      </div>

      <div className="quiz-content">
        {currentQuestion && (
          <QuizQuestion
            question={currentQuestion}
            answer={getAnswer(currentQuestion.id)}
            onAnswerChange={(answer) => setAnswer(currentQuestion.id, answer)}
            questionNumber={currentQuestionIndex + 1}
            totalQuestions={course.questions.length}
            className="current-question"
          />
        )}
      </div>

      <div className="quiz-navigation">
        <div className="nav-buttons">
          <Button
            onClick={goToPrevious}
            disabled={!canGoPrevious}
            variant="secondary"
            leftIcon="←"
          >
            Previous
          </Button>
          
          {canGoNext ? (
            <Button
              onClick={goToNext}
              variant="primary"
              rightIcon="→"
            >
              Next
            </Button>
          ) : (
            <Button
              onClick={handleSubmitQuiz}
              variant="primary"
              disabled={!isComplete}
              className="submit-button"
            >
              {isComplete ? 'Submit Quiz' : `Answer ${course.questions.length - answeredCount} more`}
            </Button>
          )}
        </div>

        <div className="question-dots">
          {course.questions.map((question, index) => (
            <button
              key={question.id}
              onClick={() => goToQuestion(index)}
              className={`question-dot ${
                index === currentQuestionIndex ? 'current' : ''
              } ${
                answers[question.id] ? 'answered' : 'unanswered'
              }`}
              title={`Question ${index + 1} ${answers[question.id] ? '(answered)' : '(unanswered)'}`}
            >
              {index + 1}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};