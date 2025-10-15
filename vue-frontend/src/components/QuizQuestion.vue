<template>
  <div class="quiz-question">
    <div class="question-header">
      <span class="question-number">Question {{ questionIndex + 1 }}</span>
      <span class="question-type">{{ formatQuestionType(question.type) }}</span>
    </div>

    <div class="question-text">
      <div v-html="renderMarkdown(question.question)" />
    </div>

    <!-- Multiple Choice -->
    <div
      v-if="isMultipleChoice"
      class="options-container"
    >
      <div
        v-for="(option, index) in question.options"
        :key="index"
        :class="['option', {
          selected: selectedAnswer === option,
          correct: isAnswered && option === question.answer,
          incorrect: isAnswered && selectedAnswer === option && option !== question.answer
        }]"
        @click="!isAnswered && selectAnswer(option)"
      >
        <span class="option-letter">{{ String.fromCharCode(65 + index) }}</span>
        <span class="option-text">
          <div v-html="renderMarkdown(option)" />
        </span>
        <span
          v-if="isAnswered && option === question.answer"
          class="option-icon"
        >✓</span>
        <span
          v-if="isAnswered && selectedAnswer === option && option !== question.answer"
          class="option-icon"
        >✗</span>
      </div>
    </div>

    <!-- True/False -->
    <div
      v-else-if="isTrueFalse"
      class="options-container"
    >
      <div
        :class="['option', {
          selected: selectedAnswer === true,
          correct: isAnswered && question.answer === true,
          incorrect: isAnswered && selectedAnswer === true && question.answer !== true
        }]"
        @click="!isAnswered && selectAnswer(true)"
      >
        <span class="option-text">
          <div v-html="renderMarkdown('✓ True')" />
        </span>
        <span
          v-if="isAnswered && question.answer === true"
          class="option-icon"
        >✓</span>
      </div>
      <div
        :class="['option', {
          selected: selectedAnswer === false,
          correct: isAnswered && question.answer === false,
          incorrect: isAnswered && selectedAnswer === false && question.answer !== false
        }]"
        @click="!isAnswered && selectAnswer(false)"
      >
        <span class="option-text">
          <div v-html="renderMarkdown('✗ False')" />
        </span>
        <span
          v-if="isAnswered && question.answer === false"
          class="option-icon"
        >✓</span>
      </div>
    </div>

    <!-- Fill in the Blank -->
    <div
      v-else-if="isFillInBlank"
      class="answer-input-container"
    >
      <input
        v-model="userAnswer"
        type="text"
        class="form-input"
        :disabled="isAnswered"
        placeholder="Type your answer here..."
        @keyup.enter="submitFillInBlank"
      >
      <button
        v-if="!isAnswered"
        :disabled="!userAnswer.trim()"
        class="btn btn-primary"
        @click="submitFillInBlank"
      >
        Submit
      </button>
    </div>

    <!-- Short Answer -->
    <div
      v-else-if="isShortAnswer"
      class="answer-input-container"
    >
      <textarea
        v-model="userAnswer"
        class="form-textarea"
        :disabled="isAnswered || validating"
        placeholder="Type your detailed answer here..."
        rows="4"
        @keydown.shift.enter.prevent="submitShortAnswer"
      />
      <div
        v-if="!isAnswered && isShortAnswer"
        class="shortcut-label desktop-only"
      >
        {{ osShortcutLabel }}
      </div>
      <button
        v-if="!isAnswered"
        :disabled="!userAnswer.trim() || validating"
        class="btn btn-primary"
        @click="submitShortAnswer"
      >
        {{ validating ? 'Validating...' : 'Submit' }}
      </button>
    </div>

    <!-- Matching -->
    <div
      v-else-if="isMatching"
      class="matching-container"
    >
      <div class="matching-instructions">
        Match each item on the left with the correct answer on the right
      </div>
      <div class="matching-pairs">
        <div
          v-for="(key, index) in matchingKeys"
          :key="index"
          class="matching-row"
        >
          <div class="matching-key">
            <div v-html="renderMarkdown(key)" />
          </div>
          <select
            v-model="matchingAnswers[key]"
            :disabled="isAnswered"
            class="form-select matching-select"
          >
            <option value="">
              Select...
            </option>
            <option
              v-for="(value, vIndex) in matchingValues"
              :key="vIndex"
              :value="value"
            >
              {{ renderPlain(value) }}
            </option>
          </select>
          <span
            v-if="isAnswered"
            class="matching-result"
          >
            {{ matchingAnswers[key] === question.answer[key] ? '✓' : '✗' }}
          </span>
        </div>
      </div>
      <button
        v-if="!isAnswered"
        :disabled="!isMatchingComplete"
        class="btn btn-primary"
        @click="submitMatching"
      >
        Submit
      </button>
    </div>

    <!-- Feedback -->
    <div
      v-if="isAnswered"
      ref="feedbackSection"
      :class="['feedback', isCorrect ? 'feedback-correct' : 'feedback-incorrect']"
    >
      <div class="feedback-header">
        {{ isCorrect ? '✅ Correct!' : '❌ Incorrect' }}
      </div>
      <div
        v-if="explanation"
        class="feedback-text"
      >
        <div v-html="renderMarkdown(explanation)" />
      </div>
      <div
        v-if="!isCorrect && expectedAnswer"
        class="correct-answer"
      >
        <strong>Correct answer:</strong> <span v-html="renderMarkdown(formatAnswer(expectedAnswer))" />
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch, onMounted, nextTick } from 'vue'
import MarkdownIt from 'markdown-it'
import DOMPurify from 'dompurify'
import api from '../services/api'

