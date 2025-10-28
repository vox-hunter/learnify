<template>
  <div class="onboarding-view">
    <div class="onboarding-container">
      <!-- Progress Bar -->
      <div class="progress-bar-container">
        <div
          class="progress-bar"
          :style="{ width: progressPercentage + '%' }"
        />
        <div class="progress-text">
          Step {{ currentStep }} of {{ totalSteps }}
        </div>
      </div>

      <!-- Question Card -->
      <Transition
        :name="prefersReducedMotion ? '' : (direction === 'backward' ? 'slide-fade-back' : 'slide-fade')"
        mode="out-in"
      >
        <div
          v-if="!showSuccess"
          :key="currentStep"
          class="question-card card"
        >
          <!-- Question Badge -->
          <div class="question-badge">
            {{ currentStep }}/{{ totalSteps }}
          </div>

          <!-- Question Title with Emoji -->
          <div
            v-if="currentQuestion"
            class="question-header"
          >
            <h1 class="question-title">
              {{ currentQuestion.emoji }} {{ currentQuestion.title }}
            </h1>
            <p
              v-if="currentQuestion.subtitle"
              class="question-subtitle"
            >
              {{ currentQuestion.subtitle }}
            </p>
          </div>

          <!-- Loading State for AI Suggestions -->
          <div
            v-if="loading"
            class="loading-state"
          >
            <div class="spinner" />
            <p class="loading-text">
              {{ loadingMessage }}
            </p>
          </div>

          <!-- Question Content -->
          <div
            v-else
            class="question-content"
          >
            <!-- Step 1: Date of Birth -->
            <div
              v-if="currentKey === 'dob'"
              class="form-group"
            >
              <label class="form-label">When were you born?</label>
              <input
                v-model="formData.date_of_birth"
                type="date"
                class="form-input"
                required
              >
              <p
                v-if="calculateAge() !== null"
                class="form-hint"
              >
                You are {{ calculateAge() }} years old
              </p>
            </div>

            <!-- Step 2: User Type Selection -->
            <div
              v-if="currentKey === 'role'"
              class="option-grid"
            >
              <div
                v-for="type in ['student', 'educator']"
                :key="type"
                :class="['option-card', { active: formData.user_type === type }]"
                @click="formData.user_type = type"
              >
                <div class="option-icon">
                  {{ type === 'student' ? '👨‍🎓' : '👨‍🏫' }}
                </div>
                <div class="option-title">
                  {{ type.charAt(0).toUpperCase() + type.slice(1) }}
                </div>
                <div class="option-description">
                  {{ type === 'student' ? 'I want to learn and study' : 'I want to teach and create content' }}
                </div>
              </div>
            </div>

            <!-- Step 3: Auto-Detection Confirmation -->
            <div
              v-if="currentKey === 'prefs'"
              class="auto-detection-form"
            >
              <div class="detection-item">
                <label class="form-label">Timezone</label>
                <div class="detection-display">
                  {{ formData.timezone }}
                </div>
                <select
                  v-model="formData.timezone"
                  class="form-select"
                >
                  <option value="UTC">
                    UTC
                  </option>
                  <option value="America/New_York">
                    America/New_York
                  </option>
                  <option value="America/Chicago">
                    America/Chicago
                  </option>
                  <option value="America/Denver">
                    America/Denver
                  </option>
                  <option value="America/Los_Angeles">
                    America/Los_Angeles
                  </option>
                  <option value="Europe/London">
                    Europe/London
                  </option>
                  <option value="Europe/Paris">
                    Europe/Paris
                  </option>
                  <option value="Asia/Tokyo">
                    Asia/Tokyo
                  </option>
                  <option value="Asia/Shanghai">
                    Asia/Shanghai
                  </option>
                  <option value="Asia/Hong_Kong">
                    Asia/Hong_Kong
                  </option>
                  <option value="Australia/Sydney">
                    Australia/Sydney
                  </option>
                </select>
              </div>

              <div class="detection-item">
                <label class="form-label">Language Preference</label>
                <div class="detection-display">
                  {{ formData.language_preference }}
                </div>
                <select
                  v-model="formData.language_preference"
                  class="form-select"
                >
                  <option value="en">
                    English
                  </option>
                  <option value="es">
                    Spanish
                  </option>
                  <option value="fr">
                    French
                  </option>
                  <option value="de">
                    German
                  </option>
                  <option value="it">
                    Italian
                  </option>
                  <option value="pt">
                    Portuguese
                  </option>
                  <option value="zh">
                    Chinese
                  </option>
                  <option value="ja">
                    Japanese
                  </option>
                  <option value="ko">
                    Korean
                  </option>
                </select>
              </div>
            </div>

            <!-- Student Path: Step 4 - Year Level -->
            <div
              v-if="currentKey === 'student_year'"
              class="form-group"
            >
              <label class="form-label">What is your year level?</label>
              <select
                v-model="formData.student_profile.year_level"
                class="form-select"
              >
                <option value="">
                  Select a year level
                </option>
                <optgroup label="Secondary">
                  <option value="Year 7">
                    Year 7
                  </option>
                  <option value="Year 8">
                    Year 8
                  </option>
                  <option value="Year 9">
                    Year 9
                  </option>
                  <option value="Year 10">
                    Year 10
                  </option>
                  <option value="Year 11">
                    Year 11
                  </option>
                  <option value="Year 12">
                    Year 12
                  </option>
                  <option value="Year 13">
                    Year 13
                  </option>
                </optgroup>
                <optgroup label="College">
                  <option value="College Year 1">
                    College Year 1
                  </option>
                  <option value="College Year 2">
                    College Year 2
                  </option>
                  <option value="College Year 3">
                    College Year 3
                  </option>
                  <option value="College Year 4">
                    College Year 4
                  </option>
                </optgroup>
                <optgroup label="University">
                  <option value="University Year 1">
                    University Year 1
                  </option>
                  <option value="University Year 2">
                    University Year 2
                  </option>
                  <option value="University Year 3">
                    University Year 3
                  </option>
                  <option value="University Year 4">
                    University Year 4
                  </option>
                </optgroup>
              </select>
            </div>

            <!-- Student Path: Step 5 - Study Stage -->
            <div
              v-if="currentKey === 'student_stage'"
              class="option-grid"
            >
              <button
                v-for="stage in ['KS3', 'IGCSE', 'A-Level', 'IB', 'AP', 'College', 'University', 'Other']"
                :key="stage"
                :class="['stage-btn', { active: formData.student_profile.study_stage === stage || (stage === 'Other' && isStudyStageOther) }]"
                tabindex="0"
                @click="handleStudyStageSelection(stage)"
                @keydown.enter.prevent="handleStudyStageSelection(stage)"
                @keydown.space.prevent="handleStudyStageSelection(stage)"
              >
                {{ stage }}
              </button>
            </div>
            <div
              v-if="currentKey === 'student_stage' && isStudyStageOther"
              class="form-group"
              style="margin-top: 1rem;"
            >
              <input
                v-model="customStudyStage"
                type="text"
                class="form-input"
                placeholder="Type your curriculum or program"
              >
              <p class="form-hint">
                Type your curriculum or program
              </p>
            </div>

            <!-- Student Path: Step 6 - Exam Board -->
            <div
              v-if="currentKey === 'student_exam_board'"
              class="form-group"
            >
              <label class="form-label">Which exam board?</label>
              <div
                v-if="examBoardLoading"
                class="loading-badge"
              >
                Loading exam boards...
              </div>
              <div
                v-else
                class="suggestions-grid"
              >
                <button
                  v-for="suggestion in examBoardSuggestions"
                  :key="suggestion.name"
                  :class="['suggestion-chip', { active: formData.student_profile.exam_board === suggestion.name }]"
                  :title="suggestion.description"
                  tabindex="0"
                  @click="selectExamBoard(suggestion.name)"
                  @keydown.enter.prevent="selectExamBoard(suggestion.name)"
                  @keydown.space.prevent="selectExamBoard(suggestion.name)"
                >
                  {{ suggestion.name }}
                </button>
                <button
                  :class="['suggestion-chip', { active: formData.student_profile.exam_board === 'Other' }]"
                  tabindex="0"
                  @click="selectExamBoard('Other')"
                  @keydown.enter.prevent="selectExamBoard('Other')"
                  @keydown.space.prevent="selectExamBoard('Other')"
                >
                  Other
                </button>
              </div>
              <div
                v-if="formData.student_profile.exam_board === 'Other'"
                class="form-group"
                style="margin-top: 1rem;"
              >
                <input
                  v-model="customExamBoard"
                  type="text"
                  class="form-input"
                  placeholder="Enter exam board name"
                >
              </div>
            </div>

            <!-- Student Path: Step 7 - Subjects -->
            <div
              v-if="currentKey === 'student_subjects'"
              class="form-group"
            >
              <label class="form-label">Select your subjects ({{ formData.student_profile.subjects.length }} selected)</label>
              
              <!-- Search input -->
              <input
                v-model="subjectQuery"
                type="text"
                class="form-input"
                placeholder="Search subjects..."
                style="margin-bottom: 1rem;"
              >
              
              <!-- Selected subjects -->
              <div
                v-if="formData.student_profile.subjects.length > 0"
                class="chip-container"
                style="margin-bottom: 1rem; padding: 0.75rem; background: var(--bg-secondary); border-radius: 0.5rem;"
              >
                <div
                  v-for="(subject, index) in formData.student_profile.subjects"
                  :key="'selected-' + index"
                  class="chip"
                >
                  {{ subject }}
                  <button
                    type="button"
                    class="chip-remove"
                    aria-label="Remove subject"
                    @click="removeSubject(index)"
                  >
                    ×
                  </button>
                </div>
              </div>
              
              <!-- Available subjects as chips -->
              <div class="suggestions-grid">
                <button
                  v-for="subject in filteredSubjects"
                  :key="subject"
                  :class="['suggestion-chip', { active: formData.student_profile.subjects.includes(subject) }]"
                  :aria-pressed="formData.student_profile.subjects.includes(subject)"
                  tabindex="0"
                  @click="toggleSubject(subject)"
                  @keydown.enter.prevent="toggleSubject(subject)"
                  @keydown.space.prevent="toggleSubject(subject)"
                >
                  {{ subject }}
                </button>
              </div>
              
              <!-- Custom subject input -->
              <div class="add-custom-subject">
                <button
                  v-if="!showCustomSubjectInput"
                  type="button"
                  class="btn-link"
                  @click="showCustomSubjectInput = true"
                >
                  + Add Custom Subject
                </button>
                <div
                  v-else
                  class="custom-subject-input"
                >
                  <input
                    v-model="customSubject"
                    type="text"
                    class="form-input"
                    placeholder="Enter subject name"
                    @keyup.enter="addCustomSubject"
                  >
                  <button
                    type="button"
                    class="btn-secondary"
                    @click="addCustomSubject"
                  >
                    Add
                  </button>
                </div>
              </div>
            </div>

            <!-- Student Path: Step 8 - Learning Goals -->
            <div
              v-if="currentKey === 'student_goals'"
              class="form-group"
            >
              <label class="form-label">What are your learning goals?</label>
              <div class="goals-grid">
                <div
                  v-for="goal in ['Revision for exams', 'Improving grades', 'Understanding concepts better', 'Preparing for specific exams', 'Homework help', 'General knowledge']"
                  :key="goal"
                  :class="['goal-checkbox', { active: formData.student_profile.learning_goals.includes(goal) }]"
                  role="checkbox"
                  :aria-checked="formData.student_profile.learning_goals.includes(goal)"
                  tabindex="0"
                  @click="toggleLearningGoal(goal)"
                  @keydown.enter.prevent="toggleLearningGoal(goal)"
                  @keydown.space.prevent="toggleLearningGoal(goal)"
                >
                  <input
                    v-model="formData.student_profile.learning_goals"
                    type="checkbox"
                    :value="goal"
                    style="position: absolute; opacity: 0; pointer-events: none;"
                  >
                  <span>{{ goal }}</span>
                </div>
              </div>
            </div>

            <!-- Educator Path: Step 4 - Subjects Taught -->
            <div
              v-if="currentKey === 'educator_subjects'"
              class="form-group"
            >
              <label class="form-label">Which subjects do you teach? ({{ formData.educator_profile.subjects_taught.length }} selected)</label>
              <div class="subjects-grid">
                <label
                  v-for="subject in subjectSuggestions"
                  :key="subject.name"
                  class="subject-checkbox"
                >
                  <input
                    v-model="formData.educator_profile.subjects_taught"
                    type="checkbox"
                    :value="subject.name"
                  >
                  <span>{{ subject.name }}</span>
                </label>
              </div>
            </div>

            <!-- Educator Path: Step 5 - Stages Covered -->
            <div
              v-if="currentKey === 'educator_stages'"
              class="option-grid"
            >
              <button
                v-for="stage in ['KS3', 'IGCSE', 'A-Level', 'IB', 'AP', 'College', 'University']"
                :key="stage"
                :class="['stage-btn', { active: formData.educator_profile.stages_covered.includes(stage) }]"
                @click="toggleEducatorStage(stage)"
              >
                {{ stage }}
              </button>
            </div>

            <!-- Educator Path: Step 6 - Exam Boards Covered -->
            <div
              v-if="currentKey === 'educator_exam_boards'"
              class="form-group"
            >
              <label class="form-label">Which exam boards do you cover?</label>
              <div class="suggestions-grid">
                <button
                  v-for="suggestion in examBoardSuggestions"
                  :key="suggestion.name"
                  :class="['suggestion-chip', { active: formData.educator_profile.exam_boards_covered.includes(suggestion.name) }]"
                  :title="suggestion.description"
                  @click="toggleEducatorExamBoard(suggestion.name)"
                >
                  {{ suggestion.name }}
                </button>
              </div>
            </div>

            <!-- Educator Path: Step 7 - Use Cases -->
            <div
              v-if="currentKey === 'educator_use_cases'"
              class="form-group"
            >
              <label class="form-label">What will you use Learnify for?</label>
              <div class="use-cases-grid">
                <label
                  v-for="useCase in ['Lesson creation', 'Student analytics', 'Resource generation', 'Assessment creation', 'Homework assignments']"
                  :key="useCase"
                  class="use-case-checkbox"
                >
                  <input
                    v-model="formData.educator_profile.use_cases"
                    type="checkbox"
                    :value="useCase"
                  >
                  <span>{{ useCase }}</span>
                </label>
              </div>
            </div>

            <!-- Educator Path: Step 9 - Class Size (Optional) -->
            <div
              v-if="currentKey === 'educator_class_size'"
              class="form-group"
            >
              <label class="form-label">Average Class Size (Optional)</label>
              <div class="class-size-grid">
                <button
                  v-for="range in ['1-10', '11-20', '21-30', '31-40', '40+']"
                  :key="range"
                  :class="['class-size-btn', { active: formData.educator_profile.class_size === range }]"
                  @click="formData.educator_profile.class_size = range"
                >
                  {{ range }}
                </button>
              </div>
            </div>

            <!-- Student Path: Step 10 - Course/Program (College/University only) -->
            <div
              v-if="currentKey === 'student_course' && (formData.student_profile.study_stage === 'College' || formData.student_profile.study_stage === 'University')"
              class="form-group"
            >
              <label class="form-label">Course or Program</label>
              <div class="input-with-suggestions">
                <input
                  v-model="formData.student_profile.course_name"
                  type="text"
                  class="form-input"
                  placeholder="e.g., Computer Science, Business Administration"
                  @input="onCourseNameInput"
                >
                <div
                  v-if="courseSuggestionsLoading"
                  class="loading-badge"
                >
                  Loading...
                </div>
              </div>
              <div
                v-if="courseSuggestions.length > 0"
                class="suggestions-grid"
              >
                <button
                  v-for="suggestion in courseSuggestions"
                  :key="suggestion.name"
                  type="button"
                  class="suggestion-chip"
                  @click="selectCourseSuggestion(suggestion)"
                >
                  {{ suggestion.name }}
                </button>
              </div>
            </div>

            <!-- Student Path: Step 11 - Institution (College/University only) -->
            <div
              v-if="currentKey === 'student_institution' && (formData.student_profile.study_stage === 'College' || formData.student_profile.study_stage === 'University')"
              class="form-group"
            >
              <label class="form-label">Institution/University</label>
              <div class="input-with-suggestions">
                <input
                  v-model="formData.student_profile.institution_name"
                  type="text"
                  class="form-input"
                  placeholder="e.g., Harvard University, MIT"
                  @input="onInstitutionInput"
                >
                <div
                  v-if="institutionSuggestionsLoading"
                  class="loading-badge"
                >
                  Loading...
                </div>
              </div>
              <div
                v-if="institutionSuggestions.length > 0"
                class="suggestions-grid"
              >
                <button
                  v-for="suggestion in institutionSuggestions"
                  :key="suggestion.name"
                  type="button"
                  class="suggestion-chip"
                  @click="selectInstitutionSuggestion(suggestion, false)"
                >
                  {{ suggestion.name }}
                </button>
              </div>
            </div>

            <!-- Educator Path: Updated Step 8 - Institution with AI Suggestions -->
            <div
              v-if="currentKey === 'educator_institution'"
              class="form-group"
            >
              <label class="form-label">Institution Name (Optional)</label>
              <div class="input-with-suggestions">
                <input
                  v-model="formData.educator_profile.institution_name"
                  type="text"
                  class="form-input"
                  placeholder="Enter your school or institution name"
                  @input="onInstitutionInput"
                >
                <div
                  v-if="institutionSuggestionsLoading"
                  class="loading-badge"
                >
                  Loading...
                </div>
              </div>
              <div
                v-if="institutionSuggestions.length > 0"
                class="suggestions-grid"
              >
                <button
                  v-for="suggestion in institutionSuggestions"
                  :key="suggestion.name"
                  type="button"
                  class="suggestion-chip"
                  @click="selectInstitutionSuggestion(suggestion, true)"
                >
                  {{ suggestion.name }}
                </button>
              </div>
            </div>

            <!-- Optional Steps (Final steps for both paths) -->
            <!-- User Intent (only for students as an optional step) -->
            <div
              v-if="currentKey === 'intent'"
              class="form-group"
            >
              <label class="form-label">What's your main intent? (Optional)</label>
              <div class="intent-grid">
                <label
                  v-for="intent in ['Exam preparation', 'Daily learning', 'Teaching aid', 'Content generation', 'Research']"
                  :key="intent"
                  class="intent-radio"
                >
                  <input
                    v-model="formData.user_intent"
                    type="radio"
                    :value="intent"
                  >
                  <span>{{ intent }}</span>
                </label>
              </div>
            </div>

            <!-- Error Message -->
            <div
              v-if="error"
              class="alert alert-error"
            >
              {{ error }}
            </div>
          </div>

          <!-- Navigation Buttons -->
          <div class="navigation-buttons">
            <button
              v-if="canGoBack"
              type="button"
              class="btn btn-secondary"
              @click="goToPreviousStep"
            >
              ← Back
            </button>

            <button
              v-if="canSkip"
              type="button"
              class="btn btn-ghost"
              @click="skipCurrentStep"
            >
              Skip
            </button>

            <button
              v-if="currentStep < totalSteps"
              type="button"
              :disabled="!canContinue"
              class="btn btn-primary"
              @click="goToNextStep"
            >
              Continue →
            </button>

            <button
              v-if="currentStep === totalSteps"
              type="button"
              :disabled="loading"
              class="btn btn-primary"
              @click="submitOnboarding"
            >
              {{ loading ? 'Finishing...' : 'Finish' }}
            </button>
          </div>
        </div>

        <!-- Success State -->
        <div
          v-else
          :key="'success'"
          class="success-state"
        >
          <div class="success-checkmark">
            <svg
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
            >
              <polyline points="20 6 9 17 4 12" />
            </svg>
          </div>
          <h2 class="success-title">
            Welcome to Learnify! 🎉
          </h2>
          <p class="success-message">
            {{ successMessage }}
          </p>
          <div class="spinner" />
          <p class="loading-text">
            Setting up your personalized experience...
          </p>
        </div>
      </Transition>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import api from '../services/api'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

