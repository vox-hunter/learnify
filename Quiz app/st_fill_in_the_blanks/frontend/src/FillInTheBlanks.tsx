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
  const { question_text_full, correctAnswer, default_value, disabled } = props.args
  const [inputValue, setInputValue] = useState<string>(default_value || "")
  const inputRef = useRef<HTMLInputElement>(null) // For the input element itself
  const componentRootRef = useRef<HTMLDivElement>(null); // Ref for the root div of the component
  let hasRenderedFirstInput = false;
  // Effect to set the component's height in Streamlit with a minimum height to ensure visibility
  useEffect(() => {
    if (componentRootRef.current) {
      // Calculate height based on content with a minimum of 40px to prevent cutting off
      const contentHeight = Math.max(componentRootRef.current.scrollHeight, 40);
      // Add some extra padding to ensure visibility
      Streamlit.setFrameHeight(contentHeight + 10);
    }
  }, [question_text_full, correctAnswer, default_value, disabled, inputValue]); // Dependencies that affect height

  // Update internal state if default_value prop changes (e.g., from Streamlit state)
  useEffect(() => {
    if (default_value !== undefined && default_value !== inputValue) {
      setInputValue(default_value)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [default_value])
  const handleInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = event.target.value
    setInputValue(newValue)
  }

  const handleBlur = () => {
    Streamlit.setComponentValue(inputValue)
  }

  // Handle key presses, particularly the Enter key
  const handleKeyDown = (event: React.KeyboardEvent<HTMLInputElement>) => {
    if (event.key === 'Enter') {
      // Prevent default behavior (like form submission)
      event.preventDefault();
      // Explicitly blur the input field, which will trigger handleBlur to submit the value
      if (inputRef.current) {
        inputRef.current.blur();
      }
    }
  }

  // Regex to find sequences of 3 or more underscores
  const BLANK_PLACEHOLDER_REGEX = /(_{3,})/g; // Keep the 'g' flag to find all occurrences
  const parts = question_text_full.split(BLANK_PLACEHOLDER_REGEX);

  // The input field's maxLength will be based on the correctAnswer's length.
  // This is a simplification assuming one blank. For multiple, this would need adjustment.
  const answerLength = correctAnswer ? correctAnswer.length : 10; // Default length if not specified
  const inputMaxLength = Math.max(1, answerLength);

  // Calculate the width of the placeholder text (underscores)
  // This is a rough estimation. For pixel-perfect, a hidden element measurement might be needed.
  const placeholderTextForSizing = correctAnswer.replace(/./g, '_');

  return (
    <div ref={componentRootRef} className={`fill-in-the-blanks-container ${disabled ? 'disabled' : ''}`}>
      {parts.map((part, index) => {
        if (BLANK_PLACEHOLDER_REGEX.test(part)) {
          BLANK_PLACEHOLDER_REGEX.lastIndex = 0; // Reset regex state for next test/exec
          if (!hasRenderedFirstInput) {
            hasRenderedFirstInput = true;
            return (
              <span key={index} className="blank-wrapper">
                <span className="blank-placeholder-text">{placeholderTextForSizing}</span>                <input
                  type="text"
                  ref={inputRef}
                  value={inputValue}
                  onChange={handleInputChange}
                  onBlur={handleBlur}
                  onKeyDown={handleKeyDown}
                  disabled={disabled}
                  maxLength={inputMaxLength}
                  className="blank-input-overlay"
                  placeholder={disabled ? "" : ""}
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
