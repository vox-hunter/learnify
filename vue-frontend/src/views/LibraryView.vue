<template>
  <div class="library-view">
    <div class="container">
      <div
        v-if="showNotification"
        :class="['app-notification', notificationType]"
      >
        {{ notificationMessage }}
      </div>
      <div class="library-header">
        <h1 class="page-title">
          Library
        </h1>
        <p class="page-subtitle">
          Explore and learn from courses and flashcards created by the community
        </p>

        <div class="search-section">
          <div class="search-bar">
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Search the library by title, topic, or keyword..."
              class="search-input"
              @keyup.enter="searchLibrary"
            >
            <button
              class="search-btn"
              :disabled="loading"
              @click="searchLibrary"
            >
              🔍
            </button>
          </div>

          <div class="filter-section">
            <select
              v-model="contentType"
              class="type-filter"
              @change="onContentTypeChange"
            >
              <option value="both">
                Courses & Flashcards
              </option>
              <option value="courses">
                Courses Only
              </option>
              <option value="flashcards">
                Flashcards Only
              </option>
            </select>

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
              @change="onSortChange"
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

      <div
        v-if="loading"
        class="loading-state"
      >
        <div class="spinner" />
        <p>Loading library items...</p>
      </div>

      <div
        v-else-if="libraryItems.length === 0"
        class="empty-state card"
      >
        <div class="empty-icon">
          📚
        </div>
        <h2>No items found</h2>
        <p v-if="searchQuery">
          Try different keywords or browse all items.
        </p>
        <p v-else>
          No community items available yet. Be the first to share one!
        </p>
        <button
          v-if="searchQuery || selectedSubject || contentType !== 'both'"
          class="btn btn-secondary"
          @click="clearFilters"
        >
          Clear Filters
        </button>
      </div>

      <div
        v-else
        class="library-grid"
      >
        <div
          v-for="item in libraryItems"
          :key="`${item.type}-${item.id}`"
          :class="['card', item.type === 'course' ? 'course-card' : 'flashcard-card']"
        >
          <template v-if="item.type === 'course'">
            <div class="course-card-header">
              <h3 class="library-card-title">
                <div v-html="renderMarkdown(item.raw.course_title || 'Untitled Course')" />
              </h3>
              <div
                v-if="item.rating > 0"
                class="course-rating"
              >
                <span class="stars">
                  {{ getStarRating(item.rating) }}
                </span>
                <span class="rating-text">{{ item.rating.toFixed(1) }}</span>
                <span class="rating-count">({{ item.totalRatings }})</span>
              </div>
            </div>

            <div
              v-if="item.raw.description"
              class="course-description"
            >
              <div v-html="renderMarkdown(item.raw.description)" />
            </div>

            <div class="course-card-meta">
              <span class="meta-badge">
                📚 {{ item.raw.total_sections || 0 }} Sections
              </span>
              <span class="meta-badge">
                ❓ {{ item.raw.total_questions || 0 }} Questions
              </span>
              <span
                v-if="item.raw.subject"
                class="meta-badge"
              >
                🏷️ {{ item.raw.subject }}
              </span>
              <span class="meta-badge">
                👤 {{ item.raw.creator || 'Anonymous' }}
              </span>
              <span class="meta-badge">
                📅 {{ formatDate(item.raw.created_at) }}
              </span>
              <span
                v-if="item.hasFlashcards"
                class="status-badge"
              >
                Flashcards Available
              </span>
            </div>

            <div
              v-if="item.raw.tags && item.raw.tags.length > 0"
              class="course-tags"
            >
              <span
                v-for="tag in item.raw.tags.slice(0, 3)"
                :key="tag"
                class="tag"
              >
                {{ tag }}
              </span>
            </div>

            <div class="course-card-footer">
              <button
                class="btn btn-secondary btn-sm"
                :disabled="isCloning('course', item.id)"
                @click="!isCloning('course', item.id) && viewCourse(item.id)"
              >
                View Course
              </button>
              <button
                class="btn btn-primary btn-sm"
                :disabled="isCloning('course', item.id)"
                @click="cloneCourse(item.id)"
              >
                <span v-if="!isCloning('course', item.id)">Clone & Edit</span>
                <span v-else>Cloning...</span>
              </button>
              <button
                class="btn btn-outline btn-sm"
                :disabled="hasUserRated(item.id, 'course')"
                :title="hasUserRated(item.id, 'course') ? 'You have already rated this course' : 'Rate this course'"
                @click="showRatingModal(item)"
              >
                {{ hasUserRated(item.id, 'course') ? 'Rated' : 'Rate' }}
              </button>
            </div>
          </template>

          <template v-else>
            <div class="course-card-header">
              <h3 class="library-card-title">
                <div v-html="renderMarkdown(item.raw.flashcard_title || 'Untitled Flashcards')" />
              </h3>
              <div
                v-if="item.rating > 0"
                class="course-rating"
              >
                <span class="stars">
                  {{ getStarRating(item.rating) }}
                </span>
                <span class="rating-text">{{ item.rating.toFixed(1) }}</span>
                <span class="rating-count">({{ item.totalRatings }})</span>
              </div>
            </div>

            <div
              v-if="item.previewCards.length"
              class="flashcard-preview"
            >
              <div
                v-for="(card, index) in item.previewCards"
                :key="index"
                class="flashcard-preview-card"
              >
                <strong>Card {{ index + 1 }}</strong>
                <div v-html="renderMarkdown(card.front)" />
              </div>
            </div>

            <div class="course-card-meta">
              <span class="meta-badge">
                🗂️ {{ item.raw.total_cards || 0 }} Cards
              </span>
              <span
                v-if="item.raw.subject"
                class="meta-badge"
              >
                🏷️ {{ item.raw.subject }}
              </span>
              <span class="meta-badge">
                👤 {{ item.raw.creator || 'Anonymous' }}
              </span>
              <span class="meta-badge">
                📅 {{ formatDate(item.raw.created_at) }}
              </span>
              <span
                v-if="item.raw.source_course_id"
                class="meta-badge"
              >
                🔗 Linked Course
              </span>
            </div>

            <div class="course-card-footer">
              <button
                class="btn btn-secondary btn-sm"
                :disabled="isCloning('flashcard', item.id)"
                @click="!isCloning('flashcard', item.id) && viewFlashcard(item.id)"
              >
                Study Flashcards
              </button>
              <button
                class="btn btn-primary btn-sm"
                :disabled="isCloning('flashcard', item.id)"
                @click="cloneFlashcard(item.id)"
              >
                <span v-if="!isCloning('flashcard', item.id)">Clone & Edit</span>
                <span v-else>Cloning...</span>
              </button>
              <button
                class="btn btn-outline btn-sm"
                :disabled="hasUserRated(item.id, 'flashcard')"
                :title="hasUserRated(item.id, 'flashcard') ? 'You have already rated this flashcard set' : 'Rate this flashcard set'"
                @click="showRatingModal(item)"
              >
                {{ hasUserRated(item.id, 'flashcard') ? 'Rated' : 'Rate' }}
              </button>
            </div>
          </template>
        </div>
      </div>

      <div
        v-if="libraryItems.length > 0 && hasMore"
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

    <div
      v-if="showRating"
      class="modal-overlay"
      @click="closeRatingModal"
    >
      <div
        class="modal-content"
        @click.stop
      >
        <h3>Rate {{ ratingItem?.type === 'flashcard' ? 'Flashcard Set' : 'Course' }}</h3>
        <p>{{ ratingItem?.title }}</p>

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
import api from '../services/api'
import MarkdownIt from 'markdown-it'
import DOMPurify from 'dompurify'

