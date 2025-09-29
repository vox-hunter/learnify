import React, { useCallback, useMemo } from 'react';
import type { Question } from '../../types/api';
import type { QuizAnswer } from './QuizQuestion';
import { Input } from '../ui/Input';

interface FillInBlanksProps {
  question: Question;
  answer: QuizAnswer | null;
  onAnswerChange: (answer: QuizAnswer) => void;
  isSubmitted?: boolean;
  showCorrectAnswer?: boolean;
}

export const FillInBlanks: React.FC<FillInBlanksProps> = ({
  question,
  answer,
  onAnswerChange,
  isSubmitted = false,
  showCorrectAnswer = false
}) => {
  // Parse the question text to find blanks (marked with ___)
  const parsedQuestion = useMemo(() => {
    const parts = question.question.split('___');
    const blanks = Array(parts.length - 1).fill('');
    
    // If we have an existing answer, populate the blanks
    if (answer?.value && typeof answer.value === 'object') {
      const answerArray = answer.value as string[];
      answerArray.forEach((value, index) => {
        if (index < blanks.length) {
          blanks[index] = value;
        }
      });
    }
    
    return { parts, blanks };
  }, [question.question, answer]);

  const handleBlankChange = useCallback((index: number, value: string) => {
    if (isSubmitted) return;
    
    const newBlanks = [...parsedQuestion.blanks];
    newBlanks[index] = value;
    
    // Check if answer is correct (if we have correct answers to compare)
    let isCorrect: boolean | undefined;
    if (showCorrectAnswer && question.correctAnswer) {
      const correctAnswers = Array.isArray(question.correctAnswer) 
        ? question.correctAnswer 
        : [question.correctAnswer];
      
      isCorrect = newBlanks.every((blank, i) => 
        correctAnswers[i] && 
        blank.toLowerCase().trim() === correctAnswers[i].toLowerCase().trim()
      );
    }
    
    const newAnswer: QuizAnswer = {
      questionId: question.id,
      type: 'fill_in_blanks',
      value: newBlanks,
      isCorrect
    };
    
    onAnswerChange(newAnswer);
  }, [question.id, question.correctAnswer, onAnswerChange, isSubmitted, showCorrectAnswer, parsedQuestion.blanks]);

  const getBlankStatus = (index: number) => {
    if (!showCorrectAnswer || !question.correctAnswer) {
      return 'default';
    }
    
    const correctAnswers = Array.isArray(question.correctAnswer) 
      ? question.correctAnswer 
      : [question.correctAnswer];
    
    const userAnswer = parsedQuestion.blanks[index]?.toLowerCase().trim();
    const correctAnswer = correctAnswers[index]?.toLowerCase().trim();
    
    if (!userAnswer) return 'default';
    
    return userAnswer === correctAnswer ? 'correct' : 'incorrect';
  };

  if (parsedQuestion.parts.length < 2) {
    return (
      <div className="fill-in-blanks-error">
        <p>No blanks found in question. Use ___ to mark blanks.</p>
      </div>
    );
  }

  return (
    <div className="fill-in-blanks">
      <div className="question-with-blanks">
        {parsedQuestion.parts.map((part: string, index: number) => (
          <React.Fragment key={index}>
            <span className="question-part">{part}</span>
            {index < parsedQuestion.blanks.length && (
              <span className="blank-container">
                <Input
                  type="text"
                  value={parsedQuestion.blanks[index]}
                  onChange={(e) => handleBlankChange(index, e.target.value)}
                  disabled={isSubmitted}
                  className={`blank-input blank-input--${getBlankStatus(index)}`}
                  placeholder={`Blank ${index + 1}`}
                  size="sm"
                />
                {showCorrectAnswer && getBlankStatus(index) !== 'default' && (
                  <span className={`blank-indicator blank-indicator--${getBlankStatus(index)}`}>
                    {getBlankStatus(index) === 'correct' ? '✓' : '✗'}
                  </span>
                )}
              </span>
            )}
          </React.Fragment>
        ))}
      </div>
      
      {showCorrectAnswer && question.correctAnswer && (
        <div className="correct-answers-hint">
          <p className="hint-text">
            <strong>Correct answers:</strong>
          </p>
          <ul className="correct-answers-list">
            {(Array.isArray(question.correctAnswer) ? question.correctAnswer : [question.correctAnswer])
              .map((answer: string, index: number) => (
                <li key={index} className="correct-answer-item">
                  Blank {index + 1}: {answer}
                </li>
              ))
            }
          </ul>
        </div>
      )}
    </div>
  );
};