// State Management
const currentIndex = ref(0)
const direction = ref('forward')
const loading = ref(false)
const loadingMessage = ref('Loading...')
const error = ref(null)
const showSuccess = ref(false)
const successMessage = ref('')
const aiSuggestionsCache = ref({})

// UI State
const showCustomSubjectInput = ref(false)
const customSubject = ref('')
const customExamBoard = ref('')
const customStudyStage = ref('')
const subjectQuery = ref('')

// Canonical subjects list covering secondary and university subjects
const CANONICAL_SUBJECTS = [
  'Mathematics', 'English', 'English Literature', 'Biology', 'Chemistry', 'Physics',
  'History', 'Geography', 'Computer Science', 'Economics', 'Business Studies',
  'Psychology', 'Sociology', 'Art', 'Music', 'Drama', 'Theatre Studies',
  'Physical Education', 'French', 'Spanish', 'German', 'Mandarin', 'Latin',
  'Religious Studies', 'Philosophy', 'Politics', 'Law', 'Engineering',
  'Medicine', 'Accounting', 'Finance', 'Literature', 'Creative Writing',
  'Environmental Science', 'Media Studies', 'Film Studies', 'Design Technology',
  'Food Technology', 'Statistics', 'Further Mathematics', 'Italian', 'Portuguese',
  'Arabic', 'Japanese', 'Anthropology', 'Archaeology', 'Architecture',
  'Astronomy', 'Biochemistry', 'Biotechnology', 'Classics', 'Data Science',
  'Earth Sciences', 'Electronics', 'Graphic Design', 'Health Sciences',
  'Information Technology', 'Journalism', 'Linguistics', 'Marketing',
  'Neuroscience', 'Nursing', 'Pharmacy', 'Photography', 'Political Science',
  'Public Health', 'Social Work', 'Sports Science', 'Urban Planning'
]

