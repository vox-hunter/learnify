<template>
  <div class="course-view">
    <div class="container">
      <!-- Loading State -->
      <div
        v-if="loading"
        class="loading-state"
      >
        <div class="spinner" />
        <p>Loading course...</p>
      </div>

      <!-- Error State -->
      <div
        v-else-if="error"
        class="alert alert-error"
      >
        {{ error }}
        <button
          class="btn btn-secondary mt-2"
          @click="$router.push('/courses')"
        >
          Back to Courses
        </button>
      </div>

      <!-- Course Content -->
      <div
        v-else-if="course"
        class="course-content"
      >
        <!-- Course Overview Screen -->
        <div
          v-if="showOverview && useStepFlow && !reviewMode"
          class="overview-screen"
        >
          <div class="overview-card card">
            <div class="overview-icon">
              📚
            </div>
            <h1 class="overview-title">
              {{ course.course_title }}
            </h1>
            
            <div class="overview-stats">
              <div class="stat-box">
                <div class="stat-value">
                  {{ course.sections?.length || 0 }}
                </div>
                <div class="stat-label">
                  Sections
                </div>
              </div>
              <div class="stat-box">
                <div class="stat-value">
                  {{ totalQuestions }}
                </div>
                <div class="stat-label">
                  Questions
                </div>
              </div>
              <div
                v-if="hasProgress"
                class="stat-box"
              >
                <div class="stat-value">
                  {{ Math.round((answeredQuestions.size / totalQuestions) * 100) }}%
                </div>
                <div class="stat-label">
                  Completed
                </div>
              </div>
            </div>

            <!-- Previous Score Display -->
            <div
              v-if="hasProgress"
              class="previous-progress"
            >
              <div class="progress-badge">
                <span class="badge-icon">⏱️</span>
                <div class="badge-content">
                  <h3>Resume Your Progress</h3>
                  <p>You've already answered {{ answeredQuestions.size }} out of {{ totalQuestions }} questions</p>
                  <p class="score-display">
                    Score: <strong>{{ score }} / {{ totalQuestions }}</strong>
                  </p>
                </div>
              </div>
            </div>

            <div class="overview-actions">
              <button
                v-if="hasProgress"
                class="btn btn-secondary"
                @click="startCourseFromBeginning"
              >
                🔄 Start from Beginning
              </button>
              <button
                class="btn btn-primary"
                @click="startCourse"
              >
                {{ hasProgress ? '▶️ Continue' : '🚀 Start Course' }}
              </button>
            </div>
          </div>
        </div>

        <!-- Course Conclusion (shows when course is complete) -->
        <div
          v-else-if="showConclusion"
          class="conclusion-wrapper"
        >
          <div class="conclusion-section card">
            <div class="conclusion-icon">
              🎉
            </div>
            <h2 class="conclusion-title">
              Congratulations!
            </h2>
            <p class="conclusion-subtitle">
              You've completed the course
            </p>

            <div class="conclusion-stats">
              <div class="stat-card">
                <div class="stat-value">
                  {{ score }}
                </div>
                <div class="stat-label">
                  Correct Answers
                </div>
              </div>
              <div class="stat-card">
                <div class="stat-value">
                  {{ totalQuestions }}
                </div>
                <div class="stat-label">
                  Total Questions
                </div>
              </div>
              <div class="stat-card">
                <div class="stat-value">
                  {{ accuracyPercentage }}%
                </div>
                <div class="stat-label">
                  Accuracy
                </div>
              </div>
              <!-- Show earned badges in conclusion -->
              <div
                v-if="earnedBadges.length"
                class="stat-card badge-summary"
              >
                <div class="stat-label">
                  Achievements
                </div>
                <div class="badge-grid">
                  <span
                    v-for="badge in earnedBadges"
                    :key="badge.id"
                    class="badge-grid-item"
                  >
                    <img
                      :src="badge.image"
                      :alt="badge.label"
                      class="badge-img-large"
                    >
                  </span>
                </div>
              </div>
            </div>

            <div class="conclusion-summary">
              <h3>Course Summary</h3>
              <p><strong>{{ course.course_title }}</strong></p>
              <p class="summary-text">
                You've successfully completed all {{ course.sections.length }} sections
                and answered {{ totalQuestions }} questions with
                <span :class="accuracyClass">{{ accuracyPercentage }}% accuracy</span>.
              </p>
              <p
                v-if="accuracyPercentage >= 80"
                class="summary-message success"
              >
                🌟 Excellent work! You have a strong understanding of the material.
              </p>
              <p
                v-else-if="accuracyPercentage >= 60"
                class="summary-message good"
              >
                👍 Good job! You have a solid grasp of most concepts.
              </p>
              <p
                v-else
                class="summary-message needs-review"
              >
                📚 Consider reviewing the material to strengthen your understanding.
              </p>
            </div>

            <div class="conclusion-actions">
              <button
                class="btn btn-secondary"
                @click="reviewCourse"
              >
                🔄 Review Course
              </button>
              <button
                class="btn btn-primary"
                @click="goToCourses"
              >
                📚 My Courses
              </button>
            </div>
          </div>
        </div>

        <!-- Step Flow Mode -->
        <div v-else-if="useStepFlow && !reviewMode">
          <div
            ref="stepFlowContainer"
            class="step-flow"
            tabindex="0"
            @keydown.enter="handleStepEnterKey"
          >
            <!-- Progress Bar at Top -->
            <div class="progress-bar-top">
              <div class="progress-bar">
                <div
                  class="progress-fill"
                  :style="{ width: stepFlowProgressPercentage + '%' }"
                />
              </div>
              <div class="progress-text">
                <span>{{ answeredQuestions.size }} / {{ totalQuestions }} questions answered</span>
                <span class="score-text">Score: {{ score }}</span>
              </div>
            </div>

            <!-- Admin Controls in Step Flow -->
            <div
              v-if="authStore.user?.isAdmin"
              class="admin-controls-stepflow"
            >
              <h3 class="admin-title">
                🛠️ Admin Debug Controls
              </h3>
              <div class="admin-buttons">
                <button
                  class="btn btn-admin"
                  @click="completeAllQuestions"
                >
                  ✅ Complete All Questions
                </button>
                <button
                  class="btn btn-admin-danger"
                  @click="resetProgress"
                >
                  🔄 Reset All Progress
                </button>
              </div>
              <div
                v-if="adminMessage"
                :class="['admin-message', adminMessageType]"
              >
                {{ adminMessage }}
              </div>
            </div>

            <!-- End Course Early Button (hidden in review mode) -->
            <div
              v-if="answeredQuestions.size > 0 && !reviewMode"
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
                name="slide-fade"
                mode="out-in"
              >
                <div
                  :key="currentStepIndex"
                  class="step-content"
                >
                  <!-- Explanation Block -->
                  <div
                    v-if="currentStep?.type === 'explanation'"
                    class="explanation-step"
                  >
                    <div class="step-header">
                      <h2 class="step-title">
                        {{ currentStep.title }}
                      </h2>
                      <span class="step-indicator">{{ currentStepIndex + 1 }} / {{ courseSteps.length }}</span>
                    </div>
                    <div class="explanation-text">
                      <p>{{ currentStep.content }}</p>
                    </div>
                  </div>

                  <!-- Question Block -->
                  <div
                    v-else-if="currentStep?.type === 'question'"
                    class="question-step"
                  >
                    <div class="step-header">
                      <h3 class="step-title">
                        Question {{ currentQuestionNumber }}
                      </h3>
                      <span class="step-indicator">{{ currentStepIndex + 1 }} / {{ courseSteps.length }}</span>
                    </div>
                    <QuizQuestion
                      :question="currentStep.question"
                      :question-index="currentStep.questionIndex"
                      :section-index="currentStep.sectionIndex"
                      :subsection-index="currentStep.subsectionIndex"
                      :saved-answer-data="currentStep.savedAnswerData"
                      @answer-submitted="handleStepFlowAnswerSubmit"
                    />
                  </div>
                </div>
              </transition>

              <!-- Navigation Controls -->
              <div
                v-if="canProceedToNextStep"
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
        </div>

        <!-- Review Mode and Legacy View -->
        <div v-else>
          <!-- Course Header -->
          <div class="course-header card">
            <h1 class="course-title">
              {{ course.course_title }}
            </h1>
            <div class="course-meta">
              <span class="meta-item">
                📚 {{ course.sections?.length || 0 }} Sections
              </span>
              <span class="meta-item">
                ❓ {{ totalQuestions }} Questions
              </span>
              <span class="meta-item">
                ✅ Score: {{ score }} / {{ totalQuestions }}
              </span>
            </div>

            <!-- Progress Bar -->
            <div class="progress-container">
              <div class="progress-header">
                <span class="progress-label">Course Progress</span>
                <span class="progress-percentage">{{ progressPercentage }}%</span>
              </div>
              <div class="progress-bar">
                <div
                  class="progress-fill"
                  :style="{ width: progressPercentage + '%' }"
                />
              </div>
              <div class="progress-stats">
                <span class="stat-completed">{{ answeredQuestions.size }} completed</span>
                <span class="stat-remaining">{{ totalQuestions - answeredQuestions.size }} remaining</span>
              </div>
              <!-- Achievement Badges -->
              <div
                v-if="earnedBadges.length"
                class="badge-container"
              >
                <span class="badge-label">Achievements:</span>
                <span
                  v-for="badge in earnedBadges"
                  :key="badge.id"
                  class="badge-item"
                >
                  <img
                    :src="badge.image"
                    :alt="badge.label"
                    class="badge-img"
                  >
                  <span class="badge-text">{{ badge.label }}</span>
                </span>
              </div>
            </div>

            <!-- End Course Button (hidden in review mode) -->
            <div
              v-if="!showConclusion && answeredQuestions.size > 0 && !reviewMode"
              class="end-course-section"
            >
              <button
                class="btn btn-secondary"
                @click="endCourseEarly"
              >
                🏁 End Course Early
              </button>
              <p class="end-course-hint">
                Save your progress and view results
              </p>
            </div>
          </div>

          <!-- Admin Controls (only visible to admin) -->
          <div
            v-if="authStore.user?.isAdmin"
            class="admin-controls card"
          >
            <h3 class="admin-title">
              🛠️ Admin Debug Controls
            </h3>
            <div class="admin-buttons">
              <button
                class="btn btn-admin"
                @click="completeAllQuestions"
              >
                ✅ Complete All Questions
              </button>
              <button
                class="btn btn-admin-danger"
                @click="resetProgress"
              >
                🔄 Reset All Progress
              </button>
            </div>
            <div
              v-if="adminMessage"
              :class="['admin-message', adminMessageType]"
            >
              {{ adminMessage }}
            </div>
          </div>

          <!-- Review Mode Banner -->
          <div
            v-if="reviewMode"
            class="review-mode-banner"
          >
            <div class="review-banner-content">
              <span class="review-icon">🔄</span>
              <div class="review-text">
                <h3>Review Mode - Quiz Only</h3>
                <p>Test your knowledge without content hints. Answer all questions to see your improvement!</p>
              </div>
              <button
                class="btn btn-secondary btn-sm"
                @click="exitReviewMode"
              >
                Exit Review
              </button>
            </div>
          </div>

          <!-- All Sections (progressively revealed question by question) -->
          <div
            v-for="(section, sectionIndex) in visibleSections"
            :id="`section-${sectionIndex}`"
            :key="`section-${sectionIndex}`"
            class="section-card card"
          >
            <div class="section-header">
              <h2 class="section-title">
                {{ section.section_title }}
              </h2>
              <div class="section-progress">
                Section {{ sectionIndex + 1 }} of {{ course.sections.length }}
                <span
                  v-if="reviewMode"
                  class="review-badge"
                >📝 Review</span>
                <span
                  v-if="isSectionComplete(sectionIndex)"
                  class="complete-badge"
                >✓ Complete</span>
              </div>
            </div>

            <!-- Explanation (hidden in review mode) -->
            <div
              v-if="!reviewMode"
              class="section-explanation"
            >
              <p>{{ section.explanation }}</p>
            </div>

            <!-- Quiz Questions (progressive reveal) -->
            <div
              v-if="section.quiz && section.quiz.length > 0"
              class="quiz-section"
            >
              <h3 class="quiz-title">
                Quiz Time! 🎯
              </h3>

              <div
                v-for="(question, qIndex) in getVisibleQuestions(sectionIndex, section.quiz, 'main')"
                :id="`question-${sectionIndex}-main-${qIndex}`"
                :key="`q-${sectionIndex}-${qIndex}-${quizKey}`"
                class="question-card"
              >
                <QuizQuestion
                  :key="`quiz-${sectionIndex}-main-${qIndex}-${quizKey}`"
                  :question="question"
                  :question-index="qIndex"
                  :section-index="sectionIndex"
                  :saved-answer-data="getSavedAnswerData(sectionIndex, null, qIndex)"
                  @answer-submitted="handleAnswerSubmit"
                />
              </div>
            </div>

            <!-- Subsections (progressive reveal) -->
            <div
              v-if="section.subsections && section.subsections.length > 0"
              class="subsections"
            >
              <div
                v-for="(subsection, subIndex) in getVisibleSubsections(sectionIndex, section.subsections)"
                :id="`subsection-${sectionIndex}-${subIndex}`"
                :key="`sub-${sectionIndex}-${subIndex}`"
                class="subsection-card"
              >
                <h4
                  v-if="!reviewMode"
                  class="subsection-title"
                >
                  {{ subsection.section_title }}
                </h4>
                <p
                  v-if="!reviewMode"
                  class="subsection-explanation"
                >
                  {{ subsection.explanation }}
                </p>

                <!-- Subsection Quiz (progressive reveal) -->
                <div
                  v-if="subsection.quiz && subsection.quiz.length > 0"
                  class="quiz-section"
                >
                  <div
                    v-for="(question, qIndex) in getVisibleQuestions(sectionIndex, subsection.quiz, subIndex)"
                    :id="`question-${sectionIndex}-${subIndex}-${qIndex}`"
                    :key="`subq-${sectionIndex}-${subIndex}-${qIndex}-${quizKey}`"
                    class="question-card"
                  >
                    <QuizQuestion
                      :key="`quiz-${sectionIndex}-sub${subIndex}-${qIndex}-${quizKey}`"
                      :question="question"
                      :question-index="qIndex"
                      :section-index="sectionIndex"
                      :subsection-index="subIndex"
                      :saved-answer-data="getSavedAnswerData(sectionIndex, subIndex, qIndex)"
                      @answer-submitted="handleAnswerSubmit"
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Review Comparison Overlay -->
    <div
      v-if="showReviewComparison"
      class="conclusion-overlay"
    >
      <div class="conclusion-content">
        <div class="confetti-container">
          <div class="confetti" />
          <div class="confetti" />
          <div class="confetti" />
          <div class="confetti" />
        </div>

        <div class="conclusion-card review-comparison">
          <h2 class="conclusion-title">
            📊 Learning Progress Analysis
          </h2>

          <div class="comparison-stats">
            <div class="comparison-row">
              <div class="comparison-column original">
                <h3>Original Attempt</h3>
                <div class="score-display">
                  <div class="score-number">
                    {{ originalScore }}
                  </div>
                  <div class="score-total">
                    / {{ originalAnsweredCount }}
                  </div>
                </div>
                <div
                  class="accuracy-badge"
                  :class="getAccuracyClass(originalAccuracy)"
                >
                  {{ originalAccuracy }}% Accuracy
                </div>
              </div>

              <div class="comparison-arrow">
                <span v-if="improvementPercentage > 0">→</span>
                <span v-else-if="improvementPercentage < 0">↓</span>
                <span v-else>=</span>
              </div>

              <div class="comparison-column review">
                <h3>Review Attempt</h3>
                <div class="score-display">
                  <div class="score-number">
                    {{ reviewScore }}
                  </div>
                  <div class="score-total">
                    / {{ reviewAnsweredQuestions.size }}
                  </div>
                </div>
                <div
                  class="accuracy-badge"
                  :class="getAccuracyClass(reviewAccuracy)"
                >
                  {{ reviewAccuracy }}% Accuracy
                </div>
              </div>
            </div>

            <div class="improvement-summary">
              <div
                v-if="improvementPercentage > 0"
                class="improvement-message positive"
              >
                <span class="improvement-icon">🎉</span>
                <div class="improvement-text">
                  <h4>Excellent Progress!</h4>
                  <p>You improved by <strong>{{ improvementPercentage }}%</strong></p>
                  <p class="insight">
                    Your understanding of the material has strengthened significantly.
                  </p>
                </div>
              </div>
              <div
                v-else-if="improvementPercentage < 0"
                class="improvement-message negative"
              >
                <span class="improvement-icon">📉</span>
                <div class="improvement-text">
                  <h4>Room for Growth</h4>
                  <p>Your score decreased by <strong>{{ Math.abs(improvementPercentage) }}%</strong></p>
                  <p class="insight">
                    Consider reviewing the material more carefully. Take your time with each question.
                  </p>
                </div>
              </div>
              <div
                v-else
                class="improvement-message neutral"
              >
                <span class="improvement-icon">✅</span>
                <div class="improvement-text">
                  <h4>Consistent Performance</h4>
                  <p>Your accuracy remained at <strong>{{ originalAccuracy }}%</strong></p>
                  <p class="insight">
                    You maintained your understanding of the material.
                  </p>
                </div>
              </div>
            </div>
          </div>

          <div class="conclusion-actions">
            <button
              class="btn btn-secondary"
              @click="reviewCourse"
            >
              🔄 Try Again
            </button>
            <button
              class="btn btn-primary"
              @click="exitReviewMode"
            >
              ✓ Exit Review
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useCourseStore } from '../stores/course'
import { useAuthStore } from '../stores/auth'
import QuizQuestion from '../components/QuizQuestion.vue'
import { achievements } from '../config/achievements'

