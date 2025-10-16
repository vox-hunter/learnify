<template>
  <div class="library-view">
    <div class="container">
      <!-- In-app notification (shows success / error messages) -->
      <div
        v-if="showNotification"
        :class="['app-notification', notificationType]"
      >
        {{ notificationMessage }}
      </div>
      <div class="library-header">
        <h1 class="page-title">
          Course Library
        </h1>
        <p class="page-subtitle">
          Explore and learn from courses created by the community
        </p>

        <!-- Search Bar -->
        <div class="search-section">
          <div class="search-bar">
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Search courses by title, topic, or keyword..."
              class="search-input"
              @keyup.enter="searchCourses"
            >
            <button
              class="search-btn"
              :disabled="loading"
              @click="searchCourses"
            >
              🔍
            </button>
          </div>

          <!-- Subject Filter -->
          <div class="filter-section">
            <select
              v-model="selectedSubject"
              class="subject-filter"
              @change="filterBySubject"
            >
              <option value="">
                All Subjects
              </option>
              <option value="mathematics">
                Mathematics
              </option>
              <option value="science">
                Science
              </option>
              <option value="history">
                History
              </option>
              <option value="literature">
                Literature
              </option>
              <option value="computer_science">
                Computer Science
              </option>
              <option value="business">
                Business
              </option>
              <option value="language">
                Languages
              </option>
              <option value="art">
                Art & Design
              </option>
              <option value="medicine">
                Medicine
              </option>
              <option value="engineering">
                Engineering
              </option>
            </select>

            <select
              v-model="sortBy"
              class="sort-filter"
              @change="loadCourses"
            >
              <option value="created_at">
                Newest First
              </option>
              <option value="rating">
                Highest Rated
              </option>
              <option value="popularity_score">
                Most Popular
              </option>
              <option value="title">
                Alphabetical
              </option>
            </select>
          </div>
        </div>
      </div>

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
        <h2>No courses found</h2>
        <p v-if="searchQuery">
          Try searching with different keywords or browse all courses.
        </p>
        <p v-else>
          No public courses available yet. Be the first to create one!
        </p>
        <button
          v-if="searchQuery || selectedSubject"
          class="btn btn-secondary"
          @click="clearFilters"
        >
          Clear Filters
        </button>
      </div>

      <!-- Courses Grid -->
      <div
        v-else
        class="courses-grid"
      >
        <div
          v-for="course in courses"
          :key="course.course_id"
          class="course-card card"
        >
          <div class="course-card-header">
            <h3 class="course-card-title">
              <div v-html="renderMarkdown(course.course_title || 'Untitled Course')" />
            </h3>
            <div
              v-if="course.rating > 0"
              class="course-rating"
            >
              <span class="stars">
                {{ getStarRating(course.rating) }}
              </span>
              <span class="rating-text">{{ course.rating.toFixed(1) }}</span>
              <span class="rating-count">({{ course.total_ratings || 0 }})</span>
            </div>
          </div>

          <div
            v-if="course.description"
            class="course-description"
          >
            <div v-html="renderMarkdown(course.description)" />
          </div>

          <div class="course-card-meta">
            <span class="meta-badge">
              📚 {{ course.total_sections || 0 }} Sections
            </span>
            <span class="meta-badge">
              ❓ {{ course.total_questions || 0 }} Questions
            </span>
            <span
              v-if="course.subject"
              class="meta-badge"
            >
              🏷️ {{ course.subject }}
            </span>
            <span class="meta-badge">
              👤 {{ course.creator || 'Anonymous' }}
            </span>
            <span class="meta-badge">
              📅 {{ formatDate(course.created_at) }}
            </span>
          </div>

          <div
            v-if="course.tags && course.tags.length > 0"
            class="course-tags"
          >
            <span
              v-for="tag in course.tags.slice(0, 3)"
              :key="tag"
              class="tag"
            >
              {{ tag }}
            </span>
          </div>

          <div class="course-card-footer">
            <button
              class="btn btn-secondary btn-sm"
              @click="viewCourse(course.course_id)"
            >
              View Course
            </button>
            <button
              class="btn btn-primary btn-sm"
              :disabled="cloning[course.course_id]"
              @click="cloneCourse(course.course_id)"
            >
              <span v-if="!cloning[course.course_id]">Clone & Edit</span>
              <span v-else>Cloning...</span>
            </button>
            <button
              class="btn btn-outline btn-sm"
              :disabled="hasUserRated(course.course_id)"
              :title="hasUserRated(course.course_id) ? 'You have already rated this course' : 'Rate this course'"
              @click="showRatingModal(course)"
            >
              {{ hasUserRated(course.course_id) ? 'Rated' : 'Rate' }}
            </button>
          </div>
        </div>
      </div>

      <!-- Load More Button -->
      <div
        v-if="courses.length > 0 && hasMore"
        class="load-more-section"
      >
        <button
          class="btn btn-secondary"
          :disabled="loading"
          @click="loadMore"
        >
          <span v-if="!loading">Load More</span>
          <span v-else>Loading...</span>
        </button>
      </div>
    </div>

    <!-- Rating Modal -->
    <div
      v-if="showRating"
      class="modal-overlay"
      @click="closeRatingModal"
    >
      <div
        class="modal-content"
        @click.stop
      >
        <h3>Rate Course</h3>
        <p>{{ ratingCourse?.course_title }}</p>

        <div class="rating-stars">
          <button
            v-for="star in 5"
            :key="star"
            class="star-btn"
            :class="{ active: star <= selectedRating }"
            @click="selectRating(star)"
          >
            ⭐
          </button>
        </div>

        <div class="modal-actions">
          <button
            class="btn btn-secondary"
            @click="closeRatingModal"
          >
            Cancel
          </button>
          <button
            class="btn btn-primary"
            :disabled="selectedRating === 0 || submittingRating"
            @click="submitRating"
          >
            <span v-if="!submittingRating">Submit Rating</span>
            <span v-else>Submitting...</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed, nextTick, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { useCourseStore } from '../stores/course'
