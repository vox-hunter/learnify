<template>
  <div class="home-view">
    <div class="container">
      <!-- Hero Section -->
      <section class="hero">
        <div class="hero-logo">
          <img src="/logo.png" alt="AI Loom" class="logo-large" />
        </div>
        <h1 class="hero-title">AI Loom</h1>
        <p class="hero-subtitle">
          Smart Learning Platform - Transform your documents into interactive courses with quizzes
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
              accept=".pdf,.docx,.doc,.txt,.pptx,.ppt,.xlsx,.xls,.md,.rtf"
              @change="handleFileChange"
              class="file-input"
              id="file-upload"
            />
            <label for="file-upload" class="file-upload-label">
              <div class="upload-icon">📄</div>
              <div v-if="!selectedFile" class="upload-text">
                <p class="upload-title">Click to upload or drag and drop</p>
                <p class="upload-subtitle">PDF, Word, PowerPoint, Excel, Text files (max 20MB)</p>
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
          <div class="progress-header">
            <span class="progress-title">⚡ Generating Your Course</span>
            <span class="progress-percentage">{{ progress }}%</span>
          </div>
          
          <div class="progress-bar">
            <div class="progress-fill" :style="{ width: progress + '%' }"></div>
          </div>
          
          <!-- Status Steps -->
          <div class="status-steps">
            <div 
              v-for="(step, index) in generationSteps" 
              :key="index"
              class="status-step"
              :class="{ 
                'active': currentStep === index, 
                'completed': currentStep > index 
              }"
            >
              <div class="step-icon">
                <span v-if="currentStep > index">✓</span>
                <span v-else-if="currentStep === index" class="spinner-small"></span>
                <span v-else>{{ index + 1 }}</span>
              </div>
              <div class="step-content">
                <div class="step-title">{{ step.title }}</div>
                <div v-if="currentStep === index" class="step-description">
                  {{ step.description }}
                </div>
              </div>
            </div>
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
          <button @click="startCourse" class="btn btn-primary">
            ▶️ Start Learning
          </button>
        </div>
      </div>

      <!-- Guest User Limit Warning -->
      <div v-if="!authStore.isAuthenticated && courseStore.remainingGuestCourses < 2" class="alert alert-warning">
        <p><strong>Guest User:</strong> You can save {{ courseStore.remainingGuestCourses }} more course{{ courseStore.remainingGuestCourses !== 1 ? 's' : '' }}.</p>
        <p v-if="courseStore.remainingGuestCourses === 0">
          You've reached the limit of 2 saved courses. Please <router-link to="/login">log in</router-link> to save more.
        </p>
        <p v-else>
          You can generate unlimited courses, but can only save {{ courseStore.remainingGuestCourses }} more as a guest.
        </p>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useCourseStore } from '../stores/course'
import { useAuthStore } from '../stores/auth'

