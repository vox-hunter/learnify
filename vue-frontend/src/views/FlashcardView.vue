<template>
  <div class="flashcard-view">
    <!-- Loading State -->
    <div
      v-if="loading"
      class="loading-container"
    >
      <div class="spinner" />
      <p>Loading flashcard set...</p>
    </div>

    <!-- Error State -->
    <div
      v-else-if="error"
      class="error-container"
    >
      <div class="error-message">
        <h2>Error Loading Flashcard</h2>
        <p>{{ error }}</p>
        <button
          class="back-button"
          @click="$router.push('/courses')"
        >
          Back to My Space
        </button>
      </div>
    </div>

    <!-- Main Flashcard Content -->
    <div
      v-else-if="flashcard"
      class="flashcard-content"
    >
      <!-- Header -->
      <div class="flashcard-header">
        <div class="header-title">
          <h1>{{ flashcard.flashcard_title }}</h1>
          <p class="subtitle">
            {{ flashcard.cards?.length || 0 }} cards
          </p>
        </div>
        <div class="mode-switcher">
          <button 
            :class="['mode-btn', { active: mode === 'study' }]"
            :aria-pressed="mode === 'study'"
            @click="switchMode('study')"
          >
            Study
          </button>
          <button 
            :class="['mode-btn', { active: mode === 'quiz' }]"
            :aria-pressed="mode === 'quiz'"
            @click="switchMode('quiz')"
          >
            Quiz
          </button>
          <button 
            :class="['mode-btn', { active: mode === 'match' }]"
            :disabled="true"
            :title="'Match mode coming soon!'"
            @click="switchMode('match')"
          >
            Match 🔒
          </button>
        </div>
      </div>

      <!-- Empty State -->
      <div
        v-if="totalCards === 0"
        class="empty-state"
      >
        <div class="empty-message">
          <h2>No Cards Available</h2>
          <p>This flashcard set doesn't contain any cards yet.</p>
        </div>
      </div>

      <!-- Card Display Area -->
      <div
        v-else-if="currentCard"
        class="card-display"
      >
        <div
          class="card-container"
          role="button"
          tabindex="0"
          :aria-label="isFlipped ? 'Card showing answer, click to show question' : 'Card showing question, click to show answer'"
          @click="flipCard"
          @keydown.enter="flipCard"
        >
          <div :class="['card-inner', { flipped: isFlipped }]">
            <!-- Front of Card -->
            <div class="card-face card-front">
              <div class="card-label">
                Question
              </div>
              <div
                class="card-content"
                v-html="renderMarkdown(currentCard.front)"
              />
              <div
                v-if="currentCard.hint && !isFlipped"
                class="card-hint"
              >
                💡 Hint: {{ currentCard.hint }}
              </div>
              <div class="flip-prompt">
                Click or press Space to flip
              </div>
            </div>

            <!-- Back of Card -->
            <div class="card-face card-back">
              <div class="card-label">
                Answer
              </div>
              <div
                class="card-content"
                v-html="renderMarkdown(currentCard.back)"
              />
              
              <!-- Quiz Mode Self-Assessment -->
              <div
                v-if="mode === 'quiz'"
                class="quiz-controls"
              >
                <button
                  class="quiz-btn incorrect"
                  @click.stop="markAnswer(false)"
                >
                  ❌ Incorrect
                </button>
                <button
                  class="quiz-btn correct"
                  @click.stop="markAnswer(true)"
                >
                  ✓ Correct
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Difficulty Badge -->
        <div
          v-if="currentCard.difficulty"
          class="difficulty-badge"
          :data-difficulty="currentCard.difficulty"
        >
          {{ currentCard.difficulty }}
        </div>
      </div>

      <!-- Navigation Controls -->
      <div
        v-if="totalCards > 0"
        class="navigation-controls"
      >
        <button 
          :disabled="!canNavigatePrevious" 
          class="nav-btn"
          @click="previousCard"
        >
          ← Previous
        </button>
        
        <button
          class="nav-btn shuffle-btn"
          @click="shuffleCards"
        >
          🔀 Shuffle
        </button>

        <button 
          :disabled="!canNavigateNext" 
          class="nav-btn"
          @click="nextCard"
        >
          Next →
        </button>
      </div>

      <!-- Progress Bar -->
      <div
        v-if="totalCards > 0"
        class="progress-bar-container"
      >
        <div
          class="progress-bar"
          :style="{ height: progressPercentage + '%' }"
        />
      </div>

      <!-- Stats Footer -->
      <div
        v-if="totalCards > 0"
        class="stats-footer"
      >
        <div class="stat-item">
          <span class="stat-label">Card</span>
          <span class="stat-value">{{ currentCardIndex + 1 }} / {{ totalCards }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">Studied</span>
          <span class="stat-value">{{ studiedCards.size }} / {{ totalCards }}</span>
        </div>
        <div
          v-if="totalAttempts > 0"
          class="stat-item"
        >
          <span class="stat-label">Accuracy</span>
          <span class="stat-value">{{ accuracyRate }}%</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">Mastery</span>
          <span class="stat-value">{{ averageMastery }}</span>
        </div>
      </div>

      <!-- Keyboard Shortcuts Hint -->
      <div class="keyboard-hints">
        <span class="hint-item">Space: Flip</span>
        <span class="hint-item">← →: Navigate</span>
        <span class="hint-item">S: Shuffle</span>
        <span class="hint-item">Esc: Exit</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useFlashcardStore } from '@/stores/flashcard'
