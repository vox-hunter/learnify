<template>
  <div class="courses-view">
    <div class="container">
      <h1 class="page-title">
        My Space
      </h1>

      <!-- Tab Navigation -->
      <div 
        class="tabs-container" 
        role="tablist"
        @keydown="handleTabKeydown"
      >
        <button
          id="tab-courses"
          :class="['tab-button', { active: activeTab === 'courses' }]"
          role="tab"
          :aria-selected="activeTab === 'courses'"
          :tabindex="activeTab === 'courses' ? 0 : -1"
          aria-controls="panel-courses"
          @click="activeTab = 'courses'; filterByCourseId = null"
        >
          Courses
          <span class="tab-badge">{{ courses.length }}</span>
        </button>
        <button
          id="tab-flashcards"
          :class="['tab-button', { active: activeTab === 'flashcards' }]"
          role="tab"
          :aria-selected="activeTab === 'flashcards'"
          :tabindex="activeTab === 'flashcards' ? 0 : -1"
          aria-controls="panel-flashcards"
          @click="activeTab = 'flashcards'; filterByCourseId = null"
        >
          Flashcards
          <span class="tab-badge">{{ flashcards.length }}</span>
        </button>
      </div>

      <!-- Courses Tab Content -->
      <div 
        v-if="activeTab === 'courses'"
        id="panel-courses"
        role="tabpanel"
        aria-labelledby="tab-courses"
      >
        <!-- Loading State -->
        <div
          v-if="loading"
          class="loading-state"
        >
          <div class="spinner" />
          <p>Loading courses...</p>
        </div>

        <!-- Empty State -->
        <div
          v-else-if="courses.length === 0"
          class="empty-state card"
        >
          <div class="empty-icon">
            📚
          </div>
          <h2>No courses yet</h2>
          <p>Generate your first course to get started!</p>
          <router-link
            to="/"
            class="btn btn-primary"
          >
            Generate Course
          </router-link>
        </div>

        <!-- Courses Grid -->
        <div
          v-else
          class="courses-grid"
        >
          <div
            v-for="course in courses"
            :key="course.course_id || course._id"
            class="course-card card"
            @click="openCourse(course.course_id || course._id)"
          >
            <div class="course-card-header">
              <h3 class="course-card-title">
                <div v-html="renderMarkdown(course.course_title || 'Untitled Course')" />
              </h3>
              <button
                class="delete-btn"
                title="Delete course"
                :disabled="deleting[course.course_id || course._id]"
                @click.stop="confirmDelete(course.course_id || course._id)"
              >
                <!-- Show spinner while deleting -->
                <span v-if="deleting[course.course_id || course._id]">⌛</span>
                <!-- If awaiting confirmation, show inline Delete? prompt in red -->
                <span
                  v-else-if="pendingDelete[course.course_id || course._id]"
                  class="delete-confirm"
                >Delete?</span>
                <!-- Default: show X -->
                <span v-else>✖</span>
              </button>
            </div>
            <div class="course-card-meta">
              <span class="meta-badge">
                📚 {{ course.sections?.length || 0 }} Sections
              </span>
              <span class="meta-badge">
                {{ formatDate(course.created_at) }}
              </span>
            </div>
            <div class="course-card-footer">
              <button class="btn btn-primary btn-sm">
                Open Course →
              </button>
              <button
                v-if="getLinkedFlashcardsCount(course.course_id || course._id) > 0"
                class="btn btn-secondary btn-sm"
                @click.stop="viewCourseFlashcards(course.course_id || course._id)"
              >
                View Flashcards ({{ getLinkedFlashcardsCount(course.course_id || course._id) }})
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Flashcards Tab Content -->
      <div 
        v-if="activeTab === 'flashcards'"
        id="panel-flashcards"
        role="tabpanel"
        aria-labelledby="tab-flashcards"
      >
        <!-- Loading State -->
        <div
          v-if="loading"
          class="loading-state"
        >
          <div class="spinner" />
          <p>Loading flashcards...</p>
        </div>

        <!-- Empty State -->
        <div
          v-else-if="flashcards.length === 0"
          class="empty-state card"
        >
          <div class="empty-icon">
            🃏
          </div>
          <h2>No flashcards yet</h2>
          <p>Generate your first flashcard set to get started!</p>
          <router-link
            to="/"
            class="btn btn-primary"
          >
            Generate Flashcards
          </router-link>
        </div>

        <!-- Flashcards Display -->
        <div v-else>
          <!-- Grouped Flashcards (Linked to Courses) -->
          <div
            v-for="(courseFlashcards, courseId) in groupedFlashcards"
            :key="courseId"
            class="flashcard-group"
          >
            <h2 class="flashcard-section-header">
              <div v-html="renderMarkdown(getCourseTitle(courseId))" />
            </h2>
            <div class="courses-grid">
              <div
                v-for="flashcard in courseFlashcards"
                :key="flashcard.flashcard_id || flashcard._id"
                class="flashcard-card card"
                @click="openFlashcard(flashcard.flashcard_id || flashcard._id)"
              >
                <div class="course-card-header">
                  <h3 class="course-card-title">
                    <div v-html="renderMarkdown(flashcard.flashcard_title || 'Untitled Flashcard')" />
                  </h3>
                  <button
                    class="delete-btn"
                    title="Delete flashcard"
                    :disabled="deletingFlashcard[flashcard.flashcard_id || flashcard._id]"
                    @click.stop="confirmDeleteFlashcard(flashcard.flashcard_id || flashcard._id)"
                  >
                    <span v-if="deletingFlashcard[flashcard.flashcard_id || flashcard._id]">⌛</span>
                    <span
                      v-else-if="pendingDeleteFlashcard[flashcard.flashcard_id || flashcard._id]"
                      class="delete-confirm"
                    >Delete?</span>
                    <span v-else>✖</span>
                  </button>
                </div>
                <div class="course-card-meta">
                  <span class="meta-badge">
                    🃏 {{ flashcard.cards?.length || 0 }} Cards
                  </span>
                  <span class="meta-badge">
                    {{ formatDate(flashcard.created_at) }}
                  </span>
                </div>
                <div class="course-card-footer">
                  <button class="btn btn-primary btn-sm">
                    Study Now →
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- Standalone Flashcards (Not Linked to Courses) -->
          <div
            v-if="standaloneFlashcards.length > 0"
            class="flashcard-group"
          >
            <h2 class="flashcard-section-header">
              Standalone Flashcards
            </h2>
            <div class="courses-grid">
              <div
                v-for="flashcard in standaloneFlashcards"
                :key="flashcard.flashcard_id || flashcard._id"
                class="flashcard-card card"
                @click="openFlashcard(flashcard.flashcard_id || flashcard._id)"
              >
                <div class="course-card-header">
                  <h3 class="course-card-title">
                    <div v-html="renderMarkdown(flashcard.flashcard_title || 'Untitled Flashcard')" />
                  </h3>
                  <button
                    class="delete-btn"
                    title="Delete flashcard"
                    :disabled="deletingFlashcard[flashcard.flashcard_id || flashcard._id]"
                    @click.stop="confirmDeleteFlashcard(flashcard.flashcard_id || flashcard._id)"
                  >
                    <span v-if="deletingFlashcard[flashcard.flashcard_id || flashcard._id]">⌛</span>
                    <span
                      v-else-if="pendingDeleteFlashcard[flashcard.flashcard_id || flashcard._id]"
                      class="delete-confirm"
                    >Delete?</span>
                    <span v-else>✖</span>
                  </button>
                </div>
                <div class="course-card-meta">
                  <span class="meta-badge">
                    🃏 {{ flashcard.cards?.length || 0 }} Cards
                  </span>
                  <span class="meta-badge">
                    {{ formatDate(flashcard.created_at) }}
                  </span>
                </div>
                <div class="course-card-footer">
                  <button class="btn btn-primary btn-sm">
                    Study Now →
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, nextTick, watch, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useCourseStore } from '../stores/course'
import { useFlashcardStore } from '../stores/flashcard'
import MarkdownIt from 'markdown-it'
import DOMPurify from 'dompurify'

