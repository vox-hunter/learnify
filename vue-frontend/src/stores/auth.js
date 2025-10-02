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
      
      // Store complete user data as JSON string
      const userData = JSON.stringify(response.data)
      
      // Store based on remember me preference
      if (rememberMe) {
        // Store in cookie for 30 days (username only for simplicity)
        setCookie('username', username, 30)
        setCookie('rememberMe', 'true', 30)
        // Store isAdmin flag if present
        if (response.data.isAdmin) {
          setCookie('isAdmin', 'true', 30)
        }
        // Store full user data in localStorage
        localStorage.setItem('userData', userData)
      } else {
        // Store in session storage only
        sessionStorage.setItem('username', username)
        sessionStorage.setItem('userData', userData)
        if (response.data.isAdmin) {
          sessionStorage.setItem('isAdmin', 'true')
        }
      }
      
      // Always store in localStorage for current session
      localStorage.setItem('username', username)
      localStorage.setItem('userData', userData)
      if (response.data.isAdmin) {
        localStorage.setItem('isAdmin', 'true')
      }
      
      return { success: true }
    } catch (error) {
      let errorMessage = 'Login failed'
      
      if (error.response) {
        // Server responded with error
        errorMessage = error.response.data?.detail || `Server error: ${error.response.status}`
      } else if (error.request) {
        // Request made but no response received
        errorMessage = 'Cannot connect to server. Please check if the backend is running.'
      } else {
        // Something else happened
        errorMessage = error.message || 'Login failed'
      }
      
      return { 
        success: false, 
        error: errorMessage
      }
    }
  }

  async function register(userData) {
    try {
      const response = await api.post('/auth/register', userData)
      return { success: true, data: response.data }
    } catch (error) {
      let errorMessage = 'Registration failed'
      
      if (error.response) {
        // Server responded with error
        errorMessage = error.response.data?.detail || `Server error: ${error.response.status}`
      } else if (error.request) {
        // Request made but no response received
        errorMessage = 'Cannot connect to server. Please check if the backend is running.'
      } else {
        // Something else happened
        errorMessage = error.message || 'Registration failed'
      }
      
      return { 
        success: false, 
        error: errorMessage
      }
    }
  }

  function logout() {
    user.value = null
    token.value = null
    localStorage.removeItem('authToken')
    localStorage.removeItem('username')
    localStorage.removeItem('userData')
    localStorage.removeItem('isAdmin')
    sessionStorage.removeItem('username')
    sessionStorage.removeItem('userData')
    sessionStorage.removeItem('isAdmin')
    deleteCookie('username')
    deleteCookie('rememberMe')
    deleteCookie('isAdmin')
  }

  // Initialize user from localStorage/cookies if available
  function initialize() {
    // Priority 1: Try to restore full user data from localStorage
    const localUserData = localStorage.getItem('userData')
    if (localUserData) {
      try {
        user.value = JSON.parse(localUserData)
        return
      } catch (e) {
        console.error('Failed to parse userData:', e)
      }
    }
    
    // Priority 2: Try sessionStorage
    const sessionUserData = sessionStorage.getItem('userData')
    if (sessionUserData) {
      try {
        user.value = JSON.parse(sessionUserData)
        return
      } catch (e) {
        console.error('Failed to parse sessionUserData:', e)
      }
    }
    
    // Fallback: Check old storage format (username only)
    const cookieUsername = getCookie('username')
    const rememberMe = getCookie('rememberMe') === 'true'
    const cookieIsAdmin = getCookie('isAdmin') === 'true'
    
    const localUsername = localStorage.getItem('username')
    const localIsAdmin = localStorage.getItem('isAdmin') === 'true'
    
    const sessionUsername = sessionStorage.getItem('username')
    const sessionIsAdmin = sessionStorage.getItem('isAdmin') === 'true'
    
    const storedUsername = cookieUsername || localUsername || sessionUsername
    const isAdmin = cookieIsAdmin || localIsAdmin || sessionIsAdmin
    
    if (storedUsername) {
      // Restore user object with admin flag (fallback format)
      user.value = { 
        username: storedUsername,
        isAdmin: isAdmin
      }
      
      // If remember me is true, ensure cookie is set
      if (rememberMe && !cookieUsername) {
        setCookie('username', storedUsername, 30)
        if (isAdmin) {
          setCookie('isAdmin', 'true', 30)
        }
      }
    } else {
      // No stored auth, clear everything
      user.value = null
      token.value = null
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
