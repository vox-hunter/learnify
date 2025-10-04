<template>
  <div
    ref="stepFlowContainer"
    class="step-flow"
    tabindex="0"
    @keydown.enter="handleEnterKey"
  >
    <!-- Progress Bar at Top -->
    <div class="progress-bar-top">
      <div class="progress-bar">
        <div
          class="progress-fill"
          :style="{ width: progressPercentage + '%' }"
        />
      </div>
      <div class="progress-text">
        <span>{{ answeredCount }} / {{ totalQuestions }} questions answered</span>
        <span class="score-text">Score: {{ score }}</span>
      </div>
    </div>

    <!-- End Course Early Button -->
    <div
      v-if="answeredCount > 0"
      class="end-early-container"
    >
      <button
        class="btn-end-early"
        @click="endCourseEarly"
      >
        🏁 End Course Early
      </button>
    </div>

    <div class="step-container">
      <!-- Current Step Content -->
      <transition
        :name="transitionName"
        mode="out-in"
      >
        <div
          :key="currentStepIndex"
          class="step-content"
        >
          <!-- Explanation Block -->
          <div
            v-if="currentStep.type === 'explanation'"
            class="explanation-step"
          >
            <div class="step-header">
              <h2 class="step-title">
                {{ currentStep.title }}
              </h2>
              <span class="step-indicator">{{ currentStepIndex + 1 }} / {{ totalSteps }}</span>
            </div>
            <div class="explanation-text">
              <p>{{ currentStep.content }}</p>
            </div>
          </div>

          <!-- Question Block -->
          <div
            v-else-if="currentStep.type === 'question'"
            class="question-step"
          >
            <div class="step-header">
              <h3 class="step-title">
                Question {{ currentQuestionNumber }}
              </h3>
              <span class="step-indicator">{{ currentStepIndex + 1 }} / {{ totalSteps }}</span>
            </div>
            <QuizQuestion
              :question="currentStep.question"
              :question-index="currentStep.questionIndex"
              :section-index="currentStep.sectionIndex"
              :subsection-index="currentStep.subsectionIndex"
              :saved-answer-data="currentStep.savedAnswerData"
              @answer-submitted="handleAnswerSubmit"
            />
          </div>
        </div>
      </transition>

      <!-- Navigation Controls -->
      <div
        v-if="canProceed"
        class="navigation-controls"
      >
        <button 
          class="btn-continue" 
          :class="{ 'pulse': showContinueHint }"
          @click="nextStep"
        >
          {{ isLastStep ? 'Finish' : 'Continue' }} →
        </button>
        <p class="hint-text">
          Press Enter to continue
        </p>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch, onMounted } from 'vue'
import QuizQuestion from './QuizQuestion.vue'

