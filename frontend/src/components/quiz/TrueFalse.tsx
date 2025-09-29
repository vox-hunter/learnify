import React, { useCallback } from 'react';
import type { Question } from '../../types/api';
import type { QuizAnswer } from './QuizQuestion';

interface TrueFalseProps {
  question: Question;
  answer: QuizAnswer | null;
  onAnswerChange: (answer: QuizAnswer) => void;
  isSubmitted?: boolean;
  showCorrectAnswer?: boolean;
}

export const TrueFalse: React.FC<TrueFalseProps> = ({
  question,
  answer,
  onAnswerChange,
  isSubmitted = false,
  showCorrectAnswer = false
}) => {
  const handleOptionSelect = useCallback((selectedValue: boolean) => {
    if (isSubmitted) return;
    
    let isCorrect: boolean | undefined;
    if (showCorrectAnswer && question.correctAnswer !== undefined) {
      const correctValue = question.correctAnswer === 'true' || question.correctAnswer === true || 
        (Array.isArray(question.correctAnswer) ? question.correctAnswer[0] === 'true' : false);
      isCorrect = selectedValue === correctValue;
    }
    
    const newAnswer: QuizAnswer = {
      questionId: question.id,
      type: 'true_false',
      value: selectedValue,
      isCorrect
    };
    
    onAnswerChange(newAnswer);
  }, [question.id, question.correctAnswer, onAnswerChange, isSubmitted, showCorrectAnswer]);

  const getOptionStatus = (optionValue: boolean) => {
    const isSelected = answer?.value === optionValue;
    
    if (!showCorrectAnswer) {
      return isSelected ? 'selected' : 'default';
    }
    
    const correctValue = question.correctAnswer === 'true' || 
      (Array.isArray(question.correctAnswer) ? question.correctAnswer[0] === 'true' : false);
    const isCorrectOption = optionValue === correctValue;
    
    if (isCorrectOption && isSelected) return 'correct-selected';
    if (isCorrectOption && !isSelected) return 'correct-unselected';
    if (!isCorrectOption && isSelected) return 'incorrect-selected';
    return 'default';
  };

  const trueStatus = getOptionStatus(true);
  const falseStatus = getOptionStatus(false);

  return (
    <div className="true-false">
      <div className="options-container">
        <div className={`option option--${trueStatus} ${
          isSubmitted ? 'option--disabled' : 'option--interactive'
        }`}>
          <label htmlFor={`${question.id}-true`} className="option__label">
            <input
              type="radio"
              id={`${question.id}-true`}
              name={`question-${question.id}`}
              value="true"
              checked={answer?.value === true}
              onChange={() => handleOptionSelect(true)}
              disabled={isSubmitted}
              className="option__input"
            />
            
            <span className="option__indicator">
              {showCorrectAnswer && (
                <>
                  {trueStatus === 'correct-selected' && '✓'}
                  {trueStatus === 'correct-unselected' && '✓'}
                  {trueStatus === 'incorrect-selected' && '✗'}
                </>
              )}
            </span>
            
            <span className="option__text">True</span>
          </label>
        </div>
        
        <div className={`option option--${falseStatus} ${
          isSubmitted ? 'option--disabled' : 'option--interactive'
        }`}>
          <label htmlFor={`${question.id}-false`} className="option__label">
            <input
              type="radio"
              id={`${question.id}-false`}
              name={`question-${question.id}`}
              value="false"
              checked={answer?.value === false}
              onChange={() => handleOptionSelect(false)}
              disabled={isSubmitted}
              className="option__input"
            />
            
            <span className="option__indicator">
              {showCorrectAnswer && (
                <>
                  {falseStatus === 'correct-selected' && '✓'}
                  {falseStatus === 'correct-unselected' && '✓'}
                  {falseStatus === 'incorrect-selected' && '✗'}
                </>
              )}
            </span>
            
            <span className="option__text">False</span>
          </label>
        </div>
      </div>
      
      {showCorrectAnswer && (
        <div className="correct-answer-hint">
          <p className="hint-text">
            <strong>Correct answer:</strong> {(question.correctAnswer === 'true' ||
              (Array.isArray(question.correctAnswer) ? question.correctAnswer[0] === 'true' : false)) ? 'True' : 'False'}
          </p>
        </div>
      )}
    </div>
  );
};