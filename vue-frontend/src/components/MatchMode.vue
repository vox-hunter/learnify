<template>
  <div class="match-mode">
    <!-- Game Header -->
    <div class="game-header">
      <div class="header-left">
        <h2>Match Mode</h2>
        <p class="card-info">
          {{ pairCount }} pairs ({{ cardCount }} cards)
        </p>
      </div>
      <div class="header-right">
        <button
          class="icon-btn"
          title="Exit Match Mode"
          @click="handleExit"
        >
          ✕
        </button>
      </div>
    </div>

    <!-- Stats Bar -->
    <div class="stats-bar">
      <div class="stat-item">
        <span class="stat-label">Time</span>
        <span class="stat-value">{{ formattedTime }}</span>
      </div>
      <div class="stat-item">
        <span class="stat-label">Moves</span>
        <span class="stat-value">{{ moveCount }}</span>
      </div>
      <div class="stat-item">
        <span class="stat-label">Matched</span>
        <span class="stat-value">{{ matchedPairs }} / {{ pairCount }}</span>
      </div>
    </div>

    <!-- Game Grid -->
    <div
      ref="gridContainer"
      class="grid-container"
    >
      <div
        :class="['game-grid', `cols-${gridCols}`]"
        :style="gridStyle"
      >
        <div
          v-for="(card, index) in shuffledCards"
          :key="card.uid"
          :class="[
            'match-card',
            {
              selected: selectedCards.includes(index),
              error: card.hasError,
              hidden: !card.isVisible
            }
          ]"
          role="button"
          :tabindex="card.isVisible ? 0 : -1"
          :aria-hidden="!card.isVisible"
          :aria-pressed="selectedCards.includes(index)"
          :aria-label="selectedCards.includes(index) ? 'Selected card' : 'Unselected card'"
          @click="handleCardClick(index)"
          @keydown.space.prevent="handleCardClick(index)"
          @keydown.enter.prevent="handleCardClick(index)"
        >
          <div class="card-face">
            <div
              class="card-content"
              v-html="renderMarkdown(card.content)"
            />
          </div>
        </div>
      </div>
    </div>

    <!-- Completion Modal -->
    <div
      v-if="isCompleted"
      class="completion-modal"
    >
      <div class="completion-card">
        <div class="completion-icon">
          🎉
        </div>
        <h2>Congratulations!</h2>
        <p class="completion-message">
          You've matched all pairs!
        </p>

        <div class="completion-stats">
          <div class="completion-stat">
            <span class="stat-label">Time</span>
            <span :class="['stat-value', { 'new-best': isNewBestTime }]">
              {{ formattedTime }}
              <span
                v-if="isNewBestTime"
                class="best-badge"
              >⭐ New Best!</span>
            </span>
          </div>
          <div class="completion-stat">
            <span class="stat-label">Moves</span>
            <span :class="['stat-value', { 'new-best': isNewBestMoves }]">
              {{ moveCount }}
              <span
                v-if="isNewBestMoves"
                class="best-badge"
              >⭐ New Best!</span>
            </span>
          </div>
          <div class="completion-stat">
            <span class="stat-label">Accuracy</span>
            <span class="stat-value">{{ accuracyRate }}%</span>
          </div>
        </div>

        <div
          v-if="personalBests"
          class="personal-bests"
        >
          <h3>Personal Bests</h3>
          <div class="best-item">
            <span>Best Time:</span>
            <span>{{ formatTime(personalBests.personal_best_time) }}</span>
          </div>
          <div class="best-item">
            <span>Fewest Moves:</span>
            <span>{{ personalBests.best_moves }}</span>
          </div>
          <div class="best-item">
            <span>Games Played:</span>
            <span>{{ personalBests.games_played }}</span>
          </div>
        </div>

        <div class="completion-actions">
          <button
            class="btn-secondary"
            @click="handleExit"
          >
            Back to Study
          </button>
          <button
            class="btn-primary"
            @click="handlePlayAgain"
          >
            Play Again
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import MarkdownIt from 'markdown-it'
import DOMPurify from 'dompurify'

