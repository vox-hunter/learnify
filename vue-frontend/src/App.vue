<template>
  <div id="app">
    <header class="app-header">
      <div class="container">
        <nav class="navbar">
          <div class="brand">
            <router-link to="/" class="brand-link">
              <span class="brand-icon">🧠</span>
              <span class="brand-name">Learnify</span>
            </router-link>
          </div>
          <div class="nav-links">
            <router-link to="/" class="nav-link">Home</router-link>
            <router-link to="/courses" class="nav-link">My Courses</router-link>
            <router-link v-if="!isAuthenticated" to="/login" class="nav-link">Login</router-link>
            <div v-else class="user-menu">
              <router-link to="/account" class="nav-link account-link">👤 Account</router-link>
              <span class="username">{{ username }}</span>
              <button @click="logout" class="logout-btn">Logout</button>
            </div>
          </div>
        </nav>
      </div>
    </header>

    <main class="main-content">
      <router-view />
    </main>

    <footer class="app-footer">
      <div class="container">
        <div class="footer-content">
          <p>&copy; 2024 Learnify. All rights reserved.</p>
          <div class="footer-links">
            <router-link to="/privacy" class="footer-link">Privacy Policy</router-link>
            <router-link to="/terms" class="footer-link">Terms & Conditions</router-link>
          </div>
        </div>
      </div>
    </footer>
  </div>
</template>

<script>
import { computed, onMounted } from 'vue'
import { useAuthStore } from './stores/auth'

export default {
  name: 'App',
  setup() {
    const authStore = useAuthStore()
    
    // Initialize auth on app mount (restore from cookies/localStorage)
    onMounted(() => {
      authStore.initialize()
    })
    
    const isAuthenticated = computed(() => authStore.isAuthenticated)
    const username = computed(() => authStore.user?.username)
    
    const logout = () => {
      authStore.logout()
    }
    
    return {
      isAuthenticated,
      username,
      logout
    }
  }
}
</script>

<style scoped>
#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
  color: #e2e8f0;
}

.app-header {
  background: rgba(15, 23, 42, 0.95);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(6, 182, 212, 0.2);
  position: sticky;
  top: 0;
  z-index: 1000;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1.5rem;
}

.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 0;
}

.brand-link {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  text-decoration: none;
  color: inherit;
  transition: transform 0.2s;
}

.brand-link:hover {
  transform: scale(1.05);
}

.brand-icon {
  font-size: 2rem;
}

.brand-name {
  font-size: 1.5rem;
  font-weight: 700;
  background: linear-gradient(135deg, #06b6d4, #0891b2);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.nav-links {
  display: flex;
  align-items: center;
  gap: 2rem;
}

.nav-link {
  color: #cbd5e0;
  text-decoration: none;
  font-weight: 500;
  transition: color 0.2s;
}

.nav-link:hover,
.nav-link.router-link-active {
  color: #06b6d4;
}

.user-menu {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.username {
  color: #06b6d4;
  font-weight: 600;
}

.logout-btn {
  background: rgba(239, 68, 68, 0.1);
  color: #f87171;
  border: 1px solid rgba(239, 68, 68, 0.3);
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s;
}

.logout-btn:hover {
  background: rgba(239, 68, 68, 0.2);
  border-color: rgba(239, 68, 68, 0.5);
}

.main-content {
  flex: 1;
  padding: 2rem 0;
}

.app-footer {
  background: rgba(15, 23, 42, 0.95);
  border-top: 1px solid rgba(6, 182, 212, 0.2);
  padding: 2rem 0;
  margin-top: 4rem;
}

.footer-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
}

.footer-links {
  display: flex;
  gap: 2rem;
}

.footer-link {
  color: #cbd5e0;
  text-decoration: none;
  font-size: 0.875rem;
  transition: color 0.2s;
}

.footer-link:hover {
  color: #06b6d4;
}

@media (max-width: 768px) {
  .navbar {
    flex-direction: column;
    gap: 1rem;
  }

  .nav-links {
    flex-direction: column;
    gap: 1rem;
  }

  .footer-content {
    flex-direction: column;
    text-align: center;
  }
}
</style>