export default {
  name: 'QuizQuestion',
  props: {
    question: {
      type: Object,
      required: true
    },
    questionIndex: {
      type: Number,
      required: true
    },
    sectionIndex: {
      type: Number,
      required: true
    },
    subsectionIndex: {
      type: Number,
      default: null
    },
    savedAnswerData: {
      type: Object,
      default: null
    }
  },
  emits: ['answer-submitted'],
  setup(props, { emit }) {
      // Feedback ref for auto-scroll
      const feedbackSection = ref(null);
      
      // OS detection for shortcut label
      const osType = ref('win');
      const osShortcutLabel = computed(() => {
        if (osType.value === 'mac') return '⌘ + Enter to submit';
        if (osType.value === 'linux') return 'Shift + Enter to submit';
        return 'Shift + Enter to submit';
      });
      
      // Auto-scroll to feedback when it appears
      const scrollToFeedback = () => {
        nextTick(() => {
          if (feedbackSection.value) {
            feedbackSection.value.scrollIntoView({ 
              behavior: 'smooth', 
              block: 'nearest' 
            });
          }
        });
      };

      onMounted(() => {
        const platform = window.navigator.platform.toLowerCase();
        if (platform.includes('mac')) osType.value = 'mac';
        else if (platform.includes('linux')) osType.value = 'linux';
        else osType.value = 'win';
        // MathJax typeset on mount
        typesetMathJax();
      });
    // Initialize from saved data if available
    const savedData = props.savedAnswerData

    const selectedAnswer = ref(savedData?.answer || null)
    const userAnswer = ref(savedData?.userAnswer || '')
    const matchingAnswers = ref(savedData?.answer && typeof savedData.answer === 'object' ? { ...savedData.answer } : {})
    const isAnswered = ref(!!savedData)
    const isCorrect = ref(savedData?.isCorrect || false)
    const explanation = ref('')
    const expectedAnswer = ref(null)
    const validating = ref(false)

    const questionType = computed(() => {
      const type = props.question.type?.toLowerCase().replace(/[_\s]/g, '')
      return type
    })

    const isMultipleChoice = computed(() => {
      return questionType.value === 'multiplechoice'
    })

    const isTrueFalse = computed(() => {
      return questionType.value === 'truefalse' || questionType.value === 'trueorfalse'
    })

    const isFillInBlank = computed(() => {
      return questionType.value === 'fillintheblank'
    })

    const isShortAnswer = computed(() => {
      return questionType.value === 'shortanswer'
    })

    const isMatching = computed(() => {
      return questionType.value === 'match'
    })

    const matchingKeys = computed(() => {
      if (!isMatching.value || !props.question.answer) return []
      return Object.keys(props.question.answer)
    })

    const matchingValues = computed(() => {
      if (!isMatching.value || !props.question.answer) return []
      const values = Object.values(props.question.answer)
      // Shuffle values for display
      return [...values].sort(() => Math.random() - 0.5)
    })

    const isMatchingComplete = computed(() => {
      return matchingKeys.value.every(key => matchingAnswers.value[key])
    })

    const formatQuestionType = (type) => {
      const typeMap = {
        'multiple_choice': 'Multiple Choice',
        'multiplechoice': 'Multiple Choice',
        'true_false': 'True/False',
        'truefalse': 'True/False',
        'trueorfalse': 'True/False',
        'fill_in_the_blank': 'Fill in the Blank',
        'fillintheblank': 'Fill in the Blank',
        'short_answer': 'Short Answer',
        'shortanswer': 'Short Answer',
        'match': 'Matching'
      }
      return typeMap[type?.toLowerCase().replace(/[_\s]/g, '')] || type
    }

    const formatAnswer = (answer) => {
      if (typeof answer === 'boolean') {
        return answer ? 'True' : 'False'
      }
      if (typeof answer === 'object' && !Array.isArray(answer)) {
        return JSON.stringify(answer, null, 2)
      }

      // For fill-in-the-blank with multiple answers, format nicely
      const answerStr = String(answer)
      if (isFillInBlank.value && answerStr.includes(',')) {
        const answers = answerStr.split(',').map(a => a.trim())
        if (answers.length > 1) {
          return `Any of: ${answers.join(', ')}`
        }
      }

      return answerStr
    }

    const selectAnswer = (answer) => {
      selectedAnswer.value = answer
      checkAnswer(answer)
    }

    const submitFillInBlank = () => {
      if (!userAnswer.value.trim()) return

      // Handle multiple correct answers separated by commas
      const correctAnswers = String(props.question.answer)
        .split(',')
        .map(ans => ans.trim().toLowerCase())

      const userAnswerLower = userAnswer.value.trim().toLowerCase()
      const correct = correctAnswers.includes(userAnswerLower)

      checkAnswer(userAnswer.value, correct)
    }

    const submitShortAnswer = async () => {
      if (!userAnswer.value.trim()) return

      validating.value = true

      try {
        // Create timeout promise for 2 seconds
        const timeoutPromise = new Promise((_, reject) => 
          setTimeout(() => reject(new Error('Validation timeout')), 2000)
        )
        
        const validationPromise = api.post('/quiz/validate-answer', {
          question: props.question.question,
          user_answer: userAnswer.value,
          expected_answer: String(props.question.answer)
        })
        
        // Race between validation and timeout
        const response = await Promise.race([validationPromise, timeoutPromise])

        const correct = response.data.is_correct
        explanation.value = response.data.explanation
        checkAnswer(userAnswer.value, correct)
        scrollToFeedback()
      } catch (error) {
        console.error('Failed to validate answer:', error)
        // Fallback: simple comparison
        const correct = userAnswer.value.trim().toLowerCase().includes(
          String(props.question.answer).toLowerCase()
        )
        checkAnswer(userAnswer.value, correct)
        scrollToFeedback()
      } finally {
        validating.value = false
      }
    }

    const submitMatching = () => {
      if (!isMatchingComplete.value) return

      let allCorrect = true
      for (const key of matchingKeys.value) {
        if (matchingAnswers.value[key] !== props.question.answer[key]) {
          allCorrect = false
          break
        }
      }

      checkAnswer(matchingAnswers.value, allCorrect)
    }

    const checkAnswer = (answer, correctOverride = null) => {
      let correct = correctOverride

      if (correct === null) {
        // Determine correctness based on question type
        if (isMultipleChoice.value || isTrueFalse.value) {
          correct = answer === props.question.answer
        } else if (isFillInBlank.value) {
          // Handle multiple correct answers separated by commas
          const correctAnswers = String(props.question.answer)
            .split(',')
            .map(ans => ans.trim().toLowerCase())
          correct = correctAnswers.includes(String(answer).toLowerCase().trim())
        }
      }

      isCorrect.value = correct
      isAnswered.value = true
      expectedAnswer.value = props.question.answer

      // Auto-scroll to feedback
      scrollToFeedback()

      // Emit result to parent with answer data for saving
      emit('answer-submitted', {
        isCorrect: correct,
        sectionIndex: props.sectionIndex,
        subsectionIndex: props.subsectionIndex,
        questionIndex: props.questionIndex,
        answer: answer,
        userAnswer: userAnswer.value || answer
      })
    }

    // Reset state when question or section changes
    watch(() => [props.question, props.sectionIndex, props.subsectionIndex, props.questionIndex], () => {
      // Only reset if there's no saved data to restore
      if (!props.savedAnswerData) {
        selectedAnswer.value = null
        userAnswer.value = ''
        isAnswered.value = false
        isCorrect.value = false
        explanation.value = ''
        expectedAnswer.value = null
        validating.value = false

        // Initialize matching answers if needed
        if (isMatching.value && props.question.answer) {
          matchingAnswers.value = Object.keys(props.question.answer).reduce((acc, key) => {
            acc[key] = ''
            return acc
          }, {})
        } else {
          matchingAnswers.value = {}
        }
      }
    }, { immediate: true })

    // Markdown renderer (MathJax handles LaTeX automatically)
    const md = new MarkdownIt({ html: false, linkify: true, typographer: true });
    const renderMarkdown = (text) => {
      if (!text) return '';
      const rendered = md.render(String(text));
      return DOMPurify.sanitize(rendered, { USE_PROFILES: { html: true } });
    };

    // Render plain text from markdown for use inside native <option> elements
    const renderPlain = (text) => {
      if (!text) return '';
      // Render inline markdown then strip any HTML tags to produce safe option text
      const renderedInline = md.renderInline(String(text));
      // Strip all tags to plain text
      const stripped = DOMPurify.sanitize(renderedInline, { ALLOWED_TAGS: [] });
      return stripped;
    };

    // MathJax typesetting helper
    function typesetMathJax() {
      // Wait for DOM update
      setTimeout(() => {
        if (window.MathJax && window.MathJax.typesetPromise) {
          // Typeset question, feedback, correct answer, option text and matching keys
          // Note: HTML inside native <option> elements is not fully supported by browsers,
          // but we include matching-select in the selector so visible rendered nodes are typeset.
          const elements = document.querySelectorAll(
            '.question-text, .feedback-text, .correct-answer, .option-text, .matching-key, .matching-select'
          );
          try {
            window.MathJax.typesetPromise(Array.from(elements)).catch(() => {});
          } catch {
            // swallow errors to avoid breaking UI
          }
        }
      }, 0);
    }

    // Typeset on question change
    watch(() => [props.question, props.sectionIndex, props.subsectionIndex, props.questionIndex], () => {
      typesetMathJax();
    }, { immediate: true });

    // When MCQ options change, ensure typesetting runs after DOM updates
    watch(() => props.question.options, async () => {
      await nextTick();
      typesetMathJax();
    }, { immediate: true, deep: true });

    // Ensure typesetting runs when matching values change (selects are plain text but keep consistent)
    watch(() => matchingValues.value, async () => {
      await nextTick();
      typesetMathJax();
    });

    // Typeset on feedback/explanation change
    watch([explanation, expectedAnswer], () => {
      typesetMathJax();
    });

    return {
      feedbackSection,
      selectedAnswer,
      userAnswer,
      matchingAnswers,
      isAnswered,
      isCorrect,
      explanation,
      expectedAnswer,
      validating,
      isMultipleChoice,
      isTrueFalse,
      isFillInBlank,
      isShortAnswer,
    osShortcutLabel,
      isMatching,
      matchingKeys,
      matchingValues,
      isMatchingComplete,
      formatQuestionType,
      formatAnswer,
      selectAnswer,
      submitFillInBlank,
      submitShortAnswer,
      submitMatching,
      renderMarkdown,
      renderPlain,
    }
  }
}
</script>