export default {
  name: 'CourseView',
  components: {
    QuizQuestion
  },
  setup() {
    const route = useRoute()
    const router = useRouter()
    const courseStore = useCourseStore()
    const authStore = useAuthStore()

    const loading = ref(false)
    const error = ref(null)
    const currentSectionIndex = ref(0)
    const score = ref(0)
    const answeredQuestions = ref(new Set())
    const answerData = ref({}) // Store actual answer data for each question
    const reviewMode = ref(false)
    const originalScore = ref(0)
    const originalAnsweredCount = ref(0)
    const reviewScore = ref(0)
    const reviewAnsweredQuestions = ref(new Set())
    const showReviewComparison = ref(false)
    const quizKey = ref(0)
    const endedEarly = ref(false)
    const useStepFlow = ref(true) // Enable step-by-step flow mode
    const showOverview = ref(true) // Show course overview before starting
    const initialStepIndex = ref(0) // For resuming from saved progress
    const currentStepIndex = ref(0) // Current step in the flow
    const showContinueHint = ref(false) // Show hint to press enter
    const stepFlowContainer = ref(null) // Ref for step flow container
    const reviewQuestionOrder = ref([]) // Store shuffled question order for review mode

    const course = computed(() => courseStore.currentCourse)

    const currentSection = computed(() => {
      if (!course.value?.sections) return null
      return course.value.sections[currentSectionIndex.value]
    })

    // Calculate which sections should be visible
    const visibleSections = computed(() => {
      if (!course.value?.sections) return []

      // In review mode, show all sections
      if (reviewMode.value) {
        return course.value.sections
      }

      // Show sections up to currentSectionIndex + 1 (next incomplete section)
      return course.value.sections.slice(0, currentSectionIndex.value + 1)
    })

    // Check if a section is complete
    const isSectionComplete = (sectionIndex) => {
      if (!course.value?.sections) return false

      const section = course.value.sections[sectionIndex]
      if (!section) return false

      // Count questions in this section
      let sectionQuestionCount = section.quiz?.length || 0
      if (section.subsections) {
        section.subsections.forEach(subsection => {
          sectionQuestionCount += subsection.quiz?.length || 0
        })
      }

      // Count answered in Section
      let answeredInSection = 0

      // Check main section questions
      if (section.quiz) {
        section.quiz.forEach((_, qIndex) => {
          const questionKey = `${sectionIndex}-main-${qIndex}`
          if (answeredQuestions.value.has(questionKey) || reviewAnsweredQuestions.value.has(questionKey)) {
            answeredInSection++
          }
        })
      }

      // Check subsection questions
      if (section.subsections) {
        section.subsections.forEach((subsection, subIndex) => {
          if (subsection.quiz) {
            subsection.quiz.forEach((_, qIndex) => {
              const questionKey = `${sectionIndex}-${subIndex}-${qIndex}`
              if (answeredQuestions.value.has(questionKey) || reviewAnsweredQuestions.value.has(questionKey)) {
                answeredInSection++
              }
            })
          }
        })
      }

      return sectionQuestionCount > 0 && answeredInSection === sectionQuestionCount
    }

    const totalQuestions = computed(() => {
      if (!course.value?.sections) return 0

      const countQuestions = (sections) => {
        let count = 0
        for (const section of sections) {
          count += section.quiz?.length || 0
          if (section.subsections) {
            count += countQuestions(section.subsections)
          }
        }
        return count
      }

      return countQuestions(course.value.sections)
    })

    const progressPercentage = computed(() => {
      if (totalQuestions.value === 0) return 0
      return Math.round((answeredQuestions.value.size / totalQuestions.value) * 100)
    })

    const showConclusion = computed(() => {
      if (reviewMode.value) {
        return false // Don't show conclusion in review mode
      }
      // Show conclusion if all questions answered OR if user ended early
      return endedEarly.value || (totalQuestions.value > 0 && answeredQuestions.value.size === totalQuestions.value)
    })

    const reviewAccuracy = computed(() => {
      if (totalQuestions.value === 0) return 0
      return Math.round((reviewScore.value / totalQuestions.value) * 100)
    })

    const originalAccuracy = computed(() => {
      if (totalQuestions.value === 0) return 0
      return Math.round((originalScore.value / totalQuestions.value) * 100)
    })

    // Progressive reveal: Show questions one at a time
    const getVisibleQuestions = (sectionIndex, questions, subsectionIndex) => {
      if (reviewMode.value || !questions) return questions

      // Find the index of the first unanswered question
      let firstUnansweredIndex = -1
      for (let i = 0; i < questions.length; i++) {
        const questionKey = subsectionIndex === 'main'
          ? `${sectionIndex}-main-${i}`
          : `${sectionIndex}-${subsectionIndex}-${i}`

        if (!answeredQuestions.value.has(questionKey)) {
          firstUnansweredIndex = i
          break
        }
      }

      // If all answered, show all questions
      if (firstUnansweredIndex === -1) {
        return questions
      }

      // Show all answered questions + the first unanswered one
      return questions.slice(0, firstUnansweredIndex + 1)
    }

    // Progressive reveal: Show subsections one at a time
    const getVisibleSubsections = (sectionIndex, subsections) => {
      if (reviewMode.value || !subsections) return subsections

      const section = course.value.sections[sectionIndex]

      // First check if main section questions are complete
      const mainQuestionsComplete = !section.quiz || section.quiz.every((_, qIndex) => {
        const questionKey = `${sectionIndex}-main-${qIndex}`
        return answeredQuestions.value.has(questionKey)
      })

      if (!mainQuestionsComplete) {
        return [] // Don't show subsections until main questions are done
      }

      // Find the first incomplete subsection
      let firstIncompleteIndex = -1
      for (let i = 0; i < subsections.length; i++) {
        const subsection = subsections[i]
        if (!subsection.quiz) continue

        const allAnswered = subsection.quiz.every((_, qIndex) => {
          const questionKey = `${sectionIndex}-${i}-${qIndex}`
          return answeredQuestions.value.has(questionKey)
        })

        if (!allAnswered) {
          firstIncompleteIndex = i
          break
        }
      }

      // If all complete, show all subsections
      if (firstIncompleteIndex === -1) {
        return subsections
      }

      // Show all complete subsections + the first incomplete one
      return subsections.slice(0, firstIncompleteIndex + 1)
    }

    const improvementPercentage = computed(() => {
      return reviewAccuracy.value - originalAccuracy.value
    })

    const accuracyPercentage = computed(() => {
      if (totalQuestions.value === 0) return 0
      return Math.round((score.value / totalQuestions.value) * 100)
    })

    const accuracyClass = computed(() => {
      const acc = accuracyPercentage.value
      if (acc >= 80) return 'accuracy-excellent'
      if (acc >= 60) return 'accuracy-good'
      return 'accuracy-needs-review'
    })

    const hasProgress = computed(() => {
      return answeredQuestions.value.size > 0
    })

    // Step Flow Computed Properties
    const currentStep = computed(() => {
      if (currentStepIndex.value >= 0 && currentStepIndex.value < courseSteps.value.length) {
        return courseSteps.value[currentStepIndex.value]
      }
      return null
    })

    const isLastStep = computed(() => currentStepIndex.value === courseSteps.value.length - 1)

    const canProceedToNextStep = computed(() => {
      if (!currentStep.value) return false
      
      // For explanation blocks, can always proceed
      if (currentStep.value.type === 'explanation') {
        return true
      }
      
      // For question blocks, must be answered
      if (currentStep.value.type === 'question') {
        const questionKey = `${currentStep.value.sectionIndex}-${currentStep.value.subsectionIndex ?? 'main'}-${currentStep.value.questionIndex}`
        return answeredQuestions.value.has(questionKey)
      }
      
      return false
    })

    const currentQuestionNumber = computed(() => {
      // In review mode, use the displayNumber from shuffled questions
      if (reviewMode.value && currentStep.value?.displayNumber) {
        return currentStep.value.displayNumber
      }
      
      // Count how many question steps come before current step
      let count = 0
      for (let i = 0; i <= currentStepIndex.value; i++) {
        if (courseSteps.value[i]?.type === 'question') {
          count++
        }
      }
      return count
    })

    const stepFlowProgressPercentage = computed(() => {
      if (courseSteps.value.length === 0) return 0
      return Math.round(((currentStepIndex.value + 1) / courseSteps.value.length) * 100)
    })

    const loadCourse = async () => {
      const courseId = route.params.id
      console.log('[CourseView] loadCourse called with ID:', courseId)
      if (!courseId) {
        error.value = 'No course ID provided'
        return
      }

      loading.value = true
      error.value = null

      console.log('[CourseView] Calling courseStore.loadCourse')
      const result = await courseStore.loadCourse(courseId)
      console.log('[CourseView] loadCourse result:', result)

      if (!result.success) {
        console.error('[CourseView] Load failed:', result.error)
        error.value = result.error

        // If guest user and course not found, redirect to login
        if (!authStore.isAuthenticated) {
          console.log('[CourseView] Guest user with failed load - redirecting to login')
          setTimeout(() => {
            router.push('/login')
          }, 2000)
        }
      } else {
        console.log('[CourseView] Course loaded successfully')
      }

      loading.value = false
    }

    const startCourse = () => {
      showOverview.value = false
      currentStepIndex.value = initialStepIndex.value
      
      // Focus the step flow container after starting
      nextTick(() => {
        if (stepFlowContainer.value) {
          stepFlowContainer.value.focus()
        }
        // Auto-show hint for explanation steps
        if (currentStep.value?.type === 'explanation') {
          setTimeout(() => {
            showContinueHint.value = true
          }, 1000)
        }
      })
    }

    const nextStep = () => {
      if (!canProceedToNextStep.value) return

      if (isLastStep.value) {
        // Flow complete
        endedEarly.value = true
        saveProgress()
      } else {
        currentStepIndex.value++
        showContinueHint.value = false
        
        // Save progress
        initialStepIndex.value = currentStepIndex.value
        saveProgress()
        
        // Scroll to content and refocus
        setTimeout(() => {
          scrollToContent()
          if (stepFlowContainer.value) {
            stepFlowContainer.value.focus()
          }
          
          // Auto-show hint for explanation steps
          if (currentStep.value?.type === 'explanation') {
            setTimeout(() => {
              showContinueHint.value = true
            }, 1000)
          }
        }, 100)
      }
    }

    const handleStepEnterKey = (event) => {
      if (canProceedToNextStep.value && !event.shiftKey && !event.ctrlKey && !event.altKey) {
        // Check if the event target is an input, textarea, or button
        const target = event.target
        const isInputElement = ['INPUT', 'TEXTAREA', 'BUTTON', 'SELECT'].includes(target.tagName)
        
        if (!isInputElement) {
          event.preventDefault()
          nextStep()
        }
      }
    }

    const scrollToContent = () => {
      // Scroll to the step content, not the very top
      const stepContent = document.querySelector('.step-content')
      if (stepContent) {
        stepContent.scrollIntoView({ behavior: 'smooth', block: 'center' })
      }
    }

    const handleStepFlowAnswerSubmit = (data) => {
      const { isCorrect, sectionIndex, subsectionIndex, questionIndex } = data
      
      // Create unique key for this question
      const questionKey = `${sectionIndex}-${subsectionIndex ?? 'main'}-${questionIndex}`
      
      if (!answeredQuestions.value.has(questionKey)) {
        if (isCorrect) {
          score.value++
        }
        
        answeredQuestions.value.add(questionKey)
        
        // Save answer data
        answerData.value[questionKey] = {
          answer: data.answer,
          userAnswer: data.userAnswer,
          isCorrect: isCorrect
        }
        
        // Update current section index
        currentSectionIndex.value = sectionIndex
        
        // Save progress
        saveProgress()
        
        // Show continue hint after a short delay
        setTimeout(() => {
          showContinueHint.value = true
          // Refocus container for keyboard navigation
          if (stepFlowContainer.value) {
            stepFlowContainer.value.focus()
          }
        }, 500)
      }
    }

    const startCourseFromBeginning = () => {
      // Reset all progress
      score.value = 0
      answeredQuestions.value.clear()
      answerData.value = {}
      currentSectionIndex.value = 0
      initialStepIndex.value = 0
      currentStepIndex.value = 0
      showOverview.value = false
      
      // Clear saved progress
      const courseId = route.params.id
      if (courseId) {
        const progressKey = `course_progress_${courseId}`
        localStorage.removeItem(progressKey)
      }
      
      // Focus the step flow container
      nextTick(() => {
        if (stepFlowContainer.value) {
          stepFlowContainer.value.focus()
        }
      })
    }

    const handleAnswerSubmit = async (data) => {
      const { isCorrect, sectionIndex, subsectionIndex, questionIndex, answer, userAnswer } = data

      // Create unique key for this question
      const questionKey = `${sectionIndex}-${subsectionIndex ?? 'main'}-${questionIndex}`

      if (reviewMode.value) {
        // Review mode - track separately
        if (!reviewAnsweredQuestions.value.has(questionKey)) {
          if (isCorrect) {
            reviewScore.value++
          }
          reviewAnsweredQuestions.value.add(questionKey)

          // Check if review is complete
          if (reviewAnsweredQuestions.value.size === totalQuestions.value) {
            showReviewComparison.value = true
          }
        }
      } else {
        // Normal mode
        if (!answeredQuestions.value.has(questionKey)) {
          if (isCorrect) {
            score.value++
          }
          answeredQuestions.value.add(questionKey)

          // Save the answer data for restoration
          answerData.value[questionKey] = {
            answer: answer,
            userAnswer: userAnswer,
            isCorrect: isCorrect
          }

          // Save progress after each answer
          await saveProgress()

          // Auto-scroll to next question/subsection/section
          setTimeout(() => {
            const section = course.value.sections[sectionIndex]

            // Determine what to show next
            if (subsectionIndex === null || subsectionIndex === undefined) {
              // We're in main section questions
              const mainQuestions = section.quiz || []
              const nextQuestionIndex = questionIndex + 1

              if (nextQuestionIndex < mainQuestions.length) {
                // Scroll to next main question
                const nextQuestionEl = document.getElementById(`question-${sectionIndex}-main-${nextQuestionIndex}`)
                if (nextQuestionEl) {
                  nextQuestionEl.scrollIntoView({ behavior: 'smooth', block: 'center' })
                }
              } else if (section.subsections && section.subsections.length > 0) {
                // Main questions done, scroll to first subsection
                const firstSubsectionEl = document.getElementById(`subsection-${sectionIndex}-0`)
                if (firstSubsectionEl) {
                  firstSubsectionEl.scrollIntoView({ behavior: 'smooth', block: 'start' })
                }
              } else if (isSectionComplete(sectionIndex) && sectionIndex === currentSectionIndex.value) {
                // Section complete, reveal next section
                if (currentSectionIndex.value < course.value.sections.length - 1) {
                  currentSectionIndex.value++
                  setTimeout(() => {
                    const nextSectionEl = document.getElementById(`section-${currentSectionIndex.value}`)
                    if (nextSectionEl) {
                      nextSectionEl.scrollIntoView({ behavior: 'smooth', block: 'start' })
                    }
                  }, 100)
                }
              }
            } else {
              // We're in subsection questions
              const subsection = section.subsections[subsectionIndex]
              const subsectionQuestions = subsection.quiz || []
              const nextQuestionIndex = questionIndex + 1

              if (nextQuestionIndex < subsectionQuestions.length) {
                // Scroll to next subsection question
                const nextQuestionEl = document.getElementById(`question-${sectionIndex}-${subsectionIndex}-${nextQuestionIndex}`)
                if (nextQuestionEl) {
                  nextQuestionEl.scrollIntoView({ behavior: 'smooth', block: 'center' })
                }
              } else if (subsectionIndex + 1 < section.subsections.length) {
                // Subsection done, scroll to next subsection
                const nextSubsectionEl = document.getElementById(`subsection-${sectionIndex}-${subsectionIndex + 1}`)
                if (nextSubsectionEl) {
                  nextSubsectionEl.scrollIntoView({ behavior: 'smooth', block: 'start' })
                }
              } else if (isSectionComplete(sectionIndex) && sectionIndex === currentSectionIndex.value) {
                // All subsections done, reveal next section
                if (currentSectionIndex.value < course.value.sections.length - 1) {
                  currentSectionIndex.value++
                  setTimeout(() => {
                    const nextSectionEl = document.getElementById(`section-${currentSectionIndex.value}`)
                    if (nextSectionEl) {
                      nextSectionEl.scrollIntoView({ behavior: 'smooth', block: 'start' })
                    }
                  }, 100)
                }
              }
            }
          }, 500)
        }
      }
    }

    const reviewCourse = () => {
      // Save original scores
      originalScore.value = score.value
      originalAnsweredCount.value = answeredQuestions.value.size

      // Enter review mode - quiz only
      reviewMode.value = true
      reviewScore.value = 0
      reviewAnsweredQuestions.value = new Set()
      showReviewComparison.value = false
      endedEarly.value = false // Reset ended early flag

      // CLEAR ALL SESSION STATES - remove answer feedback/dialogs
      answeredQuestions.value = new Set()
      answerData.value = {}
      
      // Force re-render of all QuizQuestion components to reset state
      quizKey.value++

      // Build and shuffle question list for review mode
      const allQuestionSteps = []
      if (course.value?.sections) {
        course.value.sections.forEach((section, sectionIndex) => {
          // Add section questions
          if (section.quiz && section.quiz.length > 0) {
            section.quiz.forEach((question, questionIndex) => {
              allQuestionSteps.push({
                type: 'question',
                question: question,
                questionIndex: questionIndex,
                sectionIndex: sectionIndex,
                subsectionIndex: null,
                savedAnswerData: getSavedAnswerData(sectionIndex, null, questionIndex)
              })
            })
          }
          
          // Add subsection questions
          if (section.subsections && section.subsections.length > 0) {
            section.subsections.forEach((subsection, subsectionIndex) => {
              if (subsection.quiz && subsection.quiz.length > 0) {
                subsection.quiz.forEach((question, questionIndex) => {
                  allQuestionSteps.push({
                    type: 'question',
                    question: question,
                    questionIndex: questionIndex,
                    sectionIndex: sectionIndex,
                    subsectionIndex: subsectionIndex,
                    savedAnswerData: getSavedAnswerData(sectionIndex, subsectionIndex, questionIndex)
                  })
                })
              }
            })
          }
        })
      }
      
      // Fisher-Yates shuffle algorithm
      const shuffled = [...allQuestionSteps]
      for (let i = shuffled.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]]
      }
      
      // Add display numbers to shuffled questions
      reviewQuestionOrder.value = shuffled.map((step, index) => ({
        ...step,
        displayNumber: index + 1
      }))

      // Enable step flow mode and reset to first step
      useStepFlow.value = true
      currentStepIndex.value = 0
      initialStepIndex.value = 0
      showOverview.value = false // Skip overview in review
      currentSectionIndex.value = 0
      
      // Focus step flow container after render
      nextTick(() => {
        if (stepFlowContainer.value) {
          stepFlowContainer.value.focus()
        }
      })
      
      window.scrollTo({ top: 0, behavior: 'smooth' })
    }

    const goToCourses = () => {
      router.push('/courses')
    }

    const exitReviewMode = () => {
      reviewMode.value = false
      showReviewComparison.value = false
      endedEarly.value = false // Reset ended early flag

      // Find the last incomplete section to return to
      let lastIncompleteIndex = 0
      for (let i = 0; i < course.value.sections.length; i++) {
        if (!isSectionComplete(i)) {
          lastIncompleteIndex = i
          break
        }
        if (i === course.value.sections.length - 1) {
          lastIncompleteIndex = i // All complete, stay at last
        }
      }
      currentSectionIndex.value = lastIncompleteIndex
      window.scrollTo({ top: 0, behavior: 'smooth' })
    }

    const getAccuracyClass = (accuracy) => {
      if (accuracy >= 80) return 'success'
      if (accuracy >= 60) return 'good'
      return 'needs-review'
    }

    // Load course on mount if we have an ID
    onMounted(async () => {
      if (route.params.id) {
        await loadCourse()
        // Load saved progress after course is loaded
        await loadSavedProgress()
      } else if (!course.value) {
        error.value = 'No course data available'
      }
    })

    // Watch for course ID changes
    watch(() => route.params.id, () => {
      if (route.params.id) {
        loadCourse()
      }
    })

    // Admin controls
    const adminMessage = ref('')
    const adminMessageType = ref('success')

    const completeAllQuestions = () => {
      if (!authStore.user?.isAdmin) return

      // Mark all questions as correct
      score.value = totalQuestions.value

      // Add all questions to answered set
      if (course.value?.sections) {
        const addAllQuestions = (sections, sectionIndex) => {
          sections.forEach((section, idx) => {
            const actualSectionIndex = sectionIndex !== undefined ? sectionIndex : idx

            // Main section questions
            if (section.quiz) {
              section.quiz.forEach((_, qIndex) => {
                const questionKey = `${actualSectionIndex}-main-${qIndex}`
                answeredQuestions.value.add(questionKey)
              })
            }

            // Subsection questions
            if (section.subsections) {
              section.subsections.forEach((subsection, subIdx) => {
                if (subsection.quiz) {
                  subsection.quiz.forEach((_, qIndex) => {
                    const questionKey = `${actualSectionIndex}-${subIdx}-${qIndex}`
                    answeredQuestions.value.add(questionKey)
                  })
                }
              })
            }
          })
        }

        addAllQuestions(course.value.sections)
      }

      adminMessage.value = `✅ Completed all ${totalQuestions.value} questions!`
      adminMessageType.value = 'success'
      setTimeout(() => { adminMessage.value = '' }, 3000)
    }

    const resetProgress = () => {
      if (!authStore.user?.isAdmin) return

      // Reset score and answered questions
      score.value = 0
      answeredQuestions.value.clear()
      currentSectionIndex.value = 0

      // Clear saved progress
      const courseId = route.params.id
      if (courseId) {
        const progressKey = `course_progress_${courseId}`
        localStorage.removeItem(progressKey)
      }

      adminMessage.value = '🔄 Progress reset successfully!'
      adminMessageType.value = 'success'
      setTimeout(() => { adminMessage.value = '' }, 3000)
    }

    const saveProgress = async () => {
      const courseId = route.params.id
      if (!courseId) return

      await courseStore.updateProgress(
        courseId,
        answeredQuestions.value,
        score.value,
        currentSectionIndex.value,
        answerData.value,
        initialStepIndex.value
      )
    }

    const loadSavedProgress = async () => {
      const courseId = route.params.id
      if (!courseId) return

      const result = await courseStore.loadProgress(courseId)

      if (result.success && result.progress) {
        const progress = result.progress

        // Restore answered questions (convert array back to Set)
        if (progress.answered_questions && Array.isArray(progress.answered_questions)) {
          answeredQuestions.value = new Set(progress.answered_questions)
        }

        // Restore score
        if (typeof progress.score === 'number') {
          score.value = progress.score
        }

        // Restore current section index
        if (typeof progress.current_section_index === 'number') {
          currentSectionIndex.value = progress.current_section_index
        }

        // Restore answer data
        if (progress.answer_data && typeof progress.answer_data === 'object') {
          answerData.value = progress.answer_data
        }

        // Calculate initial step index based on answered questions
        // Find the first unanswered question
        let calculatedStepIndex = 0
        if (answeredQuestions.value.size > 0) {
          // Wait for course to be loaded and steps to be generated
          await nextTick()
          
          for (let i = 0; i < courseSteps.value.length; i++) {
            const step = courseSteps.value[i]
            if (step.type === 'question') {
              const questionKey = `${step.sectionIndex}-${step.subsectionIndex ?? 'main'}-${step.questionIndex}`
              if (!answeredQuestions.value.has(questionKey)) {
                calculatedStepIndex = i
                break
              }
            }
          }
          // If all questions answered, set to last step
          if (calculatedStepIndex === 0 && answeredQuestions.value.size > 0) {
            calculatedStepIndex = courseSteps.value.length - 1
          }
        }
        
        initialStepIndex.value = calculatedStepIndex
        currentStepIndex.value = calculatedStepIndex

        console.log('[CourseView] Loaded progress:', progress)
        console.log('[CourseView] Calculated initial step index:', calculatedStepIndex)
      }
    }

    const endCourseEarly = () => {
      // Save progress one final time
      saveProgress()

      // Set flag to show conclusion
      endedEarly.value = true

      // Show the conclusion screen
      // We'll scroll to bottom where conclusion appears
      setTimeout(() => {
        window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' })
      }, 100)
    }

    const getSavedAnswerData = (sectionIndex, subsectionIndex, questionIndex) => {
      const questionKey = `${sectionIndex}-${subsectionIndex ?? 'main'}-${questionIndex}`
      return answerData.value[questionKey] || null
    }

    // Achievement Badges Logic
    const earnedBadges = computed(() => {
      const badges = []
      if (course.value?.sections && isSectionComplete(0)) {
        badges.push(achievements.find(a => a.id === 'first-section'))
      }
      if (course.value?.sections && course.value.sections.every((_, idx) => isSectionComplete(idx))) {
        badges.push(achievements.find(a => a.id === 'all-sections'))
      }
      if (score.value === totalQuestions.value && totalQuestions.value > 0) {
        badges.push(achievements.find(a => a.id === 'quiz-master'))
      }
      if (accuracyPercentage.value >= 80 && totalQuestions.value > 0) {
        badges.push(achievements.find(a => a.id === 'accuracy-80'))
      }
      if (answeredQuestions.value.size > 0) {
        badges.push(achievements.find(a => a.id === 'participation'))
      }
      return badges.filter(Boolean)
    })

    // Convert course sections into linear steps for StepFlow
    const courseSteps = computed(() => {
      if (!course.value?.sections) return []
      
      const steps = []
      
      course.value.sections.forEach((section, sectionIndex) => {
        // Add section explanation as a step
        if (!reviewMode.value && section.explanation) {
          steps.push({
            type: 'explanation',
            title: section.section_title,
            content: section.explanation,
            sectionIndex
          })
        }
        
        // Add section questions as steps
        if (section.quiz && section.quiz.length > 0) {
          section.quiz.forEach((question, questionIndex) => {
            steps.push({
              type: 'question',
              question: question,
              questionIndex: questionIndex,
              sectionIndex: sectionIndex,
              subsectionIndex: null,
              savedAnswerData: getSavedAnswerData(sectionIndex, null, questionIndex)
            })
          })
        }
        
        // Add subsections
        if (section.subsections && section.subsections.length > 0) {
          section.subsections.forEach((subsection, subsectionIndex) => {
            // Add subsection explanation
            if (!reviewMode.value && subsection.section_title) {
              steps.push({
                type: 'explanation',
                title: subsection.section_title,
                content: subsection.explanation || '',
                sectionIndex,
                subsectionIndex
              })
            }
            
            // Add subsection questions
            if (subsection.quiz && subsection.quiz.length > 0) {
              subsection.quiz.forEach((question, questionIndex) => {
                steps.push({
                  type: 'question',
                  question: question,
                  questionIndex: questionIndex,
                  sectionIndex: sectionIndex,
                  subsectionIndex: subsectionIndex,
                  savedAnswerData: getSavedAnswerData(sectionIndex, subsectionIndex, questionIndex)
                })
              })
            }
          })
        }
      })
      
      // In review mode, use shuffled order (set in reviewCourse function)
      if (reviewMode.value && reviewQuestionOrder.value.length > 0) {
        // Return shuffled questions with updated display numbers
        return reviewQuestionOrder.value
      }
      
      return steps
    })

    const handleEndEarly = () => {
      // Save final progress
      initialStepIndex.value = currentStepIndex.value
      saveProgress()
      
      // Show conclusion
      endedEarly.value = true
    }

    return {
      loading,
      error,
      course,
      currentSection,
      currentSectionIndex,
      totalQuestions,
      score,
      answeredQuestions,
      progressPercentage,
      showConclusion,
      accuracyPercentage,
      accuracyClass,
      handleAnswerSubmit,
      reviewCourse,
      goToCourses,
      authStore,
      adminMessage,
      adminMessageType,
      completeAllQuestions,
      resetProgress,
      reviewMode,
      originalScore,
      originalAnsweredCount,
      reviewScore,
      reviewAnsweredQuestions,
      showReviewComparison,
      reviewAccuracy,
      originalAccuracy,
      improvementPercentage,
      exitReviewMode,
      getAccuracyClass,
      quizKey,
      visibleSections,
      isSectionComplete,
      getVisibleQuestions,
      getVisibleSubsections,
      endCourseEarly,
      getSavedAnswerData,
      earnedBadges,
      useStepFlow,
      courseSteps,
      showOverview,
      hasProgress,
      startCourse,
      startCourseFromBeginning,
      initialStepIndex,
      currentStepIndex,
      currentStep,
      isLastStep,
      canProceedToNextStep,
      currentQuestionNumber,
      stepFlowProgressPercentage,
      showContinueHint,
      stepFlowContainer,
      nextStep,
      handleStepEnterKey,
      handleStepFlowAnswerSubmit,
      handleEndEarly
    }
  }
}
</script>

