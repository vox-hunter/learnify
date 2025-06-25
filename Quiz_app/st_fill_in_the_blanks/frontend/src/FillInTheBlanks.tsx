import React, { useState, useEffect, useRef } from "react"
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
  console.log("FillInTheBlanks component props:", props);
  
  const { question_text_full, correctAnswer, default_value, disabled } = props.args
  
  const safeQuestionText = typeof question_text_full === 'string' ? question_text_full : String(question_text_full || "");
  
  // Handle both single answer and array of answers
  const answersArray = Array.isArray(correctAnswer) ? correctAnswer : [correctAnswer];
  const safeAnswers = answersArray.map(ans => typeof ans === 'string' ? ans : String(ans || ""));
  
  console.log("Safe values - question:", safeQuestionText, "answers:", safeAnswers);
  
  // Initialize blank states
  const [blanks, setBlanks] = useState<BlankState[]>([]);
  const [currentBlankIndex, setCurrentBlankIndex] = useState(0);
  const [allCompleted, setAllCompleted] = useState(false);
  const [showFeedback, setShowFeedback] = useState(false);
  const [feedbackMessage, setFeedbackMessage] = useState("");
  
  const componentRootRef = useRef<HTMLDivElement>(null);
  const inputRefs = useRef<(HTMLInputElement | null)[]>([]);

  // Initialize blanks from answers
  useEffect(() => {
    const initialBlanks = safeAnswers.map(answer => ({
      answer: answer.trim(),
      userInput: "",
      isCorrect: false,
      isAttempted: false,
      isRevealed: false
    }));
    setBlanks(initialBlanks);
    setCurrentBlankIndex(0);
    setAllCompleted(false);
    setShowFeedback(false);
    inputRefs.current = new Array(initialBlanks.length).fill(null);
  }, [safeAnswers.join(',')]);

  // Set component height
  useEffect(() => {
    if (componentRootRef.current) {
      const contentHeight = Math.max(componentRootRef.current.scrollHeight, 80);
      Streamlit.setFrameHeight(contentHeight + 20);
    }
  }, [safeQuestionText, safeAnswers, blanks, showFeedback]);
  // Check if current blank is correct
  const checkCurrentBlank = () => {
    if (currentBlankIndex >= blanks.length || allCompleted) return;

    const currentBlank = blanks[currentBlankIndex];
    const isCorrect = currentBlank.userInput.trim().toLowerCase() === currentBlank.answer.toLowerCase();

    setBlanks(prev => {
      const newBlanks = [...prev];
      newBlanks[currentBlankIndex] = {
        ...currentBlank,
        isCorrect,
        isAttempted: true,
        isRevealed: false
      };
      
      // Check if this was the last blank to complete
      const updatedBlanks = newBlanks;
      const hasUnatttempted = updatedBlanks.some(blank => !blank.isAttempted);
      
      // Schedule the next action after state update
      setTimeout(() => {
        if (!hasUnatttempted) {
          setAllCompleted(true);
          const allCorrect = updatedBlanks.every(blank => blank.isCorrect);
          const correctCount = updatedBlanks.filter(blank => blank.isCorrect).length;
          
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
          }        }
      }, isCorrect ? 1000 : 1600); // Faster for correct answers, slower for incorrect
      
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
  };
  // Give up on current blank
  const giveUpCurrentBlank = () => {
    if (currentBlankIndex >= blanks.length || allCompleted) return;

    const currentBlank = blanks[currentBlankIndex];
    setBlanks(prev => {
      const newBlanks = [...prev];
      newBlanks[currentBlankIndex] = {
        ...currentBlank,
        isCorrect: false,
        isAttempted: true,
        isRevealed: true,
        userInput: ""
      };
      
      // Check if this was the last blank to complete
      const updatedBlanks = newBlanks;
      const hasUnatttempted = updatedBlanks.some(blank => !blank.isAttempted);
      
      // Schedule the next action after state update
      setTimeout(() => {
        if (!hasUnatttempted) {
          setAllCompleted(true);
          const allCorrect = updatedBlanks.every(blank => blank.isCorrect);
          const correctCount = updatedBlanks.filter(blank => blank.isCorrect).length;
          
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
      }, 2100); // After feedback disappears
      
      return newBlanks;
    });

    setFeedbackMessage(`💡 The answer was: ${currentBlank.answer}`);
    setShowFeedback(true);
    setTimeout(() => {
      setShowFeedback(false);
    }, 2000);
  };  // Handle input change for current blank
  const handleInputChange = (value: string) => {
    if (allCompleted) return;

    setBlanks(prev => {
      const newBlanks = [...prev];
      if (newBlanks[currentBlankIndex]) {
        newBlanks[currentBlankIndex] = {
          ...newBlanks[currentBlankIndex],
          userInput: value
        };
      }
      return newBlanks;
    });

    // Auto-check answer as user types
    const currentBlank = blanks[currentBlankIndex];
    if (currentBlank && value.trim().toLowerCase() === currentBlank.answer.toLowerCase()) {
      // Answer is correct! Auto-submit with a small delay to show the correct input
      setTimeout(() => {
        checkCurrentBlank();
      }, 300);
    }
  };
  // Handle key press
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

    return parts.map((part, index) => {
      if (BLANK_PLACEHOLDER_REGEX.test(part)) {
        BLANK_PLACEHOLDER_REGEX.lastIndex = 0;
        
        if (blankIndex < blanks.length) {
          const blank = blanks[blankIndex];
          const isCurrentBlank = blankIndex === currentBlankIndex && !allCompleted;
          const answerLength = Math.max(blank.answer.length, 3);
          
          let displayValue = "";
          let blankClass = "blank-wrapper";
          
          if (blank.isAttempted) {
            if (blank.isCorrect) {
              displayValue = blank.userInput;
              blankClass += " correct";
            } else if (blank.isRevealed) {
              displayValue = blank.answer;
              blankClass += " revealed";
            } else {
              displayValue = blank.userInput;
              blankClass += " incorrect";
            }
          } else if (isCurrentBlank) {
            blankClass += " current";
          } else {
            blankClass += " pending";
          }

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
                  placeholder={`${answerLength} letters`}
                  maxLength={answerLength + 5}
                  autoFocus
                  disabled={showFeedback}
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
      return <span key={index}>{part}</span>;
    });
  };

  const currentBlank = blanks[currentBlankIndex];
  const progressText = `${blanks.filter(b => b.isAttempted).length}/${blanks.length}`;

  return (
    <div ref={componentRootRef} className={`fill-in-the-blanks-container ${allCompleted ? 'completed' : ''}`}>
      <div className="question-display">
        {renderQuestion()}
      </div>
        {!allCompleted && !showFeedback && currentBlank && (
        <div className="controls-section">
          <div className="progress-info">
            Blank {currentBlankIndex + 1} of {blanks.length} | Progress: {progressText}
            <br />
            <small>💡 Type your answer - correct answers auto-submit!</small>
          </div>
          <div className="button-group">
            <button 
              onClick={checkCurrentBlank}
              disabled={!currentBlank.userInput.trim()}
              className="check-btn"
            >
              Submit
            </button>
            <button 
              onClick={giveUpCurrentBlank}
              className="give-up-btn"
              title="Press Escape key or click here to skip this blank"
            >
              Give Up
            </button>
          </div>
        </div>
      )}

      {showFeedback && (
        <div className="feedback-section">
          <div className="feedback-message">{feedbackMessage}</div>
        </div>
      )}

      {allCompleted && (
        <div className="completion-section">
          <div className={`completion-message ${blanks.every(b => b.isCorrect) ? 'all-correct' : 'partial'}`}>
            {blanks.every(b => b.isCorrect) 
              ? '🎉 Perfect! All blanks correct!' 
              : `✅ ${blanks.filter(b => b.isCorrect).length} out of ${blanks.length} blanks correct.`
            }
          </div>
        </div>
      )}
    </div>
  )
}

export default withStreamlitConnection(FillInTheBlanks);
