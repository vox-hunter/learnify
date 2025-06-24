import React, { useState, useEffect, useRef } from "react"
import {
  Streamlit,
  withStreamlitConnection,
} from "streamlit-component-lib"
import "./FillInTheBlanks.css"

interface FillInTheBlanksProps {
  args: {
    question_text_full: string
    correctAnswer: string // This prop now holds the actual correct answer string
    default_value?: string
    disabled?: boolean
  }
}

const FillInTheBlanks: React.FC<FillInTheBlanksProps> = (props) => {
  // Debug logging
  console.log("FillInTheBlanks component props:", props);
  console.log("Args received:", props.args);
  
  const { question_text_full, correctAnswer, default_value, disabled } = props.args
  
  // Type checking and validation with debug output
  console.log("question_text_full type:", typeof question_text_full, "value:", question_text_full);
  console.log("correctAnswer type:", typeof correctAnswer, "value:", correctAnswer);
  
  // Ensure we have valid string values
  const safeQuestionText = typeof question_text_full === 'string' ? question_text_full : String(question_text_full || "");
  const safeCorrectAnswer = typeof correctAnswer === 'string' ? correctAnswer : String(correctAnswer || "");
  
  console.log("Safe values - question:", safeQuestionText, "answer:", safeCorrectAnswer);
  const [inputValue, setInputValue] = useState<string>(default_value || "")
  const [isCorrect, setIsCorrect] = useState<boolean>(false)
  const [isLocked, setIsLocked] = useState<boolean>(disabled || false)
  const [isWrong, setIsWrong] = useState<boolean>(false) // New state for wrong answers
  const inputRef = useRef<HTMLInputElement>(null) // For the input element itself
  const componentRootRef = useRef<HTMLDivElement>(null); // Ref for the root div of the component
  let hasRenderedFirstInput = false;// Effect to set the component's height in Streamlit with a minimum height to ensure visibility
  useEffect(() => {
    if (componentRootRef.current) {
      // Calculate height based on content with a minimum of 40px to prevent cutting off
      const contentHeight = Math.max(componentRootRef.current.scrollHeight, 40);
      // Add some extra padding to ensure visibility
      Streamlit.setFrameHeight(contentHeight + 10);
    }
  }, [safeQuestionText, safeCorrectAnswer, default_value, disabled, inputValue]); // Dependencies that affect height
  // Effect to check if answer is correct
  useEffect(() => {
    const trimmedInput = inputValue.trim().toLowerCase()
    const trimmedAnswer = safeCorrectAnswer.trim().toLowerCase()
    const correct = trimmedInput === trimmedAnswer && trimmedInput.length > 0
    
    console.log("Answer check:", {
      input: trimmedInput,
      expected: trimmedAnswer,
      isCorrect: correct
    })
    
    setIsCorrect(correct)
    
    if (correct && !isLocked) {
      console.log("Answer is correct! Locking input...")
      setIsLocked(true)
      setIsWrong(false) // Clear wrong state if correct
      // Send success signal to Streamlit
      Streamlit.setComponentValue({
        value: inputValue,
        isCorrect: true,
        isWrong: false,
        action: 'correct_answer'
      })
    }
  }, [inputValue, safeCorrectAnswer, isLocked])  // Update locked state when disabled prop changes
  useEffect(() => {
    setIsLocked(disabled || false)
    if (disabled) {
      setIsWrong(false) // Clear wrong state when disabled externally
    }
  }, [disabled])

  // Update internal state if default_value prop changes (e.g., from Streamlit state)
  useEffect(() => {
    if (default_value !== undefined && default_value !== inputValue) {
      setInputValue(default_value)
    }    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [default_value])
    const handleInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (isLocked) return // Don't allow changes if locked
    
    const newValue = event.target.value
    console.log("Input changed:", newValue)
    setInputValue(newValue)
    
    // Clear wrong state when user starts typing again
    if (isWrong) {
      setIsWrong(false)
    }
    
    // Send value to Streamlit on every keystroke for real-time checking
    Streamlit.setComponentValue({
      value: newValue,
      isCorrect: false,
      isWrong: false,
      action: 'typing'
    })
  }

  const handleBlur = () => {
    if (!isLocked) {
      Streamlit.setComponentValue({
        value: inputValue,
        isCorrect: isCorrect,
        isWrong: isWrong,
        action: 'blur'
      })
    }
  }

  // Handle key presses, particularly the Enter key for "give up" functionality
  const handleKeyDown = (event: React.KeyboardEvent<HTMLInputElement>) => {
    if (event.key === 'Enter') {
      console.log("Enter pressed - giving up or confirming")
      if (!isCorrect) {
        // Mark as wrong and lock the input
        console.log("Answer is wrong! Marking as wrong and locking...")
        setIsWrong(true)
        setIsLocked(true)
        Streamlit.setComponentValue({
          value: inputValue,
          isCorrect: false,
          isWrong: true,
          action: 'give_up'
        })
      }
      // Prevent default behavior (like form submission)
      event.preventDefault()
    }
  }
  // Regex to find sequences of 3 or more underscores
  const BLANK_PLACEHOLDER_REGEX = /(_{3,})/g; // Keep the 'g' flag to find all occurrences
  
  // Safely split the question text
  const parts = safeQuestionText.split(BLANK_PLACEHOLDER_REGEX);
  console.log("Split parts:", parts);

  // The input field's maxLength will be based on the correctAnswer's length.
  // This is a simplification assuming one blank. For multiple, this would need adjustment.
  const answerLength = safeCorrectAnswer ? safeCorrectAnswer.length : 10; // Default length if not specified
  const inputMaxLength = Math.max(1, answerLength);
  // Calculate the width of the placeholder text (underscores)
  // Use the original underscores from the question, not generated ones
  let originalBlankText = "___"; // Default fallback
  const blankMatch = safeQuestionText.match(BLANK_PLACEHOLDER_REGEX);
  if (blankMatch && blankMatch[0]) {
    originalBlankText = blankMatch[0]; // Use the actual underscores from the question
  }
  const placeholderTextForSizing = originalBlankText;
  console.log("Original blank text:", originalBlankText);  console.log("Placeholder text for sizing:", placeholderTextForSizing);
  
  return (
    <div ref={componentRootRef} className={`fill-in-the-blanks-container ${isLocked ? 'disabled' : ''} ${isCorrect ? 'correct' : ''} ${isWrong ? 'wrong' : ''}`}>
      {parts.map((part, index) => {
        if (BLANK_PLACEHOLDER_REGEX.test(part)) {
          BLANK_PLACEHOLDER_REGEX.lastIndex = 0; // Reset regex state for next test/exec
          if (!hasRenderedFirstInput) {
            hasRenderedFirstInput = true;
            return (
              <span key={index} className={`blank-wrapper ${isCorrect ? 'correct' : ''} ${isLocked ? 'locked' : ''} ${isWrong ? 'wrong' : ''}`}>
                <span className="blank-placeholder-text">{placeholderTextForSizing}</span>
                <input
                  type="text"
                  ref={inputRef}
                  value={inputValue}
                  onChange={handleInputChange}
                  onBlur={handleBlur}
                  onKeyDown={handleKeyDown}
                  disabled={isLocked}
                  maxLength={inputMaxLength}
                  className={`blank-input-overlay ${isCorrect ? 'correct' : ''} ${isLocked ? 'locked' : ''} ${isWrong ? 'wrong' : ''}`}
                  placeholder=""
                  aria-label={`Fill in the blank for: ${parts[index-1] || ''}`}
                />
              </span>
            );
          } else {
            // For subsequent blanks, render them as static text (styled underscores)
            return <span key={index} className="blank-placeholder-text">{part}</span>;
          }
        } else {
          return <span key={index}>{part}</span>;
        }
      })}
    </div>
  )
}

export default withStreamlitConnection(FillInTheBlanks);