import MarkdownIt from 'markdown-it'
import DOMPurify from 'dompurify'

const route = useRoute()
const router = useRouter()
const flashcardStore = useFlashcardStore()

// Initialize markdown parser
const md = new MarkdownIt({
  html: true,
  linkify: true,
  typographer: true
})

// State
const loading = ref(true)
const error = ref(null)
const flashcard = ref(null)
const currentCardIndex = ref(0)
const isFlipped = ref(false)
const mode = ref('study')
const studiedCards = ref(new Set())
const masteryLevels = ref(new Map())
const correctAnswers = ref(0)
const totalAttempts = ref(0)
const shuffledIndices = ref([])
const loadedAccuracyRate = ref(null)
let mathJaxTimer = null

// Computed Properties
const currentCard = computed(() => {
  if (!flashcard.value?.cards) return null
  const index = shuffledIndices.value.length > 0 
    ? shuffledIndices.value[currentCardIndex.value] 
    : currentCardIndex.value
  return flashcard.value.cards[index]
})

const totalCards = computed(() => flashcard.value?.cards?.length || 0)

const progressPercentage = computed(() => {
  if (totalCards.value === 0) return 0
  return (studiedCards.value.size / totalCards.value) * 100
})

const accuracyRate = computed(() => {
  if (loadedAccuracyRate.value !== null) return loadedAccuracyRate.value
  if (totalAttempts.value === 0) return 0
  return Math.round((correctAnswers.value / totalAttempts.value) * 100)
})

const averageMastery = computed(() => {
  if (masteryLevels.value.size === 0) return '0/5'
  let sum = 0
  masteryLevels.value.forEach(level => sum += level)
  const avg = Math.round(sum / masteryLevels.value.size)
  return `${avg}/5`
})

const canNavigatePrevious = computed(() => currentCardIndex.value > 0)

const canNavigateNext = computed(() => currentCardIndex.value < totalCards.value - 1)

// Functions
const renderMarkdown = (content) => {
  if (!content) return ''
  const rendered = md.render(content)
  return DOMPurify.sanitize(rendered)
}

const loadFlashcard = async () => {
  try {
    loading.value = true
    error.value = null
    
    const flashcardId = route.params.id
    await flashcardStore.loadFlashcard(flashcardId)
    
    flashcard.value = flashcardStore.currentFlashcard
    
    if (!flashcard.value) {
      error.value = 'Flashcard not found'
      return
    }

    // Initialize shuffled indices with sequential order
    shuffledIndices.value = Array.from({ length: totalCards.value }, (_, i) => i)
    
    // Load saved progress
    const { success, progress } = await flashcardStore.loadFlashcardProgress(flashcardId)
    if (success && progress) {
      studiedCards.value = new Set(progress.studied_cards || [])
      if (progress.mastery_levels) {
        masteryLevels.value = new Map(Object.entries(progress.mastery_levels).map(([k, v]) => [parseInt(k), v]))
      }
      if (progress.accuracy_rate !== undefined) {
        loadedAccuracyRate.value = progress.accuracy_rate
      }
    }
    
    loading.value = false
    
    // Typeset math after content loads
    await nextTick()
    typesetMath()
  } catch (err) {
    console.error('Error loading flashcard:', err)
    error.value = err.message || 'Failed to load flashcard'
    loading.value = false
  }
}