export default {
  name: 'CoursesView',
  setup() {
    const router = useRouter()
    const courseStore = useCourseStore()
    const flashcardStore = useFlashcardStore()

    const loading = ref(true)
    const courses = ref([])
    const flashcards = ref([])
    const deleting = ref({})
    const pendingDelete = ref({})
    const deletingFlashcard = ref({})
    const pendingDeleteFlashcard = ref({})
    const activeTab = ref('courses')
    const filterByCourseId = ref(null)

    // Simple notification helper (re-use library pattern used elsewhere)
    const showNotification = (message, type = 'success') => {
      // minimal inline approach: try to log the notification; apps with a global toast
      // can replace this implementation with a proper toast emitter
      try {
        console.log('[notify]', type, message)
      } catch {
        alert(message)
      }
    }

    // MathJax typesetting helper
    function typesetMathJax() {
      nextTick(() => {
        if (window.MathJax && window.MathJax.typesetPromise) {
          // Typeset all course-card-title and meta-badge blocks
          const elements = document.querySelectorAll('.course-card-title, .meta-badge');
          window.MathJax.typesetPromise(Array.from(elements)).catch(() => {});
        }
      });
    }

    // Computed properties for flashcard organization
    const groupedFlashcards = computed(() => {
      const filtered = filterByCourseId.value 
        ? flashcards.value.filter(f => String(f.source_course_id) === String(filterByCourseId.value))
        : flashcards.value
      
      const groups = {}
      filtered.forEach(flashcard => {
        if (flashcard.source_course_id) {
          const courseId = String(flashcard.source_course_id)
          if (!groups[courseId]) {
            groups[courseId] = []
          }
          groups[courseId].push(flashcard)
        }
      })
      return groups
    })

    const standaloneFlashcards = computed(() => {
      if (filterByCourseId.value) {
        return []
      }
      return flashcards.value.filter(f => !f.source_course_id)
    })

    const linkedFlashcardsMap = computed(() => {
      const map = new Map()
      flashcards.value.forEach(flashcard => {
        if (flashcard.source_course_id) {
          const courseId = String(flashcard.source_course_id)
          const count = map.get(courseId) || 0
          map.set(courseId, count + 1)
        }
      })
      return map
    })

    const loadCourses = async () => {
      loading.value = true
      try {
        await courseStore.loadCourses()
        await loadFlashcards()
        // courseStore.courses may be a ref or a raw array depending on Pinia proxying.
        const storeCourses = courseStore.courses
        let resolved = []
        if (Array.isArray(storeCourses)) {
          resolved = storeCourses
        } else if (storeCourses && Array.isArray(storeCourses.value)) {
          resolved = storeCourses.value
        }
        courses.value = resolved
        console.log('[CoursesView] Resolved courses count:', courses.value.length, 'sample:', courses.value[0])
        typesetMathJax();
      } catch (err) {
        console.error('[CoursesView] Error loading courses:', err)
        // Fallback to empty list so UI doesn't stay stuck
        courses.value = []
        showNotification && showNotification('Failed to load courses. Check connection.', 'error')
      } finally {
        loading.value = false
      }
    }

    const loadFlashcards = async () => {
      try {
        await flashcardStore.loadFlashcards()
        const storeFlashcards = flashcardStore.flashcards
        let resolved = []
        if (Array.isArray(storeFlashcards)) {
          resolved = storeFlashcards
        } else if (storeFlashcards && Array.isArray(storeFlashcards.value)) {
          resolved = storeFlashcards.value
        }
        flashcards.value = resolved
        console.log('[CoursesView] Resolved flashcards count:', flashcards.value.length)
        typesetMathJax()
      } catch (err) {
        console.error('[CoursesView] Error loading flashcards:', err)
        flashcards.value = []
      }
    }

    const openCourse = (courseId) => {
      router.push(`/course/${courseId}`)
    }

    const openFlashcard = (flashcardId) => {
      router.push(`/flashcard/${flashcardId}`)
    }

    const getLinkedFlashcardsCount = (courseId) => {
      return linkedFlashcardsMap.value.get(String(courseId)) || 0
    }

    const viewCourseFlashcards = (courseId) => {
      activeTab.value = 'flashcards'
      filterByCourseId.value = String(courseId)
      window.scrollTo({ top: 0, behavior: 'smooth' })
    }

    const getCourseTitle = (courseId) => {
      const course = courses.value.find(c => String(c.course_id || c._id) === String(courseId))
      return course?.course_title || 'Course Flashcards'
    }

    const formatDate = (dateString) => {
      if (!dateString) return 'Unknown date'
      const date = new Date(dateString)
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      })
    }

    onMounted(() => {
      loadCourses()
      typesetMathJax();
    })

    // Watch for changes in courses and flashcards and typeset
    watch(courses, () => {
      typesetMathJax();
    });

    watch(flashcards, () => {
      typesetMathJax();
    });

    // Markdown renderer
    const md = new MarkdownIt({ html: false, linkify: true, typographer: true });
    const renderMarkdown = (text) => {
      if (!text) return '';
      const rendered = md.render(String(text));
      return DOMPurify.sanitize(rendered, { USE_PROFILES: { html: true } });
    };

    const confirmDelete = async (courseId) => {
      // If this course is not pending delete, set pending and wait for second click
      if (!pendingDelete.value[courseId]) {
        pendingDelete.value = { ...pendingDelete.value, [courseId]: true }

        // Auto-clear pending after 5 seconds
        setTimeout(() => {
          pendingDelete.value = { ...pendingDelete.value, [courseId]: false }
        }, 5000)

        return
      }

      // Second click: proceed to delete
      deleting.value = { ...deleting.value, [courseId]: true }
      // clear pending state immediately
      pendingDelete.value = { ...pendingDelete.value, [courseId]: false }

      const res = await courseStore.deleteCourse(courseId)
      deleting.value = { ...deleting.value, [courseId]: false }

      if (!res.success) {
        showNotification(res.error || 'Failed to delete course', 'error')
      } else {
        showNotification('Course deleted', 'success')
        // refresh local courses binding
        const storeCourses2 = courseStore.courses
        if (Array.isArray(storeCourses2)) {
          courses.value = storeCourses2
        } else if (storeCourses2 && Array.isArray(storeCourses2.value)) {
          courses.value = storeCourses2.value
        } else {
          courses.value = []
        }
        console.log('[CoursesView] After delete refresh - courses count:', courses.value.length, 'sample:', courses.value[0])
      }
    }

    const handleTabKeydown = (event) => {
      const tabs = ['courses', 'flashcards']
      const currentIndex = tabs.indexOf(activeTab.value)
      let newIndex = currentIndex

      if (event.key === 'ArrowLeft') {
        event.preventDefault()
        newIndex = currentIndex > 0 ? currentIndex - 1 : tabs.length - 1
      } else if (event.key === 'ArrowRight') {
        event.preventDefault()
        newIndex = currentIndex < tabs.length - 1 ? currentIndex + 1 : 0
      } else if (event.key === 'Home') {
        event.preventDefault()
        newIndex = 0
      } else if (event.key === 'End') {
        event.preventDefault()
        newIndex = tabs.length - 1
      } else {
        return
      }

      activeTab.value = tabs[newIndex]
      filterByCourseId.value = null
      // Focus the newly active tab
      nextTick(() => {
        const tabButton = document.getElementById(`tab-${tabs[newIndex]}`)
        if (tabButton) {
          tabButton.focus()
        }
      })
    }

    const confirmDeleteFlashcard = async (flashcardId) => {
      // If this flashcard is not pending delete, set pending and wait for second click
      if (!pendingDeleteFlashcard.value[flashcardId]) {
        pendingDeleteFlashcard.value = { ...pendingDeleteFlashcard.value, [flashcardId]: true }

        // Auto-clear pending after 5 seconds
        setTimeout(() => {
          pendingDeleteFlashcard.value = { ...pendingDeleteFlashcard.value, [flashcardId]: false }
        }, 5000)

        return
      }

      // Second click: proceed to delete
      deletingFlashcard.value = { ...deletingFlashcard.value, [flashcardId]: true }
      // clear pending state immediately
      pendingDeleteFlashcard.value = { ...pendingDeleteFlashcard.value, [flashcardId]: false }

      const res = await flashcardStore.deleteFlashcard(flashcardId)
      deletingFlashcard.value = { ...deletingFlashcard.value, [flashcardId]: false }

      if (!res.success) {
        showNotification(res.error || 'Failed to delete flashcard', 'error')
      } else {
        showNotification('Flashcard deleted', 'success')
        // Refresh local flashcards binding
        flashcards.value = flashcards.value.filter(f => (f.flashcard_id || f._id) !== flashcardId)
        console.log('[CoursesView] After delete refresh - flashcards count:', flashcards.value.length)
      }
    }

    return {
      loading,
      courses,
      flashcards,
      deleting,
      pendingDelete,
      deletingFlashcard,
      pendingDeleteFlashcard,
      activeTab,
      filterByCourseId,
      groupedFlashcards,
      standaloneFlashcards,
      linkedFlashcardsMap,
      confirmDelete,
      confirmDeleteFlashcard,
      openCourse,
      openFlashcard,
      getLinkedFlashcardsCount,
      viewCourseFlashcards,
      getCourseTitle,
      formatDate,
      renderMarkdown,
      handleTabKeydown
    }
  }
}
</script>