// Loading flags for AI suggestions (per-type)
const examBoardLoading = ref(false)
// Removed unused loading flags per Comment 12 (no global loading during suggestion fetches)

// Comment 19: Detect prefers-reduced-motion for accessibility
const prefersReducedMotion = computed(() => {
  return window.matchMedia('(prefers-reduced-motion: reduce)').matches
})

// Suggestions
const subjectSuggestions = ref([])
const examBoardSuggestions = ref([])
const courseSuggestions = ref([])
const institutionSuggestions = ref([])
const courseSuggestionsLoading = ref(false)
const institutionSuggestionsLoading = ref(false)
let courseDebounceTimer = null
let institutionDebounceTimer = null

// Form Data
const formData = ref({
  date_of_birth: '',
  user_type: '',
  timezone: 'UTC',
  language_preference: 'en',
  student_profile: {
    year_level: '',
    study_stage: '',
    course_name: '',
    institution_name: '',
    exam_board: '',
    subjects: [],
    learning_goals: []
  },
  educator_profile: {
    subjects_taught: [],
    stages_covered: [],
    exam_boards_covered: [],
    use_cases: [],
    institution_name: '',
    class_size: null
  },
  user_intent: '',
})

// Computed Properties
const isStudentPath = computed(() => formData.value.user_type === 'student')
const isEducatorPath = computed(() => formData.value.user_type === 'educator')

