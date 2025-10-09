<template>
  <aside
    :class="['sidebar', { collapsed: isCollapsed }]"
    @mouseenter="handleMouseEnter"
    @mouseleave="handleMouseLeave"
  >
    <!-- Top Section -->
    <div class="sidebar-top">
      <!-- Brand (Decorative Only) -->
      <div class="sidebar-brand">
        <img
          v-if="!isCollapsed"
          src="/logo.png"
          alt="AI Loom"
          class="brand-logo"
        >
        <img
          v-else
          src="/logo.png"
          alt="AI Loom"
          class="brand-logo-small"
        >
        <span
          v-if="!isCollapsed"
          class="brand-text"
        >AI Loom</span>
      </div>

      <!-- New Chat Button - Primary CTA with Glow -->
      <button
        class="new-chat-btn"
        :title="isCollapsed ? 'New Chat' : ''"
        @click="startNewChat"
      >
        <span class="icon">+</span>
        <span
          v-if="!isCollapsed"
          class="text"
        >New Chat</span>
      </button>
    </div>

    <!-- Navigation -->
    <nav class="sidebar-nav">
      <router-link
        to="/"
        class="nav-item"
        :title="isCollapsed ? 'Chat' : ''"
      >
        <span class="nav-icon">💬</span>
        <span
          v-if="!isCollapsed"
          class="nav-label"
        >Chat</span>
      </router-link>

      <router-link
        to="/courses"
        class="nav-item"
        :title="isCollapsed ? 'Courses' : ''"
      >
        <span class="nav-icon">📚</span>
        <span
          v-if="!isCollapsed"
          class="nav-label"
        >Courses</span>
      </router-link>

      <router-link
        to="/library"
        class="nav-item"
        :title="isCollapsed ? 'Library' : ''"
      >
        <span class="nav-icon">🏛️</span>
        <span
          v-if="!isCollapsed"
          class="nav-label"
        >Library</span>
      </router-link>

      <router-link
        v-if="!isAuthenticated"
        to="/login"
        class="nav-item"
        :title="isCollapsed ? 'Login' : ''"
      >
        <span class="nav-icon">🔐</span>
        <span
          v-if="!isCollapsed"
          class="nav-label"
        >Login</span>
      </router-link>
    </nav>

    <!-- Bottom Section -->
    <div class="sidebar-bottom">
      <!-- Theme Toggle -->
      <button
        class="theme-toggle-btn"
        :title="theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'"
        @click="toggleTheme"
      >
        <span class="nav-icon">{{ theme === 'dark' ? '☀️' : '🌙' }}</span>
        <span
          v-if="!isCollapsed"
          class="nav-label"
        >
          {{ theme === 'dark' ? 'Light Mode' : 'Dark Mode' }}
        </span>
      </button>

      <!-- User Profile with Dropdown -->
      <div
        v-if="isAuthenticated"
        class="user-profile"
      >
        <div
          class="user-trigger"
          :title="isCollapsed ? username : ''"
          @click="toggleDropdown"
        >
          <div class="user-avatar">
            {{ userInitials }}
          </div>
          <div
            v-if="!isCollapsed"
            class="user-info"
          >
            <div class="user-name">
              {{ username }}
            </div>
          </div>
        </div>

        <!-- Dropdown Menu (Top-aligned) -->
        <transition name="dropdown">
          <div
            v-if="showDropdown && !isCollapsed"
            class="user-dropdown"
          >
            <router-link
              to="/account"
              class="dropdown-item"
              @click="closeDropdown"
            >
              <span class="dropdown-icon">⚙️</span>
              <span class="dropdown-label">Settings</span>
            </router-link>
            <button
              class="dropdown-item logout"
              @click="logout"
            >
              <span class="dropdown-icon">🚪</span>
              <span class="dropdown-label">Logout</span>
            </button>
          </div>
        </transition>
      </div>
    </div>
  </aside>
</template>

<script>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { useThemeStore } from '../stores/theme'

