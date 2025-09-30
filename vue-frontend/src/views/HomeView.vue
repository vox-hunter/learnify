<template>
  <div class="home-view">
    <div class="container">
      <!-- Hero Section -->
      <section class="hero">
        <h1 class="hero-title">AI-Powered Learning</h1>
        <p class="hero-subtitle">
          Transform your documents into interactive courses with quizzes
        </p>
      </section>

      <!-- Course Generation Card -->
      <div class="generation-card card">
        <h2 class="section-title">Generate a Course</h2>
        <p class="section-description">
          Upload a PDF or provide a URL to generate a course with quizzes
        </p>

        <!-- Input Method Tabs -->
        <div class="tabs">
          <button 
            :class="['tab', { active: inputMethod === 'upload' }]"
            @click="inputMethod = 'upload'"
          >
            📤 Upload File
          </button>
          <button 
            :class="['tab', { active: inputMethod === 'url' }]"
            @click="inputMethod = 'url'"
          >
            🔗 Provide URL
          </button>
        </div>

        <!-- Upload Method -->
        <div v-if="inputMethod === 'upload'" class="input-section">
          <div class="file-upload-area">
            <input
              ref="fileInput"
              type="file"
              accept=".pdf"
              @change="handleFileChange"
              class="file-input"
              id="file-upload"
            />
            <label for="file-upload" class="file-upload-label">
              <div class="upload-icon">📄</div>
              <div v-if="!selectedFile" class="upload-text">
                <p class="upload-title">Click to upload or drag and drop</p>
                <p class="upload-subtitle">PDF files only (max 20MB)</p>
              </div>
              <div v-else class="selected-file">
                <p class="file-name">{{ selectedFile.name }}</p>
                <p class="file-size">{{ formatFileSize(selectedFile.size) }}</p>
              </div>
            </label>
          </div>
        </div>

        <!-- URL Method -->
        <div v-if="inputMethod === 'url'" class="input-section">
          <div class="form-group">
            <label class="form-label">PDF URL</label>
            <input
              v-model="pdfUrl"
              type="url"
              class="form-input"
              placeholder="https://example.com/document.pdf"
            />
          </div>
        </div>

        <!-- Error Message -->
        <div v-if="error" class="alert alert-error">
          {{ error }}
        </div>

        <!-- Progress -->
        <div v-if="generating" class="progress-section">
          <div class="progress-bar">
            <div class="progress-fill" :style="{ width: progress + '%' }"></div>
          </div>
          <p class="progress-text">{{ statusMessage }}</p>
        </div>

        <!-- Generate Button -->
        <button
          @click="generateCourse"
          :disabled="generating || (!selectedFile && !pdfUrl)"
          class="btn btn-primary btn-generate"
        >
          {{ generating ? 'Generating...' : '🚀 Generate Course' }}
        </button>
      </div>

      <!-- Generated Course Display -->
      <div v-if="generatedCourse" class="course-preview card">
        <h2 class="section-title">Course Generated Successfully! 🎉</h2>
        <h3 class="course-title">{{ generatedCourse.course_title }}</h3>
        <p class="course-info">
          {{ generatedCourse.sections?.length || 0 }} sections with 
          {{ totalQuestions }} questions
        </p>
        
        <div class="course-actions">
          <button @click="saveCourse" class="btn btn-primary">
            💾 Save Course
          </button>
          <button @click="startCourse" class="btn btn-secondary">
            ▶️ Start Learning
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useCourseStore } from '../stores/course'