<style scoped>
.quiz-question {
  background: var(--bg-tertiary);
  border: 1px solid var(--border-light);
  border-radius: 1rem;
  padding: 2rem;
}

.question-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.question-number {
  font-weight: 600;
  color: var(--accent-primary);
  font-size: 0.875rem;
}

.question-type {
  background: var(--bg-tertiary);
  color: var(--accent-secondary);
  padding: 0.25rem 0.75rem;
  border-radius: 0.5rem;
  font-size: 0.75rem;
  font-weight: 500;
}

.question-text {
  font-size: 1.125rem;
  color: var(--text-primary);
  margin-bottom: 1.5rem;
  line-height: 1.6;
}

.options-container {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.option {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem 1.5rem;
  background: var(--bg-tertiary);
  border: 2px solid var(--border-light);
  border-radius: 0.75rem;
  cursor: pointer;
  transition: all 0.2s;
}

.option:hover:not(.correct):not(.incorrect) {
  background: var(--card-bg);
  border-color: var(--border-color);
}

.option.selected {
  background: var(--card-bg);
  border-color: var(--accent-primary);
}

.option.correct {
  background: rgba(34, 197, 94, 0.1);
  border-color: #22c55e;
  cursor: default;
}

.option.incorrect {
  background: rgba(239, 68, 68, 0.1);
  border-color: #ef4444;
  cursor: default;
}

.option-letter {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 2rem;
  height: 2rem;
  background: var(--bg-tertiary);
  border-radius: 50%;
  font-weight: 600;
  color: var(--accent-primary);
  flex-shrink: 0;
}

.option.correct .option-letter {
  background: rgba(34, 197, 94, 0.2);
  color: #22c55e;
}

.option.incorrect .option-letter {
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
}

.option-text {
  flex: 1;
  color: var(--text-primary);
}

.option-icon {
  font-size: 1.25rem;
  font-weight: 700;
}

.option.correct .option-icon {
  color: #22c55e;
}

.option.incorrect .option-icon {
  color: #ef4444;
}

.answer-input-container {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-bottom: 1rem;
  position: relative;
}

.shortcut-label {
  position: absolute;
  right: 1.25rem;
  bottom: 0.5rem;
  font-size: 0.85rem;
  color: var(--text-secondary);
  background: rgba(0,0,0,0.04);
  padding: 2px 8px;
  border-radius: 6px;
  pointer-events: none;
  z-index: 2;
}

.answer-input-container .btn {
  align-self: flex-start;
}

.matching-container {
  margin-bottom: 1rem;
}

.matching-instructions {
  color: var(--text-secondary);
  margin-bottom: 1.5rem;
  font-size: 0.875rem;
  padding: 0.75rem 1rem;
  background: var(--bg-tertiary);
  border-left: 3px solid var(--accent-primary);
  border-radius: 0.5rem;
}

.matching-pairs {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.matching-row {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.5rem;
  background: var(--bg-primary);
  border-radius: 0.75rem;
  transition: all 0.2s;
}

.matching-row:hover {
  background: var(--bg-tertiary);
}

.matching-key {
  flex: 1;
  padding: 1rem 1.25rem;
  background: var(--card-bg);
  border: 2px solid var(--border-color);
  border-radius: 0.75rem;
  color: var(--text-primary);
  font-weight: 500;
  box-shadow: 0 2px 8px var(--shadow-color);
}

.matching-select {
  flex: 1;
  padding: 1rem 1.25rem;
  background: var(--input-bg);
  border: 2px solid var(--border-color);
  border-radius: 0.75rem;
  color: var(--text-primary);
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.2s;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24' fill='none' stroke='%2306b6d4' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 0.75rem center;
  background-size: 1.25rem;
  padding-right: 3rem;
}

.matching-select:hover:not(:disabled) {
  border-color: rgba(6, 182, 212, 0.4);
  background-color: rgba(30, 41, 59, 0.9);
}

.matching-select:focus {
  outline: none;
  border-color: #06b6d4;
  box-shadow: 0 0 0 3px rgba(6, 182, 212, 0.1);
}

.matching-select:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

.matching-select option {
  background: #1e293b;
  color: #e2e8f0;
  padding: 0.75rem;
}

.matching-result {
  font-size: 1.75rem;
  font-weight: 700;
  width: 2.5rem;
  text-align: center;
  animation: popIn 0.3s ease;
}

@keyframes popIn {
  0% {
    transform: scale(0);
  }

  50% {
    transform: scale(1.2);
  }

  100% {
    transform: scale(1);
  }
}

.feedback {
  margin-top: 1.5rem;
  padding: 1.5rem;
  border-radius: 0.75rem;
  animation: slideIn 0.3s ease;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.feedback-correct {
  background: rgba(34, 197, 94, 0.1);
  border: 1px solid rgba(34, 197, 94, 0.3);
}

.feedback-incorrect {
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.3);
}

.feedback-header {
  font-size: 1.125rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
}

.feedback-correct .feedback-header {
  color: #4ade80;
}

.feedback-incorrect .feedback-header {
  color: #f87171;
}

.feedback-text {
  color: var(--text-secondary);
  line-height: 1.6;
  margin-bottom: 0.5rem;
}

.correct-answer {
  color: var(--text-secondary);
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid var(--border-color);
}

.correct-answer strong {
  color: #06b6d4;
}

/* Hide keyboard hint on touch devices */
@media (pointer: coarse) {
  .desktop-only {
    display: none;
  }
}

/* Also hide on small screens */
@media (max-width: 768px) {
  .desktop-only {
    display: none;
  }
  
  .quiz-question {
    padding: 1.5rem;
  }

  .matching-row {
    flex-direction: column;
    align-items: stretch;
  }

  .matching-result {
    align-self: center;
  }
}

@media (max-width: 1024px) {
  .option {
    padding: 1rem 1rem;
    gap: 0.75rem;
  }

  .option-letter {
    width: 2.5rem;
    height: 2.5rem;
    font-size: 1rem;
  }

  .question-text {
    font-size: 1.05rem;
  }
}
</style>
