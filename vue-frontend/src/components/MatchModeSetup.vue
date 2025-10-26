<template>
  <div class="match-mode-setup">
    <div class="setup-card">
      <h2>Match Mode Setup</h2>
      <p class="subtitle">
        Select the number of pairs you'd like to match
      </p>

      <div class="card-count-selector">
        <button
          v-for="count in availableCounts"
          :key="count"
          :class="['count-btn', { active: selectedCount === count }]"
          @click="selectedCount = count"
        >
          {{ count }} pairs
        </button>
      </div>

      <div class="info-section">
        <div class="info-item">
          <span class="info-label">Total Cards:</span>
          <span class="info-value">{{ selectedCount * 2 }}</span>
        </div>
        <div class="info-item">
          <span class="info-label">Available Pairs:</span>
          <span class="info-value">{{ maxPairs }}</span>
        </div>
      </div>

      <div class="actions">
        <button
          class="btn-secondary"
          @click="$emit('cancel')"
        >
          Cancel
        </button>
        <button
          class="btn-primary"
          :disabled="selectedCount === 0"
          @click="startGame"
        >
          Start Game
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  totalCards: {
    type: Number,
    required: true
  }
})

const emit = defineEmits(['start', 'cancel'])

const maxPairs = computed(() => Math.floor(props.totalCards / 2))

// Generate available count options (2, 4, 6, 8, 10, 12 up to maxPairs)
const availableCounts = computed(() => {
  const counts = []
  for (let i = 2; i <= Math.min(maxPairs.value, 12); i += 2) {
    counts.push(i)
  }
  // If maxPairs is odd but greater than 2, add it
  if (maxPairs.value > 2 && maxPairs.value % 2 !== 0 && !counts.includes(maxPairs.value)) {
    counts.push(maxPairs.value)
  }
  return counts
})

const selectedCount = ref(availableCounts.value[0] || 2)

const startGame = () => {
  emit('start', selectedCount.value)
}
</script>

<style scoped>
.match-mode-setup {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.setup-card {
  background: var(--card-bg);
  border-radius: 1.5rem;
  padding: 2.5rem;
  max-width: 600px;
  width: 100%;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  animation: slideIn 0.3s ease-out;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.setup-card h2 {
  margin: 0 0 0.5rem 0;
  font-size: 1.8rem;
  color: var(--text-primary);
}

.subtitle {
  color: var(--text-secondary);
  margin: 0 0 2rem 0;
  font-size: 1rem;
}

.card-count-selector {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
  gap: 0.75rem;
  margin-bottom: 2rem;
}

.count-btn {
  padding: 1rem;
  background: var(--bg-secondary);
  color: var(--text-primary);
  border: 2px solid var(--border-color);
  border-radius: 0.75rem;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.count-btn:hover {
  border-color: var(--accent-primary);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.count-btn.active {
  background: var(--accent-primary);
  color: white;
  border-color: var(--accent-primary);
}

.info-section {
  background: var(--bg-secondary);
  border-radius: 0.75rem;
  padding: 1.5rem;
  margin-bottom: 2rem;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 0;
}

.info-item + .info-item {
  border-top: 1px solid var(--border-color);
  margin-top: 0.5rem;
  padding-top: 1rem;
}

.info-label {
  color: var(--text-secondary);
  font-size: 0.95rem;
}

.info-value {
  color: var(--accent-primary);
  font-weight: 700;
  font-size: 1.1rem;
}

.actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
}

.btn-primary,
.btn-secondary {
  padding: 0.875rem 2rem;
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

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
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

@media (max-width: 768px) {
  .setup-card {
    padding: 2rem;
  }

  .card-count-selector {
    grid-template-columns: repeat(auto-fill, minmax(80px, 1fr));
  }

  .actions {
    flex-direction: column-reverse;
  }

  .btn-primary,
  .btn-secondary {
    width: 100%;
  }
}
</style>
