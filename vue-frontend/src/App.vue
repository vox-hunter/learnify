<template>
  <div id="app" :class="{ 'sidebar-collapsed': sidebarCollapsed }">
    <!-- Sidebar Navigation -->
    <Sidebar @toggle-collapse="handleSidebarToggle" />

    <!-- Main Content Area -->
    <main class="main-content">
      <router-view />
    </main>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useAuthStore } from './stores/auth'
import Sidebar from './components/Sidebar.vue'

export default {
  name: 'App',
  components: {
    Sidebar
  },
  setup() {
    const authStore = useAuthStore()
    const sidebarCollapsed = ref(true) // Start collapsed (hover to expand)

    // Initialize auth on app mount (restore from cookies/localStorage)
    onMounted(() => {
      authStore.initialize()
    })

    const handleSidebarToggle = (collapsed) => {
      sidebarCollapsed.value = collapsed
    }

    return {
      sidebarCollapsed,
      handleSidebarToggle
    }
  }
}
</script>

<style scoped>
#app {
  display: flex;
  min-height: 100vh;
  background: var(--bg-primary);
  color: var(--text-primary);
  transition: background 0.3s ease, color 0.3s ease;
}

.main-content {
  flex: 1;
  margin-left: 260px;
  transition: margin-left 0.3s ease;
  overflow-y: auto;
  height: 100vh;
}

/* When sidebar is collapsed */
#app.sidebar-collapsed .main-content {
  margin-left: 80px;
}

@media (max-width: 768px) {
  .main-content {
    margin-left: 80px;
  }

  #app:not(.sidebar-collapsed) .main-content {
    margin-left: 260px;
  }
}
</style>
