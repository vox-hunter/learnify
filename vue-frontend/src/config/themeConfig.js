/**
 * Theme Configuration
 * 
 * Easily customize your app's color schemes by editing the hex codes below.
 * Changes here will automatically apply to the entire application.
 */

export const themeConfig = {
  // DARK MODE THEME
  dark: {
    // Background Colors
    bgPrimary: '#000000',           // Main background
    bgSecondary: '#1a1a1a',         // Secondary background (gradients)
    bgTertiary: 'rgba(255, 255, 255, 0.08)',  // Card backgrounds, hover states
    
    // Text Colors
    textPrimary: '#e2e8f0',         // Main text color
    textSecondary: '#cbd5e0',       // Secondary text, labels
    textMuted: '#94a3b8',           // Muted text, hints
    
    // Accent Colors
    accentPrimary: '#7733ff',       // Primary accent (buttons, links, titles)
    accentSecondary: '#9d5dff',     // Secondary accent (gradients, hover)
    accentLight: '#5a1fd9',         // Light accent variant
    
    // Border Colors
    borderColor: 'rgba(119, 51, 255, 0.2)',   // Primary borders
    borderLight: 'rgba(255, 255, 255, 0.15)', // Light borders
    
    // UI Element Colors
    cardBg: 'rgba(255, 255, 255, 0.08)',      // Card backgrounds
    inputBg: 'rgba(255, 255, 255, 0.1)',      // Form input backgrounds
    shadowColor: 'rgba(0, 0, 0, 0.3)',        // Box shadows
  },
  
  // LIGHT MODE THEME
  light: {
    // Background Colors
    bgPrimary: '#F9FAFB',           // Main background (off-white)
    bgSecondary: '#ffffff',         // Secondary background (pure white)
    bgTertiary: '#ffffff',          // Card backgrounds
    
    // Text Colors
    textPrimary: '#1E3A8A',         // Main text (deep navy blue)
    textSecondary: '#1f2937',       // Secondary text
    textMuted: '#6b7280',           // Muted text, hints
    
    // Accent Colors
    accentPrimary: '#559bfd',       // Primary accent (vibrant teal-green)
    accentSecondary: '#559bfd',     // Secondary accent (darker teal)
    accentLight: '#559bfd',         // Light accent variant
    
    // Border Colors
    borderColor: 'rgba(30, 58, 138, 0.15)',   // Primary borders (navy)
    borderLight: 'rgba(16, 185, 129, 0.2)',   // Light borders (teal)
    
    // UI Element Colors
    cardBg: '#ffffff',              // Card backgrounds
    inputBg: '#ffffff',             // Form input backgrounds
    shadowColor: 'rgba(0, 0, 0, 0.1)',        // Box shadows
  }
}

/**
 * Apply theme colors to CSS variables
 * @param {string} themeName - 'dark' or 'light'
 */
export function applyThemeColors(themeName) {
  const theme = themeConfig[themeName]
  if (!theme) {
    console.error(`Theme "${themeName}" not found in themeConfig`)
    return
  }
  
  const root = document.documentElement
  
  // Apply all theme colors as CSS variables
  root.style.setProperty('--bg-primary', theme.bgPrimary)
  root.style.setProperty('--bg-secondary', theme.bgSecondary)
  root.style.setProperty('--bg-tertiary', theme.bgTertiary)
  
  root.style.setProperty('--text-primary', theme.textPrimary)
  root.style.setProperty('--text-secondary', theme.textSecondary)
  root.style.setProperty('--text-muted', theme.textMuted)
  
  root.style.setProperty('--accent-primary', theme.accentPrimary)
  root.style.setProperty('--accent-secondary', theme.accentSecondary)
  root.style.setProperty('--accent-light', theme.accentLight)
  
  root.style.setProperty('--border-color', theme.borderColor)
  root.style.setProperty('--border-light', theme.borderLight)
  
  root.style.setProperty('--card-bg', theme.cardBg)
  root.style.setProperty('--input-bg', theme.inputBg)
  root.style.setProperty('--shadow-color', theme.shadowColor)
}

/**
 * Get a specific theme configuration
 * @param {string} themeName - 'dark' or 'light'
 * @returns {object} Theme configuration object
 */
export function getTheme(themeName) {
  return themeConfig[themeName] || themeConfig.dark
}

export default themeConfig