<style scoped>
.course-view {
  padding: 2rem 0;
  min-height: calc(100vh - 200px);
}

.loading-state {
  text-align: center;
  padding: 4rem 0;
  color: var(--text-secondary);
}

.course-header {
  margin-bottom: 2rem;
}

.course-title {
  font-size: 2.5rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 1rem;
}

.course-meta {
  display: flex;
  gap: 2rem;
  flex-wrap: wrap;
}

.meta-item {
  color: var(--text-secondary);
  font-size: 1rem;
}

.section-card {
  margin-bottom: 2rem;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 2px solid var(--border-color);
}

.section-title {
  font-size: 2rem;
  font-weight: 600;
  color: var(--accent-primary);
}

.section-progress {
  color: var(--text-secondary);
  font-size: 0.875rem;
  background: var(--bg-tertiary);
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.review-badge {
  background: rgba(168, 85, 247, 0.2);
  color: #a855f7;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 600;
  border: 1px solid rgba(168, 85, 247, 0.3);
}

.complete-badge {
  background: rgba(34, 197, 94, 0.2);
  color: #4ade80;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 600;
  border: 1px solid rgba(34, 197, 94, 0.3);
}

.section-explanation {
  margin-bottom: 2rem;
  padding: 1.5rem;
  background: var(--bg-tertiary);
  border-left: 4px solid var(--accent-primary);
  border-radius: 0.5rem;
  color: var(--text-secondary);
  line-height: 1.6;
}

.quiz-section {
  margin: 2rem 0;
}

.quiz-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 1.5rem;
}

