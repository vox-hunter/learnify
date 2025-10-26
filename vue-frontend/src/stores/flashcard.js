import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../services/api'
import { useAuthStore } from './auth'

export const useFlashcardStore = defineStore('flashcard', () => {
  const flashcards = ref([])
  const currentFlashcard = ref(null)
  const loading = ref(false)
  const error = ref(null)
  const guestFlashcardCount = ref(parseInt(localStorage.getItem('guestFlashcardCount') || '0'))
  
  // Cache for loaded flashcards to prevent redundant fetches
  const flashcardCache = ref(new Map())

  // Guest user limit
  const GUEST_FLASHCARD_LIMIT = 3

  const canGenerateFlashcard = computed(() => {
    const authStore = useAuthStore()
    if (authStore.isAuthenticated) {
      console.log('[Flashcard Store] User authenticated, unlimited flashcards')
      return true
    }
    console.log(`[Flashcard Store] Guest check: ${guestFlashcardCount.value}/${GUEST_FLASHCARD_LIMIT} flashcards saved`)
    return guestFlashcardCount.value < GUEST_FLASHCARD_LIMIT
  })

  const remainingGuestFlashcards = computed(() => {
    return Math.max(0, GUEST_FLASHCARD_LIMIT - guestFlashcardCount.value)
  })

  function incrementGuestFlashcardCount() {
    guestFlashcardCount.value++
    localStorage.setItem('guestFlashcardCount', guestFlashcardCount.value.toString())
  }

  function saveToLocalStorage(flashcard) {
    try {
      const flashcardId = Date.now().toString()
      console.log('[Flashcard Store] saveToLocalStorage - generating ID:', flashcardId)
      const storedFlashcards = JSON.parse(localStorage.getItem('guestFlashcards') || '[]')
      console.log('[Flashcard Store] Current stored flashcards:', storedFlashcards.length)
      const newFlashcard = {
        ...flashcard,
        flashcard_id: flashcardId,
        created_at: new Date().toISOString()
      }
      storedFlashcards.push(newFlashcard)
      localStorage.setItem('guestFlashcards', JSON.stringify(storedFlashcards))
      console.log('[Flashcard Store] ✅ Saved to localStorage successfully')
      return flashcardId
    } catch (e) {
      console.error('Failed to save flashcard to localStorage:', e)
      return null
    }
  }

  function loadFromLocalStorage() {
    try {
      const flashcards = JSON.parse(localStorage.getItem('guestFlashcards') || '[]')
      console.log('[Flashcard Store] loadFromLocalStorage - found', flashcards.length, 'flashcards')
      if (flashcards.length > 0) {
        console.log('[Flashcard Store] Flashcard IDs:', flashcards.map(f => f.flashcard_id))
      }
      return flashcards
    } catch (e) {
      console.error('Failed to load flashcards from localStorage:', e)
      return []
    }
  }

  async function generateFlashcard(message, file = null) {
    loading.value = true
    error.value = null
    
    try {
      const formData = new FormData()
      formData.append('message', message)
      if (file) {
        formData.append('file', file)
      }
      
      const response = await api.post('/chat/message', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
      
      if (!response.data.success) {
        throw new Error(response.data.error || 'Flashcard generation failed')
      }

      // Check if AI detected and generated flashcards
      if (response.data.is_flashcard && response.data.flashcard_data) {
        currentFlashcard.value = response.data.flashcard_data
        return { success: true, flashcard: response.data.flashcard_data }
      } else {
        // AI didn't generate flashcards - maybe not suitable content
        error.value = 'The uploaded file does not contain suitable content for flashcard generation. Please try a different file with educational material.'
        return { success: false, error: error.value }
      }
    } catch (err) {
      error.value = err.response?.data?.detail || err.message || 'Flashcard generation failed'
      return { success: false, error: error.value }
    } finally {
      loading.value = false
    }
  }

  function invalidateFlashcard(flashcardId) {
    flashcardCache.value.delete(flashcardId)
    console.log(`[Flashcard Store] Invalidated cache for flashcard ${flashcardId}`)
  }

  async function saveFlashcard(flashcardData, flashcardTitle, sourceCourseId = null) {
    const authStore = useAuthStore()
    console.log('[Flashcard Store] saveFlashcard called')
    console.log('[Flashcard Store] Is authenticated:', authStore.isAuthenticated)
    console.log('[Flashcard Store] Flashcard title:', flashcardTitle)
    console.log('[Flashcard Store] Guest flashcard count:', guestFlashcardCount.value)
    
    // If not authenticated, save to localStorage
    if (!authStore.isAuthenticated) {
      console.log('[Flashcard Store] Guest user - checking limit')
      console.log('[Flashcard Store] canGenerateFlashcard.value:', canGenerateFlashcard.value)
      // Check if guest has reached the limit
      if (!canGenerateFlashcard.value) {
        console.log('[Flashcard Store] ❌ Guest limit reached! Requiring login.')
        error.value = 'You have reached the limit of 3 saved flashcard sets as a guest. Please log in to save more flashcards.'
        return { 
          success: false, 
          error: error.value,
          requiresLogin: true
        }
      }
      
      console.log('[Flashcard Store] ✅ Guest within limit - saving to localStorage')
      const flashcardId = saveToLocalStorage({
        flashcard_title: flashcardTitle,
        cards: flashcardData,
        source_course_id: sourceCourseId
      })
      console.log('[Flashcard Store] Saved with ID:', flashcardId)
      // Guard: only increment if save was successful
      if (!flashcardId) {
        error.value = 'Failed to save flashcard to localStorage. Please try again.'
        return { success: false, error: error.value }
      }
      // Increment guest flashcard count when flashcard is actually saved
      incrementGuestFlashcardCount()
      console.log('[Flashcard Store] New guest flashcard count:', guestFlashcardCount.value)
      return { success: true, flashcardId: flashcardId, isLocal: true }
    }
    
    try {
      const response = await api.post('/flashcard/save', {
        flashcard_data: flashcardData,
        flashcard_title: flashcardTitle,
        source_course_id: sourceCourseId
      }, {
        params: { username: authStore.user?.username }
      })
      // Cache the newly saved flashcard
      if (response.data.flashcard_id && flashcardData) {
        flashcardCache.value.set(response.data.flashcard_id, {
          flashcard_id: response.data.flashcard_id,
          flashcard_title: flashcardTitle,
          cards: flashcardData,
          source_course_id: sourceCourseId
        })
      }
      return { success: true, flashcardId: response.data.flashcard_id }
    } catch (err) {
      return { 
        success: false, 
        error: err.response?.data?.detail || 'Failed to save flashcard' 
      }
    }
  }

  async function loadFlashcards() {
    const authStore = useAuthStore()
    loading.value = true
    console.log('[Flashcard Store] loadFlashcards started. Authenticated:', authStore.isAuthenticated)
    try {
      if (!authStore.isAuthenticated) {
        // Load from localStorage for guest users
        flashcards.value = loadFromLocalStorage()
        console.log('[Flashcard Store] Loaded flashcards from localStorage:', flashcards.value.length)
      } else {
        // Load from API for authenticated users
        const response = await api.get('/flashcards', {
          params: { username: authStore.user?.username }
        })
        flashcards.value = response.data.flashcards || []
        console.log('[Flashcard Store] Loaded flashcards from API:', flashcards.value.length)
      }
    } catch (err) {
      console.error('[Flashcard Store] loadFlashcards error:', err)
      error.value = err.response?.data?.detail || 'Failed to load flashcards'
      flashcards.value = []
    } finally {
      loading.value = false
    }
  }

  async function loadFlashcard(flashcardId) {
    // Check cache first to prevent redundant fetches
    if (flashcardCache.value.has(flashcardId)) {
      console.log(`[Flashcard Store] Loading flashcard ${flashcardId} from cache`)
      const cachedFlashcard = flashcardCache.value.get(flashcardId)
      currentFlashcard.value = cachedFlashcard
      return { success: true, flashcard: cachedFlashcard }
    }
    
    loading.value = true
    const authStore = useAuthStore()
    console.log(`[Flashcard Store] loadFlashcard called with flashcardId: ${flashcardId}`)
    console.log(`[Flashcard Store] User authenticated: ${authStore.isAuthenticated}`)
    
    try {
      // For guest users, try localStorage first
      if (!authStore.isAuthenticated) {
        console.log('[Flashcard Store] Guest user - checking localStorage')
        const localFlashcards = loadFromLocalStorage()
        console.log(`[Flashcard Store] Found ${localFlashcards.length} flashcards in localStorage`)
        const localFlashcard = localFlashcards.find(f => f.flashcard_id === flashcardId)
        
        if (localFlashcard) {
          console.log('[Flashcard Store] Found flashcard in localStorage:', localFlashcard.flashcard_title)
          // Transform localStorage format to match API format
          currentFlashcard.value = {
            flashcard_id: localFlashcard.flashcard_id,
            flashcard_title: localFlashcard.flashcard_title,
            cards: localFlashcard.cards,
            source_course_id: localFlashcard.source_course_id
          }
          // Cache the loaded flashcard
          flashcardCache.value.set(flashcardId, currentFlashcard.value)
          loading.value = false
          return { success: true, flashcard: currentFlashcard.value }
        } else {
          console.log('[Flashcard Store] Flashcard NOT found in localStorage - will try to load from API')
        }
      }
      
      // Try loading from API (for authenticated users or if not found in localStorage)
      console.log('[Flashcard Store] Attempting to load from API')
      const response = await api.get(`/flashcard/${flashcardId}`)
      currentFlashcard.value = response.data
      // Cache the loaded flashcard
      flashcardCache.value.set(flashcardId, currentFlashcard.value)
      console.log('[Flashcard Store] Successfully loaded from API')
      return { success: true, flashcard: response.data }
    } catch (err) {
      console.error('[Flashcard Store] Error loading flashcard:', err)
      error.value = err.response?.data?.detail || 'Failed to load flashcard'
      return { success: false, error: error.value }
    } finally {
      loading.value = false
    }
  }

  async function loadFlashcardsByCourse(courseId) {
    const authStore = useAuthStore()
    console.log('[Flashcard Store] loadFlashcardsByCourse called with courseId:', courseId)
    
    try {
      if (!authStore.isAuthenticated) {
        // Filter localStorage flashcards by source_course_id for guest users
        console.log('[Flashcard Store] Guest user - filtering localStorage by course')
        const localFlashcards = loadFromLocalStorage()
        const filtered = localFlashcards.filter(f => String(f.source_course_id) === String(courseId))
        console.log(`[Flashcard Store] Found ${filtered.length} flashcards for course ${courseId}`)
        return filtered
      } else {
        // Load from API for authenticated users
        const response = await api.get(`/flashcards/by-course/${courseId}`, {
          params: { username: authStore.user?.username }
        })
        console.log('[Flashcard Store] Loaded flashcards by course from API:', response.data.flashcards?.length || 0)
        return response.data.flashcards || []
      }
    } catch (err) {
      console.error('[Flashcard Store] Error loading flashcards by course:', err)
      error.value = err.response?.data?.detail || 'Failed to load flashcards by course'
      return []
    }
  }

  async function deleteFlashcard(flashcardId) {
    const authStore = useAuthStore()
    // Clear from cache
    flashcardCache.value.delete(flashcardId)
    
    // If guest user, remove from localStorage
    if (!authStore.isAuthenticated) {
      const stored = JSON.parse(localStorage.getItem('guestFlashcards') || '[]')
      const remaining = stored.filter(f => f.flashcard_id !== flashcardId)
      localStorage.setItem('guestFlashcards', JSON.stringify(remaining))
      // Decrement guest flashcard count
      if (guestFlashcardCount.value > 0) {
        guestFlashcardCount.value--
        localStorage.setItem('guestFlashcardCount', guestFlashcardCount.value.toString())
      }
      // Update in-memory list if loaded
      flashcards.value = flashcards.value.filter(f => (f.flashcard_id || f._id) !== flashcardId)
      return { success: true, isLocal: true }
    }
    
    // Authenticated user - call API
    try {
      await api.delete(`/flashcard/${flashcardId}`, {
        params: { username: authStore.user?.username }
      })
      // Remove from in-memory list
      flashcards.value = flashcards.value.filter(f => (f.flashcard_id || f._id) !== flashcardId)
      return { success: true }
    } catch (e) {
      return { success: false, error: e }
    }
  }

  async function updateFlashcardProgress(flashcardId, studiedCards, masteryLevels, accuracyRate) {
    const authStore = useAuthStore()
    const progressData = {
      studied_cards: studiedCards,
      mastery_levels: masteryLevels,
      last_studied: new Date().toISOString(),
      accuracy_rate: accuracyRate
    }
    
    try {
      // Only make API call if authenticated
      if (authStore.isAuthenticated) {
        await api.post(`/flashcard/${flashcardId}/progress`, progressData)
      }
      
      // Always save to localStorage for persistence
      const progressKey = `flashcard_progress_${flashcardId}`
      localStorage.setItem(progressKey, JSON.stringify(progressData))
      
      return { success: true }
    } catch (err) {
      console.error('[Flashcard Store] Error updating progress:', err)
      return { success: false, error: 'Failed to update progress' }
    }
  }

  async function loadFlashcardProgress(flashcardId) {
    const authStore = useAuthStore()
    
    try {
      // Only make API call if authenticated
      if (authStore.isAuthenticated) {
        const response = await api.get(`/flashcard/${flashcardId}/progress`)
        return { success: true, progress: response.data }
      }
      
      // For guests, load from localStorage only
      const progressKey = `flashcard_progress_${flashcardId}`
      const savedProgress = localStorage.getItem(progressKey)
      
      if (savedProgress) {
        return { success: true, progress: JSON.parse(savedProgress) }
      }
      
      return { success: false, progress: null }
    } catch {
      // Fallback to localStorage on API error
      const progressKey = `flashcard_progress_${flashcardId}`
      const savedProgress = localStorage.getItem(progressKey)
      
      if (savedProgress) {
        return { success: true, progress: JSON.parse(savedProgress) }
      }
      
      return { success: false, progress: null }
    }
  }

  // Clear entire cache (useful when user logs out or switches accounts)
  function clearCache() {
    flashcardCache.value.clear()
    console.log('[Flashcard Store] Cache cleared')
  }

  // Match mode statistics functions
  async function saveMatchModeStats(flashcardId, statsData) {
    const authStore = useAuthStore()
    
    try {
      // Only make API call if authenticated
      if (authStore.isAuthenticated) {
        await api.post(`/flashcard/${flashcardId}/match-stats`, statsData)
      }
      
      // Always save to localStorage for persistence
      const statsKey = `match_stats_${flashcardId}`
      const existingStats = JSON.parse(localStorage.getItem(statsKey) || 'null')
      
      // Update local stats
      const updatedStats = {
        personal_best_time: existingStats?.personal_best_time 
          ? Math.min(existingStats.personal_best_time, statsData.completion_time)
          : statsData.completion_time,
        best_moves: existingStats?.best_moves
          ? Math.min(existingStats.best_moves, statsData.moves_count)
          : statsData.moves_count,
        games_played: (existingStats?.games_played || 0) + 1,
        total_time: (existingStats?.total_time || 0) + statsData.completion_time,
        total_moves: (existingStats?.total_moves || 0) + statsData.moves_count,
        last_played: statsData.timestamp
      }
      
      updatedStats.average_time = updatedStats.total_time / updatedStats.games_played
      updatedStats.average_moves = updatedStats.total_moves / updatedStats.games_played
      
      localStorage.setItem(statsKey, JSON.stringify(updatedStats))
      
      return { success: true, stats: updatedStats }
    } catch (err) {
      console.error('[Flashcard Store] Error saving match stats:', err)
      return { success: false, error: 'Failed to save match statistics' }
    }
  }

  async function loadMatchModeStats(flashcardId) {
    const authStore = useAuthStore()
    
    try {
      // Only make API call if authenticated
      if (authStore.isAuthenticated) {
        const response = await api.get(`/flashcard/${flashcardId}/match-stats`)
        return { success: true, stats: response.data }
      }
      
      // For guests, load from localStorage only
      const statsKey = `match_stats_${flashcardId}`
      const savedStats = localStorage.getItem(statsKey)
      
      if (savedStats) {
        return { success: true, stats: JSON.parse(savedStats) }
      }
      
      return { success: false, stats: null }
    } catch {
      // Fallback to localStorage on API error
      const statsKey = `match_stats_${flashcardId}`
      const savedStats = localStorage.getItem(statsKey)
      
      if (savedStats) {
        return { success: true, stats: JSON.parse(savedStats) }
      }
      
      return { success: false, stats: null }
    }
  }

  return {
    flashcards,
    currentFlashcard,
    loading,
    error,
    guestFlashcardCount,
    canGenerateFlashcard,
    remainingGuestFlashcards,
    generateFlashcard,
    saveFlashcard,
    loadFlashcards,
    loadFlashcard,
    loadFlashcardsByCourse,
    deleteFlashcard,
    updateFlashcardProgress,
    loadFlashcardProgress,
    invalidateFlashcard,
    clearCache,
    saveMatchModeStats,
    loadMatchModeStats
  }
})