const flipCard = () => {
  isFlipped.value = !isFlipped.value
  
  // Mark card as studied when first flipped
  if (isFlipped.value) {
    const actualIndex = shuffledIndices.value.length > 0 
      ? shuffledIndices.value[currentCardIndex.value] 
      : currentCardIndex.value
    studiedCards.value.add(actualIndex)
  }
}

const nextCard = () => {
  if (canNavigateNext.value) {
    currentCardIndex.value++
    isFlipped.value = false
    saveProgress()
  }
}

const previousCard = () => {
  if (canNavigatePrevious.value) {
    currentCardIndex.value--
    isFlipped.value = false
    saveProgress()
  }
}

const shuffleCards = () => {
  // Fisher-Yates shuffle
  const indices = Array.from({ length: totalCards.value }, (_, i) => i)
  for (let i = indices.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1))
    ;[indices[i], indices[j]] = [indices[j], indices[i]]
  }
  shuffledIndices.value = indices
  currentCardIndex.value = 0
  isFlipped.value = false
}

const switchMode = (newMode) => {
  mode.value = newMode
  isFlipped.value = false
}

const markAnswer = (isCorrect) => {
  // Reset loaded accuracy once user starts new session
  if (loadedAccuracyRate.value !== null) {
    loadedAccuracyRate.value = null
  }
  
  if (isCorrect) {
    correctAnswers.value++
  }
  totalAttempts.value++
  
  // Update mastery level
  const actualIndex = shuffledIndices.value.length > 0 
    ? shuffledIndices.value[currentCardIndex.value] 
    : currentCardIndex.value
  
  const currentMastery = masteryLevels.value.get(actualIndex) || 0
  if (isCorrect && currentMastery < 5) {
    masteryLevels.value.set(actualIndex, currentMastery + 1)
  } else if (!isCorrect && currentMastery > 0) {
    masteryLevels.value.set(actualIndex, Math.max(0, currentMastery - 1))
  }
  
  saveProgress()
  
  // Auto-advance to next card after a short delay
  setTimeout(() => {
    if (canNavigateNext.value) {
      nextCard()
    }
  }, 500)
}

const saveProgress = async () => {
  try {
    await flashcardStore.updateFlashcardProgress(
      route.params.id,
      Array.from(studiedCards.value),
      Object.fromEntries(masteryLevels.value),
      accuracyRate.value
    )
  } catch (err) {
    console.error('Error saving progress:', err)
  }
}

const handleKeyboard = (event) => {
  // Don't trigger if user is typing in an input
  if (event.target.tagName === 'INPUT' || event.target.tagName === 'TEXTAREA') {
    return
  }
  
  switch (event.key) {
    case ' ':
      event.preventDefault()
      flipCard()
      break
    case 'ArrowLeft':
      event.preventDefault()
      previousCard()
      break
    case 'ArrowRight':
      event.preventDefault()
      nextCard()
      break
    case 's':
    case 'S':
      event.preventDefault()
      shuffleCards()
      break
    case 'Escape':
      event.preventDefault()
      router.push('/courses')
      break
  }
}

const typesetMath = () => {
  // Clear existing timer
  if (mathJaxTimer) {
    clearTimeout(mathJaxTimer)
  }
  
  // Debounce MathJax typesetting to reduce redundant reflows
  mathJaxTimer = setTimeout(() => {
    if (window.MathJax) {
      window.MathJax.typesetPromise?.()
        .catch((err) => console.error('MathJax typesetting failed:', err))
    }
  }, 200)
}

// Watchers
watch(currentCardIndex, async () => {
  await nextTick()
  typesetMath()
})

watch(isFlipped, async () => {
  await nextTick()
  typesetMath()
})

// Lifecycle Hooks
onMounted(() => {
  loadFlashcard()
  window.addEventListener('keydown', handleKeyboard)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeyboard)
  saveProgress()
})
</script>

<style scoped>
.flashcard-view {
  min-height: 100vh;
  background: var(--bg-primary);
  color: var(--text-primary);
  padding: 2rem;
  position: relative;
}