const PAGE_SIZE = 20

export default {
  name: 'LibraryView',
  setup() {
    const router = useRouter()
    const authStore = useAuthStore()

    const courses = ref([])
    const flashcards = ref([])
    const loading = ref(false)
    const searchQuery = ref('')
    const selectedSubject = ref('')
    const contentType = ref('both')
    const sortBy = ref('created_at')
    const currentPage = ref(0)
    const hasMoreState = ref({ courses: true, flashcards: true })
    const cloning = ref({})
    const navigatingToCourseId = ref(null)
    const navigatingToFlashcardId = ref(null)

    const showRating = ref(false)
    const ratingItem = ref(null)
    const selectedRating = ref(0)
    const submittingRating = ref(false)

    const showNotification = ref(false)
    const notificationMessage = ref('')
    const notificationType = ref('success')

    const isAuthenticated = computed(() => authStore.isAuthenticated)

    const md = new MarkdownIt({ html: false, linkify: true, typographer: true })
    const renderMarkdown = (text) => {
      if (!text) return ''
      const rendered = md.render(String(text))
      return DOMPurify.sanitize(rendered, { USE_PROFILES: { html: true } })
    }

    const typesetMathJax = () => {
      nextTick(() => {
        if (window.MathJax && window.MathJax.typesetPromise) {
          const elements = document.querySelectorAll('.library-card-title, .meta-badge, .flashcard-preview')
          window.MathJax.typesetPromise(Array.from(elements)).catch(() => {})
        }
      })
    }

    const hasMore = computed(() => {
      if (contentType.value === 'courses') return hasMoreState.value.courses
      if (contentType.value === 'flashcards') return hasMoreState.value.flashcards
      return hasMoreState.value.courses || hasMoreState.value.flashcards
    })

    const buildQueryParams = () => {
      const params = new URLSearchParams({
        content_type: contentType.value,
        page: currentPage.value.toString(),
        limit: PAGE_SIZE.toString(),
        sort_by: sortBy.value,
        sort_order: sortBy.value === 'title' ? '1' : '-1'
      })

      if (searchQuery.value.trim()) {
        params.set('q', searchQuery.value.trim())
      } else if (selectedSubject.value) {
        params.set('subject', selectedSubject.value)
      }

      return params
    }

    const loadLibraryContent = async (reset = true) => {
      if (loading.value) return
      loading.value = true

      if (reset) {
        currentPage.value = 0
        courses.value = []
        flashcards.value = []
        hasMoreState.value = { courses: true, flashcards: true }
      }

      try {
        const response = await api.get(`/library/content?${buildQueryParams().toString()}`)
        const { courses: newCourses = [], flashcards: newFlashcards = [], has_more: hasMoreData = {} } = response.data || {}

        if (contentType.value !== 'flashcards') {
          courses.value = reset ? newCourses : [...courses.value, ...newCourses]
        }
        if (contentType.value !== 'courses') {
          flashcards.value = reset ? newFlashcards : [...flashcards.value, ...newFlashcards]
        }

        if (contentType.value === 'courses') {
          hasMoreState.value = {
            courses: hasMoreData?.courses ?? (newCourses.length === PAGE_SIZE),
            flashcards: false
          }
        } else if (contentType.value === 'flashcards') {
          hasMoreState.value = {
            courses: false,
            flashcards: hasMoreData?.flashcards ?? (newFlashcards.length === PAGE_SIZE)
          }
        } else {
          hasMoreState.value = {
            courses: hasMoreData?.courses ?? (newCourses.length === PAGE_SIZE),
            flashcards: hasMoreData?.flashcards ?? (newFlashcards.length === PAGE_SIZE)
          }
        }

        await nextTick()
        typesetMathJax()
      } catch (error) {
        console.error('Error loading library content:', error)
        if (reset) {
          courses.value = []
          flashcards.value = []
        }
      } finally {
        loading.value = false
      }
    }

    const libraryItems = computed(() => {
      const items = []

      if (contentType.value !== 'flashcards') {
        items.push(...courses.value.map((course) => ({
          type: 'course',
          id: course.course_id,
          title: course.course_title || 'Untitled Course',
          rating: course.rating || 0,
          totalRatings: course.total_ratings || 0,
          createdAt: course.created_at,
          popularityScore: course.popularity_score || 0,
          hasFlashcards: Boolean(course.has_flashcards),
          linkedFlashcardCount: course.linked_flashcard_count || 0,
          raw: course
        })))
      }

      if (contentType.value !== 'courses') {
        items.push(...flashcards.value.map((flashcard) => ({
          type: 'flashcard',
          id: flashcard.flashcard_id,
          title: flashcard.flashcard_title || 'Untitled Flashcards',
          rating: flashcard.rating || 0,
          totalRatings: flashcard.total_ratings || 0,
          createdAt: flashcard.created_at,
          popularityScore: flashcard.popularity_score || 0,
          previewCards: Array.isArray(flashcard.cards) ? flashcard.cards.slice(0, 2) : [],
          raw: flashcard
        })))
      }

      const getSortValue = (item) => {
        switch (sortBy.value) {
          case 'rating':
            return item.rating || 0
          case 'popularity_score':
            return item.popularityScore || 0
          case 'title':
            return (item.title || '').toLowerCase()
          case 'created_at':
          default:
            return item.createdAt ? new Date(item.createdAt).getTime() : 0
        }
      }

      return items.sort((a, b) => {
        const valueA = getSortValue(a)
        const valueB = getSortValue(b)

        if (sortBy.value === 'title') {
          const compare = valueA.localeCompare(valueB)
          if (compare !== 0) return compare
          return a.title.localeCompare(b.title)
        }

        const diff = (valueB || 0) - (valueA || 0)
        if (diff !== 0) return diff
        return a.title.localeCompare(b.title)
      })
    })

    const isCloning = (type, id) => Boolean(cloning.value[`${type}_${id}`])

    const loadMore = () => {
      if (!hasMore.value || loading.value) return
      currentPage.value += 1
      loadLibraryContent(false)
    }

    const searchLibrary = () => {
      loadLibraryContent(true)
    }

    const filterBySubject = () => {
      searchQuery.value = ''
      loadLibraryContent(true)
    }

    const clearFilters = () => {
      searchQuery.value = ''
      selectedSubject.value = ''
      contentType.value = 'both'
      loadLibraryContent(true)
    }

    const onContentTypeChange = () => {
      loadLibraryContent(true)
    }

    const onSortChange = () => {
      loadLibraryContent(true)
    }

    const viewCourse = (courseId) => {
      router.push(`/course/${courseId}`)
    }

    const viewFlashcard = (flashcardId) => {
      router.push(`/flashcard/${flashcardId}`)
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
      const key = `course_${courseId}`
      if (isCloning('course', courseId)) return

      cloning.value = { ...cloning.value, [key]: true }

      try {
        const params = isAuthenticated.value ? { username: authStore.user?.username } : {}
        const response = await api.post(`/library/course/${courseId}/clone`, {}, { params })

        if (response.data.success) {
          showNotificationMessage('Course cloned successfully! You can find it in your courses.', 'success')
          navigatingToCourseId.value = response.data.course_id
          setTimeout(() => {
            if (router.currentRoute.value.params.id !== response.data.course_id &&
                navigatingToCourseId.value === response.data.course_id) {
              router.push(`/course/${response.data.course_id}`)
            }
          }, 300)
        }
      } catch (error) {
        console.error('Error cloning course:', error)
        showNotificationMessage('Failed to clone course. Please try again.', 'error')
      } finally {
        cloning.value = { ...cloning.value, [key]: false }
      }
    }

    const cloneFlashcard = async (flashcardId) => {
      const key = `flashcard_${flashcardId}`
      if (isCloning('flashcard', flashcardId)) return

      cloning.value = { ...cloning.value, [key]: true }

      try {
        const params = isAuthenticated.value ? { username: authStore.user?.username } : {}
        const response = await api.post(`/library/flashcard/${flashcardId}/clone`, {}, { params })

        if (response.data.success) {
          showNotificationMessage('Flashcard set cloned successfully! You can review it now.', 'success')
          navigatingToFlashcardId.value = response.data.flashcard_id
          setTimeout(() => {
            if (router.currentRoute.value.params.id !== response.data.flashcard_id &&
                navigatingToFlashcardId.value === response.data.flashcard_id) {
              router.push(`/flashcard/${response.data.flashcard_id}`)
            }
          }, 300)
        }
      } catch (error) {
        console.error('Error cloning flashcards:', error)
        showNotificationMessage('Failed to clone flashcards. Please try again.', 'error')
      } finally {
        cloning.value = { ...cloning.value, [key]: false }
      }
    }

    const getRatingsKey = (type) => {
      const username = authStore.user?.username || 'guest'
      return type === 'flashcard' ? `flashcard_ratings_${username}` : `user_ratings_${username}`
    }

    const hasUserRated = (itemId, type) => {
      const ratingsData = localStorage.getItem(getRatingsKey(type))
      if (!ratingsData) return false
      try {
        const ratings = JSON.parse(ratingsData)
        return ratings.includes(itemId)
      } catch {
        return false
      }
    }

    const markItemAsRated = (itemId, type) => {
      const key = getRatingsKey(type)
      const existing = localStorage.getItem(key)
      let ratings = []
      if (existing) {
        try {
          ratings = JSON.parse(existing)
        } catch {
          ratings = []
        }
      }
      if (!ratings.includes(itemId)) {
        ratings.push(itemId)
        localStorage.setItem(key, JSON.stringify(ratings))
      }
    }

    const showRatingModal = (item) => {
      if (!isAuthenticated.value) {
        showNotificationMessage('Please log in to rate items', 'error', 3000)
        return
      }
      ratingItem.value = item
      selectedRating.value = 0
      showRating.value = true
    }

    const closeRatingModal = () => {
      showRating.value = false
      ratingItem.value = null
      selectedRating.value = 0
    }

    const selectRating = (rating) => {
      selectedRating.value = rating
    }

    const submitRating = async () => {
      if (!ratingItem.value || selectedRating.value === 0) return

      const item = ratingItem.value
      const ratingValue = selectedRating.value

      if (hasUserRated(item.id, item.type)) {
        closeRatingModal()
        showNotificationMessage('You have already rated this item', 'error', 3000)
        return
      }

      closeRatingModal()
      markItemAsRated(item.id, item.type)

      const targetList = item.type === 'course' ? courses : flashcards
      const idKey = item.type === 'course' ? 'course_id' : 'flashcard_id'
      const target = targetList.value.find(entry => entry[idKey] === item.id)
      let rollbackData = null

      if (target) {
        rollbackData = { rating: target.rating || 0, total_ratings: target.total_ratings || 0 }
        const originalRating = target.rating || 0
        const originalTotal = target.total_ratings || 0
        const newTotal = originalTotal + 1
        const newAverage = ((originalRating * originalTotal) + ratingValue) / newTotal
        target.rating = newAverage
        target.total_ratings = newTotal
      }

      showNotificationMessage('Thanks for rating — submitted!')

      try {
        const params = isAuthenticated.value ? { username: authStore.user?.username } : {}
        const endpoint = item.type === 'course'
          ? `/library/course/${item.id}/rate`
          : `/library/flashcard/${item.id}/rate`

        submittingRating.value = true
        await api.post(endpoint, { rating: ratingValue }, { params })
        loadLibraryContent(true)
      } catch (error) {
        console.error('Error submitting rating:', error)
        if (target && rollbackData) {
          target.rating = rollbackData.rating
          target.total_ratings = rollbackData.total_ratings
        }
        showNotificationMessage('Failed to submit rating. Reverted.', 'error')
      } finally {
        submittingRating.value = false
      }
    }

    const getStarRating = (rating) => {
      const fullStars = Math.floor(rating)
      const hasHalfStar = rating % 1 >= 0.5
      return '⭐'.repeat(fullStars) + (hasHalfStar ? '⭐' : '')
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
      loadLibraryContent(true)
    })

    watch([courses, flashcards], () => {
      typesetMathJax()
    })

    return {
      libraryItems,
      loading,
      searchQuery,
      selectedSubject,
      contentType,
      sortBy,
      hasMore,
      showNotification,
      notificationMessage,
      notificationType,
      searchLibrary,
      filterBySubject,
      clearFilters,
      onContentTypeChange,
      onSortChange,
      loadMore,
      viewCourse,
      viewFlashcard,
      cloneCourse,
      cloneFlashcard,
      showRatingModal,
      closeRatingModal,
      selectRating,
      submitRating,
      getStarRating,
      formatDate,
      hasUserRated,
      renderMarkdown,
      showRating,
      ratingItem,
      selectedRating,
      submittingRating,
      isAuthenticated,
      isCloning
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

.type-filter,
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

.library-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
    gap: 2rem;
}

.course-card,
.flashcard-card {
  display: flex;
  flex-direction: column;
  height: 100%;
  position: relative;
  transition: all 0.3s ease;
}

.course-card:hover,
.flashcard-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 20px 40px rgba(119, 51, 255, 0.2);
}

.course-card-header {
    margin-bottom: 1rem;
}

.library-card-title {
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

.status-badge {
  background: linear-gradient(135deg, rgba(119, 51, 255, 0.15), rgba(0, 212, 255, 0.15));
  color: var(--accent-primary);
  padding: 0.25rem 0.75rem;
  border-radius: 0.5rem;
  font-size: 0.8rem;
  font-weight: 600;
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

.flashcard-preview {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.flashcard-preview-card {
  background: var(--bg-tertiary);
  border-radius: 0.5rem;
  padding: 0.75rem;
  color: var(--text-secondary);
  font-size: 0.9rem;
  line-height: 1.4;
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
  .library-grid {
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