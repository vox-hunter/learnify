<template>
  <div class="quiz-question">
    <div class="question-header">
      <span class="question-number">Question {{ questionIndex + 1 }}</span>
      <span class="question-type">{{ formatQuestionType(question.type) }}</span>
    </div>

    <div class="question-text">{{ question.question }}</div>

    <!-- Multiple Choice -->
    <div v-if="isMultipleChoice" class="options-container">
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
        <span class="option-text">{{ option }}</span>
        <span v-if="isAnswered && option === question.answer" class="option-icon">✓</span>
        <span v-if="isAnswered && selectedAnswer === option && option !== question.answer" class="option-icon">✗</span>
      </div>
    </div>

    <!-- True/False -->
    <div v-else-if="isTrueFalse" class="options-container">
      <div 
        :class="['option', { 
          selected: selectedAnswer === true,
          correct: isAnswered && question.answer === true,
          incorrect: isAnswered && selectedAnswer === true && question.answer !== true
        }]"
        @click="!isAnswered && selectAnswer(true)"
      >
        <span class="option-text">✓ True</span>
        <span v-if="isAnswered && question.answer === true" class="option-icon">✓</span>
      </div>
      <div 
        :class="['option', { 
          selected: selectedAnswer === false,
          correct: isAnswered && question.answer === false,
          incorrect: isAnswered && selectedAnswer === false && question.answer !== false
        }]"
        @click="!isAnswered && selectAnswer(false)"
      >
        <span class="option-text">✗ False</span>
        <span v-if="isAnswered && question.answer === false" class="option-icon">✓</span>
      </div>
    </div>

    <!-- Fill in the Blank -->
    <div v-else-if="isFillInBlank" class="answer-input-container">
      <input
        v-model="userAnswer"
        type="text"
        class="form-input"
        :disabled="isAnswered"
        placeholder="Type your answer here..."
        @keyup.enter="submitFillInBlank"
      />
      <button 
        v-if="!isAnswered" 
        @click="submitFillInBlank"
        :disabled="!userAnswer.trim()"
        class="btn btn-primary"
      >
        Submit
      </button>
    </div>

    <!-- Short Answer -->
    <div v-else-if="isShortAnswer" class="answer-input-container">
      <textarea
        v-model="userAnswer"
        class="form-textarea"
        :disabled="isAnswered || validating"
        placeholder="Type your detailed answer here..."
        rows="4"
      ></textarea>
      <button 
        v-if="!isAnswered" 
        @click="submitShortAnswer"
        :disabled="!userAnswer.trim() || validating"
        class="btn btn-primary"
      >
        {{ validating ? 'Validating...' : 'Submit' }}
      </button>
    </div>

    <!-- Matching -->
    <div v-else-if="isMatching" class="matching-container">
      <div class="matching-instructions">
        Match each item on the left with the correct answer on the right
      </div>
      <div class="matching-pairs">
        <div 
          v-for="(key, index) in matchingKeys" 
          :key="index"
          class="matching-row"
        >
          <div class="matching-key">{{ key }}</div>
          <select 
            v-model="matchingAnswers[key]"
            :disabled="isAnswered"
            class="form-select matching-select"
          >
            <option value="">Select...</option>
            <option 
              v-for="(value, vIndex) in matchingValues" 
              :key="vIndex"
              :value="value"
            >
              {{ value }}
            </option>
          </select>
          <span v-if="isAnswered" class="matching-result">
            {{ matchingAnswers[key] === question.answer[key] ? '✓' : '✗' }}
          </span>
        </div>
      </div>
      <button 
        v-if="!isAnswered" 
        @click="submitMatching"
        :disabled="!isMatchingComplete"
        class="btn btn-primary"
      >
        Submit
      </button>
    </div>

    <!-- Feedback -->
    <div v-if="isAnswered" :class="['feedback', isCorrect ? 'feedback-correct' : 'feedback-incorrect']">
      <div class="feedback-header">
        {{ isCorrect ? '✅ Correct!' : '❌ Incorrect' }}
      </div>
      <div v-if="explanation" class="feedback-text">
        {{ explanation }}
      </div>
      <div v-if="!isCorrect && expectedAnswer" class="correct-answer">
        <strong>Correct answer:</strong> {{ formatAnswer(expectedAnswer) }}
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch } from 'vue'
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
    }
  },
  emits: ['answer-submitted'],
  setup(props, { emit }) {
    const selectedAnswer = ref(null)
    const userAnswer = ref('')
    const matchingAnswers = ref({})
    const isAnswered = ref(false)
    const isCorrect = ref(false)
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
        const response = await api.post('/quiz/validate-answer', {
          question: props.question.question,
          user_answer: userAnswer.value,
          expected_answer: String(props.question.answer)
        })
        
        const correct = response.data.is_correct
        explanation.value = response.data.explanation
        checkAnswer(userAnswer.value, correct)
      } catch (error) {
        console.error('Failed to validate answer:', error)
        // Fallback: simple comparison
        const correct = userAnswer.value.trim().toLowerCase().includes(
          String(props.question.answer).toLowerCase()
        )
        checkAnswer(userAnswer.value, correct)
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
      
      // Emit result to parent
      emit('answer-submitted', {
        isCorrect: correct,
        sectionIndex: props.sectionIndex,
        subsectionIndex: props.subsectionIndex,
        questionIndex: props.questionIndex
      })
    }

    // Reset state when question or section changes
    watch(() => [props.question, props.sectionIndex, props.subsectionIndex, props.questionIndex], () => {
      // Reset all state
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
    }, { immediate: true })

    return {
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
      isMatching,
      matchingKeys,
      matchingValues,
      isMatchingComplete,
      formatQuestionType,
      formatAnswer,
      selectAnswer,
      submitFillInBlank,
      submitShortAnswer,
      submitMatching
    }
  }
}
</script>

