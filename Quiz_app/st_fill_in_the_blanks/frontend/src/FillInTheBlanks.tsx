import React, { useState, useEffect, useRef, useMemo } from "react"
import {
  Streamlit,
  withStreamlitConnection,
} from "streamlit-component-lib"
import "./FillInTheBlanks.css"

interface BlankState {
  answer: string;
  userInput: string;
  isCorrect: boolean;
  isAttempted: boolean;
  isRevealed: boolean;
}

interface FillInTheBlanksProps {
  args: {
    question_text_full: string
    correctAnswer: string | string[] // Can be single answer or array for multiple blanks
    default_value?: string | string[]
    disabled?: boolean
  }
}

const FillInTheBlanks: React.FC<FillInTheBlanksProps> = (props) => {
  // Initialize all hooks first (React rules requirement)
  const [blanks, setBlanks] = useState<BlankState[]>([]);
  const [currentBlankIndex, setCurrentBlankIndex] = useState(0);
  const [allCompleted, setAllCompleted] = useState(false);
  const [showFeedback, setShowFeedback] = useState(false);
  const [feedbackMessage, setFeedbackMessage] = useState("");
  const [hasError, setHasError] = useState<string | null>(null);
  
  const componentRootRef = useRef<HTMLDivElement>(null);
  const inputRefs = useRef<(HTMLInputElement | null)[]>([]);
  // Process props safely using useMemo
  const { safeQuestionText, safeAnswers, isDisabled } = useMemo(() => {
    let questionText = "";
    let answers: string[] = [];
    let disabled = false;
    
    try {
      const { question_text_full, correctAnswer, disabled: propDisabled } = props.args || {};
      
      // Extract disabled state
      disabled = Boolean(propDisabled);
      
      // Enhanced type safety for question text
      if (question_text_full != null) {
        if (typeof question_text_full === 'string') {
          questionText = question_text_full;
        } else {
          console.warn("Converting non-string question_text_full:", typeof question_text_full, question_text_full);
          questionText = String(question_text_full);
        }
      }
      
      // Enhanced type safety for answers
      if (correctAnswer != null) {
        if (Array.isArray(correctAnswer)) {
          answers = correctAnswer.map(ans => {
            if (ans != null) {
              if (typeof ans === 'string') {
                return ans;
              } else {
                console.warn("Converting non-string answer:", typeof ans, ans);
                return String(ans);
              }
            }
            return "";
          });        } else {
          if (typeof correctAnswer === 'string') {
            answers = [correctAnswer];
          } else {
            answers = [String(correctAnswer)];
          }
        }
      }
      
    } catch (error) {
      console.error("Error processing component props:", error);
      setHasError(`Error processing props: ${error instanceof Error ? error.message : String(error)}`);
    }
    
    return { safeQuestionText: questionText, safeAnswers: answers, isDisabled: disabled };
  }, [props.args]);  // Validate data and set error if needed
  useEffect(() => {
    if (!safeQuestionText || safeAnswers.length === 0) {
      setHasError(`Invalid fill-in-the-blanks data. Question: '${safeQuestionText}', Answers: ${JSON.stringify(safeAnswers)}`);
    } else {
      setHasError(null);
    }
  }, [safeQuestionText, safeAnswers]);
  // Initialize blanks from answers
  useEffect(() => {
    if (safeAnswers.length > 0 && !hasError) {
      const initialBlanks = safeAnswers.map((answer: string) => {
        if (isDisabled) {
          // If component is disabled, pre-fill with correct answers and mark as correct
          return {
            answer: answer.trim(),
            userInput: answer.trim(),
            isCorrect: true,
            isAttempted: true,
            isRevealed: false
          };
        } else {
          // Normal initialization for active component
          return {
            answer: answer.trim(),
            userInput: "",
            isCorrect: false,
            isAttempted: false,
            isRevealed: false
          };
        }
      });
      setBlanks(initialBlanks);
      setCurrentBlankIndex(0);
      setAllCompleted(isDisabled); // If disabled, mark as completed
      setShowFeedback(false);
      inputRefs.current = new Array(initialBlanks.length).fill(null);
    }
  }, [safeAnswers, hasError, isDisabled]);

  // Set component height
  useEffect(() => {
    if (componentRootRef.current) {
      const contentHeight = Math.max(componentRootRef.current.scrollHeight, 80);
      Streamlit.setFrameHeight(contentHeight + 20);
    }
  }, [safeQuestionText, safeAnswers, blanks, showFeedback]);

  // Return error state if there's an error
  if (hasError) {
    return (
      <div style={{ color: 'red', padding: '10px', border: '1px solid red', borderRadius: '4px' }}>
        <strong>Fill-in-the-blanks component error:</strong>
        <br />
        {hasError}
        <br />
        <small>Props: {JSON.stringify(props, null, 2)}</small>
      </div>
    );
  }  // Check if current blank is correct
  const checkCurrentBlank = (overrideValue?: string) => {
    if (currentBlankIndex >= blanks.length || allCompleted || isDisabled) return;

    const currentBlank = blanks[currentBlankIndex];
    // Use override value if provided (for auto-check), otherwise use current state
    const inputValue = overrideValue !== undefined ? overrideValue : currentBlank.userInput;
    const userAnswer = inputValue.trim().toLowerCase();
    const correctAnswer = currentBlank.answer.toLowerCase();
    const isCorrect = userAnswer === correctAnswer;    // Remove debug logging
    setBlanks(prev => {
      const newBlanks = [...prev];
      newBlanks[currentBlankIndex] = {
        ...currentBlank,
        userInput: inputValue, // Use the actual input value, not just currentBlank.userInput
        isCorrect,
        isAttempted: true,
        isRevealed: false
      };
      
      // Check if this was the last blank to complete
      const updatedBlanks = newBlanks;
      const hasUnatttempted = updatedBlanks.some(blank => !blank.isAttempted);
      
      // Calculate the correct score immediately with the updated blanks
      const allCorrect = updatedBlanks.every(blank => blank.isCorrect);
      const correctCount = updatedBlanks.filter(blank => blank.isCorrect).length;
        // Remove debug logging
      
        // Schedule the next action after state update
      if (!hasUnatttempted) {
        setAllCompleted(true);
        
        // Use the pre-calculated values to ensure accuracy
        Streamlit.setComponentValue({
          value: updatedBlanks.map(blank => blank.userInput || blank.answer),
          isCorrect: allCorrect,
          correctCount: correctCount,
          totalBlanks: updatedBlanks.length,
          action: 'question_complete'
        });
      } else {
        // Find next unattempted blank
        const nextIndex = updatedBlanks.findIndex(blank => !blank.isAttempted);
        if (nextIndex !== -1) {
          setCurrentBlankIndex(nextIndex);
          // Focus next input
          setTimeout(() => {
            if (inputRefs.current[nextIndex]) {
              inputRefs.current[nextIndex]?.focus();
            }
          }, 100);
        }
      }
      
      return newBlanks;
    });

    if (isCorrect) {
      setFeedbackMessage("✅ Correct!");
    } else {
      setFeedbackMessage(`❌ Incorrect. The answer was: ${currentBlank.answer}`);
    }
    
    setShowFeedback(true);
    setTimeout(() => {
      setShowFeedback(false);
    }, isCorrect ? 800 : 1500); // Shorter feedback display for correct answers
  };  // Give up on current blank
  const giveUpCurrentBlank = () => {
    if (currentBlankIndex >= blanks.length || allCompleted || isDisabled) return;

    const currentBlank = blanks[currentBlankIndex];    setBlanks(prev => {
      const newBlanks = [...prev];      newBlanks[currentBlankIndex] = {
        ...currentBlank,
        isCorrect: false,
        isAttempted: true,
        isRevealed: true,
        userInput: currentBlank.userInput // Keep the user's input, we'll show the correct answer via isRevealed
      };
      
      // Check if this was the last blank to complete
      const updatedBlanks = newBlanks;
      const hasUnatttempted = updatedBlanks.some(blank => !blank.isAttempted);
      
      // Calculate the correct score immediately with the updated blanks
      const allCorrect = updatedBlanks.every(blank => blank.isCorrect);
      const correctCount = updatedBlanks.filter(blank => blank.isCorrect).length;
        // Remove debug logging
      
        // Schedule the next action after state update
      if (!hasUnatttempted) {
        setAllCompleted(true);
        
        // Use the pre-calculated values to ensure accuracy
        Streamlit.setComponentValue({
          value: updatedBlanks.map(blank => blank.userInput || blank.answer),
          isCorrect: allCorrect,
          correctCount: correctCount,
          totalBlanks: updatedBlanks.length,
          action: 'question_complete'
        });
      } else {
        // Find next unattempted blank
        const nextIndex = updatedBlanks.findIndex(blank => !blank.isAttempted);
        if (nextIndex !== -1) {
          setCurrentBlankIndex(nextIndex);
          // Focus next input
          setTimeout(() => {
            if (inputRefs.current[nextIndex]) {
              inputRefs.current[nextIndex]?.focus();
            }
          }, 100);
        }
      }
      
      return newBlanks;
    });

    setFeedbackMessage(`💡 The answer was: ${currentBlank.answer}`);
    setShowFeedback(true);
    setTimeout(() => {
      setShowFeedback(false);
    }, 2000);
  };  // Handle input change for current blank
  const handleInputChange = (value: string) => {
    if (allCompleted || isDisabled) return;

    setBlanks(prev => {
      const newBlanks = [...prev];
      if (newBlanks[currentBlankIndex]) {
        newBlanks[currentBlankIndex] = {
          ...newBlanks[currentBlankIndex],
          userInput: value
        };
      }
      return newBlanks;
    });    // Auto-check answer as user types
    const currentBlank = blanks[currentBlankIndex];
    if (currentBlank) {
      const userAnswer = value.trim().toLowerCase();
      const correctAnswer = currentBlank.answer.toLowerCase();
      const isMatch = userAnswer === correctAnswer;
        // Remove debug logging
      
        if (isMatch) {
        // Answer is correct! Auto-submit with a small delay to show the correct input
        setTimeout(() => {
          checkCurrentBlank(value); // Pass the actual typed value
        }, 300);
      }
    }
  };  // Handle key press
  const handleKeyDown = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter' && !showFeedback) {
      const currentBlank = blanks[currentBlankIndex];
      if (currentBlank?.userInput.trim()) {
        checkCurrentBlank();
      }
    } else if (event.key === 'Escape') {
      // Allow users to give up with Escape key
      giveUpCurrentBlank();
    }
  };

  // Render the question with blanks
  const renderQuestion = () => {
    const BLANK_PLACEHOLDER_REGEX = /(_{3,})/g;
    const parts = safeQuestionText.split(BLANK_PLACEHOLDER_REGEX);
    let blankIndex = 0;

    return parts.map((part: string, index: number) => {
      if (BLANK_PLACEHOLDER_REGEX.test(part)) {
        BLANK_PLACEHOLDER_REGEX.lastIndex = 0;
          if (blankIndex < blanks.length) {
          const blank = blanks[blankIndex];
          const isCurrentBlank = blankIndex === currentBlankIndex && !allCompleted && !isDisabled;
          const answerLength = Math.max(blank.answer.length, 3);
            let displayValue = "";
          let blankClass = "blank-wrapper";
          
          if (blank.isAttempted) {
            if (blank.isCorrect) {
              displayValue = blank.userInput || blank.answer; // Ensure we show the answer even if userInput is empty
              blankClass += " correct";
            } else if (blank.isRevealed) {
              displayValue = blank.answer; // Show correct answer when revealed
              blankClass += " revealed";
            } else {
              displayValue = blank.userInput;
              blankClass += " incorrect";
            }
          } else if (isCurrentBlank) {
            blankClass += " current";
          } else {
            blankClass += " pending";
          }          // Remove debug logging

          const element = (
            <span key={index} className={blankClass}>
              {blank.isAttempted ? (
                <span 
                  className="completed-blank"
                  style={{ 
                    minWidth: `${answerLength * 0.8}em`,
                    display: 'inline-block',
                    textAlign: 'center'
                  }}
                >
                  {displayValue}
                </span>              ) : isCurrentBlank ? (
                <input
                  ref={el => inputRefs.current[blankIndex] = el}
                  type="text"
                  value={blank.userInput}
                  onChange={(e) => handleInputChange(e.target.value)}
                  onKeyDown={handleKeyDown}
                  className={`blank-input ${
                    blank.userInput.trim().toLowerCase() === blank.answer.toLowerCase() 
                      ? 'near-correct' 
                      : ''
                  }`}
                  style={{ 
                    width: `${Math.max(answerLength * 0.8, 5)}em`
                  }}
                  placeholder=""
                  maxLength={answerLength + 5}
                  autoFocus
                  disabled={showFeedback || isDisabled}
                />
              ) : (
                <span 
                  className="pending-blank"
                  style={{ 
                    minWidth: `${answerLength * 0.8}em`,
                    display: 'inline-block',
                    textAlign: 'center'
                  }}
                >
                  {'_'.repeat(answerLength)}
                </span>
              )}
            </span>
          );
          
          blankIndex++;
          return element;
        }
      }
      return <span key={index}>{part}</span>;    });
  };

  return (
    <div ref={componentRootRef} className={`fill-in-the-blanks-container ${allCompleted ? 'completed' : ''}`}>
      <div className="question-display">
        {renderQuestion()}
      </div>

      {showFeedback && (
        <div className="feedback-section">
          <div className="feedback-message">{feedbackMessage}</div>
        </div>
      )}      {allCompleted && (
        <div className="completion-section" style={{ display: 'none' }}>
          {/* Completion message removed for cleaner UI */}
        </div>
      )}
    </div>
  )
}

export default withStreamlitConnection(FillInTheBlanks);