// Helper function to derive country code from browser locale
const getCountryCode = () => {
  try {
    const lang = navigator.language || 'en-US'
    const parts = lang.split('-')
    return parts.length > 1 ? parts[1].toUpperCase() : 'US'
  } catch {
    return 'US'
  }
}

// Build step flow array based on user type
const stepFlow = computed(() => {
  const flow = ['dob', 'role', 'prefs']
  
  if (!formData.value.user_type) {
    return flow
  }
  
  if (isStudentPath.value) {
    flow.push('student_year', 'student_stage', 'student_exam_board', 'student_subjects', 'student_goals')
    
    // Conditional steps for College/University
    if (formData.value.student_profile.study_stage === 'College' || 
        formData.value.student_profile.study_stage === 'University') {
      flow.push('student_course', 'student_institution')
    }
    
    // Optional steps
    flow.push('intent')
  } else if (isEducatorPath.value) {
    flow.push('educator_subjects', 'educator_stages', 'educator_exam_boards', 'educator_use_cases', 'educator_institution', 'educator_class_size')
  }
  
  return flow
})

// Current step key and index
const currentKey = computed(() => stepFlow.value[currentIndex.value] || null)
const currentStep = computed(() => currentIndex.value + 1)
const totalSteps = computed(() => stepFlow.value.length)

const progressPercentage = computed(() => {
  return (currentStep.value / totalSteps.value) * 100
})

const canGoBack = computed(() => currentIndex.value > 0)

// Step configuration for headers
const stepHeaders = {
  dob: { emoji: '🎂', title: 'Date of Birth', subtitle: 'We use this to personalize your experience' },
  role: { emoji: '👤', title: 'Who are you?', subtitle: 'Choose your role to get started' },
  prefs: { emoji: '🌍', title: 'Preferences', subtitle: 'We auto-detected your timezone and language' },
  student_year: { emoji: '📚', title: 'Year Level', subtitle: 'What year level are you in?' },
  student_stage: { emoji: '🎓', title: 'Study Stage', subtitle: 'What exam stage are you in?' },
  student_exam_board: { emoji: '🏢', title: 'Exam Board', subtitle: 'Select your exam board' },
  student_subjects: { emoji: '📖', title: 'Subjects', subtitle: 'Select your subjects' },
  student_goals: { emoji: '�', title: 'Learning Goals', subtitle: 'What do you want to achieve?' },
  student_style: { emoji: '🧠', title: 'Learning Style', subtitle: 'How do you prefer to learn?' },
  student_course: { emoji: '�', title: 'Course or Program', subtitle: 'What is your course?' },
  student_institution: { emoji: '🏫', title: 'Institution/University', subtitle: 'Where do you study?' },
  educator_subjects: { emoji: '�', title: 'Subjects Taught', subtitle: 'Which subjects do you teach?' },
  educator_stages: { emoji: '�', title: 'Stages Covered', subtitle: 'Which stages do you teach?' },
  educator_exam_boards: { emoji: '�', title: 'Exam Boards', subtitle: 'Which exam boards do you work with?' },
  educator_use_cases: { emoji: '💼', title: 'Use Cases', subtitle: 'How will you use Learnify?' },
  educator_institution: { emoji: '🏫', title: 'Institution', subtitle: 'Where do you teach? (Optional)' },
  educator_class_size: { emoji: '👥', title: 'Class Size', subtitle: 'How many students do you teach? (Optional)' },
  intent: { emoji: '🎯', title: 'Your Intent', subtitle: 'What is your main goal? (Optional)' }
}