const props = defineProps({
  cards: {
    type: Array,
    required: true
  },
  pairCount: {
    type: Number,
    required: true
  },
  personalBests: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['exit', 'complete', 'playAgain'])

// Initialize markdown parser
const md = new MarkdownIt({
  html: true,
  linkify: true,
  typographer: true
})

// MathJax global loader (assumes MathJax is loaded in public/mathjax/tex-chtml.js)
function typesetMathJax(el) {
  if (window.MathJax && window.MathJax.typesetPromise) {
    window.MathJax.typesetPromise([el])
  }
}

function mathjaxTypesetNextTick() {
  nextTick(() => {
    const gridContainer = document.querySelector('.game-grid')
    if (gridContainer) typesetMathJax(gridContainer)
  })
}

// Game state
const shuffledCards = ref([])
const selectedCards = ref([])
const matchedPairs = ref(0)
const moveCount = ref(0)
const sessionTime = ref(0)
const isCompleted = ref(false)
const isChecking = ref(false)
const gridContainer = ref(null)
const gridCols = ref(4)
const gridRows = ref(3)
const isNewBestTime = ref(false)
const isNewBestMoves = ref(false)

// Timer
let timerInterval = null

// Computed
const cardCount = computed(() => props.pairCount * 2)

const formattedTime = computed(() => formatTime(sessionTime.value))

const accuracyRate = computed(() => {
  if (moveCount.value === 0) return 0
  const perfectMoves = props.pairCount
  return Math.round((perfectMoves / moveCount.value) * 100)
})

const gridStyle = computed(() => {
  return {
    gridTemplateColumns: `repeat(${gridCols.value}, 1fr)`,
    gridTemplateRows: `repeat(${gridRows.value}, 1fr)`
  }
})

// Functions
const formatTime = (seconds) => {
  if (seconds === null || seconds === undefined) return '--:--'
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
}

const renderMarkdown = (content) => {
  if (!content) return ''
  const rendered = md.render(content)
  return DOMPurify.sanitize(rendered)
}

const computeGridLayout = () => {
  if (!gridContainer.value) return

  const container = gridContainer.value
  const containerWidth = container.clientWidth
  const containerHeight = container.clientHeight
  
  const totalCells = shuffledCards.value.length
  const MIN_CARD_WIDTH = 80
  const MIN_CARD_HEIGHT = 100
  const GAP = 12
  
  let bestCols = 4
  let bestRows = 3
  let bestScore = Infinity
  
  // Try different grid configurations
  for (let cols = 2; cols <= Math.min(totalCells, 8); cols++) {
    const rows = Math.ceil(totalCells / cols)
    
    // Calculate card dimensions
    const cardWidth = (containerWidth - GAP * (cols + 1)) / cols
    const cardHeight = (containerHeight - GAP * (rows + 1)) / rows
    
    // Skip if cards would be too small
    if (cardWidth < MIN_CARD_WIDTH || cardHeight < MIN_CARD_HEIGHT) continue
    
    // Prefer configurations where cards fit well (4:3 aspect ratio)
    const aspectRatio = cardWidth / cardHeight
    const score = Math.abs(aspectRatio - 1.33) + Math.abs(rows * cardHeight - containerHeight) / 100
    
    if (score < bestScore) {
      bestScore = score
      bestCols = cols
      bestRows = rows
    }
  }
  
  gridCols.value = bestCols
  gridRows.value = bestRows
}

const initializeGame = () => {
  // Select random cards from the flashcard set
  const availableIndices = [...Array(props.cards.length).keys()]
  
  // Shuffle available indices
  for (let i = availableIndices.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1))
    ;[availableIndices[i], availableIndices[j]] = [availableIndices[j], availableIndices[i]]
  }
  
  // Take first pairCount cards
  const pickedCards = availableIndices.slice(0, props.pairCount).map(i => props.cards[i])
  
  // Create pairs (each card appears twice)
  const pairs = []
  let uidCounter = 0
  pickedCards.forEach((card, index) => {
    // Use front for one card
    pairs.push({
      uid: `card-${uidCounter++}`,
      content: card.front,
      pairId: index,
      isVisible: true,
      hasError: false
    })
    // Use back for the matching card
    pairs.push({
      uid: `card-${uidCounter++}`,
      content: card.back,
      pairId: index,
      isVisible: true,
      hasError: false
    })
  })
  
  // Shuffle pairs using Fisher-Yates
  for (let i = pairs.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1))
    ;[pairs[i], pairs[j]] = [pairs[j], pairs[i]]
  }
  
  shuffledCards.value = pairs
  selectedCards.value = []
  matchedPairs.value = 0
  moveCount.value = 0
  sessionTime.value = 0
  isCompleted.value = false
  isNewBestTime.value = false
  isNewBestMoves.value = false
  
  // Start timer
  startTimer()
  
  // Compute grid layout
  computeGridLayout()
}

const startTimer = () => {
  if (timerInterval) clearInterval(timerInterval)
  timerInterval = setInterval(() => {
    sessionTime.value++
  }, 1000)
}

const stopTimer = () => {
  if (timerInterval) {
    clearInterval(timerInterval)
    timerInterval = null
  }
}

const handleCardClick = (index) => {
  const card = shuffledCards.value[index]
  
  // Ignore if checking, card not visible (already matched), or card has error animation
  if (isChecking.value || !card.isVisible || card.hasError) {
    return
  }
  
  // If clicking the same card again, deselect it
  const cardIndex = selectedCards.value.indexOf(index)
  if (cardIndex !== -1) {
    selectedCards.value.splice(cardIndex, 1)
    return
  }
  
  // Ignore if already two cards selected
  if (selectedCards.value.length >= 2) {
    return
  }
  
  // Select the card
  selectedCards.value.push(index)
  
  // Check for match if two cards selected
  if (selectedCards.value.length === 2) {
    checkMatch()
  }
}