/* Loading State */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 60vh;
  gap: 1rem;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 4px solid var(--border-color);
  border-top-color: var(--accent-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Error State */
.error-container {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 60vh;
}

.error-message {
  text-align: center;
  padding: 2rem;
  background: var(--card-bg);
  border-radius: 1rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.error-message h2 {
  color: var(--error-color);
  margin-bottom: 1rem;
}

.back-button {
  margin-top: 1.5rem;
  padding: 0.75rem 2rem;
  background: var(--accent-primary);
  color: white;
  border: none;
  border-radius: 0.5rem;
  cursor: pointer;
  font-size: 1rem;
  transition: all 0.3s ease;
}

.back-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

/* Empty State */
.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 40vh;
  margin: 3rem 0;
}

.empty-message {
  text-align: center;
  padding: 3rem;
  background: var(--card-bg);
  border-radius: 1rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.empty-message h2 {
  color: var(--text-secondary);
  margin-bottom: 0.5rem;
  font-size: 1.5rem;
}

.empty-message p {
  color: var(--text-secondary);
  opacity: 0.8;
}

/* Main Content */
.flashcard-content {
  max-width: 1200px;
  margin: 0 auto;
  padding-right: 80px;
}

/* Header */
.flashcard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 3rem;
  flex-wrap: wrap;
  gap: 1.5rem;
}

.header-title h1 {
  font-size: 2rem;
  font-weight: 700;
  margin: 0 0 0.5rem 0;
  color: var(--text-primary);
}

.subtitle {
  color: var(--text-secondary);
  margin: 0;
  font-size: 0.95rem;
}

.mode-switcher {
  display: flex;
  gap: 0.5rem;
  background: var(--card-bg);
  padding: 0.5rem;
  border-radius: 0.75rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.mode-btn {
  padding: 0.75rem 1.5rem;
  background: transparent;
  color: var(--text-secondary);
  border: none;
  border-radius: 0.5rem;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s ease;
  font-size: 0.95rem;
}

.mode-btn:hover {
  background: var(--bg-secondary);
  color: var(--text-primary);
}

.mode-btn.active {
  background: var(--accent-primary);
  color: white;
}

.mode-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.mode-btn:disabled:hover {
  background: transparent;
  color: var(--text-secondary);
}

/* Card Display */
.card-display {
  position: relative;
  margin-bottom: 2.5rem;
}

.card-container {
  perspective: 1000px;
  cursor: pointer;
  min-height: 400px;
  display: flex;
  align-items: center;
  justify-content: center;
  outline: none;
}

.card-container:focus {
  outline: 3px solid var(--accent-primary);
  outline-offset: 8px;
  border-radius: 1.5rem;
}

.card-inner {
  position: relative;
  width: 100%;
  max-width: 700px;
  min-height: 400px;
  transition: transform 0.6s;
  transform-style: preserve-3d;
}

.card-inner.flipped {
  transform: rotateY(180deg);
}

.card-face {
  position: absolute;
  width: 100%;
  min-height: 400px;
  backface-visibility: hidden;
  background: var(--card-bg);
  border-radius: 1.5rem;
  padding: 3rem;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
}

.card-front {
  transform: rotateY(0deg);
}

.card-back {
  transform: rotateY(180deg);
}

.card-label {
  position: absolute;
  top: 1.5rem;
  left: 2rem;
  font-size: 0.85rem;
  font-weight: 700;
  text-transform: uppercase;
  color: var(--accent-primary);
  letter-spacing: 1px;
}

.card-content {
  font-size: 1.5rem;
  line-height: 1.6;
  color: var(--text-primary);
  margin: 1rem 0;
  max-width: 100%;
  overflow-wrap: break-word;
}

.card-content :deep(p) {
  margin: 0.5rem 0;
}

.card-content :deep(code) {
  background: var(--bg-secondary);
  padding: 0.2rem 0.4rem;
  border-radius: 0.25rem;
  font-size: 0.9em;
}

.card-hint {
  margin-top: 1.5rem;
  padding: 1rem;
  background: var(--bg-secondary);
  border-radius: 0.75rem;
  font-size: 0.95rem;
  color: var(--text-secondary);
  max-width: 90%;
}

.flip-prompt {
  position: absolute;
  bottom: 1.5rem;
  font-size: 0.85rem;
  color: var(--text-secondary);
  opacity: 0.7;
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 0.5; }
  50% { opacity: 1; }
}

/* Quiz Controls */
.quiz-controls {
  display: flex;
  gap: 1rem;
  margin-top: 2rem;
}

.quiz-btn {
  padding: 0.75rem 2rem;
  border: none;
  border-radius: 0.75rem;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  color: white;
}

.quiz-btn.correct {
  background: var(--success-color, #22c55e);
}

.quiz-btn.incorrect {
  background: var(--error-color, #ef4444);
}

.quiz-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.quiz-btn:active {
  transform: translateY(0);
}

/* Difficulty Badge */
.difficulty-badge {
  position: absolute;
  top: 1rem;
  right: 1rem;
  padding: 0.5rem 1rem;
  border-radius: 2rem;
  font-size: 0.85rem;
  font-weight: 600;
  text-transform: capitalize;
}

.difficulty-badge[data-difficulty="easy"] {
  background: rgba(34, 197, 94, 0.2);
  color: #22c55e;
}

.difficulty-badge[data-difficulty="medium"] {
  background: rgba(251, 146, 60, 0.2);
  color: #fb923c;
}

.difficulty-badge[data-difficulty="hard"] {
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
}

/* Navigation Controls */
.navigation-controls {
  display: flex;
  justify-content: center;
  gap: 1rem;
  margin-bottom: 2.5rem;
}

.nav-btn {
  padding: 0.875rem 2rem;
  background: var(--card-bg);
  color: var(--text-primary);
  border: 2px solid var(--border-color);
  border-radius: 0.75rem;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 600;
  transition: all 0.3s ease;
}

.nav-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  border-color: var(--accent-primary);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.nav-btn:active:not(:disabled) {
  transform: translateY(0);
}

.nav-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.shuffle-btn {
  background: var(--accent-primary);
  color: white;
  border-color: var(--accent-primary);
}

/* Progress Bar */
.progress-bar-container {
  position: fixed;
  right: 2rem;
  top: 50%;
  transform: translateY(-50%);
  width: 8px;
  height: 300px;
  background: var(--bg-secondary);
  border-radius: 1rem;
  overflow: hidden;
}

.progress-bar {
  width: 100%;
  background: linear-gradient(to top, var(--accent-primary), var(--accent-secondary, #a78bfa));
  border-radius: 1rem;
  transition: height 0.4s ease;
  position: absolute;
  bottom: 0;
}

/* Stats Footer */
.stats-footer {
  display: flex;
  justify-content: center;
  gap: 2rem;
  padding: 1.5rem;
  background: var(--card-bg);
  border-radius: 1rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.25rem;
}

.stat-label {
  font-size: 0.85rem;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  font-weight: 600;
}

.stat-value {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--accent-primary);
}

/* Keyboard Hints */
.keyboard-hints {
  display: flex;
  justify-content: center;
  gap: 1.5rem;
  flex-wrap: wrap;
}

.hint-item {
  font-size: 0.85rem;
  color: var(--text-secondary);
  padding: 0.5rem 1rem;
  background: var(--bg-secondary);
  border-radius: 0.5rem;
  animation: pulse 3s ease-in-out infinite;
}

/* Responsive Design */
@media (max-width: 768px) {
  .flashcard-view {
    padding: 1rem;
  }

  .flashcard-content {
    padding-right: 0;
  }

  .flashcard-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .header-title h1 {
    font-size: 1.5rem;
  }

  .mode-switcher {
    width: 100%;
    justify-content: space-between;
  }

  .mode-btn {
    flex: 1;
    padding: 0.75rem 1rem;
    font-size: 0.85rem;
  }

  .card-face {
    min-height: 350px;
    padding: 2rem 1.5rem;
  }

  .card-content {
    font-size: 1.25rem;
  }

  .navigation-controls {
    flex-direction: column;
    gap: 0.75rem;
  }

  .nav-btn {
    width: 100%;
  }

  .progress-bar-container {
    right: 0.5rem;
    height: 200px;
    width: 6px;
  }

  .stats-footer {
    gap: 1rem;
  }

  .stat-item {
    flex: 1;
    min-width: 80px;
  }

  .keyboard-hints {
    gap: 0.5rem;
  }

  .hint-item {
    font-size: 0.75rem;
    padding: 0.4rem 0.8rem;
  }

  .difficulty-badge {
    top: 0.5rem;
    right: 0.5rem;
    font-size: 0.75rem;
    padding: 0.4rem 0.8rem;
  }
}

@media (max-width: 480px) {
  .card-content {
    font-size: 1.1rem;
  }

  .quiz-controls {
    flex-direction: column;
    width: 100%;
  }

  .quiz-btn {
    width: 100%;
  }
}
</style>
