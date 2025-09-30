<template>
  <div class="course-view">
    <div class="container">
      <!-- Loading State -->
      <div v-if="loading" class="loading-state">
        <div class="spinner"></div>
        <p>Loading course...</p>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="alert alert-error">
        {{ error }}
        <button @click="$router.push('/courses')" class="btn btn-secondary mt-2">
          Back to Courses
        </button>
      </div>

      <!-- Course Content -->
      <div v-else-if="course" class="course-content">
        <!-- Course Header -->
        <div class="course-header card">
          <h1 class="course-title">{{ course.course_title }}</h1>
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
        </div>

        <!-- Current Section -->
        <div v-if="currentSection" class="section-card card">
          <div class="section-header">
            <h2 class="section-title">{{ currentSection.section_title }}</h2>
            <div class="section-progress">
              Section {{ currentSectionIndex + 1 }} of {{ course.sections.length }}
            </div>
          </div>

          <!-- Explanation -->
          <div class="section-explanation">
            <p>{{ currentSection.explanation }}</p>
          </div>

          <!-- Quiz Questions -->
          <div v-if="currentSection.quiz && currentSection.quiz.length > 0" class="quiz-section">
            <h3 class="quiz-title">Quiz Time! 🎯</h3>
            
            <div 
              v-for="(question, qIndex) in currentSection.quiz" 
              :key="`q-${qIndex}`"
              class="question-card"
            >
              <QuizQuestion
                :question="question"
                :questionIndex="qIndex"
                :sectionIndex="currentSectionIndex"
                @answer-submitted="handleAnswerSubmit"
              />
            </div>
          </div>

          <!-- Subsections -->
          <div v-if="currentSection.subsections && currentSection.subsections.length > 0" class="subsections">
            <h3 class="subsections-title">Subsections</h3>
            <div 
              v-for="(subsection, subIndex) in currentSection.subsections"
              :key="`sub-${subIndex}`"
              class="subsection-card"
            >
              <h4 class="subsection-title">{{ subsection.section_title }}</h4>
              <p class="subsection-explanation">{{ subsection.explanation }}</p>
              
              <!-- Subsection Quiz -->
              <div v-if="subsection.quiz && subsection.quiz.length > 0" class="quiz-section">
                <div 
                  v-for="(question, qIndex) in subsection.quiz" 
                  :key="`subq-${subIndex}-${qIndex}`"
                  class="question-card"
                >
                  <QuizQuestion
                    :question="question"
                    :questionIndex="qIndex"
                    :sectionIndex="currentSectionIndex"
                    :subsectionIndex="subIndex"
                    @answer-submitted="handleAnswerSubmit"
                  />
                </div>
              </div>
            </div>
          </div>

          <!-- Navigation -->
          <div class="section-navigation">
            <button 
              @click="previousSection"
              :disabled="currentSectionIndex === 0"
              class="btn btn-secondary"
            >
              ⬅️ Previous Section
            </button>
            <button 
              @click="nextSection"
              :disabled="currentSectionIndex >= course.sections.length - 1"
              class="btn btn-primary"
            >
              Next Section ➡️
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useCourseStore } from '../stores/course'
import QuizQuestion from '../components/QuizQuestion.vue'

export default {
  name: 'CourseView',
  components: {
    QuizQuestion
  },
  setup() {
    const route = useRoute()
    const courseStore = useCourseStore()

    const loading = ref(false)
    const error = ref(null)
    const currentSectionIndex = ref(0)
    const score = ref(0)
    const answeredQuestions = ref(new Set())

    const course = computed(() => courseStore.currentCourse)

    const currentSection = computed(() => {
      if (!course.value?.sections) return null
      return course.value.sections[currentSectionIndex.value]
    })

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

    const loadCourse = async () => {
      const courseId = route.params.id
      if (!courseId) {
        error.value = 'No course ID provided'
        return
      }

      loading.value = true
      error.value = null

      const result = await courseStore.loadCourse(courseId)

      if (!result.success) {
        error.value = result.error
      }

      loading.value = false
    }

    const handleAnswerSubmit = async (data) => {
      const { isCorrect, sectionIndex, subsectionIndex, questionIndex } = data
      
      // Create unique key for this question
      const questionKey = `${sectionIndex}-${subsectionIndex ?? 'main'}-${questionIndex}`
      
      // Only count if not already answered
      if (!answeredQuestions.value.has(questionKey)) {
        if (isCorrect) {
          score.value++
        }
        answeredQuestions.value.add(questionKey)

        // Update progress in backend if course has an ID
        if (route.params.id) {
          await courseStore.updateProgress(
            route.params.id,
            sectionIndex,
            questionIndex,
            isCorrect,
            subsectionIndex
          )
        }
      }
    }

    const previousSection = () => {
      if (currentSectionIndex.value > 0) {
        currentSectionIndex.value--
        window.scrollTo({ top: 0, behavior: 'smooth' })
      }
    }

    const nextSection = () => {
      if (currentSectionIndex.value < course.value.sections.length - 1) {
        currentSectionIndex.value++
        window.scrollTo({ top: 0, behavior: 'smooth' })
      }
    }

    // Load course on mount if we have an ID
    onMounted(() => {
      if (route.params.id) {
        loadCourse()
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

    return {
      loading,
      error,
      course,
      currentSection,
      currentSectionIndex,
      totalQuestions,
      score,
      handleAnswerSubmit,
      previousSection,
      nextSection
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
  color: #cbd5e0;
}

.course-header {
  margin-bottom: 2rem;
}

.course-title {
  font-size: 2.5rem;
  font-weight: 700;
  color: #e2e8f0;
  margin-bottom: 1rem;
}

.course-meta {
  display: flex;
  gap: 2rem;
  flex-wrap: wrap;
}

.meta-item {
  color: #cbd5e0;
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
  border-bottom: 2px solid rgba(6, 182, 212, 0.2);
}

.section-title {
  font-size: 2rem;
  font-weight: 600;
  color: #06b6d4;
}

.section-progress {
  color: #cbd5e0;
  font-size: 0.875rem;
  background: rgba(6, 182, 212, 0.1);
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
}

.section-explanation {
  margin-bottom: 2rem;
  padding: 1.5rem;
  background: rgba(6, 182, 212, 0.05);
  border-left: 4px solid #06b6d4;
  border-radius: 0.5rem;
  color: #cbd5e0;
  line-height: 1.6;
}

.quiz-section {
  margin: 2rem 0;
}

.quiz-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: #e2e8f0;
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
  color: #e2e8f0;
  margin-bottom: 1.5rem;
}

.subsection-card {
  background: rgba(6, 182, 212, 0.05);
  border: 1px solid rgba(6, 182, 212, 0.1);
  border-radius: 1rem;
  padding: 2rem;
  margin-bottom: 2rem;
}

.subsection-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: #0891b2;
  margin-bottom: 1rem;
}

.subsection-explanation {
  color: #cbd5e0;
  line-height: 1.6;
  margin-bottom: 1.5rem;
}

.section-navigation {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  margin-top: 3rem;
  padding-top: 2rem;
  border-top: 2px solid rgba(6, 182, 212, 0.2);
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
</style>