const checkMatch = () => {
  moveCount.value++
  isChecking.value = true
  
  const [firstIndex, secondIndex] = selectedCards.value
  const firstCard = shuffledCards.value[firstIndex]
  const secondCard = shuffledCards.value[secondIndex]
  
  if (firstCard.pairId === secondCard.pairId) {
    // Match found! Start fade-out animation
    firstCard.isVisible = false
    secondCard.isVisible = false
    matchedPairs.value++
    
    // Clear selection immediately
    selectedCards.value = []
    
    // Wait for fade-out animation to complete before removing cards
    setTimeout(() => {
      // Remove matched cards from array in descending order to avoid index shift
      const indices = [firstIndex, secondIndex].sort((a, b) => b - a)
      indices.forEach(idx => {
        shuffledCards.value.splice(idx, 1)
      })
      
      // Recompute grid layout for optimal card sizing
      computeGridLayout()
      
      isChecking.value = false
      
      // Check if game completed
      if (matchedPairs.value === props.pairCount) {
        completeGame()
      }
    }, 400)
  } else {
    // No match - show error animation
    firstCard.hasError = true
    secondCard.hasError = true
    
    // Wait for shake animation to complete
    setTimeout(() => {
      firstCard.hasError = false
      secondCard.hasError = false
      selectedCards.value = []
      isChecking.value = false
    }, 600)
  }
}

const completeGame = () => {
  stopTimer()
  isCompleted.value = true
  
  // Check for new personal bests
  if (props.personalBests) {
    if (!props.personalBests.personal_best_time || sessionTime.value < props.personalBests.personal_best_time) {
      isNewBestTime.value = true
    }
    if (!props.personalBests.best_moves || moveCount.value < props.personalBests.best_moves) {
      isNewBestMoves.value = true
    }
  } else {
    // First time playing
    isNewBestTime.value = true
    isNewBestMoves.value = true
  }
  
  // Emit completion event with stats
  emit('complete', {
    completion_time: sessionTime.value,
    moves_count: moveCount.value,
    card_count: props.pairCount,
    timestamp: new Date().toISOString()
  })
}

const handleExit = () => {
  stopTimer()
  emit('exit')
}

const handlePlayAgain = () => {
  emit('playAgain')
}

const handleResize = () => {
  computeGridLayout()
}

// Lifecycle
onMounted(() => {
  initializeGame()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  stopTimer()
  window.removeEventListener('resize', handleResize)
})

// Watch for progress changes and re-render MathJax
watch(shuffledCards, () => {
  mathjaxTypesetNextTick()
}, { deep: true })

// Watch for card state changes
watch([selectedCards, moveCount], () => {
  mathjaxTypesetNextTick()
}, { deep: true })
</script>

<style scoped>
.match-mode {
  min-height: 100vh;
  background: var(--bg-primary);
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
}

/* Header */
.game-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.header-left h2 {
  margin: 0;
  font-size: 1.8rem;
  color: var(--text-primary);
}

