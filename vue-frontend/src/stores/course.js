import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../services/api'
import { useAuthStore } from './auth'

export const useCourseStore = defineStore('course', () => {
  const courses = ref([])
  const currentCourse = ref(null)
  const loading = ref(false)
  const error = ref(null)
  const guestCourseCount = ref(parseInt(localStorage.getItem('guestCourseCount') || '0'))

  // Guest user limit
  const GUEST_COURSE_LIMIT = 3

  const canGenerateCourse = computed(() => {
    const authStore = useAuthStore()
    if (authStore.isAuthenticated) {
      return true
    }
    return guestCourseCount.value < GUEST_COURSE_LIMIT
  })

  const remainingGuestCourses = computed(() => {
    return Math.max(0, GUEST_COURSE_LIMIT - guestCourseCount.value)
  })

  function incrementGuestCourseCount() {
    guestCourseCount.value++
    localStorage.setItem('guestCourseCount', guestCourseCount.value.toString())
  }

  function saveToLocalStorage(course) {
    try {
      const storedCourses = JSON.parse(localStorage.getItem('guestCourses') || '[]')
      storedCourses.push({
        ...course,
        course_id: Date.now().toString(),
        created_at: new Date().toISOString()
      })
      localStorage.setItem('guestCourses', JSON.stringify(storedCourses))
    } catch (e) {
      console.error('Failed to save course to localStorage:', e)
    }
  }

  function loadFromLocalStorage() {
    try {
      return JSON.parse(localStorage.getItem('guestCourses') || '[]')
    } catch (e) {
      console.error('Failed to load courses from localStorage:', e)
      return []
    }
  }

  async function generateCourse(file) {
    const authStore = useAuthStore()
    
    // Check guest limit
    if (!authStore.isAuthenticated && !canGenerateCourse.value) {
      error.value = 'You have reached the limit of 3 courses as a guest. Please log in to generate more courses.'
      return { success: false, error: error.value, requiresLogin: true }
    }

    loading.value = true
    error.value = null
    
    try {
      const formData = new FormData()
      formData.append('file', file)
      
      const response = await api.post('/course/generate/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
      
      currentCourse.value = response.data.course_data
      
      // Increment guest course count if not authenticated
      if (!authStore.isAuthenticated) {
        incrementGuestCourseCount()
      }
      
      return { success: true, course: response.data.course_data }
    } catch (err) {
      error.value = err.response?.data?.detail || 'Course generation failed'
      return { success: false, error: error.value }
    } finally {
      loading.value = false
    }
  }

  async function generateCourseFromUrl(url) {
    const authStore = useAuthStore()
    
    // Check guest limit
    if (!authStore.isAuthenticated && !canGenerateCourse.value) {
      error.value = 'You have reached the limit of 3 courses as a guest. Please log in to generate more courses.'
      return { success: false, error: error.value, requiresLogin: true }
    }

    loading.value = true
    error.value = null
    
    try {
      const response = await api.post('/course/generate/url', { file_url: url })
      currentCourse.value = response.data.course_data
      
      // Increment guest course count if not authenticated
      if (!authStore.isAuthenticated) {
        incrementGuestCourseCount()
      }
      
      return { success: true, course: response.data.course_data }
    } catch (err) {
      error.value = err.response?.data?.detail || 'Course generation failed'
      return { success: false, error: error.value }
    } finally {
      loading.value = false
    }
  }

  async function saveCourse(courseData, courseTitle, isPublic = true) {
    const authStore = useAuthStore()
    
    // If not authenticated, save to localStorage
    if (!authStore.isAuthenticated) {
      saveToLocalStorage({
        course_title: courseTitle,
        sections: courseData,
        is_public: isPublic
      })
      return { success: true, courseId: Date.now().toString(), isLocal: true }
    }
    
    try {
      const response = await api.post('/course/save', {
        course_data: courseData,
        course_title: courseTitle,
        is_public: isPublic
      }, {
        params: { username: authStore.user?.username }
      })
      return { success: true, courseId: response.data.course_id }
    } catch (err) {
      return { 
        success: false, 
        error: err.response?.data?.detail || 'Failed to save course' 
      }
    }
  }

  async function loadCourses() {
    const authStore = useAuthStore()
    loading.value = true
    
    try {
      if (!authStore.isAuthenticated) {
        // Load from localStorage for guest users
        courses.value = loadFromLocalStorage()
      } else {
        // Load from API for authenticated users
        const response = await api.get('/courses', {
          params: { username: authStore.user?.username }
        })
        courses.value = response.data.courses || []
      }
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to load courses'
      courses.value = []
    } finally {
      loading.value = false
    }
  }

  async function loadCourse(courseId) {
    loading.value = true
    try {
      const response = await api.get(`/course/${courseId}`)
      currentCourse.value = response.data
      return { success: true, course: response.data }
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to load course'
      return { success: false, error: error.value }
    } finally {
      loading.value = false
    }
  }

  async function updateProgress(courseId, sectionIndex, questionIndex, isCorrect, subsectionIndex = null) {
    try {
      await api.post(`/course/${courseId}/progress`, {
        course_id: courseId,
        section_index: sectionIndex,
        subsection_index: subsectionIndex,
        question_index: questionIndex,
        is_correct: isCorrect
      })
      return { success: true }
    } catch (err) {
      return { success: false, error: err.response?.data?.detail || 'Failed to update progress' }
    }
  }

  return {
    courses,
    currentCourse,
    loading,
    error,
    guestCourseCount,
    canGenerateCourse,
    remainingGuestCourses,
    generateCourse,
    generateCourseFromUrl,
    saveCourse,
    loadCourses,
    loadCourse,
    updateProgress
  }
})