<style scoped>
.quiz-question {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
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
  color: #06b6d4;
  font-size: 0.875rem;
}

.question-type {
  background: rgba(6, 182, 212, 0.1);
  color: #0891b2;
  padding: 0.25rem 0.75rem;
  border-radius: 0.5rem;
  font-size: 0.75rem;
  font-weight: 500;
}

.question-text {
  font-size: 1.125rem;
  color: #e2e8f0;
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
  background: rgba(255, 255, 255, 0.05);
  border: 2px solid rgba(255, 255, 255, 0.1);
  border-radius: 0.75rem;
  cursor: pointer;
  transition: all 0.2s;
}

.option:hover:not(.correct):not(.incorrect) {
  background: rgba(6, 182, 212, 0.1);
  border-color: rgba(6, 182, 212, 0.3);
}

.option.selected {
  background: rgba(6, 182, 212, 0.1);
  border-color: #06b6d4;
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
  background: rgba(6, 182, 212, 0.2);
  border-radius: 50%;
  font-weight: 600;
  color: #06b6d4;
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
  color: #e2e8f0;
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
}

.answer-input-container .btn {
  align-self: flex-start;
}

.matching-container {
  margin-bottom: 1rem;
}

.matching-instructions {
  color: #cbd5e0;
  margin-bottom: 1.5rem;
  font-size: 0.875rem;
  padding: 0.75rem 1rem;
  background: rgba(102, 126, 234, 0.1);
  border-left: 3px solid #667eea;
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
  background: rgba(255, 255, 255, 0.02);
  border-radius: 0.75rem;
  transition: all 0.2s;
}

.matching-row:hover {
  background: rgba(255, 255, 255, 0.05);
}

.matching-key {
  flex: 1;
  padding: 1rem 1.25rem;
  background: linear-gradient(135deg, rgba(6, 182, 212, 0.15), rgba(6, 182, 212, 0.05));
  border: 2px solid rgba(6, 182, 212, 0.2);
  border-radius: 0.75rem;
  color: #e2e8f0;
  font-weight: 500;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.matching-select {
  flex: 1;
  padding: 1rem 1.25rem;
  background: rgba(30, 41, 59, 0.8);
  border: 2px solid rgba(148, 163, 184, 0.2);
  border-radius: 0.75rem;
  color: #e2e8f0;
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
  color: #cbd5e0;
  line-height: 1.6;
  margin-bottom: 0.5rem;
}

.correct-answer {
  color: #cbd5e0;
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.correct-answer strong {
  color: #06b6d4;
}

@media (max-width: 768px) {
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
</style>
