import { ref, watch } from 'vue'
import { defineStore } from 'pinia'

export const useThemeStore = defineStore('theme', () => {
  // Initialize from localStorage or default to 'dark'
  const theme = ref(localStorage.getItem('theme') || 'dark')
  
  // Apply theme to document
  const applyTheme = (newTheme) => {
    document.documentElement.setAttribute('data-theme', newTheme)
  }
  
  // Toggle between dark and light
  const toggleTheme = () => {
    theme.value = theme.value === 'dark' ? 'light' : 'dark'
  }
  
  // Set specific theme
  const setTheme = (newTheme) => {
    if (newTheme === 'dark' || newTheme === 'light') {
      theme.value = newTheme
    }
  }
  
  // Watch for theme changes and persist
  watch(theme, (newTheme) => {
    localStorage.setItem('theme', newTheme)
    applyTheme(newTheme)
  })
  
  // Apply theme on store initialization
  applyTheme(theme.value)
  
  return {
    theme,
    toggleTheme,
    setTheme
  }
})
