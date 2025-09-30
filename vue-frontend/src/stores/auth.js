import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../services/api'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const token = ref(localStorage.getItem('authToken') || null)

  const isAuthenticated = computed(() => !!user.value)

  async function login(username, password) {
    try {
      const response = await api.post('/auth/login', { username, password })
      user.value = response.data
      // Store username in localStorage for persistence
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
  }

  // Initialize user from localStorage if available
  function initialize() {
    const storedUsername = localStorage.getItem('username')
    if (storedUsername) {
      user.value = { username: storedUsername }
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