import api from '../services/api'
import MarkdownIt from 'markdown-it'
import DOMPurify from 'dompurify'

export default {
    name: 'LibraryView',
    setup() {
    // MathJax typesetting helper
    function typesetMathJax() {
      nextTick(() => {
        if (window.MathJax && window.MathJax.typesetPromise) {
          // Typeset all course-card-title, meta-badge, and course-description blocks
          const elements = document.querySelectorAll('.course-card-title, .meta-badge, .course-description');
          window.MathJax.typesetPromise(Array.from(elements)).catch(() => {});
        }
      });
    }
        const router = useRouter()
        const authStore = useAuthStore()
        const courseStore = useCourseStore()

        const courses = ref([])
        const loading = ref(false)
        const searchQuery = ref('')
        const selectedSubject = ref('')
        const sortBy = ref('created_at')
        const currentPage = ref(0)
        const hasMore = ref(true)
        const cloning = ref({})

        // Rating modal state
        const showRating = ref(false)
        const ratingCourse = ref(null)
        const selectedRating = ref(0)
        const submittingRating = ref(false)

        const isAuthenticated = computed(() => authStore.isAuthenticated)

        // Track user ratings in localStorage
        const getUserRatingsKey = () => {
            const username = authStore.user?.username || 'guest'
            return `user_ratings_${username}`
        }

        const hasUserRated = (courseId) => {
            const ratingsKey = getUserRatingsKey()
            const ratingsData = localStorage.getItem(ratingsKey)
            if (!ratingsData) return false
            try {
                const ratings = JSON.parse(ratingsData)
                return ratings.includes(courseId)
            } catch (e) {
                return false
            }
        }

        const markCourseAsRated = (courseId) => {
            const ratingsKey = getUserRatingsKey()
            const ratingsData = localStorage.getItem(ratingsKey)
            let ratings = []
            if (ratingsData) {
                try {
                    ratings = JSON.parse(ratingsData)
                } catch (e) {
                    ratings = []
                }
            }
            if (!ratings.includes(courseId)) {
                ratings.push(courseId)
                localStorage.setItem(ratingsKey, JSON.stringify(ratings))
            }
        }

        // In-app notification state
        const showNotification = ref(false)
        const notificationMessage = ref('')
        const notificationType = ref('success')

    const loadCourses = async (reset = true) => {
      loading.value = true

      if (reset) {
        currentPage.value = 0
        courses.value = []
      }

      try {
        let url = `/library/courses?page=${currentPage.value}&limit=20&sort_by=${sortBy.value}&sort_order=-1`

        if (searchQuery.value.trim()) {
          url = `/library/search?q=${encodeURIComponent(searchQuery.value)}&page=${currentPage.value}&limit=20`
        } else if (selectedSubject.value) {
          url = `/library/subject/${selectedSubject.value}?page=${currentPage.value}&limit=20`
        }

        const response = await api.get(url)
        const newCourses = response.data.courses || []

        if (reset) {
          courses.value = newCourses
        } else {
          courses.value = [...courses.value, ...newCourses]
        }

        hasMore.value = newCourses.length === 20
        typesetMathJax();
      } catch (error) {
        console.error('Error loading courses:', error)
        courses.value = []
      } finally {
        loading.value = false
      }
    }

        const loadMore = () => {
            currentPage.value++
            loadCourses(false)
        }

        const searchCourses = () => {
            loadCourses(true)
        }

        const filterBySubject = () => {
            searchQuery.value = ''
            loadCourses(true)
        }

        const clearFilters = () => {
            searchQuery.value = ''
            selectedSubject.value = ''
            loadCourses(true)
        }

        const viewCourse = (courseId) => {
            router.push(`/course/${courseId}`)
        }

        const showNotificationMessage = (message, type = 'success', timeout = 3500) => {
            notificationMessage.value = message
            notificationType.value = type
            showNotification.value = true
            setTimeout(() => {
                showNotification.value = false
            }, timeout)
        }

        const cloneCourse = async (courseId) => {
      if (cloning.value[courseId]) return; // Prevent double navigation
      cloning.value = { ...cloning.value, [courseId]: true }

      try {
        const params = isAuthenticated.value ? { username: authStore.user?.username } : {}
        const response = await api.post(`/library/course/${courseId}/clone`, {}, { params })

        if (response.data.success) {
          showNotificationMessage('Course cloned successfully! You can find it in your courses.', 'success')
          // Debounce navigation to prevent double reloads
          setTimeout(() => {
            if (router.currentRoute.value.path !== `/course/${response.data.course_id}`) {
              router.push(`/course/${response.data.course_id}`)
            }
          }, 300);
        }
      } catch (error) {
        console.error('Error cloning course:', error)
        showNotificationMessage('Failed to clone course. Please try again.', 'error')
      } finally {
        cloning.value = { ...cloning.value, [courseId]: false }
      }
        }

        const showRatingModal = (course) => {
            // Check if user is authenticated
            if (!isAuthenticated.value) {
                showNotificationMessage('Please log in to rate courses', 'error', 3000)
                return
            }
            ratingCourse.value = course
            selectedRating.value = 0
            showRating.value = true
        }

        const closeRatingModal = () => {
            showRating.value = false
            ratingCourse.value = null
            selectedRating.value = 0
        }

        const selectRating = (rating) => {
            selectedRating.value = rating
        }

        const submitRating = async () => {
            if (!ratingCourse.value || selectedRating.value === 0) return

            const courseToRate = ratingCourse.value
            const ratingValue = selectedRating.value

            // Check if user already rated this course
            if (hasUserRated(courseToRate.course_id)) {
                closeRatingModal()
                showNotificationMessage('You have already rated this course', 'error', 3000)
                return
            }

            // Close modal immediately for instant feedback
            closeRatingModal()

            // Mark course as rated locally
            markCourseAsRated(courseToRate.course_id)

            // Optimistic UI update: adjust course rating locally
            const originalCourse = courses.value.find(c => c.course_id === courseToRate.course_id)
            let rollbackData = null
            if (originalCourse) {
                rollbackData = { rating: originalCourse.rating, total_ratings: originalCourse.total_ratings }
                const originalRating = originalCourse.rating || 0
                const originalTotalRatings = originalCourse.total_ratings || 0
                const newTotalRatings = originalTotalRatings + 1
                const newAverageRating = ((originalRating * originalTotalRatings) + ratingValue) / newTotalRatings
                originalCourse.rating = newAverageRating
                originalCourse.total_ratings = newTotalRatings
            }

            // Show success notification
            showNotificationMessage('Thanks for rating — submitted!')

            // Submit rating in background and refresh/rollback on failure
            try {
                const params = isAuthenticated.value ? { username: authStore.user?.username } : {}
                await api.post(`/library/course/${courseToRate.course_id}/rate`, {
                    rating: ratingValue
                }, { params })

                // Refresh the course in the background to get accurate server values
                loadCourses(true)
            } catch (error) {
                console.error('Error rating course:', error)
                // Rollback optimistic update if present
                if (originalCourse && rollbackData) {
                    originalCourse.rating = rollbackData.rating
                    originalCourse.total_ratings = rollbackData.total_ratings
                }
                showNotificationMessage('Failed to submit rating. Reverted.', 'error')
            }
        }

        const getStarRating = (rating) => {
            const fullStars = Math.floor(rating)
            const hasHalfStar = rating % 1 >= 0.5
            return '⭐'.repeat(fullStars) + (hasHalfStar ? '⭐' : '')
        }

        // Markdown renderer
        const md = new MarkdownIt({ html: false, linkify: true, typographer: true });
        const renderMarkdown = (text) => {
            if (!text) return '';
            const rendered = md.render(String(text));
            return DOMPurify.sanitize(rendered, { USE_PROFILES: { html: true } });
        };

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

    // Watch for changes in courses and typeset
    watch(courses, () => {
      typesetMathJax();
    });

        return {
            courses,
            loading,
            searchQuery,
            selectedSubject,
            sortBy,
            hasMore,
            cloning,
            showRating,
            ratingCourse,
            selectedRating,
            submittingRating,
            isAuthenticated,
            loadCourses,
            loadMore,
            searchCourses,
            filterBySubject,
            clearFilters,
            viewCourse,
            cloneCourse,
            showRatingModal,
            closeRatingModal,
            selectRating,
            submitRating,
            getStarRating,
            formatDate,
            hasUserRated,
            // notification state for template
            showNotification,
            notificationMessage,
            notificationType,
            renderMarkdown
        }
    }
}
</script>

