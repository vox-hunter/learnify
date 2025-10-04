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
          @click="openCourse(course.course_id || course._id)"
        >
          <div class="course-card-header">
            <h3 class="course-card-title">
              {{ course.course_title || 'Untitled Course' }}
            </h3>
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
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useCourseStore } from '../stores/course'

export default {
  name: 'CoursesView',
  setup() {
    const router = useRouter()
    const courseStore = useCourseStore()

    const loading = ref(true)
    const courses = ref([])

    const loadCourses = async () => {
      loading.value = true
      await courseStore.loadCourses()
      courses.value = courseStore.courses
      loading.value = false
    }

    const openCourse = (courseId) => {
      router.push(`/course/${courseId}`)
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

    return {
      loading,
      courses,
      openCourse,
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
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  height: 100%;
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