const currentQuestion = computed(() => {
  return stepHeaders[currentKey.value] || null
})

const canContinue = computed(() => {
  const key = currentKey.value
  
  // Validate by step key
  switch (key) {
    case 'dob':
      return formData.value.date_of_birth && isValidAge()
    case 'role':
      return formData.value.user_type !== ''
    case 'prefs':
      return formData.value.timezone && formData.value.language_preference
    case 'student_year':
      return formData.value.student_profile.year_level !== ''
    case 'student_stage':
      // If "Other" is selected, require customStudyStage to be filled
      if (formData.value.student_profile.study_stage === 'Other') {
        return customStudyStage.value.trim() !== ''
      }
      return formData.value.student_profile.study_stage !== ''
    case 'student_exam_board':
      // If "Other" is selected, require customExamBoard to be filled
      if (formData.value.student_profile.exam_board === 'Other') {
        return customExamBoard.value.trim() !== ''
      }
      return formData.value.student_profile.exam_board !== ''
    case 'student_subjects':
      return formData.value.student_profile.subjects.length > 0
    case 'student_goals':
      return formData.value.student_profile.learning_goals.length > 0
    case 'student_course':
      return formData.value.student_profile.course_name !== ''
    case 'student_institution':
      return formData.value.student_profile.institution_name !== ''
    case 'educator_subjects':
      return formData.value.educator_profile.subjects_taught.length > 0
    case 'educator_stages':
      return formData.value.educator_profile.stages_covered.length > 0
    case 'educator_exam_boards':
      return formData.value.educator_profile.exam_boards_covered.length > 0
    case 'educator_use_cases':
      return formData.value.educator_profile.use_cases.length > 0
    // Optional steps always allow continue
    default:
      return true
  }
})

const canSkip = computed(() => {
  const key = currentKey.value
  // Optional educator steps
  if (key === 'educator_institution' || key === 'educator_class_size') return true
  // Optional student conditional steps (course/institution)
  if (key === 'student_course' || key === 'student_institution') return true
  // Optional final steps
  if (key === 'intent') return true
  return false
})

// Computed property for filtered subjects based on search query
const filteredSubjects = computed(() => {
  // Merge canonical subjects with AI suggestions
  const allSubjects = [...new Set([...CANONICAL_SUBJECTS, ...subjectSuggestions.value.map(s => typeof s === 'string' ? s : s.name)])]
  
  if (!subjectQuery.value || subjectQuery.value.trim() === '') {
    return allSubjects.sort()
  }
  
  const query = subjectQuery.value.toLowerCase().trim()
  return allSubjects.filter(subject => 
    subject.toLowerCase().includes(query)
  ).sort()
})

// Computed property to detect if "Other" is selected for study stage
const isStudyStageOther = computed(() => {
  return formData.value.student_profile.study_stage === 'Other'
})

// Methods
const autoDetectSettings = () => {
  try {
    // Detect timezone
    formData.value.timezone = Intl.DateTimeFormat().resolvedOptions().timeZone
  } catch {
    formData.value.timezone = 'UTC'
  }

  try {
    // Detect language
    const lang = navigator.language || navigator.userLanguage || 'en'
    formData.value.language_preference = lang.split('-')[0]
  } catch {
    formData.value.language_preference = 'en'
  }
}

const calculateAge = () => {
  if (!formData.value.date_of_birth) return null
  // Comment 22: Parse as UTC to prevent timezone-based date shifts
  const birthDate = new Date(formData.value.date_of_birth + 'T00:00:00Z')
  const today = new Date()
  let age = today.getFullYear() - birthDate.getFullYear()
  const monthDiff = today.getMonth() - birthDate.getMonth()
  if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
    age--
  }
  return age
}

const isValidAge = () => {
  const age = calculateAge()
  return age !== null && age >= 5 && age <= 120
}

const fetchAISuggestions = async (type, context) => {
  // Comment 15: Sort context keys to ensure cache hits even if key order differs
  const sortedContext = Object.fromEntries(Object.entries(context).sort())
  const cacheKey = type + JSON.stringify(sortedContext)
  if (aiSuggestionsCache.value[cacheKey]) {
    return aiSuggestionsCache.value[cacheKey]
  }

  // Comment 9: Use specific loading state, not global
  loadingMessage.value = 'Loading suggestions...'

  try {
    const response = await api.post('/onboarding/ai-suggestions', {
      suggestion_type: type,
      context,
      max_suggestions: 10
    })

    const suggestions = response.data.suggestions || []
    aiSuggestionsCache.value[cacheKey] = suggestions
    return suggestions
  } catch (err) {
    console.error('Error fetching AI suggestions:', err)
    error.value = 'Failed to load suggestions. Please try again.'
    return []
  }
}

const handleStudyStageSelection = async (stage) => {
  if (stage === 'Other') {
    formData.value.student_profile.study_stage = 'Other'
    // Don't fetch exam boards for Other, wait for custom input
    return
  }
  
  formData.value.student_profile.study_stage = stage

  // Fetch exam board suggestions with country from browser locale
  try {
    examBoardLoading.value = true
    const country = getCountryCode()
    const suggestions = await fetchAISuggestions('exam_boards', {
      stage,
      country
    })

    examBoardSuggestions.value = suggestions.map((s) => ({
      name: typeof s === 'string' ? s : s.name || s,
      description: typeof s === 'object' ? s.description || '' : ''
    }))
  } catch (err) {
    console.error('Error loading exam boards:', err)
  } finally {
    examBoardLoading.value = false
  }
}

const selectExamBoard = (board) => {
  formData.value.student_profile.exam_board = board
  if (board !== 'Other') {
    customExamBoard.value = '' // Clear custom input if switching away from Other
  }
}

const toggleSubject = (subject) => {
  const idx = formData.value.student_profile.subjects.indexOf(subject)
  if (idx > -1) {
    formData.value.student_profile.subjects.splice(idx, 1)
  } else {
    formData.value.student_profile.subjects.push(subject)
  }
}

const removeSubject = (index) => {
  formData.value.student_profile.subjects.splice(index, 1)
}

const toggleLearningGoal = (goal) => {
  const idx = formData.value.student_profile.learning_goals.indexOf(goal)
  if (idx > -1) {
    formData.value.student_profile.learning_goals.splice(idx, 1)
  } else {
    formData.value.student_profile.learning_goals.push(goal)
  }
}

