import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../services/api'

export const useCourseStore = defineStore('course', () => {
  const courses = ref([])
  const currentCourse = ref(null)
  const loading = ref(false)
  const error = ref(null)

  async function generateCourse(file) {
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
      return { success: true, course: response.data.course_data }
    } catch (err) {
      error.value = err.response?.data?.detail || 'Course generation failed'
      return { success: false, error: error.value }
    } finally {
      loading.value = false
    }
  }

  async function generateCourseFromUrl(url) {
    loading.value = true
    error.value = null
    
    try {
      const response = await api.post('/course/generate/url', { file_url: url })
      currentCourse.value = response.data.course_data
      return { success: true, course: response.data.course_data }
    } catch (err) {
      error.value = err.response?.data?.detail || 'Course generation failed'
      return { success: false, error: error.value }
    } finally {
      loading.value = false
    }
  }

  async function saveCourse(courseData, courseTitle, isPublic = true) {
    try {
      const response = await api.post('/course/save', {
        course_data: courseData,
        course_title: courseTitle,
        is_public: isPublic
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
    loading.value = true
    try {
      const response = await api.get('/courses')
      courses.value = response.data.courses
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to load courses'
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
    generateCourse,
    generateCourseFromUrl,
    saveCourse,
    loadCourses,
    loadCourse,
    updateProgress
  }
})