export default {
  name: 'HomeView',
  setup() {
    const router = useRouter()
    const courseStore = useCourseStore()
    const authStore = useAuthStore()

    const inputMethod = ref('upload')
    const selectedFile = ref(null)
    const pdfUrl = ref('')
    const generating = ref(false)
    const progress = ref(0)
    const statusMessage = ref('')
    const error = ref(null)
    const generatedCourse = ref(null)
    const fileInput = ref(null)
    const currentStep = ref(-1)

    const generationSteps = [
      { title: 'Uploading', description: 'Uploading your document to the server...' },
      { title: 'Processing', description: 'Extracting and analyzing content...' },
      { title: 'Generating', description: 'Creating course structure and sections...' },
      { title: 'Quiz Creation', description: 'Generating quiz questions and answers...' },
      { title: 'Finalizing', description: 'Preparing your course for learning...' }
    ]

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
        // Allow common document formats
        const allowedTypes = [
          'application/pdf',
          'application/vnd.openxmlformats-officedocument.wordprocessingml.document', // .docx
          'application/msword', // .doc
          'text/plain',
          'application/vnd.openxmlformats-officedocument.presentationml.presentation', // .pptx
          'application/vnd.ms-powerpoint', // .ppt
          'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', // .xlsx
          'application/vnd.ms-excel', // .xls
          'text/markdown',
          'application/rtf'
        ]
        
        const allowedExtensions = ['.pdf', '.docx', '.doc', '.txt', '.pptx', '.ppt', '.xlsx', '.xls', '.md', '.rtf']
        const fileExtension = '.' + file.name.split('.').pop().toLowerCase()
        
        if (!allowedTypes.includes(file.type) && !allowedExtensions.includes(fileExtension)) {
          error.value = 'File type not supported. Please upload PDF, Word, PowerPoint, Excel, or Text files.'
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
      currentStep.value = 0
      statusMessage.value = 'Starting course generation...'

      // No limit check here - guests can generate unlimited courses
      // The limit is enforced when trying to SAVE the course

      // Simulate realistic progress updates through steps
      const updateProgress = (step, progressValue, message) => {
        currentStep.value = step
        progress.value = progressValue
        statusMessage.value = message
      }

      try {
        let result
        
        // Step 0: Uploading
        updateProgress(0, 10, 'Uploading your document...')
        await new Promise(resolve => setTimeout(resolve, 500))
        
        // Step 1: Processing
        updateProgress(1, 25, 'Extracting and analyzing content...')
        
        if (inputMethod.value === 'upload' && selectedFile.value) {
          result = await courseStore.generateCourse(selectedFile.value)
        } else if (inputMethod.value === 'url' && pdfUrl.value) {
          result = await courseStore.generateCourseFromUrl(pdfUrl.value)
        } else {
          throw new Error('Please provide a file or URL')
        }

        // Step 2: Generating
        updateProgress(2, 50, 'Creating course structure...')
        await new Promise(resolve => setTimeout(resolve, 800))
        
        // Step 3: Quiz Creation
        updateProgress(3, 75, 'Generating quiz questions...')
        await new Promise(resolve => setTimeout(resolve, 800))
        
        // Step 4: Finalizing
        updateProgress(4, 95, 'Finalizing your course...')
        await new Promise(resolve => setTimeout(resolve, 500))

        if (result.success) {
          progress.value = 100
          statusMessage.value = '✨ Course generated successfully!'
          generatedCourse.value = result.course
          
          // Reset form
          selectedFile.value = null
          pdfUrl.value = ''
          if (fileInput.value) {
            fileInput.value.value = ''
          }
        } else {
          if (result.requiresLogin) {
            router.push('/login')
          }
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

    const startCourse = async () => {
      console.log('[HomeView] startCourse called')
      if (!generatedCourse.value) return

      try {
        console.log('[HomeView] Generated course:', generatedCourse.value.course_title)
        // Auto-save the course when starting
        const result = await courseStore.saveCourse(
          generatedCourse.value.sections,
          generatedCourse.value.course_title
        )

        console.log('[HomeView] Save result:', result)
        if (result.success) {
          console.log(`[HomeView] Success! Navigating to /course/${result.courseId}`)
          // Navigate to the course - works for both logged-in and guest users
          router.push(`/course/${result.courseId}`)
        } else {
          // Check if guest limit was reached
          if (result.requiresLogin) {
            console.log('[HomeView] Requires login - showing alert')
            error.value = 'You have reached the limit of 2 saved courses as a guest. Please log in to save more.'
            // Optional: Auto-redirect to login after showing message
            setTimeout(() => {
              console.log('[HomeView] Redirecting to login')
              router.push('/login')
            }, 2000)
          } else {
            console.error('[HomeView] Error:', result.error)
            error.value = result.error || 'Failed to save course'
          }
        }
      } catch (err) {
        console.error('[HomeView] Exception:', err)
        error.value = err.message || 'Failed to start course'
      }
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
      currentStep,
      generationSteps,
      authStore,
      courseStore,
      handleFileChange,
      formatFileSize,
      generateCourse,
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

.hero-logo {
  margin-bottom: 1.5rem;
  display: flex;
  justify-content: center;
  align-items: center;
}

.logo-large {
  height: 120px;
  width: auto;
  object-fit: contain;
  filter: drop-shadow(0 0 20px rgba(6, 182, 212, 0.3));
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-10px);
  }
}

.hero-title {
  font-size: 3.5rem;
  font-weight: 700;
  background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 1rem;
}

.hero-subtitle {
  font-size: 1.25rem;
  color: var(--text-secondary);
  max-width: 700px;
  margin: 0 auto;
}

.generation-card {
  margin-bottom: 2rem;
}

.section-title {
  font-size: 2rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 0.5rem;
}

.section-description {
  color: var(--text-secondary);
  margin-bottom: 2rem;
}

.tabs {
  display: flex;
  gap: 0.5rem;
  background: var(--bg-tertiary);
  border-radius: 0.75rem;
  padding: 0.25rem;
  margin-bottom: 2rem;
}

.tab {
  flex: 1;
  padding: 0.75rem 1.5rem;
  border: none;
  background: transparent;
  color: var(--text-muted);
  font-weight: 500;
  cursor: pointer;
  border-radius: 0.5rem;
  transition: all 0.2s;
}

.tab.active {
  background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
  color: white;
  box-shadow: 0 4px 15px rgba(119, 51, 255, 0.3);
}

:root[data-theme="light"] .tab.active {
  box-shadow: 0 4px 15px rgba(16, 185, 129, 0.25);
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
  border: 2px dashed var(--border-color);
  border-radius: 1rem;
  background: var(--bg-tertiary);
  cursor: pointer;
  transition: all 0.2s;
  text-align: center;
}

.file-upload-label:hover {
  border-color: var(--accent-primary);
  background: var(--card-bg);
}

.upload-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.upload-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 0.5rem;
}

.upload-subtitle {
  color: var(--text-secondary);
  font-size: 0.875rem;
}

.selected-file {
  color: var(--accent-primary);
}

.file-name {
  font-weight: 600;
  margin-bottom: 0.25rem;
}

.file-size {
  font-size: 0.875rem;
  color: var(--text-secondary);
}

.progress-section {
  margin: 2rem 0;
  padding: 2rem;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 1rem;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.progress-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #e2e8f0;
}

.progress-percentage {
  font-size: 1.5rem;
  font-weight: 700;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.progress-bar {
  height: 12px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 1rem;
  overflow: hidden;
  margin-bottom: 1.5rem;
  box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.2);
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  transition: width 0.5s ease;
  position: relative;
  overflow: hidden;
}

.progress-fill::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(
    90deg,
    rgba(255, 255, 255, 0) 0%,
    rgba(255, 255, 255, 0.3) 50%,
    rgba(255, 255, 255, 0) 100%
  );
  animation: shimmer 2s infinite;
}

@keyframes shimmer {
  0% {
    transform: translateX(-100%);
  }
  100% {
    transform: translateX(100%);
  }
}

.status-steps {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.status-step {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  padding: 0.75rem;
  border-radius: 0.5rem;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.05);
  transition: all 0.3s ease;
  opacity: 0.5;
}

.status-step.active {
  opacity: 1;
  background: rgba(102, 126, 234, 0.1);
  border-color: rgba(102, 126, 234, 0.3);
  transform: translateX(5px);
}

.status-step.completed {
  opacity: 0.7;
  background: rgba(74, 222, 128, 0.05);
  border-color: rgba(74, 222, 128, 0.2);
}

.step-icon {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  flex-shrink: 0;
  background: rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.6);
  border: 2px solid rgba(255, 255, 255, 0.2);
}

.status-step.active .step-icon {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-color: transparent;
  animation: pulse 2s ease infinite;
}

.status-step.completed .step-icon {
  background: #4ade80;
  color: white;
  border-color: transparent;
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.05);
  }
}

.spinner-small {
  width: 14px;
  height: 14px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  display: inline-block;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.step-content {
  flex: 1;
}

.step-title {
  font-weight: 600;
  color: #e2e8f0;
  margin-bottom: 0.25rem;
}

.step-description {
  font-size: 0.875rem;
  color: rgba(255, 255, 255, 0.6);
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.progress-text {
  text-align: center;
  color: #cbd5e0;
  font-size: 0.875rem;
  font-weight: 500;
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
  color: var(--accent-primary);
  margin: 1rem 0;
}

.course-info {
  color: var(--text-secondary);
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