export default {
  name: 'StepFlow',
  components: {
    QuizQuestion
  },
  props: {
    steps: {
      type: Array,
      required: true,
      // Steps array format: [{ type: 'explanation'|'question', ... }, ...]
    },
    initialStepIndex: {
      type: Number,
      default: 0
    }
  },
  emits: ['answer-submitted', 'step-changed', 'flow-complete', 'end-early'],
  setup(props, { emit }) {
    const stepFlowContainer = ref(null)
    const currentStepIndex = ref(props.initialStepIndex)
    const answeredSteps = ref(new Set())
    const score = ref(0)
    const transitionName = ref('slide-fade')
    const showContinueHint = ref(false)

    // Computed properties
    const totalSteps = computed(() => props.steps.length)
    
    const currentStep = computed(() => {
      if (currentStepIndex.value >= 0 && currentStepIndex.value < props.steps.length) {
        return props.steps[currentStepIndex.value]
      }
      return null
    })

    const isLastStep = computed(() => currentStepIndex.value === totalSteps.value - 1)

    const canProceed = computed(() => {
      if (!currentStep.value) return false
      
      // For explanation blocks, can always proceed
      if (currentStep.value.type === 'explanation') {
        return true
      }
      
      // For question blocks, must be answered
      if (currentStep.value.type === 'question') {
        const stepKey = `${currentStepIndex.value}`
        return answeredSteps.value.has(stepKey)
      }
      
      return false
    })

    const totalQuestions = computed(() => {
      return props.steps.filter(step => step.type === 'question').length
    })

    const answeredCount = computed(() => {
      return Array.from(answeredSteps.value).filter(key => {
        const index = parseInt(key)
        return props.steps[index]?.type === 'question'
      }).length
    })

    const currentQuestionNumber = computed(() => {
      // Count how many question steps come before current step
      let count = 0
      for (let i = 0; i <= currentStepIndex.value; i++) {
        if (props.steps[i]?.type === 'question') {
          count++
        }
      }
      return count
    })

    const progressPercentage = computed(() => {
      if (totalSteps.value === 0) return 0
      return Math.round(((currentStepIndex.value + 1) / totalSteps.value) * 100)
    })

    // Methods
    const nextStep = () => {
      if (!canProceed.value) return

      if (isLastStep.value) {
        emit('flow-complete', {
          score: score.value,
          totalQuestions: totalQuestions.value,
          answeredCount: answeredCount.value
        })
      } else {
        currentStepIndex.value++
        emit('step-changed', currentStepIndex.value)
        // Use setTimeout to ensure DOM is updated before scrolling
        setTimeout(() => scrollToContent(), 100)
        showContinueHint.value = false
      }
    }

    const handleAnswerSubmit = (data) => {
      const stepKey = `${currentStepIndex.value}`
      
      if (!answeredSteps.value.has(stepKey)) {
        answeredSteps.value.add(stepKey)
        
        if (data.isCorrect) {
          score.value++
        }
        
        // Emit to parent for tracking
        emit('answer-submitted', {
          ...data,
          stepIndex: currentStepIndex.value
        })

        // Show continue hint after a short delay
        setTimeout(() => {
          showContinueHint.value = true
        }, 500)
      }
    }

    const handleEnterKey = (event) => {
      if (canProceed.value && !event.shiftKey && !event.ctrlKey) {
        event.preventDefault()
        nextStep()
      }
    }

    const scrollToContent = () => {
      // Scroll to the step content, not the very top
      const stepContent = document.querySelector('.step-content')
      if (stepContent) {
        stepContent.scrollIntoView({ behavior: 'smooth', block: 'center' })
      }
    }

    const endCourseEarly = () => {
      emit('end-early', {
        score: score.value,
        totalQuestions: totalQuestions.value,
        answeredCount: answeredCount.value,
        currentStepIndex: currentStepIndex.value
      })
    }

    // Watch for step changes to trigger animations
    watch(currentStepIndex, () => {
      // Could add sound effects or other feedback here
      showContinueHint.value = false
    })

    // Auto-show hint for explanation steps
    watch(currentStep, (newStep) => {
      if (newStep?.type === 'explanation') {
        setTimeout(() => {
          showContinueHint.value = true
        }, 1000)
      }
    }, { immediate: true })

    onMounted(() => {
      // Focus on the step flow for keyboard navigation
      if (stepFlowContainer.value) {
        stepFlowContainer.value.focus()
      }
    })

    return {
      stepFlowContainer,
      currentStepIndex,
      currentStep,
      totalSteps,
      canProceed,
      isLastStep,
      score,
      answeredCount,
      totalQuestions,
      currentQuestionNumber,
      progressPercentage,
      transitionName,
      showContinueHint,
      nextStep,
      handleAnswerSubmit,
      handleEnterKey,
      endCourseEarly
    }
  }
}
</script>

<style scoped>
.step-flow {
  min-height: calc(100vh - 200px);
  display: flex;
  flex-direction: column;
  padding: 0;
  outline: none;
}

.step-flow:focus {
  outline: 2px solid transparent;
}

/* Progress Bar at Top */
.progress-bar-top {
  position: sticky;
  top: 0;
  z-index: 100;
  background: var(--bg-primary);
  padding: 1rem 1.5rem;
  border-bottom: 1px solid var(--border-color);
  box-shadow: 0 2px 8px var(--shadow-color);
}

/* End Course Early Button */
.end-early-container {
  padding: 0.5rem 1.5rem;
  text-align: right;
}

.btn-end-early {
  background: rgba(248, 113, 113, 0.1);
  border: 1px solid rgba(248, 113, 113, 0.3);
  color: #f87171;
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-end-early:hover {
  background: rgba(248, 113, 113, 0.2);
  border-color: rgba(248, 113, 113, 0.5);
}

.step-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 100%;
  max-width: 800px;
  margin: 0 auto;
  padding: 2rem 1rem;
}