.question-card {
  margin-bottom: 2rem;
}

.subsections {
  margin-top: 3rem;
}

.subsections-title {
  font-size: 1.75rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 1.5rem;
}

.subsection-card {
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: 1rem;
  padding: 2rem;
  margin-bottom: 2rem;
}

.subsection-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--accent-primary);
  margin-bottom: 1rem;
}

.subsection-explanation {
  color: var(--text-secondary);
  line-height: 1.6;
  margin-bottom: 1.5rem;
}

.section-navigation {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  margin-top: 3rem;
  padding-top: 2rem;
  border-top: 2px solid var(--border-color);
}

@media (max-width: 768px) {
  .course-title {
    font-size: 2rem;
  }

  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }

  .course-meta {
    flex-direction: column;
    gap: 0.5rem;
  }

  .section-navigation {
    flex-direction: column;
  }

  .section-navigation .btn {
    width: 100%;
  }
}

/* Admin Controls */
.admin-controls {
  background: linear-gradient(135deg, var(--bg-tertiary), var(--bg-tertiary));
  border: 2px solid var(--border-color);
  margin-bottom: 2rem;
  padding: 1.5rem;
}

.admin-title {
  color: var(--accent-primary);
  font-size: 1.25rem;
  margin-bottom: 1rem;
  font-weight: 600;
}

