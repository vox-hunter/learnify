import { ref, watch } from 'vue'
import { defineStore } from 'pinia'
import { applyThemeColors } from '../config/themeConfig'

export const useThemeStore = defineStore('theme', () => {
  // Default to light mode for all users, but respect saved preference
  const getDefaultTheme = () => {
    // Check localStorage first - if user has manually changed theme, respect it
    const savedTheme = localStorage.getItem('theme')
    if (savedTheme) return savedTheme
    
    // Default to light mode for all users
    return 'light'
  }
  
  const theme = ref(getDefaultTheme())
  
  // Apply theme to document
  const applyTheme = (newTheme) => {
    // Set data-theme attribute for CSS selectors
    document.documentElement.setAttribute('data-theme', newTheme)
    
    // Apply theme colors from centralized config
    applyThemeColors(newTheme)
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