const toggleEducatorStage = (stage) => {
  const idx = formData.value.educator_profile.stages_covered.indexOf(stage)
  if (idx > -1) {
    formData.value.educator_profile.stages_covered.splice(idx, 1)
  } else {
    formData.value.educator_profile.stages_covered.push(stage)
  }
}

const toggleEducatorExamBoard = (board) => {
  const idx = formData.value.educator_profile.exam_boards_covered.indexOf(board)
  if (idx > -1) {
    formData.value.educator_profile.exam_boards_covered.splice(idx, 1)
  } else {
    formData.value.educator_profile.exam_boards_covered.push(board)
  }
}

const addCustomSubject = () => {
  if (customSubject.value.trim()) {
    formData.value.student_profile.subjects.push(customSubject.value.trim())
    customSubject.value = ''
    showCustomSubjectInput.value = false
  }
}

const onCourseNameInput = (event) => {
  const query = event.target.value
  
  // Clear existing timer
  if (courseDebounceTimer) {
    clearTimeout(courseDebounceTimer)
  }
  
  if (query.length < 2) {
    courseSuggestions.value = []
    return
  }
  
  courseSuggestionsLoading.value = true
  courseDebounceTimer = setTimeout(async () => {
    try {
      const suggestions = await fetchAISuggestions('courses', {
        stage: formData.value.student_profile.study_stage,
        country: 'worldwide'
      })
      courseSuggestions.value = suggestions.map((s) => ({
        name: typeof s === 'string' ? s : s.name || s
      }))
    } catch (err) {
      console.error('Error loading course suggestions:', err)
      courseSuggestions.value = []
    } finally {
      courseSuggestionsLoading.value = false
    }
  }, 300)
}

const selectCourseSuggestion = (suggestion) => {
  formData.value.student_profile.course_name = suggestion.name
  courseSuggestions.value = []
}

const onInstitutionInput = (event) => {
  const query = event.target.value
  
  // Clear existing timer
  if (institutionDebounceTimer) {
    clearTimeout(institutionDebounceTimer)
  }
  
  if (query.length < 2) {
    institutionSuggestions.value = []
    return
  }
  
  institutionSuggestionsLoading.value = true
  institutionDebounceTimer = setTimeout(async () => {
    try {
      const context = isStudentPath.value
        ? {
            stage: formData.value.student_profile.study_stage,
            country: 'worldwide',
            course_name: formData.value.student_profile.course_name
          }
        : {
            user_type: 'educator'
          }
      
      const suggestions = await fetchAISuggestions('institutions', context)
      institutionSuggestions.value = suggestions.map((s) => ({
        name: typeof s === 'string' ? s : s.name || s
      }))
    } catch (err) {
      console.error('Error loading institution suggestions:', err)
      institutionSuggestions.value = []
    } finally {
      institutionSuggestionsLoading.value = false
    }
  }, 300)
}

const selectInstitutionSuggestion = (suggestion, isEducator = false) => {
  if (isEducator) {
    formData.value.educator_profile.institution_name = suggestion.name
  } else {
    formData.value.student_profile.institution_name = suggestion.name
  }
  institutionSuggestions.value = []
}

const goToNextStep = async () => {
  error.value = null
  direction.value = 'forward'

  const key = currentKey.value

  // Handle custom study stage persistence
  if (key === 'student_stage' && formData.value.student_profile.study_stage === 'Other' && customStudyStage.value.trim()) {
    formData.value.student_profile.study_stage = customStudyStage.value.trim()
    customStudyStage.value = ''
  }

  // Handle custom exam board persistence
  if (key === 'student_exam_board' && formData.value.student_profile.exam_board === 'Other' && customExamBoard.value.trim()) {
    formData.value.student_profile.exam_board = customExamBoard.value.trim()
    customExamBoard.value = ''
  }

  if (currentIndex.value < totalSteps.value - 1) {
    currentIndex.value++
    // Smooth scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' })
  } else {
    await submitOnboarding()
  }
}