<style scoped>
.library-view {
    padding: 2rem 0;
    min-height: calc(100vh - 200px);
}

.library-header {
    text-align: center;
    margin-bottom: 3rem;
}

.page-title {
    font-size: 3rem;
    font-weight: 700;
    color: var(--text-primary);
    margin-bottom: 0.5rem;
}

.page-subtitle {
    font-size: 1.2rem;
    color: var(--text-secondary);
    margin-bottom: 2rem;
}

.search-section {
    max-width: 800px;
    margin: 0 auto;
}

.search-bar {
    display: flex;
    gap: 0.5rem;
    margin-bottom: 1rem;
}

.search-input {
    flex: 1;
    padding: 1rem;
    border: 2px solid var(--border-color);
    border-radius: 0.75rem;
    background: var(--bg-secondary);
    color: var(--text-primary);
    font-size: 1rem;
    transition: border-color 0.3s ease;
}

.search-input:focus {
    outline: none;
    border-color: var(--accent-primary);
}

.search-btn {
    padding: 1rem 1.5rem;
    background: var(--accent-primary);
    color: white;
    border: none;
    border-radius: 0.75rem;
    font-size: 1.2rem;
    cursor: pointer;
    transition: background-color 0.3s ease;
}

.search-btn:hover:not(:disabled) {
    background: var(--accent-secondary);
}