export default {
    name: 'Sidebar',
    emits: ['toggle-collapse'],
    setup(props, { emit }) {
        const router = useRouter()
        const authStore = useAuthStore()
        const themeStore = useThemeStore()

        const isCollapsed = ref(true) // Start collapsed
        const showDropdown = ref(false)

        const isAuthenticated = computed(() => authStore.isAuthenticated)
        const username = computed(() => authStore.user?.username || 'Guest')
        const theme = computed(() => themeStore.theme)

        const userInitials = computed(() => {
            const name = username.value
            if (!name || name === 'Guest') return '?'
            return name.slice(0, 2).toUpperCase()
        })

        const handleMouseEnter = () => {
            isCollapsed.value = false
            emit('toggle-collapse', false)
        }

        const handleMouseLeave = () => {
            isCollapsed.value = true
            showDropdown.value = false // Close dropdown when leaving sidebar
            emit('toggle-collapse', true)
        }

        const toggleDropdown = () => {
            if (!isCollapsed.value) {
                showDropdown.value = !showDropdown.value
            }
        }

        const closeDropdown = () => {
            showDropdown.value = false
        }

        const startNewChat = () => {
            // Clear chat session and navigate to home
            localStorage.removeItem('chat_session_id')
      localStorage.removeItem('chat_messages')
            router.push('/')
            // Force page reload to clear chat
            if (router.currentRoute.value.path === '/') {
                window.location.reload()
            }
        }

        const toggleTheme = () => {
            themeStore.toggleTheme()
        }

        const logout = () => {
            authStore.logout()
            showDropdown.value = false
            router.push('/login')
        }

        return {
            isCollapsed,
            showDropdown,
            isAuthenticated,
            username,
            userInitials,
            theme,
            handleMouseEnter,
            handleMouseLeave,
            toggleDropdown,
            closeDropdown,
            startNewChat,
            toggleTheme,
            logout
        }
    }
}
</script>

<style scoped>
.sidebar {
    position: fixed;
    left: 0;
    top: 0;
    height: 100vh;
    width: 80px;
    background: var(--card-bg);
    border-right: 1px solid var(--border-color);
    display: flex;
    flex-direction: column;
    transition: width 280ms ease-in-out;
    z-index: 1000;
    padding: 1rem;
    overflow: hidden;
}

.sidebar:not(.collapsed) {
    width: 260px;
}

/* Top Section */
.sidebar-top {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    margin-bottom: 1.5rem;
}

.sidebar-brand {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.5rem;
    overflow: hidden;
    pointer-events: none;
    /* Decorative only */
}

.brand-logo {
    width: 32px;
    height: 32px;
    flex-shrink: 0;
}

.brand-logo-small {
    width: 32px;
    height: 32px;
    margin: 0 auto;
}

.brand-text {
    font-size: 1.25rem;
    font-weight: 700;
    color: var(--text-primary);
    white-space: nowrap;
    opacity: 0;
    max-width: 0;
    overflow: hidden;
    transition: opacity 280ms ease-in-out, max-width 280ms ease-in-out;
}

.sidebar:not(.collapsed) .brand-text {
    opacity: 1;
    max-width: 200px;
}

/* New Chat Button - Primary CTA with Glow */
.new-chat-btn {
    width: 100%;
    padding: 0.75rem;
    background: linear-gradient(135deg, #7733ff, #00d4ff);
    color: white;
    border: none;
    border-radius: 0.75rem;
    font-weight: 600;
    font-size: 1.5rem;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 0 4px 20px rgba(119, 51, 255, 0.4);
    position: relative;
    overflow: hidden;
}

.new-chat-btn::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle, rgba(255, 255, 255, 0.3) 0%, transparent 70%);
    transform: scale(0);
    transition: transform 0.6s;
}

.new-chat-btn:hover::before {
    transform: scale(1);
}

.new-chat-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 30px rgba(119, 51, 255, 0.6);
}

.new-chat-btn:active {
    transform: translateY(0);
}

.new-chat-btn .icon {
    font-size: 1.5rem;
    font-weight: 300;
}

.new-chat-btn .text {
    white-space: nowrap;
    opacity: 0;
    max-width: 0;
    overflow: hidden;
    transition: opacity 280ms ease-in-out, max-width 280ms ease-in-out;
    font-size: 1rem;
}

.sidebar:not(.collapsed) .new-chat-btn .text {
    opacity: 1;
    max-width: 150px;
}

/* Navigation */
.sidebar-nav {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    overflow-y: auto;
    padding: 0.5rem 0;
}

.nav-item {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.75rem;
    border-radius: 0.75rem;
    color: var(--text-secondary);
    text-decoration: none;
    transition: all 0.2s;
    position: relative;
    white-space: nowrap;
}

.sidebar.collapsed .nav-item {
    justify-content: center;
}

.nav-item:hover {
    background: var(--bg-tertiary);
    color: var(--text-primary);
}

