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
  const GUEST_COURSE_LIMIT = 2

  const canGenerateCourse = computed(() => {
    const authStore = useAuthStore()
    if (authStore.isAuthenticated) {
      console.log('[Course Store] User authenticated, unlimited courses')
      return true
    }
    console.log(`[Course Store] Guest check: ${guestCourseCount.value}/${GUEST_COURSE_LIMIT} courses saved`)
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
      const courseId = Date.now().toString()
      console.log('[Course Store] saveToLocalStorage - generating ID:', courseId)
      const storedCourses = JSON.parse(localStorage.getItem('guestCourses') || '[]')
      console.log('[Course Store] Current stored courses:', storedCourses.length)
      const newCourse = {
        ...course,
        course_id: courseId,
        created_at: new Date().toISOString()
      }
      storedCourses.push(newCourse)
      localStorage.setItem('guestCourses', JSON.stringify(storedCourses))
      console.log('[Course Store] ✅ Saved to localStorage successfully')
      return courseId
    } catch (e) {
      console.error('Failed to save course to localStorage:', e)
      return null
    }
  }

  function loadFromLocalStorage() {
    try {
      const courses = JSON.parse(localStorage.getItem('guestCourses') || '[]')
      console.log('[Course Store] loadFromLocalStorage - found', courses.length, 'courses')
      if (courses.length > 0) {
        console.log('[Course Store] Course IDs:', courses.map(c => c.course_id))
      }
      return courses
    } catch (e) {
      console.error('Failed to load courses from localStorage:', e)
      return []
    }
  }

  async function generateCourse(file) {
    const authStore = useAuthStore()
    
    // Don't check limit here - check when saving instead
    // This allows guests to generate courses but limits saving

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
      
      // Don't increment count here - it will be incremented when course is saved
      
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
    
    // Don't check limit here - check when saving instead
    // This allows guests to generate courses but limits saving

    loading.value = true
    error.value = null
    
    try {
      const response = await api.post('/course/generate/url', { file_url: url })
      currentCourse.value = response.data.course_data
      
      // Don't increment count here - it will be incremented when course is saved
      
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
    console.log('[Course Store] saveCourse called')
    console.log('[Course Store] Is authenticated:', authStore.isAuthenticated)
    console.log('[Course Store] Course title:', courseTitle)
    console.log('[Course Store] Guest course count:', guestCourseCount.value)
    
    // If not authenticated, save to localStorage
    if (!authStore.isAuthenticated) {
      console.log('[Course Store] Guest user - checking limit')
      console.log('[Course Store] canGenerateCourse.value:', canGenerateCourse.value)
      // Check if guest has reached the limit
      if (!canGenerateCourse.value) {
        console.log('[Course Store] ❌ Guest limit reached! Requiring login.')
        error.value = 'You have reached the limit of 2 saved courses as a guest. Please log in to save more courses.'
        return { 
          success: false, 
          error: error.value,
          requiresLogin: true
        }
      }
      
      console.log('[Course Store] ✅ Guest within limit - saving to localStorage')
      const courseId = saveToLocalStorage({
        course_title: courseTitle,
        sections: courseData,
        is_public: isPublic
      })
      console.log('[Course Store] Saved with ID:', courseId)
      // Increment guest course count when course is actually saved
      incrementGuestCourseCount()
      console.log('[Course Store] New guest course count:', guestCourseCount.value)
      return { success: true, courseId: courseId, isLocal: true }
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
    const authStore = useAuthStore()
    console.log(`[Course Store] loadCourse called with courseId: ${courseId}`)
    console.log(`[Course Store] User authenticated: ${authStore.isAuthenticated}`)
    
    try {
      // For guest users, try localStorage first
      if (!authStore.isAuthenticated) {
        console.log('[Course Store] Guest user - checking localStorage')
        const localCourses = loadFromLocalStorage()
        console.log(`[Course Store] Found ${localCourses.length} courses in localStorage`)
        const localCourse = localCourses.find(c => c.course_id === courseId)
        
        if (localCourse) {
          console.log('[Course Store] Found course in localStorage:', localCourse.course_title)
          // Transform localStorage format to match API format
          currentCourse.value = {
            course_id: localCourse.course_id,
            course_title: localCourse.course_title,
            sections: localCourse.sections
          }
          return { success: true, course: currentCourse.value }
        } else {
          console.log('[Course Store] Course NOT found in localStorage')
        }
      }
      
      // Try loading from API (for authenticated users or if not found in localStorage)
      console.log('[Course Store] Attempting to load from API')
      const response = await api.get(`/course/${courseId}`)
      currentCourse.value = response.data
      console.log('[Course Store] Successfully loaded from API')
      return { success: true, course: response.data }
    } catch (err) {
      console.error('[Course Store] Error loading course:', err)
      error.value = err.response?.data?.detail || 'Failed to load course'
      return { success: false, error: error.value }
    } finally {
      loading.value = false
    }
  }

  async function updateProgress(courseId, answeredQuestions, score, currentSectionIndex) {
    const authStore = useAuthStore()
    
    try {
      // Convert Set to Array for JSON serialization
      const answeredArray = Array.from(answeredQuestions)
      
      await api.post(`/course/${courseId}/progress`, {
        answered_questions: answeredArray,
        score: score,
        current_section_index: currentSectionIndex
      })
      
      // Also save to localStorage for persistence
      const progressKey = `course_progress_${courseId}`
      localStorage.setItem(progressKey, JSON.stringify({
        answered_questions: answeredArray,
        score: score,
        current_section_index: currentSectionIndex,
        last_updated: new Date().toISOString()
      }))
      
      return { success: true }
    } catch (err) {
      console.error('[Course Store] Error updating progress:', err)
      return { success: false, error: err.response?.data?.detail || 'Failed to update progress' }
    }
  }
  
  async function loadProgress(courseId) {
    const authStore = useAuthStore()
    
    try {
      // Try to load from API first
      const response = await api.get(`/course/${courseId}/progress`)
      return { success: true, progress: response.data }
    } catch (err) {
      // Fallback to localStorage
      const progressKey = `course_progress_${courseId}`
      const savedProgress = localStorage.getItem(progressKey)
      
      if (savedProgress) {
        return { success: true, progress: JSON.parse(savedProgress) }
      }
      
      return { success: false, progress: null }
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
    updateProgress,
    loadProgress
  }
})