.search-btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
}

.filter-section {
    display: flex;
    gap: 1rem;
    justify-content: center;
}

.subject-filter,
.sort-filter {
    padding: 0.75rem 1rem;
    border: 2px solid var(--border-color);
    border-radius: 0.5rem;
    background: var(--bg-secondary);
    color: var(--text-primary);
    cursor: pointer;
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
    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
    gap: 2rem;
}

.course-card {
    display: flex;
    flex-direction: column;
    height: 100%;
    position: relative;
    transition: all 0.3s ease;
}

.course-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 20px 40px rgba(119, 51, 255, 0.2);
}

.course-card-header {
    margin-bottom: 1rem;
}

.course-card-title {
    font-size: 1.4rem;
    font-weight: 600;
    color: var(--accent-primary);
    margin-bottom: 0.5rem;
    line-height: 1.3;
}

.course-rating {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-top: 0.5rem;
}

.stars {
    font-size: 0.9rem;
}

.rating-text {
    font-weight: 600;
    color: var(--text-primary);
}

.rating-count {
    font-size: 0.9rem;
    color: var(--text-secondary);
}

.course-description {
    margin-bottom: 1rem;
    flex: 1;
}

.course-description p {
    color: var(--text-secondary);
    line-height: 1.5;
    font-size: 0.95rem;
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
    font-size: 0.8rem;
}