export default {
  name: 'HomeView',
  setup() {
    const router = useRouter()
    const courseStore = useCourseStore()

    const inputMethod = ref('upload')
    const selectedFile = ref(null)
    const pdfUrl = ref('')
    const generating = ref(false)
    const progress = ref(0)
    const statusMessage = ref('')
    const error = ref(null)
    const generatedCourse = ref(null)
    const fileInput = ref(null)

    const totalQuestions = computed(() => {
      if (!generatedCourse.value?.sections) return 0
      
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
      
      return countQuestions(generatedCourse.value.sections)
    })

    const handleFileChange = (event) => {
      const file = event.target.files[0]
      if (file) {
        if (file.size > 20 * 1024 * 1024) {
          error.value = 'File size must be less than 20MB'
          selectedFile.value = null
          return
        }
        if (file.type !== 'application/pdf') {
          error.value = 'Only PDF files are supported'
          selectedFile.value = null
          return
        }
        selectedFile.value = file
        error.value = null
      }
    }

    const formatFileSize = (bytes) => {
      if (bytes < 1024) return bytes + ' B'
      if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
      return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
    }

    const generateCourse = async () => {
      error.value = null
      generating.value = true
      progress.value = 0
      statusMessage.value = 'Starting course generation...'

      // Simulate progress updates
      const progressInterval = setInterval(() => {
        if (progress.value < 90) {
          progress.value += Math.random() * 10
        }
      }, 1000)

      try {
        let result
        if (inputMethod.value === 'upload' && selectedFile.value) {
          statusMessage.value = 'Uploading file...'
          result = await courseStore.generateCourse(selectedFile.value)
        } else if (inputMethod.value === 'url' && pdfUrl.value) {
          statusMessage.value = 'Fetching document...'
          result = await courseStore.generateCourseFromUrl(pdfUrl.value)
        } else {
          throw new Error('Please provide a file or URL')
        }

        clearInterval(progressInterval)

        if (result.success) {
          progress.value = 100
          statusMessage.value = 'Course generated successfully!'
          generatedCourse.value = result.course
          
          // Reset form
          selectedFile.value = null
          pdfUrl.value = ''
          if (fileInput.value) {
            fileInput.value.value = ''
          }
        } else {
          throw new Error(result.error)
        }
      } catch (err) {
        clearInterval(progressInterval)
        error.value = err.message || 'Failed to generate course'
        progress.value = 0
      } finally {
        generating.value = false
      }
    }

    const saveCourse = async () => {
      if (!generatedCourse.value) return

      const result = await courseStore.saveCourse(
        generatedCourse.value.sections,
        generatedCourse.value.course_title
      )

      if (result.success) {
        alert('Course saved successfully!')
        router.push(`/course/${result.courseId}`)
      } else {
        error.value = result.error
      }
    }

    const startCourse = () => {
      // Store current course in the store and navigate
      courseStore.currentCourse = generatedCourse.value
      router.push('/courses')
    }

    return {
      inputMethod,
      selectedFile,
      pdfUrl,
      generating,
      progress,
      statusMessage,
      error,
      generatedCourse,
      totalQuestions,
      fileInput,
      handleFileChange,
      formatFileSize,
      generateCourse,
      saveCourse,
      startCourse
    }
  }
}
</script>

<style scoped>
.home-view {
  padding: 2rem 0;
}

.hero {
  text-align: center;
  margin-bottom: 3rem;
}

.hero-title {
  font-size: 3.5rem;
  font-weight: 700;
  background: linear-gradient(135deg, #06b6d4, #0891b2);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 1rem;
}

.hero-subtitle {
  font-size: 1.25rem;
  color: #cbd5e0;
  max-width: 600px;
  margin: 0 auto;
}

.generation-card {
  margin-bottom: 2rem;
}

.section-title {
  font-size: 2rem;
  font-weight: 600;
  color: #e2e8f0;
  margin-bottom: 0.5rem;
}

.section-description {
  color: #cbd5e0;
  margin-bottom: 2rem;
}

.tabs {
  display: flex;
  gap: 0.5rem;
  background: rgba(6, 182, 212, 0.1);
  border-radius: 0.75rem;
  padding: 0.25rem;
  margin-bottom: 2rem;
}

.tab {
  flex: 1;
  padding: 0.75rem 1.5rem;
  border: none;
  background: transparent;
  color: #a0aec0;
  font-weight: 500;
  cursor: pointer;
  border-radius: 0.5rem;
  transition: all 0.2s;
}

.tab.active {
  background: linear-gradient(135deg, #06b6d4, #0891b2);
  color: white;
  box-shadow: 0 4px 15px rgba(6, 182, 212, 0.3);
}

.input-section {
  margin-bottom: 2rem;
}

.file-upload-area {
  position: relative;
}

.file-input {
  display: none;
}

.file-upload-label {
  display: block;
  padding: 3rem;
  border: 2px dashed rgba(6, 182, 212, 0.3);
  border-radius: 1rem;
  background: rgba(6, 182, 212, 0.05);
  cursor: pointer;
  transition: all 0.2s;
  text-align: center;
}

.file-upload-label:hover {
  border-color: #06b6d4;
  background: rgba(6, 182, 212, 0.1);
}

.upload-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.upload-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: #e2e8f0;
  margin-bottom: 0.5rem;
}

.upload-subtitle {
  color: #cbd5e0;
  font-size: 0.875rem;
}

.selected-file {
  color: #06b6d4;
}

.file-name {
  font-weight: 600;
  margin-bottom: 0.25rem;
}

.file-size {
  font-size: 0.875rem;
  color: #cbd5e0;
}

.progress-section {
  margin: 2rem 0;
}

.progress-bar {
  height: 8px;
  background: rgba(6, 182, 212, 0.2);
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 0.5rem;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #06b6d4, #0891b2);
  transition: width 0.3s ease;
}

.progress-text {
  text-align: center;
  color: #cbd5e0;
  font-size: 0.875rem;
}

.btn-generate {
  width: 100%;
  font-size: 1.125rem;
  padding: 1rem;
}

.course-preview {
  animation: slideIn 0.3s ease;
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

.course-title {
  font-size: 1.5rem;
  color: #06b6d4;
  margin: 1rem 0;
}

.course-info {
  color: #cbd5e0;
  margin-bottom: 2rem;
}

.course-actions {
  display: flex;
  gap: 1rem;
}

@media (max-width: 768px) {
  .hero-title {
    font-size: 2.5rem;
  }

  .course-actions {
    flex-direction: column;
  }

  .course-actions .btn {
    width: 100%;
  }
}
</style>
