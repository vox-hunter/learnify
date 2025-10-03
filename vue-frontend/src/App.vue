<template>
  <div id="app">
    <header class="app-header">
      <div class="container">
        <nav class="navbar">
          <div class="brand">
            <router-link to="/" class="brand-link">
              <img src="/logo.png" alt="AI Loom" class="brand-logo" />
              <span class="brand-name">AI Loom</span>
            </router-link>
          </div>
          <div class="nav-links">
            <router-link to="/" class="nav-link">Home</router-link>
            <router-link to="/courses" class="nav-link">My Courses</router-link>
            <router-link v-if="!isAuthenticated" to="/login" class="nav-link">Login</router-link>
            <div v-else class="user-menu">
              <router-link to="/account" class="nav-link account-link">👤 Account</router-link>
                <span class="username">Welcome, {{ username }}</span>
              <button @click="logout" class="logout-btn">Logout</button>
            </div>
            <button @click="toggleTheme" class="theme-toggle" :title="theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'">
              <span v-if="theme === 'dark'">☀️</span>
              <span v-else>🌙</span>
            </button>
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
          <div class="footer-brand">
            <img src="/logo.png" alt="AI Loom" class="footer-logo" />
            <div>
              <p class="footer-title">AI Loom</p>
              <p class="footer-copyright">&copy; 2025 AI Loom. All rights reserved.</p>
            </div>
          </div>
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
import { useThemeStore } from './stores/theme'

export default {
  name: 'App',
  setup() {
    const authStore = useAuthStore()
    const themeStore = useThemeStore()
    
    // Initialize auth on app mount (restore from cookies/localStorage)
    onMounted(() => {
      authStore.initialize()
    })
    
    const isAuthenticated = computed(() => authStore.isAuthenticated)
    const username = computed(() => authStore.user?.username)
    const theme = computed(() => themeStore.theme)
    
    const logout = () => {
      authStore.logout()
    }
    
    const toggleTheme = () => {
      themeStore.toggleTheme()
    }
    
    return {
      isAuthenticated,
      username,
      theme,
      logout,
      toggleTheme
    }
  }
}
</script>

<style scoped>
#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: linear-gradient(135deg, var(--bg-primary) 0%, var(--bg-secondary) 100%);
  color: var(--text-primary);
  transition: background 0.3s ease, color 0.3s ease;
}

.app-header {
  background: var(--bg-primary);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid var(--border-color);
  position: sticky;
  top: 0;
  z-index: 1000;
  box-shadow: 0 4px 6px -1px var(--shadow-color);
  transition: background-color 0.3s ease, border-color 0.3s ease;
}

:root[data-theme="light"] .app-header {
  background: rgba(255, 255, 255, 0.95);
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

.brand-logo {
  height: 40px;
  width: auto;
  object-fit: contain;
}

.brand-name {
  font-size: 1.5rem;
  font-weight: 700;
  background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
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
  color: var(--text-secondary);
  text-decoration: none;
  font-weight: 500;
  transition: color 0.2s;
}

.nav-link:hover,
.nav-link.router-link-active {
  color: var(--accent-primary);
}

.user-menu {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.username {
  color: var(--accent-primary);
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

.theme-toggle {
  background: var(--card-bg);
  border: 1px solid var(--border-color);
  padding: 0.5rem 0.75rem;
  border-radius: 0.5rem;
  cursor: pointer;
  font-size: 1.25rem;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 2.5rem;
  height: 2.5rem;
}

.theme-toggle:hover {
  transform: scale(1.1);
  border-color: var(--accent-primary);
}

.main-content {
  flex: 1;
  padding: 2rem 0;
}

.app-footer {
  background: var(--bg-primary);
  border-top: 1px solid var(--border-color);
  padding: 2rem 0;
  margin-top: 4rem;
  transition: background-color 0.3s ease, border-color 0.3s ease;
}

:root[data-theme="light"] .app-footer {
  background: rgba(255, 255, 255, 0.95);
}

.footer-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 2rem;
}

.footer-brand {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.footer-logo {
  height: 40px;
  width: auto;
  object-fit: contain;
}

.footer-title {
  font-weight: 700;
  font-size: 1.25rem;
  background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 0.25rem;
}

.footer-copyright {
  color: var(--text-secondary);
  font-size: 0.875rem;
}

.footer-links {
  display: flex;
  gap: 2rem;
}

.footer-link {
  color: var(--text-secondary);
  text-decoration: none;
  font-size: 0.875rem;
  transition: color 0.2s;
}

.footer-link:hover {
  color: var(--accent-primary);
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
