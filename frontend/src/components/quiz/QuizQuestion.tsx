import React from 'react';
import type { Question } from '../../types/api';
import { MultipleChoice } from './MultipleChoice';
import { FillInBlanks } from './FillInBlanks';
import { TrueFalse } from './TrueFalse';
import { ShortAnswer } from './ShortAnswer';

export interface QuizAnswer {
  questionId: string;
  type: string;
  value: string | boolean | string[];
  isCorrect?: boolean;
}

interface QuizQuestionProps {
  question: Question;
  answer: QuizAnswer | null;
  onAnswerChange: (answer: QuizAnswer) => void;
  isSubmitted?: boolean;
  showCorrectAnswer?: boolean;
  questionNumber?: number;
  totalQuestions?: number;
  className?: string;
}

export const QuizQuestion: React.FC<QuizQuestionProps> = ({
  question,
  answer,
  onAnswerChange,
  isSubmitted = false,
  showCorrectAnswer = false,
  questionNumber,
  totalQuestions,
  className = ''
}) => {
  const renderQuestionContent = () => {
    const commonProps = {
      question,
      answer,
      onAnswerChange,
      isSubmitted,
      showCorrectAnswer
    };

    switch (question.type) {
      case 'multiple_choice':
        return <MultipleChoice {...commonProps} />;
      
      case 'fill_in_blank':
        return <FillInBlanks {...commonProps} />;
      
      case 'true_false':
        return <TrueFalse {...commonProps} />;
      
      case 'short_answer':
        return <ShortAnswer {...commonProps} />;
      
      default:
        return (
          <div className="question-error">
            <p>Unsupported question type: {question.type}</p>
          </div>
        );
    }
  };

  const getQuestionStatus = () => {
    if (!isSubmitted) return null;
    
    if (showCorrectAnswer) {
      const isCorrect = answer?.isCorrect === true;
      return isCorrect ? 'correct' : 'incorrect';
    }
    
    return 'submitted';
  };

  const questionStatus = getQuestionStatus();

  return (
    <div className={`quiz-question ${questionStatus ? `quiz-question--${questionStatus}` : ''} ${className}`}>
      {(questionNumber !== undefined && totalQuestions !== undefined) && (
        <div className="question-header">
          <span className="question-number">
            Question {questionNumber} of {totalQuestions}
          </span>
          {questionStatus && (
            <span className={`question-status question-status--${questionStatus}`}>
              {questionStatus === 'correct' && '✓ Correct'}
              {questionStatus === 'incorrect' && '✗ Incorrect'}
              {questionStatus === 'submitted' && '⏳ Submitted'}
            </span>
          )}
        </div>
      )}
      
      <div className="question-content">
        <h3 className="question-text">{question.question}</h3>
        
        {question.explanation && showCorrectAnswer && (
          <div className="question-explanation">
            <h4>Explanation:</h4>
            <p>{question.explanation}</p>
          </div>
        )}
        
        <div className="question-input">
          {renderQuestionContent()}
        </div>
      </div>
      

    </div>
  );
};