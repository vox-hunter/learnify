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
  
  // Cache for loaded courses to prevent redundant fetches
  const courseCache = ref(new Map())

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
    // Don't check limit here - check when saving instead
    // This allows guests to generate courses but limits saving

    loading.value = true
    error.value = null
    
    try {
      const formData = new FormData()
      formData.append('message', 'Please generate a course from this file.')
      formData.append('file', file)
      
      const response = await api.post('/chat/message', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
      
      if (!response.data.success) {
        throw new Error(response.data.error || 'Course generation failed')
      }

      // Check if AI detected and generated a course
      if (response.data.is_course && response.data.course_data) {
        currentCourse.value = response.data.course_data
        // Cache invalidation handled in saveCourse() where course_id is available
        return { success: true, course: response.data.course_data }
      } else {
        // AI didn't generate a course - maybe not suitable content
        error.value = 'The uploaded file does not contain suitable content for course generation. Please try a different file with educational material.'
        return { success: false, error: error.value }
      }
    } catch (err) {
      error.value = err.response?.data?.detail || err.message || 'Course generation failed'
      return { success: false, error: error.value }
    } finally {
      loading.value = false
    }
  }

  // Comment 2: Cache invalidation method
  function invalidateCourse(courseId) {
    courseCache.value.delete(courseId);
    console.log(`[Course Store] Invalidated cache for course ${courseId}`);
  }

  // URL-based course generation removed

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
      // Comment 2: Cache the newly saved course
      if (response.data.course_id && courseData) {
        courseCache.value.set(response.data.course_id, {
          course_id: response.data.course_id,
          course_title: courseTitle,
          sections: courseData
        });
      }
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
    console.log('[Course Store] loadCourses started. Authenticated:', authStore.isAuthenticated)
    try {
      if (!authStore.isAuthenticated) {
        // Load from localStorage for guest users
        courses.value = loadFromLocalStorage()
        console.log('[Course Store] Loaded courses from localStorage:', courses.value.length)
      } else {
        // Load from API for authenticated users
        const response = await api.get('/courses', {
          params: { username: authStore.user?.username }
        })
        courses.value = response.data.courses || []
        console.log('[Course Store] Loaded courses from API:', courses.value.length)
      }
    } catch (err) {
      console.error('[Course Store] loadCourses error:', err)
      error.value = err.response?.data?.detail || 'Failed to load courses'
      courses.value = []
    } finally {
      loading.value = false
    }
  }

  async function loadCourse(courseId) {
    // Check cache first to prevent redundant fetches
    if (courseCache.value.has(courseId)) {
      console.log(`[Course Store] Loading course ${courseId} from cache`)
      const cachedCourse = courseCache.value.get(courseId)
      currentCourse.value = cachedCourse
      return { success: true, course: cachedCourse }
    }
    
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
          // Cache the loaded course
          courseCache.value.set(courseId, currentCourse.value)
          loading.value = false
          return { success: true, course: currentCourse.value }
        } else {
          console.log('[Course Store] Course NOT found in localStorage - will try to load from API (library course)')
        }
      }
      
      // Try loading from API (for authenticated users or if not found in localStorage)
      console.log('[Course Store] Attempting to load from API')
      const response = await api.get(`/course/${courseId}`)
      currentCourse.value = response.data
      // Cache the loaded course
      courseCache.value.set(courseId, currentCourse.value)
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

  async function updateProgress(courseId, answeredQuestions, score, currentSectionIndex, answerData = {}, initialStepIndex = 0) {
    
    try {
      // Convert Set to Array for JSON serialization
      const answeredArray = Array.from(answeredQuestions)
      
      await api.post(`/course/${courseId}/progress`, {
        answered_questions: answeredArray,
        score: score,
        current_section_index: currentSectionIndex,
        answer_data: answerData,
        initial_step_index: initialStepIndex
      })
      
      // Also save to localStorage for persistence
      const progressKey = `course_progress_${courseId}`
      localStorage.setItem(progressKey, JSON.stringify({
        answered_questions: answeredArray,
        score: score,
        current_section_index: currentSectionIndex,
        answer_data: answerData,
        initial_step_index: initialStepIndex,
        last_updated: new Date().toISOString()
      }))
      
      return { success: true }
    } catch {
      console.error('[Course Store] Error updating progress:')
      return { success: false, error: 'Failed to update progress' }
    }
  }
  
  async function loadProgress(courseId) {
    
    try {
      // Try to load from API first
      const response = await api.get(`/course/${courseId}/progress`)
      return { success: true, progress: response.data }
    } catch {
      // Fallback to localStorage
      const progressKey = `course_progress_${courseId}`
      const savedProgress = localStorage.getItem(progressKey)
      
      if (savedProgress) {
        return { success: true, progress: JSON.parse(savedProgress) }
      }
      
      return { success: false, progress: null }
    }
  }

  async function deleteCourse(courseId) {
    const authStore = useAuthStore()
    // Clear from cache
    courseCache.value.delete(courseId)
    
    // If guest user, remove from localStorage
    if (!authStore.isAuthenticated) {
      const stored = JSON.parse(localStorage.getItem('guestCourses') || '[]')
      const remaining = stored.filter(c => c.course_id !== courseId)
      localStorage.setItem('guestCourses', JSON.stringify(remaining))
      // Decrement guest course count
      if (guestCourseCount.value > 0) {
        guestCourseCount.value--
        localStorage.setItem('guestCourseCount', guestCourseCount.value.toString())
      }
      // update in-memory list if loaded
      courses.value = courses.value.filter(c => (c.course_id || c._id) !== courseId);
      return { success: true, isLocal: true }
    }
    // Authenticated user - call API
    try {
      await api.delete(`/course/${courseId}`)
      // Remove from in-memory list
      courses.value = courses.value.filter(c => (c.course_id || c._id) !== courseId)
      return { success: true }
    } catch (e) {
      return { success: false, error: e }
    }
  }
  
  // Clear entire cache (useful when user logs out or switches accounts)
  function clearCache() {
    courseCache.value.clear()
    console.log('[Course Store] Cache cleared')
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
    saveCourse,
    loadCourses,
    loadCourse,
    updateProgress,
    loadProgress,
    deleteCourse,
    invalidateCourse,
    clearCache
  };
});