.nav-item.router-link-active {
    background: linear-gradient(135deg, rgba(119, 51, 255, 0.15), rgba(0, 212, 255, 0.15));
    color: var(--accent-primary);
    font-weight: 600;
}

.nav-icon {
    font-size: 1.25rem;
    flex-shrink: 0;
}

.nav-label {
    font-size: 0.95rem;
    font-weight: 500;
    opacity: 0;
    max-width: 0;
    overflow: hidden;
    transition: opacity 280ms ease-in-out, max-width 280ms ease-in-out;
}

.sidebar:not(.collapsed) .nav-label {
    opacity: 1;
    max-width: 200px;
}

/* Bottom Section */
.sidebar-bottom {
    border-top: 1px solid var(--border-color);
    padding-top: 1rem;
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
}

.theme-toggle-btn {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.75rem;
    background: transparent;
    border: 1px solid var(--border-color);
    border-radius: 0.75rem;
    color: var(--text-secondary);
    cursor: pointer;
    transition: all 0.2s;
    white-space: nowrap;
}

.sidebar.collapsed .theme-toggle-btn {
    justify-content: center;
}

.theme-toggle-btn:hover {
    background: var(--bg-tertiary);
    border-color: var(--accent-primary);
    color: var(--accent-primary);
}

/* User Profile with Dropdown */
.user-profile {
    position: relative;
}

.user-trigger {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.75rem;
    background: var(--bg-tertiary);
    border-radius: 0.75rem;
    cursor: pointer;
    transition: all 0.2s;
}

.user-trigger:hover {
    background: var(--card-bg);
    box-shadow: 0 2px 8px var(--shadow-color);
}

.sidebar.collapsed .user-trigger {
    justify-content: center;
}

.user-avatar {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background: linear-gradient(135deg, #7733ff, #00d4ff);
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    font-size: 0.875rem;
    flex-shrink: 0;
    box-shadow: 0 4px 12px rgba(119, 51, 255, 0.3);
}

.user-info {
    flex: 1;
    min-width: 0;
    opacity: 0;
    max-width: 0;
    overflow: hidden;
    transition: opacity 280ms ease-in-out, max-width 280ms ease-in-out;
}

.sidebar:not(.collapsed) .user-info {
    opacity: 1;
    max-width: 200px;
}

.user-name {
    font-size: 0.875rem;
    font-weight: 600;
    color: var(--text-primary);
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

/* Dropdown Menu */
.user-dropdown {
    position: absolute;
    bottom: 100%;
    left: 0;
    right: 0;
    margin-bottom: 0.5rem;
    background: var(--card-bg);
    border: 1px solid var(--border-color);
    border-radius: 0.75rem;
    box-shadow: 0 8px 24px var(--shadow-color);
    overflow: hidden;
    z-index: 100;
}

/* Ensure solid dropdown in dark mode (no translucency) */
:root[data-theme="dark"] .user-dropdown {
  background-color: #111827; /* solid slate-900 */
  border-color: rgba(255, 255, 255, 0.08);
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.6);
}

.dropdown-item {
    width: 100%;
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.75rem 1rem;
    border: none;
    background: transparent;
    color: var(--text-secondary);
    text-decoration: none;
    cursor: pointer;
    transition: all 0.2s;
    text-align: left;
    font-size: 0.875rem;
}

.dropdown-item:hover {
    background: var(--bg-tertiary);
    color: var(--text-primary);
}

.dropdown-item.logout {
    color: #f87171;
}

.dropdown-item.logout:hover {
    background: rgba(239, 68, 68, 0.1);
}

.dropdown-icon {
    font-size: 1rem;
}

.dropdown-label {
    font-weight: 500;
}

/* Dropdown Animation */
.dropdown-enter-active,
.dropdown-leave-active {
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.dropdown-enter-from,
.dropdown-leave-to {
    opacity: 0;
    transform: translateY(10px);
}

/* Scrollbar */
.sidebar-nav::-webkit-scrollbar {
    width: 6px;
}

.sidebar-nav::-webkit-scrollbar-track {
    background: transparent;
}

.sidebar-nav::-webkit-scrollbar-thumb {
    background: var(--border-color);
    border-radius: 3px;
}

.sidebar-nav::-webkit-scrollbar-thumb:hover {
    background: var(--text-muted);
}

/* Mobile Responsive */
@media (max-width: 768px) {
    .sidebar {
        width: 80px;
    }

    .sidebar:hover {
        width: 260px;
    }
}
</style>