const goToPreviousStep = () => {
  error.value = null
  direction.value = 'backward'
  if (currentIndex.value > 0) {
    currentIndex.value--
    // Smooth scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }
}

const skipCurrentStep = () => {
  error.value = null
  direction.value = 'forward'
  const key = currentKey.value
  
  // Clear data for skipped optional steps
  switch (key) {
    case 'student_course':
      formData.value.student_profile.course_name = ''
      break
    case 'student_institution':
      formData.value.student_profile.institution_name = ''
      break
    case 'educator_institution':
      formData.value.educator_profile.institution_name = ''
      break
    case 'educator_class_size':
      formData.value.educator_profile.class_size = null
      break
    case 'intent':
      formData.value.user_intent = ''
      break
  }
  
  if (currentIndex.value < totalSteps.value - 1) {
    currentIndex.value++
    // Smooth scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }
}

const submitOnboarding = async () => {
  loading.value = true
  loadingMessage.value = 'Saving your profile...'
  showSuccess.value = true
  successMessage.value = 'Your profile is being set up...'

  try {
    // Prepare payload - remove empty nested objects
    const payload = {
      date_of_birth: formData.value.date_of_birth,
      user_type: formData.value.user_type,
      timezone: formData.value.timezone,
      language_preference: formData.value.language_preference
    }

    // Only include optional fields if they have non-empty values
    if (formData.value.user_intent && formData.value.user_intent.trim()) {
      payload.user_intent = formData.value.user_intent
    }

    // Add path-specific data
    if (isStudentPath.value) {
      payload.student_profile = formData.value.student_profile
    }
    if (isEducatorPath.value) {
      payload.educator_profile = formData.value.educator_profile
    }

    // Submit to backend
    console.log('Submitting onboarding payload:', JSON.stringify(payload, null, 2))
    await api.post('/onboarding/profile', payload)

    successMessage.value = 'Welcome! Setting up your experience...'

    // Mark onboarding as complete in auth store
    authStore.markOnboardingComplete()

    // Wait for success animation
    setTimeout(() => {
      // Check for redirect destination or go to home
      const redirect = route.query.redirect || '/'
      router.push(redirect)
    }, 1500)
  } catch (err) {
    console.error('Error submitting onboarding:', err)
    console.error('Response data:', err.response?.data)
    console.error('Request payload:', err.config?.data)
    loading.value = false
    showSuccess.value = false

    let errorMessage = 'Failed to save profile'
    if (err.response) {
      errorMessage = err.response.data?.detail || `Server error: ${err.response.status}`
    } else if (err.request) {
      errorMessage = 'Cannot connect to server. Please check if the backend is running.'
    } else {
      errorMessage = err.message || 'Failed to save profile'
    }

    error.value = errorMessage
  }
}

// Lifecycle hooks
onMounted(() => {
  autoDetectSettings()

  // Load initial subject suggestions
  if (isStudentPath.value) {
    fetchAISuggestions('subjects', { default: true })
      .then((suggestions) => {
        subjectSuggestions.value = suggestions.map((s) => ({
          name: typeof s === 'string' ? s : s.name || s
        }))
      })
      .catch((err) => {
        console.error('Error loading initial subjects:', err)
      })
  }

  if (isEducatorPath.value) {
    fetchAISuggestions('subjects', { user_type: 'educator' })
      .then((suggestions) => {
        subjectSuggestions.value = suggestions.map((s) => ({
          name: typeof s === 'string' ? s : s.name || s
        }))
      })
      .catch((err) => {
        console.error('Error loading initial subjects:', err)
      })
  }
})

onBeforeUnmount(() => {
  // Clear debounce timers to prevent memory leaks
  if (courseDebounceTimer) {
    clearTimeout(courseDebounceTimer)
    courseDebounceTimer = null
  }
  if (institutionDebounceTimer) {
    clearTimeout(institutionDebounceTimer)
    institutionDebounceTimer = null
  }
})

// Watch for step changes to prefetch suggestions
watch(currentStep, async (newStep, oldStep) => {
  if (isStudentPath.value && newStep === 5 && oldStep === 4) {
    // Study stage selection, will be handled in handleStudyStageSelection
  }
})

// Watch study_stage to clear conditional fields when changing away from College/University
watch(() => formData.value.student_profile.study_stage, (newStage, oldStage) => {
  if (oldStage && (oldStage === 'College' || oldStage === 'University') && 
      newStage !== 'College' && newStage !== 'University') {
    // Clear course/institution fields
    formData.value.student_profile.course_name = ''
    formData.value.student_profile.institution_name = ''
  }
  
  // Clear custom fields when switching away from Other
  if (oldStage === 'Other' && newStage !== 'Other') {
    customStudyStage.value = ''
  }
})

// Watch exam_board to clear customExamBoard when switching away from Other
watch(() => formData.value.student_profile.exam_board, (newBoard, oldBoard) => {
  if (oldBoard === 'Other' && newBoard !== 'Other') {
    customExamBoard.value = ''
  }
})

// Comment 8: Watch stepFlow changes to reset currentIndex if out of bounds
// and clear College/University-specific fields when leaving those stages
watch(stepFlow, (newFlow, oldFlow) => {
  // Reset currentIndex if it exceeds the new flow length
  if (currentIndex.value >= newFlow.length) {
    currentIndex.value = Math.min(currentIndex.value, newFlow.length - 1)
  }

  // Clear course/institution fields if study_stage changes away from College/University
  const hadCourseStep = oldFlow.includes('student_course')
  const hasCourseStep = newFlow.includes('student_course')
  
  if (hadCourseStep && !hasCourseStep) {
    formData.value.student_profile.course_name = ''
    formData.value.student_profile.institution_name = ''
  }
}, { deep: true })
</script>

<style scoped>
.onboarding-view {
  min-height: 100vh;
  background: linear-gradient(135deg, var(--bg-primary) 0%, var(--bg-secondary) 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem 1rem;
  position: relative;
}

.onboarding-container {
  width: 100%;
  max-width: 800px;
  position: relative;
}

/* Progress Bar */
.progress-bar-container {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: rgba(119, 51, 255, 0.1);
  z-index: 100;
}

.progress-bar {
  height: 100%;
  background: linear-gradient(90deg, var(--accent-primary), var(--accent-secondary));
  width: 0;
  transition: width 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.progress-text {
  position: fixed;
  top: 0.5rem;
  right: 1.5rem;
  font-size: 0.75rem;
  color: var(--text-muted);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  z-index: 101;
}

/* Question Card */
.question-card {
  margin-top: 2rem;
  position: relative;
  animation: slideIn 0.4s ease-out;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.question-badge {
  position: absolute;
  top: 1.5rem;
  right: 1.5rem;
  background: var(--accent-primary);
  color: white;
  padding: 0.4rem 0.8rem;
  border-radius: 2rem;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
}

.question-header {
  margin-bottom: 2rem;
  padding-top: 1rem;
}

.question-title {
  font-size: 2rem;
  margin-bottom: 0.5rem;
  color: var(--text-primary);
  font-weight: 700;
  background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.question-subtitle {
  color: var(--text-secondary);
  font-size: 1rem;
  margin-bottom: 0;
}

.question-content {
  margin-bottom: 2rem;
}

/* Loading State */
.loading-state {
  text-align: center;
  padding: 2rem;
}

.loading-text {
  margin-top: 1rem;
  color: var(--text-secondary);
}

/* Auto-Detection Form */
.auto-detection-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.detection-item {
  display: flex;
  flex-direction: column;
}

.detection-display {
  padding: 0.75rem 1rem;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 0.5rem;
  margin-bottom: 0.5rem;
  font-size: 0.95rem;
  color: var(--accent-primary);
  font-weight: 500;
}

/* Option Grid */
.option-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 1rem;
  margin-bottom: 1rem;
}

.option-card {
  padding: 1.5rem;
  background: var(--bg-secondary);
  border: 2px solid var(--border-color);
  border-radius: 1rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  min-height: 140px;
}

.option-card:hover {
  border-color: var(--accent-primary);
  transform: translateY(-2px);
}

.option-card.active {
  background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
  color: white;
  border-color: var(--accent-primary);
}

.option-icon {
  font-size: 2.5rem;
}

.option-title {
  font-weight: 600;
  font-size: 1.1rem;
}

.option-description {
  font-size: 0.85rem;
  opacity: 0.8;
}

/* Study Stage Buttons */
.stage-btn {
  padding: 0.75rem 1.5rem;
  background: var(--bg-secondary);
  color: var(--text-primary);
  border: 2px solid var(--border-color);
  border-radius: 0.75rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.stage-btn:hover {
  border-color: var(--accent-primary);
  transform: translateY(-2px);
}

.stage-btn.active {
  background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
  color: white;
  border-color: var(--accent-primary);
}

/* Suggestions Grid */
.suggestions-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.suggestion-chip {
  padding: 0.6rem 1.2rem;
  background: var(--bg-secondary);
  color: var(--text-primary);
  border: 1px solid var(--border-color);
  border-radius: 2rem;
  font-size: 0.95rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.suggestion-chip:hover {
  border-color: var(--accent-primary);
}

.suggestion-chip.active {
  background: var(--accent-primary);
  color: white;
  border-color: var(--accent-primary);
}

/* Subjects Grid */
.subjects-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.subject-checkbox,
.goal-checkbox,
.intent-radio,
.use-case-checkbox {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.subject-checkbox:hover,
.goal-checkbox:hover,
.intent-radio:hover,
.use-case-checkbox:hover {
  border-color: var(--accent-primary);
  background: var(--bg-tertiary);
}

.subject-checkbox input,
.goal-checkbox input,
.intent-radio input,
.use-case-checkbox input {
  cursor: pointer;
}

.subject-checkbox input:checked + span,
.goal-checkbox input:checked + span,
.intent-radio input:checked + span,
.use-case-checkbox input:checked + span {
  color: var(--accent-primary);
  font-weight: 600;
}

/* Custom Subject Input */
.add-custom-subject {
  margin-top: 1rem;
}

.custom-subject-input {
  display: flex;
  gap: 0.5rem;
  margin-top: 0.5rem;
}

.custom-subject-input .form-input {
  flex: 1;
}

/* Chip container for selected subjects */
.chip-container {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  min-height: 2rem;
}

.chip {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.75rem;
  background: var(--accent-primary);
  color: white;
  border-radius: 1.5rem;
  font-size: 0.875rem;
  font-weight: 500;
}

.chip-remove {
  background: transparent;
  border: none;
  color: white;
  font-size: 1.25rem;
  line-height: 1;
  cursor: pointer;
  padding: 0;
  margin-left: 0.25rem;
  transition: transform 0.2s;
}

.chip-remove:hover {
  transform: scale(1.2);
}

/* Goals Grid */
.goals-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 0.75rem;
}

/* Learning Style Grid */
.learning-style-grid {
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
}

.learning-style-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  padding: 1.5rem;
}

.style-emoji {
  font-size: 2rem;
}

.style-name {
  font-size: 0.9rem;
  font-weight: 600;
}

/* Tech Level Grid */
.tech-level-grid {
  grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
}

.tech-level-btn {
  padding: 1rem;
  font-weight: 600;
}

/* AI Familiarity Grid */
.ai-familiarity-grid {
  grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
}

.ai-familiarity-btn {
  padding: 1rem;
  font-weight: 600;
}

/* Class Size Grid */
.class-size-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
  gap: 0.75rem;
}

.class-size-btn {
  padding: 0.75rem;
  background: var(--bg-secondary);
  color: var(--text-primary);
  border: 2px solid var(--border-color);
  border-radius: 0.75rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.class-size-btn:hover {
  border-color: var(--accent-primary);
}

.class-size-btn.active {
  background: var(--accent-primary);
  color: white;
  border-color: var(--accent-primary);
}

/* Success State */
.success-state {
  text-align: center;
  padding: 3rem 2rem;
}

.success-checkmark {
  width: 80px;
  height: 80px;
  margin: 0 auto 2rem;
  color: var(--accent-primary);
  animation: scaleIn 0.6s cubic-bezier(0.34, 1.56, 0.64, 1);
}

@keyframes scaleIn {
  from {
    opacity: 0;
    transform: scale(0.3);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

.success-checkmark svg {
  width: 100%;
  height: 100%;
  stroke-width: 2;
}

.success-title {
  font-size: 1.8rem;
  margin-bottom: 1rem;
  color: var(--text-primary);
}

.success-message {
  color: var(--text-secondary);
  margin-bottom: 1.5rem;
}

/* Navigation Buttons */
.navigation-buttons {
  display: flex;
  gap: 1rem;
  justify-content: space-between;
  margin-top: 2rem;
  flex-wrap: wrap;
}

.btn {
  flex: 1;
  min-width: 120px;
}

.btn-ghost {
  background: transparent;
  border: 1px solid var(--border-color);
  color: var(--text-secondary);
}

.btn-ghost:hover {
  background: var(--bg-secondary);
  border-color: var(--accent-primary);
  color: var(--accent-primary);
}

.btn-link {
  background: none;
  border: none;
  color: var(--accent-primary);
  cursor: pointer;
  font-size: 0.95rem;
  text-decoration: underline;
  padding: 0;
  margin-top: 1rem;
}

.btn-link:hover {
  color: var(--accent-secondary);
}

/* Input with Suggestions */
.input-with-suggestions {
  position: relative;
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.input-with-suggestions .form-input {
  flex: 1;
}

.loading-badge {
  padding: 0.4rem 0.8rem;
  background: var(--accent-primary);
  color: white;
  border-radius: 1rem;
  font-size: 0.75rem;
  font-weight: 600;
  white-space: nowrap;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* Transitions */
.slide-fade-enter-active {
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.slide-fade-leave-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.slide-fade-enter-from {
  opacity: 0;
  transform: translateX(30px);
}

.slide-fade-leave-to {
  opacity: 0;
  transform: translateX(-30px);
}

/* Backward direction transitions */
.slide-fade-back-enter-active {
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.slide-fade-back-leave-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.slide-fade-back-enter-from {
  opacity: 0;
  transform: translateX(-30px);
}

.slide-fade-back-leave-to {
  opacity: 0;
  transform: translateX(30px);
}

/* Error Alert */
.alert-error {
  margin-bottom: 1rem;
}

/* Responsive Design */
@media (max-width: 768px) {
  .onboarding-view {
    padding: 1rem;
  }

  .question-card {
    margin-top: 1rem;
  }

  .question-title {
    font-size: 1.5rem;
  }

  .progress-text {
    font-size: 0.65rem;
    top: 0.75rem;
    right: 1rem;
  }

  .option-grid {
    grid-template-columns: 1fr;
  }

  .subjects-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .goals-grid {
    grid-template-columns: 1fr;
  }

  .learning-style-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .navigation-buttons {
    flex-direction: column;
  }

  .btn {
    width: 100%;
  }
}

@media (max-width: 480px) {
  .question-badge {
    top: 1rem;
    right: 1rem;
    font-size: 0.65rem;
    padding: 0.35rem 0.7rem;
  }

  .question-title {
    font-size: 1.25rem;
  }

  .subjects-grid {
    grid-template-columns: 1fr;
  }

  .learning-style-grid {
    grid-template-columns: 1fr;
  }

  .class-size-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

/* GPU Acceleration for animations */
.question-card,
.success-state {
  will-change: transform, opacity;
  transform: translateZ(0);
  backface-visibility: hidden;
}

/* Accessibility */
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}

/* Focus states for accessibility */
.option-card:focus,
.stage-btn:focus,
.suggestion-chip:focus,
.class-size-btn:focus,
.btn:focus {
  outline: 2px solid var(--accent-primary);
  outline-offset: 2px;
}

input[type='checkbox']:focus + span,
input[type='radio']:focus + span {
  outline: 2px solid var(--accent-primary);
  outline-offset: 2px;
}
</style>