.course-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    margin-bottom: 1rem;
}

.tag {
    background: linear-gradient(135deg, rgba(119, 51, 255, 0.2), rgba(0, 212, 255, 0.2));
    color: var(--accent-primary);
    padding: 0.25rem 0.5rem;
    border-radius: 0.25rem;
    font-size: 0.75rem;
    font-weight: 500;
}

.course-card-footer {
    display: flex;
    gap: 0.5rem;
    padding-top: 1rem;
    border-top: 1px solid var(--border-color);
    flex-wrap: wrap;
}

.btn-sm {
    padding: 0.5rem 1rem;
    font-size: 0.875rem;
    flex: 1;
    min-width: 80px;
}

.btn-outline {
    background: transparent;
    border: 1px solid var(--accent-primary);
    color: var(--accent-primary);
}

.btn-outline:hover {
    background: var(--accent-primary);
    color: white;
}

.load-more-section {
    text-align: center;
    padding: 2rem 0;
}

/* Modal Styles */
.modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
  /* Solid background (no transparency) to fully obscure underlying content */
  background: var(--bg-primary);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
}

.modal-content {
    background: var(--card-bg);
    padding: 2rem;
    border-radius: 1rem;
    border: 1px solid var(--border-color);
    max-width: 400px;
    width: 90%;
    text-align: center;
}

.modal-content h3 {
    color: var(--text-primary);
    margin-bottom: 1rem;
}

.rating-stars {
    display: flex;
    justify-content: center;
    gap: 0.5rem;
    margin: 2rem 0;
}

.star-btn {
    background: none;
    border: none;
    font-size: 2rem;
    cursor: pointer;
    opacity: 0.3;
    transition: opacity 0.2s ease;
}

.star-btn.active {
    opacity: 1;
}

.star-btn:hover {
    opacity: 0.8;
}

.modal-actions {
    display: flex;
    gap: 1rem;
    justify-content: center;
    margin-top: 2rem;
}

@media (max-width: 768px) {
    .courses-grid {
        grid-template-columns: 1fr;
    }

    .filter-section {
        flex-direction: column;
        align-items: center;
    }

    .course-card-footer {
        flex-direction: column;
    }

    .btn-sm {
        flex: none;
    }
}

/* In-app notification */
.app-notification {
    position: fixed;
    top: 20px;
    right: 20px;
    z-index: 2000;
    padding: 0.75rem 1rem;
    border-radius: 0.5rem;
    color: white;
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.2);
}

.app-notification.success {
    background: linear-gradient(90deg, #2ecc71, #27ae60);
}

.app-notification.error {
    background: linear-gradient(90deg, #ff7a7a, #ff4d4d);
}
</style>