.step-content {
  min-height: 400px;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* Explanation Step Styles */
.explanation-step {
  background: var(--card-bg);
  border: 1px solid var(--border-color);
  border-radius: 1.5rem;
  padding: 3rem;
  box-shadow: 0 10px 30px var(--shadow-color);
  width: 100%;
  animation: fadeIn 0.5s ease;
}

.step-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 2px solid var(--border-color);
}

.step-title {
  font-size: 2rem;
  font-weight: 700;
  color: var(--accent-primary);
  margin: 0;
}

.step-indicator {
  font-size: 0.875rem;
  color: var(--text-secondary);
  background: var(--bg-tertiary);
  padding: 0.5rem 1rem;
  border-radius: 2rem;
  font-weight: 600;
}

.explanation-text {
  font-size: 1.25rem;
  line-height: 1.8;
  color: var(--text-primary);
}

.explanation-text p {
  margin: 0;
  text-align: left;
}

/* Question Step Styles */
.question-step {
  width: 100%;
}

.question-step .step-title {
  font-size: 1.5rem;
}

/* Navigation Controls */
.navigation-controls {
  margin-top: 3rem;
  text-align: center;
  animation: slideUp 0.5s ease;
}

.btn-continue {
  background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
  color: white;
  border: none;
  padding: 1.25rem 3rem;
  border-radius: 3rem;
  font-size: 1.25rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(119, 51, 255, 0.3);
  min-width: 200px;
}

.btn-continue:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 25px rgba(119, 51, 255, 0.4);
}

.btn-continue:active {
  transform: translateY(-1px);
}

.btn-continue.pulse {
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
    box-shadow: 0 4px 15px rgba(119, 51, 255, 0.3);
  }
  50% {
    transform: scale(1.05);
    box-shadow: 0 6px 25px rgba(119, 51, 255, 0.5);
  }
}

.hint-text {
  margin-top: 1rem;
  color: var(--text-secondary);
  font-size: 0.875rem;
  font-style: italic;
}

.progress-bar {
  width: 100%;
  height: 0.75rem;
  background: var(--bg-tertiary);
  border-radius: 1rem;
  overflow: hidden;
  margin-bottom: 1rem;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--accent-primary), var(--accent-secondary));
  border-radius: 1rem;
  transition: width 0.5s ease;
  position: relative;
}

.progress-fill::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(90deg,
      rgba(255, 255, 255, 0) 0%,
      rgba(255, 255, 255, 0.3) 50%,
      rgba(255, 255, 255, 0) 100%);
  animation: shimmer 2s infinite;
}

@keyframes shimmer {
  0% {
    transform: translateX(-100%);
  }
  100% {
    transform: translateX(100%);
  }
}

.progress-text {
  display: flex;
  justify-content: space-between;
  font-size: 0.875rem;
  color: var(--text-secondary);
}

.score-text {
  font-weight: 600;
  color: var(--accent-primary);
}

/* Transitions */
.slide-fade-enter-active {
  transition: all 0.4s ease;
}

.slide-fade-leave-active {
  transition: all 0.3s ease;
}

.slide-fade-enter-from {
  transform: translateY(30px);
  opacity: 0;
}

.slide-fade-leave-to {
  transform: translateY(-30px);
  opacity: 0;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Responsive Design */
@media (max-width: 768px) {
  .step-flow {
    padding: 1rem 0;
  }

  .explanation-step {
    padding: 2rem 1.5rem;
  }

  .step-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }

  .step-title {
    font-size: 1.5rem;
  }

  .explanation-text {
    font-size: 1.125rem;
  }

  .btn-continue {
    width: 100%;
    padding: 1rem 2rem;
    font-size: 1.125rem;
  }

  .step-content {
    min-height: 300px;
  }
}

/* Light Theme Adjustments */
:root[data-theme="light"] .btn-continue {
  box-shadow: 0 4px 15px rgba(16, 185, 129, 0.25);
}

:root[data-theme="light"] .btn-continue:hover {
  box-shadow: 0 6px 25px rgba(16, 185, 129, 0.35);
}

:root[data-theme="light"] .btn-continue.pulse {
  animation: pulseLightTheme 2s infinite;
}

@keyframes pulseLightTheme {
  0%, 100% {
    transform: scale(1);
    box-shadow: 0 4px 15px rgba(16, 185, 129, 0.25);
  }
  50% {
    transform: scale(1.05);
    box-shadow: 0 6px 25px rgba(16, 185, 129, 0.4);
  }
}
</style>