.admin-buttons {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.btn-admin {
  background: linear-gradient(135deg, var(--accent-primary), var(--accent-light));
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 0.5rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-admin:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(119, 51, 255, 0.4);
}

:root[data-theme="light"] .btn-admin:hover {
  box-shadow: 0 4px 15px rgba(16, 185, 129, 0.35);
}

.btn-admin-danger {
  background: linear-gradient(135deg, #ef4444, #dc2626);
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 0.5rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-admin-danger:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(239, 68, 68, 0.4);
}

.admin-message {
  margin-top: 1rem;
  padding: 0.75rem;
  border-radius: 0.5rem;
  font-weight: 500;
}

.admin-message.success {
  background: rgba(34, 197, 94, 0.1);
  border: 1px solid rgba(34, 197, 94, 0.3);
  color: #4ade80;
}

/* Course Conclusion Styles */
.conclusion-section {
  margin-top: 2rem;
  text-align: center;
  animation: slideUp 0.5s ease;
}

@keyframes slideUp {
  from {
    transform: translateY(30px);
    opacity: 0;
  }

  to {
    transform: translateY(0);
    opacity: 1;
  }
}

/* Keep overlay styles for review comparison */
.conclusion-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.85);
  backdrop-filter: blur(10px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.3s ease;
  padding: 2rem;
  overflow-y: auto;
}

:root[data-theme="light"] .conclusion-overlay {
  background: rgba(255, 255, 255, 0.95);
}

.conclusion-content {
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  display: flex;
  align-items: center;
  justify-content: center;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }

  to {
    opacity: 1;
  }
}