<style scoped>
.courses-view {
  padding: 2rem 0;
  min-height: calc(100vh - 200px);
}

.page-title {
  font-size: 2.5rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 2rem;
  text-align: center;
}

/* Tab Styles */
.tabs-container {
  display: flex;
  justify-content: center;
  gap: 1rem;
  margin-bottom: 2rem;
}

.tab-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  background: var(--bg-tertiary);
  border: 2px solid transparent;
  border-radius: 0.75rem;
  color: var(--text-secondary);
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.tab-button:hover {
  background: var(--card-bg);
  color: var(--text-primary);
}

.tab-button.active {
  background: linear-gradient(135deg, rgba(119, 51, 255, 0.15), rgba(0, 212, 255, 0.15));
  border-color: var(--accent-primary);
  color: var(--accent-primary);
  font-weight: 700;
}

.tab-badge {
  background: var(--accent-primary);
  color: white;
  padding: 0.125rem 0.5rem;
  border-radius: 0.5rem;
  font-size: 0.75rem;
  font-weight: 700;
}

.loading-state {
  text-align: center;
  padding: 4rem 0;
  color: var(--text-secondary);
}

.empty-state {
  text-align: center;
  padding: 4rem 2rem;
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.empty-state h2 {
  font-size: 2rem;
  color: var(--text-primary);
  margin-bottom: 1rem;
}

.empty-state p {
  color: var(--text-secondary);
  margin-bottom: 2rem;
}

.courses-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 2rem;
}

