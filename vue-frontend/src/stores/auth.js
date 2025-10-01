import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../services/api'

// Simple cookie helper functions
function setCookie(name, value, days) {
  let expires = ''
  if (days) {
    const date = new Date()
    date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000))
    expires = '; expires=' + date.toUTCString()
  }
  document.cookie = name + '=' + (value || '') + expires + '; path=/'
}

function getCookie(name) {
  const nameEQ = name + '='
  const ca = document.cookie.split(';')
  for (let i = 0; i < ca.length; i++) {
    let c = ca[i]
    while (c.charAt(0) === ' ') c = c.substring(1, c.length)
    if (c.indexOf(nameEQ) === 0) return c.substring(nameEQ.length, c.length)
  }
  return null
}

function deleteCookie(name) {
  document.cookie = name + '=; Path=/; Expires=Thu, 01 Jan 1970 00:00:01 GMT;'
}

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const token = ref(localStorage.getItem('authToken') || null)

  const isAuthenticated = computed(() => !!user.value)

  async function login(username, password, rememberMe = false) {
    try {
      const response = await api.post('/auth/login', { username, password })
      user.value = response.data
      
      // Store username based on remember me preference
      if (rememberMe) {
        // Store in cookie for 30 days
        setCookie('username', username, 30)
        setCookie('rememberMe', 'true', 30)
      } else {
        // Store in session storage only
        sessionStorage.setItem('username', username)
      }
      
      // Always store in localStorage for current session
      localStorage.setItem('username', username)
      
      return { success: true }
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Login failed' 
      }
    }
  }

  async function register(userData) {
    try {
      const response = await api.post('/auth/register', userData)
      return { success: true, data: response.data }
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Registration failed' 
      }
    }
  }

  function logout() {
    user.value = null
    token.value = null
    localStorage.removeItem('authToken')
    localStorage.removeItem('username')
    sessionStorage.removeItem('username')
    deleteCookie('username')
    deleteCookie('rememberMe')
  }

  // Initialize user from localStorage/cookies if available
  function initialize() {
    // Check cookie first (for remember me)
    let storedUsername = getCookie('username')
    const rememberMe = getCookie('rememberMe') === 'true'
    
    // Fall back to localStorage/sessionStorage
    if (!storedUsername) {
      storedUsername = localStorage.getItem('username') || sessionStorage.getItem('username')
    }
    
    if (storedUsername) {
      user.value = { username: storedUsername }
      
      // If we found username but not in cookie, and remember me is not set, it's a session login
      if (!rememberMe && !getCookie('username')) {
        // This is a session login, don't persist to cookie
      }
    }
  }

  return {
    user,
    token,
    isAuthenticated,
    login,
    register,
    logout,
    initialize
  }
})