.card-info {
  margin: 0.25rem 0 0 0;
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.icon-btn {
  width: 40px;
  height: 40px;
  border: none;
  background: var(--bg-secondary);
  color: var(--text-primary);
  border-radius: 50%;
  cursor: pointer;
  font-size: 1.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.icon-btn:hover {
  background: var(--accent-primary);
  color: white;
  transform: scale(1.1);
}

/* Stats Bar */
.stats-bar {
  display: flex;
  gap: 1.5rem;
  justify-content: center;
  padding: 1.25rem;
  background: var(--card-bg);
  border-radius: 1rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  margin-bottom: 1.5rem;
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
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--accent-primary);
}

/* Grid Container */
.grid-container {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 0;
  overflow: auto;
  padding: 1rem 0;
}

.game-grid {
  display: grid;
  gap: 12px;
  max-width: 100%;
  max-height: 100%;
  padding: 1rem;
}

/* Match Cards */
.match-card {
  cursor: pointer;
  aspect-ratio: 4 / 3;
  min-width: 120px;
  min-height: 90px;
  transition: all 0.2s ease;
}

.card-face {
  width: 100%;
  height: 100%;
  border-radius: 0.75rem;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.75rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  background: var(--card-bg);
  color: var(--text-primary);
  overflow: hidden;
  border: 2px solid transparent;
  transition: all 0.2s ease;
}

.card-content {
  font-size: 0.85rem;
  line-height: 1.3;
  text-align: center;
  word-wrap: break-word;
  overflow-wrap: break-word;
  max-width: 100%;
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  hyphens: auto;
}

.card-content :deep(p) {
  margin: 0;
  padding: 0;
}

.card-content :deep(code) {
  background: rgba(0, 0, 0, 0.1);
  padding: 0.2rem 0.4rem;
  border-radius: 0.25rem;
  font-size: 0.8em;
  word-break: break-all;
}

.card-content :deep(strong),
.card-content :deep(b) {
  font-weight: 600;
}

.card-content :deep(em),
.card-content :deep(i) {
  font-style: italic;
}

/* Card States */
.match-card.selected .card-face {
  border: 3px solid var(--accent-primary);
  transform: scale(1.05);
  box-shadow: 0 4px 20px rgba(var(--accent-primary-rgb, 139, 92, 246), 0.4),
              0 0 0 4px rgba(var(--accent-primary-rgb, 139, 92, 246), 0.1);
}

.match-card.error .card-face {
  border: 3px solid #ef4444;
  background: rgba(239, 68, 68, 0.1);
  animation: shake 0.5s ease-in-out;
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  10%, 30%, 50%, 70%, 90% { transform: translateX(-10px); }
  20%, 40%, 60%, 80% { transform: translateX(10px); }
}

.match-card.hidden {
  animation: fadeOut 0.4s ease-out forwards;
  pointer-events: none;
}

@keyframes fadeOut {
  0% {
    opacity: 1;
    transform: scale(1);
  }
  100% {
    opacity: 0;
    transform: scale(0.8);
    visibility: hidden;
  }
}

/* Hover Effects */
.match-card:not(.hidden):not(.selected):hover {
  transform: scale(1.03);
}

.match-card:not(.hidden):not(.selected):hover .card-face {
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.15);
}

/* Completion Modal */
.completion-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
  animation: fadeIn 0.3s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.completion-card {
  background: var(--card-bg);
  border-radius: 1.5rem;
  padding: 2.5rem;
  max-width: 500px;
  width: 100%;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  animation: slideUp 0.4s ease-out;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.completion-icon {
  font-size: 4rem;
  text-align: center;
  margin-bottom: 1rem;
}

.completion-card h2 {
  margin: 0 0 0.5rem 0;
  text-align: center;
  font-size: 2rem;
  color: var(--text-primary);
}

.completion-message {
  text-align: center;
  color: var(--text-secondary);
  margin: 0 0 2rem 0;
}

.completion-stats {
  background: var(--bg-secondary);
  border-radius: 1rem;
  padding: 1.5rem;
  margin-bottom: 2rem;
}

.completion-stat {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 0;
}

.completion-stat + .completion-stat {
  border-top: 1px solid var(--border-color);
  margin-top: 0.75rem;
  padding-top: 1.25rem;
}

.completion-stat .stat-value {
  font-size: 1.25rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.completion-stat .stat-value.new-best {
  color: #22c55e;
}

.best-badge {
  font-size: 0.85rem;
  font-weight: 600;
}

.personal-bests {
  background: var(--bg-secondary);
  border-radius: 1rem;
  padding: 1.5rem;
  margin-bottom: 2rem;
}

.personal-bests h3 {
  margin: 0 0 1rem 0;
  font-size: 1.1rem;
  color: var(--text-primary);
}

.best-item {
  display: flex;
  justify-content: space-between;
  padding: 0.5rem 0;
  color: var(--text-secondary);
  font-size: 0.95rem;
}

.best-item + .best-item {
  border-top: 1px solid var(--border-color);
  margin-top: 0.5rem;
  padding-top: 0.75rem;
}

.best-item span:last-child {
  color: var(--text-primary);
  font-weight: 600;
}

.completion-actions {
  display: flex;
  gap: 1rem;
}

.btn-primary,
.btn-secondary {
  flex: 1;
  padding: 1rem;
  border: none;
  border-radius: 0.75rem;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-primary {
  background: var(--accent-primary);
  color: white;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.btn-secondary {
  background: var(--bg-secondary);
  color: var(--text-primary);
  border: 2px solid var(--border-color);
}

.btn-secondary:hover {
  border-color: var(--accent-primary);
  transform: translateY(-2px);
}

/* Responsive */
@media (max-width: 768px) {
  .match-mode {
    padding: 1rem;
  }

  .game-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }

  .stats-bar {
    flex-direction: column;
    gap: 1rem;
  }

  .stat-item {
    flex-direction: row;
    justify-content: space-between;
    width: 100%;
  }

  .game-grid {
    gap: 8px;
  }

  .match-card {
    min-width: 60px;
    min-height: 80px;
  }

  .card-content {
    font-size: 0.75rem;
  }

  .completion-card {
    padding: 2rem;
  }

  .completion-actions {
    flex-direction: column;
  }
}
</style>