.conclusion-card {
  background: linear-gradient(135deg, var(--bg-primary) 0%, var(--bg-secondary) 100%);
  border-radius: 1.5rem;
  padding: 2rem;
  max-width: 600px;
  width: 100%;
  box-shadow: 0 20px 60px var(--shadow-color);
  border: 1px solid var(--border-light);
  text-align: center;
  margin: auto;
}

.conclusion-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
  animation: bounce 1s ease infinite;
}

@keyframes bounce {

  0%,
  100% {
    transform: translateY(0);
  }

  50% {
    transform: translateY(-20px);
  }
}

.conclusion-title {
  font-size: 2.5rem;
  font-weight: 700;
  background: linear-gradient(135deg, var(--accent-primary) 0%, var(--accent-secondary) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 0.5rem;
}

.conclusion-subtitle {
  font-size: 1.25rem;
  color: var(--text-secondary);
  margin-bottom: 2rem;
}

.conclusion-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: var(--bg-tertiary);
  border: 1px solid var(--border-light);
  border-radius: 1rem;
  padding: 1.5rem 1rem;
  transition: transform 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-5px);
  background: var(--card-bg);
}

.stat-value {
  font-size: 2.5rem;
  font-weight: 700;
  background: linear-gradient(135deg, var(--accent-primary) 0%, var(--accent-secondary) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 0.5rem;
}

.stat-label {
  font-size: 0.875rem;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.conclusion-summary {
  background: var(--bg-tertiary);
  border: 1px solid var(--border-light);
  border-radius: 1rem;
  padding: 1.5rem;
  margin-bottom: 2rem;
  text-align: left;
}

.conclusion-summary h3 {
  color: var(--text-primary);
  margin-bottom: 1rem;
  font-size: 1.25rem;
}

.conclusion-summary strong {
  color: var(--accent-primary);
}

.summary-text {
  color: var(--text-secondary);
  line-height: 1.6;
  margin-bottom: 1rem;
}

.accuracy-excellent {
  color: #4ade80;
  font-weight: 600;
}

.accuracy-good {
  color: #fbbf24;
  font-weight: 600;
}

.accuracy-needs-review {
  color: #f87171;
  font-weight: 600;
}

.summary-message {
  padding: 0.75rem 1rem;
  border-radius: 0.5rem;
  font-weight: 500;
  margin-top: 1rem;
}

.summary-message.success {
  background: rgba(74, 222, 128, 0.1);
  border: 1px solid rgba(74, 222, 128, 0.3);
  color: #4ade80;
}

.summary-message.good {
  background: rgba(251, 191, 36, 0.1);
  border: 1px solid rgba(251, 191, 36, 0.3);
  color: #fbbf24;
}

.summary-message.needs-review {
  background: rgba(248, 113, 113, 0.1);
  border: 1px solid rgba(248, 113, 113, 0.3);
  color: #f87171;
}

.conclusion-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
}

.conclusion-actions .btn {
  flex: 1;
  padding: 1rem 2rem;
  font-size: 1rem;
}

/* Progress Bar Styles */
.progress-container {
  margin-top: 1.5rem;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 0.75rem;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}

.progress-label {
  font-size: 0.875rem;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
}

.progress-percentage {
  font-size: 1.25rem;
  font-weight: 700;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.progress-bar {
  width: 100%;
  height: 1.5rem;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 1rem;
  overflow: hidden;
  position: relative;
  box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.2);
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  border-radius: 1rem;
  transition: width 0.5s ease;
  position: relative;
  overflow: hidden;
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

.progress-stats {
  display: flex;
  justify-content: space-between;
  margin-top: 0.75rem;
  font-size: 0.813rem;
  font-weight: 500;
}

.stat-completed {
  color: #4ade80;
}

.stat-remaining {
  color: rgba(255, 255, 255, 0.6);
}

/* End Course Section */
.end-course-section {
  margin-top: 2rem;
  padding-top: 2rem;
  border-top: 1px solid rgba(119, 51, 255, 0.2);
  text-align: center;
}

.end-course-section .btn {
  min-width: 200px;
  margin-bottom: 0.5rem;
}

.end-course-hint {
  color: #94a3b8;
  font-size: 0.875rem;
  margin: 0;
}

/* Review Comparison Styles */
.review-comparison {
  max-width: 900px;
}

.comparison-stats {
  margin: 2rem 0;
}

.comparison-row {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  gap: 2rem;
  align-items: center;
  margin-bottom: 2rem;
}

.comparison-column {
  padding: 1.5rem;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 1rem;
  border: 2px solid rgba(255, 255, 255, 0.1);
  text-align: center;
}

.comparison-column.original {
  border-color: rgba(100, 116, 139, 0.3);
}

.comparison-column.review {
  border-color: rgba(102, 126, 234, 0.3);
}

.comparison-column h3 {
  font-size: 0.875rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: rgba(255, 255, 255, 0.6);
  margin-bottom: 1rem;
}

.score-display {
  display: flex;
  align-items: baseline;
  justify-content: center;
  gap: 0.25rem;
  margin-bottom: 0.75rem;
}

.score-number {
  font-size: 3rem;
  font-weight: 700;
  color: #e2e8f0;
}

.score-total {
  font-size: 1.5rem;
  color: rgba(255, 255, 255, 0.5);
}

.accuracy-badge {
  display: inline-block;
  padding: 0.5rem 1rem;
  border-radius: 2rem;
  font-size: 0.875rem;
  font-weight: 600;
}

.accuracy-badge.success {
  background: rgba(74, 222, 128, 0.15);
  border: 1px solid rgba(74, 222, 128, 0.3);
  color: #4ade80;
}

.accuracy-badge.good {
  background: rgba(251, 191, 36, 0.15);
  border: 1px solid rgba(251, 191, 36, 0.3);
  color: #fbbf24;
}

.accuracy-badge.needs-review {
  background: rgba(248, 113, 113, 0.15);
  border: 1px solid rgba(248, 113, 113, 0.3);
  color: #f87171;
}

.comparison-arrow {
  font-size: 2rem;
  color: rgba(255, 255, 255, 0.4);
  font-weight: 700;
}

.improvement-summary {
  padding: 2rem;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 1rem;
  border: 2px solid rgba(255, 255, 255, 0.1);
}

.improvement-message {
  display: flex;
  align-items: flex-start;
  gap: 1.5rem;
}

.improvement-icon {
  font-size: 3rem;
  flex-shrink: 0;
}

.improvement-text h4 {
  font-size: 1.25rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
  color: #e2e8f0;
}

.improvement-text p {
  font-size: 1rem;
  margin-bottom: 0.5rem;
  color: rgba(255, 255, 255, 0.8);
}

.improvement-text p strong {
  font-weight: 700;
  font-size: 1.25rem;
}

.improvement-message.positive .improvement-text p strong {
  color: #4ade80;
}

.improvement-message.negative .improvement-text p strong {
  color: #f87171;
}

.improvement-message.neutral .improvement-text p strong {
  color: #fbbf24;
}

.improvement-text .insight {
  font-size: 0.875rem;
  color: rgba(255, 255, 255, 0.6);
  font-style: italic;
  margin-top: 0.5rem;
}

.badge-container {
  margin-top: 1rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.badge-label {
  font-weight: 600;
  margin-right: 0.5rem;
}

.badge-item {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  background: #f6f8fa;
  border-radius: 8px;
  padding: 0.25rem 0.5rem;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
}

.badge-img {
  width: 32px;
  height: 32px;
  object-fit: contain;
  border-radius: 6px;
  margin-right: 0.25rem;
}

.badge-text {
  font-size: 0.95rem;
  color: var(--text-primary);
}

.badge-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(80px, 1fr));
  gap: 1rem;
  justify-items: center;
  margin-top: 1rem;
}

.badge-grid-item {
  display: flex;
  align-items: center;
  justify-content: center;
}

.badge-img-large {
  width: 80px;
  height: 80px;
  object-fit: contain;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

@media (max-width: 768px) {
  .admin-buttons {
    flex-direction: column;
  }

  .btn-admin,
  .btn-admin-danger {
    width: 100%;
  }

  .progress-percentage {
    font-size: 1rem;
  }

  .progress-bar {
    height: 1.25rem;
  }

  .conclusion-section {
    margin-top: 1.5rem;
  }

  .conclusion-title {
    font-size: 1.75rem;
  }

  .conclusion-icon {
    font-size: 3rem;
  }

  .conclusion-subtitle {
    font-size: 1rem;
  }

  .conclusion-stats {
    grid-template-columns: 1fr;
    gap: 0.75rem;
  }

  /* Keep overlay styles for review comparison */
  .conclusion-overlay {
    padding: 1rem;
  }

  .conclusion-content {
    max-height: 95vh;
  }

  .conclusion-card {
    padding: 1.5rem 1rem;
  }

  .stat-value {
    font-size: 2rem;
  }

  .conclusion-actions {
    flex-direction: column;
  }

  .conclusion-actions .btn {
    width: 100%;
  }

  .comparison-row {
    grid-template-columns: 1fr;
    gap: 1rem;
  }

  .comparison-arrow {
    transform: rotate(90deg);
    margin: 0.5rem 0;
  }

  .score-number {
    font-size: 2rem;
  }

  .score-total {
    font-size: 1.25rem;
  }

  .improvement-message {
    flex-direction: column;
    text-align: center;
  }

  .improvement-icon {
    font-size: 2rem;
  }

  .improvement-text h4 {
    font-size: 1rem;
  }
}

/* Course Overview Screen Styles */
.overview-screen {
  min-height: calc(100vh - 200px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem 0;
}

.overview-card {
  max-width: 700px;
  margin: 0 auto;
  text-align: center;
  padding: 3rem;
  animation: fadeIn 0.5s ease;
}

.overview-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
  animation: bounce 1s ease infinite;
}

.overview-title {
  font-size: 2.5rem;
  font-weight: 700;
  color: var(--accent-primary);
  margin-bottom: 2rem;
}

.overview-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.stat-box {
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: 1rem;
  padding: 1.5rem 1rem;
  transition: transform 0.3s ease;
}

.stat-box:hover {
  transform: translateY(-5px);
}

.stat-value {
  font-size: 2.5rem;
  font-weight: 700;
  background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 0.5rem;
}

.stat-label {
  font-size: 0.875rem;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.previous-progress {
  margin: 2rem 0;
}

.progress-badge {
  background: var(--bg-tertiary);
  border: 2px solid var(--accent-primary);
  border-radius: 1rem;
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  text-align: left;
}

.badge-icon {
  font-size: 2.5rem;
  flex-shrink: 0;
}

.badge-content h3 {
  font-size: 1.25rem;
  color: var(--accent-primary);
  margin-bottom: 0.5rem;
}

.badge-content p {
  color: var(--text-secondary);
  margin: 0.25rem 0;
  font-size: 0.938rem;
}

.score-display {
  margin-top: 0.5rem;
  font-size: 1rem;
}

.score-display strong {
  color: var(--accent-primary);
  font-size: 1.25rem;
}

.overview-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
}

.overview-actions .btn {
  padding: 1rem 2rem;
  font-size: 1.125rem;
  min-width: 180px;
}

@media (max-width: 768px) {
  .overview-card {
    padding: 2rem 1.5rem;
  }

  .overview-title {
    font-size: 1.75rem;
  }

  .overview-icon {
    font-size: 3rem;
  }

  .overview-stats {
    grid-template-columns: 1fr;
    gap: 1rem;
  }

  .overview-actions {
    flex-direction: column;
  }

  .overview-actions .btn {
    width: 100%;
  }

  .progress-badge {
    flex-direction: column;
    text-align: center;
  }

  .badge-content {
    text-align: center;
  }
}

/* Step Flow Styles (Merged from StepFlow.vue) */
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

/* Admin Controls in Step Flow */
.admin-controls-stepflow {
  background: linear-gradient(135deg, var(--bg-tertiary), var(--bg-tertiary));
  border: 2px solid var(--border-color);
  margin: 1rem 1.5rem;
  padding: 1.5rem;
  border-radius: 1rem;
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
  width: 100%;
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

/* Responsive Design for Step Flow */
@media (max-width: 768px) {
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

/* Light Theme Adjustments for Step Flow */
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

