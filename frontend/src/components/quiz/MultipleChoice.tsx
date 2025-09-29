import React, { useCallback } from 'react';
import type { Question } from '../../types/api';
import type { QuizAnswer } from './QuizQuestion';

interface MultipleChoiceProps {
  question: Question;
  answer: QuizAnswer | null;
  onAnswerChange: (answer: QuizAnswer) => void;
  isSubmitted?: boolean;
  showCorrectAnswer?: boolean;
}

export const MultipleChoice: React.FC<MultipleChoiceProps> = ({
  question,
  answer,
  onAnswerChange,
  isSubmitted = false,
  showCorrectAnswer = false
}) => {
  const handleOptionSelect = useCallback((selectedOption: string) => {
    if (isSubmitted) return;
    
    const newAnswer: QuizAnswer = {
      questionId: question.id,
      type: 'multiple_choice',
      value: selectedOption,
      isCorrect: showCorrectAnswer ? selectedOption === question.correctAnswer : undefined
    };
    
    onAnswerChange(newAnswer);
  }, [question.id, question.correctAnswer, onAnswerChange, isSubmitted, showCorrectAnswer]);

  const getOptionStatus = (option: string) => {
    if (!showCorrectAnswer) {
      return answer?.value === option ? 'selected' : 'default';
    }
    
    const isCorrectOption = option === question.correctAnswer;
    const isSelectedOption = answer?.value === option;
    
    if (isCorrectOption && isSelectedOption) return 'correct-selected';
    if (isCorrectOption && !isSelectedOption) return 'correct-unselected';
    if (!isCorrectOption && isSelectedOption) return 'incorrect-selected';
    return 'default';
  };

  if (!question.options || question.options.length === 0) {
    return (
      <div className="multiple-choice-error">
        <p>No options available for this question.</p>
      </div>
    );
  }

  return (
    <div className="multiple-choice">
      <div className="options-list">
        {question.options?.map((option: string, index: number) => {
          const optionStatus = getOptionStatus(option);
          const optionId = `${question.id}-option-${index}`;
          
          return (
            <div
              key={index}
              className={`option option--${optionStatus} ${
                isSubmitted ? 'option--disabled' : 'option--interactive'
              }`}
            >
              <label htmlFor={optionId} className="option__label">
                <input
                  type="radio"
                  id={optionId}
                  name={`question-${question.id}`}
                  value={option}
                  checked={answer?.value === option}
                  onChange={() => handleOptionSelect(option)}
                  disabled={isSubmitted}
                  className="option__input"
                />
                
                <span className="option__indicator">
                  {showCorrectAnswer && (
                    <>
                      {optionStatus === 'correct-selected' && '✓'}
                      {optionStatus === 'correct-unselected' && '✓'}
                      {optionStatus === 'incorrect-selected' && '✗'}
                    </>
                  )}
                </span>
                
                <span className="option__text">{option}</span>
              </label>
            </div>
          );
        })}
      </div>
      
      {showCorrectAnswer && answer?.value !== question.correctAnswer && (
        <div className="correct-answer-hint">
          <p className="hint-text">
            <strong>Correct answer:</strong> {question.correctAnswer}
          </p>
        </div>
      )}
    </div>
  );
};