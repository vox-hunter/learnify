import React, { useCallback, useState } from 'react';
import type { Question } from '../../types/api';
import type { QuizAnswer } from './QuizQuestion';
import { Input } from '../ui/Input';

interface ShortAnswerProps {
  question: Question;
  answer: QuizAnswer | null;
  onAnswerChange: (answer: QuizAnswer) => void;
  isSubmitted?: boolean;
  showCorrectAnswer?: boolean;
}

export const ShortAnswer: React.FC<ShortAnswerProps> = ({
  question,
  answer,
  onAnswerChange,
  isSubmitted = false,
  showCorrectAnswer = false
}) => {
  const [inputValue, setInputValue] = useState(answer?.value as string || '');

  const handleInputChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    if (isSubmitted) return;
    
    const newValue = e.target.value;
    setInputValue(newValue);
    
    // Check if answer is correct (case-insensitive comparison)
    let isCorrect: boolean | undefined;
    if (showCorrectAnswer && question.correctAnswer) {
      const correctAnswer = question.correctAnswer.toString().toLowerCase().trim();
      const userAnswer = newValue.toLowerCase().trim();
      isCorrect = userAnswer === correctAnswer;
    }
    
    const newAnswer: QuizAnswer = {
      questionId: question.id,
      type: 'short_answer',
      value: newValue,
      isCorrect
    };
    
    onAnswerChange(newAnswer);
  }, [question.id, question.correctAnswer, onAnswerChange, isSubmitted, showCorrectAnswer]);

  const getInputStatus = () => {
    if (!showCorrectAnswer || !question.correctAnswer || !inputValue.trim()) {
      return 'default';
    }
    
    const correctAnswer = question.correctAnswer.toString().toLowerCase().trim();
    const userAnswer = inputValue.toLowerCase().trim();
    
    return userAnswer === correctAnswer ? 'correct' : 'incorrect';
  };

  const inputStatus = getInputStatus();
  const showHint = showCorrectAnswer && inputStatus === 'incorrect' && inputValue.trim();

  return (
    <div className="short-answer">
      <div className="answer-input-container">
        <Input
          type="text"
          value={inputValue}
          onChange={handleInputChange}
          disabled={isSubmitted}
          placeholder="Enter your answer here..."
          className={`answer-input answer-input--${inputStatus}`}
          size="md"
        />
        
        {showCorrectAnswer && inputStatus !== 'default' && (
          <span className={`answer-indicator answer-indicator--${inputStatus}`}>
            {inputStatus === 'correct' ? '✓' : '✗'}
          </span>
        )}
      </div>
      
      {showHint && (
        <div className="correct-answer-hint">
          <p className="hint-text">
            <strong>Correct answer:</strong> {question.correctAnswer}
          </p>
        </div>
      )}
      

    </div>
  );
};