<template>
  <div class="courses-view">
    <div class="container">
      <h1 class="page-title">
        My Courses
      </h1>

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
        >
          <div
            class="course-card-content"
            @click="openCourse(course.course_id || course._id)"
          >
            <div class="course-card-header">
              <h3 class="course-card-title">
                {{ course.course_title || 'Untitled Course' }}
              </h3>
              <div class="course-actions">
                <button
                  class="edit-btn"
                  title="Edit with AI"
                  @click.stop="() => openCourseChat(course.course_id || course._id)"
                >
                  ✏️✨
                </button>
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
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useCourseStore } from '../stores/course'
import { useChatStore } from '../stores/chat'
import { useAuthStore } from '../stores/auth'

export default {
  name: 'CoursesView',
  setup() {
    const router = useRouter()
    const courseStore = useCourseStore()
    const chatStore = useChatStore()
    const authStore = useAuthStore()

    const loading = ref(true)
    const courses = ref([])
    const deleting = ref({})
    const pendingDelete = ref({})

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

    const loadCourses = async () => {
      loading.value = true
      try {
        await courseStore.loadCourses()
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
      } catch (err) {
        console.error('[CoursesView] Error loading courses:', err)
        // Fallback to empty list so UI doesn't stay stuck
        courses.value = []
        showNotification && showNotification('Failed to load courses. Check connection.', 'error')
      } finally {
        loading.value = false
      }
    }

    const openCourse = (courseId) => {
      router.push(`/course/${courseId}`)
    }

    const openCourseChat = async (courseId) => {
      if (!authStore.user?.username) {
        showNotification('Please login to use course chat', 'error')
        return
      }

      try {
        // Get or create course chat
        const chat = await chatStore.getCourseChat(authStore.user.username, courseId)
        if (chat) {
          // Navigate to chat with course context
          router.push(`/?chat_id=${chat.chat_id}`)
        }
      } catch (err) {
        console.error('Failed to open course chat:', err)
        showNotification('Failed to open course chat', 'error')
      }
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
    })

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

    return {
      loading,
      courses,
      deleting,
      pendingDelete,
      confirmDelete,
      openCourse,
      openCourseChat,
      formatDate
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
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  height: 100%;
  position: relative;
}

.course-card-content {
  cursor: pointer;
  flex: 1;
  display: flex;
  flex-direction: column;
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
  display: flex;
  justify-content: space-between;
  align-items: start;
}

.course-card-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--accent-primary);
  margin-bottom: 0.5rem;
  line-height: 1.3;
  flex: 1;
  padding-right: 0.5rem;
}

.course-actions {
  display: flex;
  gap: 0.5rem;
  flex-shrink: 0;
}

.edit-btn,
.delete-btn {
  background: transparent;
  border: none;
  color: var(--text-secondary);
  font-size: 1rem;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
}

.edit-btn:hover {
  background: var(--bg-tertiary);
  color: var(--accent-primary);
  transform: scale(1.1);
}

.delete-btn:hover:not(:disabled) {
  background: rgba(255, 77, 77, 0.1);
  color: #ff4d4d;
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
}

.btn-sm {
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
}

@media (max-width: 768px) {
  .courses-grid {
    grid-template-columns: 1fr;
  }
}
</style>