.course-card {
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  height: 100%;
  position: relative;
}

.course-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 20px 40px rgba(119, 51, 255, 0.2);
  border-color: var(--accent-primary);
}

:root[data-theme="light"] .course-card:hover {
  box-shadow: 0 20px 40px rgba(16, 185, 129, 0.15);
}

.course-card-header {
  flex: 1;
  margin-bottom: 1rem;
}

.course-card-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--accent-primary);
  margin-bottom: 0.5rem;
  line-height: 1.3;
}

.delete-btn {
  position: absolute;
  top: 0.75rem;
  right: 0.75rem;
  background: transparent;
  border: none;
  color: var(--text-secondary);
  font-size: 0.9rem;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  cursor: pointer;
}

.delete-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.delete-confirm {
  color: #ff4d4d;
  font-weight: 700;
}

.course-card-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.meta-badge {
  background: var(--bg-tertiary);
  color: var(--text-secondary);
  padding: 0.25rem 0.75rem;
  border-radius: 0.5rem;
  font-size: 0.875rem;
}

.course-card-footer {
  padding-top: 1rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.btn-sm {
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
}

.btn-secondary {
  background: transparent;
  border: 1px solid var(--accent-primary);
  color: var(--accent-primary);
}

.btn-secondary:hover {
  background: var(--accent-primary);
  color: white;
}

/* Flashcard Styles */
.flashcard-group {
  margin-bottom: 3rem;
}

.flashcard-section-header {
  font-size: 1.75rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 1.5rem;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid var(--border-color);
}

.flashcard-card {
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  height: 100%;
  position: relative;
}

.flashcard-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 20px 40px rgba(119, 51, 255, 0.2);
  border-color: var(--accent-primary);
}

:root[data-theme="light"] .flashcard-card:hover {
  box-shadow: 0 20px 40px rgba(16, 185, 129, 0.15);
}

@media (max-width: 768px) {
  .tabs-container {
    flex-direction: row;
    gap: 0.5rem;
  }

  .tab-button {
    flex: 1;
    justify-content: center;
    padding: 0.75rem 1rem;
    font-size: 0.875rem;
  }

  .tab-badge {
    font-size: 0.625rem;
    padding: 0.125rem 0.375rem;
  }

  .flashcard-section-header {
    font-size: 1.5rem;
  }
  .courses-grid {
    grid-template-columns: 1fr;
  }
}
</style>
