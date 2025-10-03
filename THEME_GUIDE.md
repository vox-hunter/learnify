# Theme Configuration Guide

## Quick Start

To customize the app's colors, edit **one file**: `src/config/themeConfig.js`

All color changes in this file will automatically apply across the entire application.

---

## How to Change Theme Colors

### 1. Open the Configuration File
Navigate to: `vue-frontend/src/config/themeConfig.js`

### 2. Edit Hex Codes
Simply change the hex color codes in the theme objects:

```javascript
export const themeConfig = {
  dark: {
    accentPrimary: '#7733ff',  // Change this to your desired color
    // ... other colors
  },
  light: {
    accentPrimary: '#10B981',  // Change this too
    // ... other colors
  }
}
```

### 3. Save and Refresh
The changes will apply immediately when you save the file (hot reload in dev mode).

---

## Color Variables Explained

### Background Colors
- **bgPrimary**: Main background color for the entire app
- **bgSecondary**: Used for gradients and secondary surfaces
- **bgTertiary**: Cards, hover states, and elevated surfaces

### Text Colors
- **textPrimary**: Main body text and headings
- **textSecondary**: Labels, secondary text, descriptions
- **textMuted**: Hints, disabled text, less important info

### Accent Colors
- **accentPrimary**: Primary brand color (buttons, links, titles)
- **accentSecondary**: Secondary brand color (gradients, hover states)
- **accentLight**: Lighter variant for shadows and effects

### Border Colors
- **borderColor**: Primary borders on cards and inputs
- **borderLight**: Lighter borders for subtle separation

### UI Elements
- **cardBg**: Background for card components
- **inputBg**: Background for form inputs
- **shadowColor**: Box shadow color

---

## Example: Creating a Custom Theme

### Ocean Theme (Dark Mode)
```javascript
dark: {
  bgPrimary: '#0a192f',           // Deep ocean blue
  bgSecondary: '#112240',         // Lighter ocean blue
  bgTertiary: 'rgba(100, 255, 218, 0.1)',
  
  textPrimary: '#ccd6f6',         // Light blue-gray
  textSecondary: '#8892b0',       // Muted blue-gray
  textMuted: '#495670',
  
  accentPrimary: '#64ffda',       // Bright cyan
  accentSecondary: '#00d9ff',     // Bright blue
  accentLight: '#4dd4ac',
  
  // ... rest of colors
}
```

### Sunset Theme (Light Mode)
```javascript
light: {
  bgPrimary: '#fff5f5',           // Warm white
  bgSecondary: '#ffffff',
  bgTertiary: '#ffffff',
  
  textPrimary: '#4a1c1c',         // Deep warm brown
  textSecondary: '#6b2d2d',
  textMuted: '#8b4545',
  
  accentPrimary: '#ff6b6b',       // Coral red
  accentSecondary: '#ee5a6f',     // Deep coral
  accentLight: '#ff8787',
  
  // ... rest of colors
}
```

---

## Tips for Choosing Colors

### Contrast Ratios
- Ensure text colors have good contrast with backgrounds (WCAG AA: 4.5:1 for body text)
- Use tools like [WebAIM Contrast Checker](https://webaim.org/resources/contrastchecker/)

### Color Psychology
- **Blue**: Trust, stability, professionalism
- **Green**: Growth, success, eco-friendly
- **Purple**: Creativity, luxury, wisdom
- **Red**: Energy, passion, urgency
- **Orange**: Enthusiasm, warmth, call-to-action

### Consistency
- Keep accent colors within the same hue family for harmony
- Use lighter/darker variants of the same base color

### Testing
1. Save your changes
2. Toggle between dark/light mode using the theme button
3. Check all pages: Home, Login, Courses, Course View, Account
4. Verify readability on different screens

---

## Reverting to Defaults

If you want to go back to the original theme, replace with these values:

**Dark Mode (Original Purple):**
- Primary: `#000000`
- Accent: `#7733ff`

**Light Mode (Original Teal):**
- Primary: `#1E3A8A`
- Accent: `#10B981`
- Background: `#F9FAFB`

---

## Advanced: Using rgba() for Transparency

You can use rgba values for transparent colors:

```javascript
bgTertiary: 'rgba(119, 51, 255, 0.08)',  // 8% opacity purple
borderColor: 'rgba(119, 51, 255, 0.2)',  // 20% opacity purple
```

Convert hex to rgba: https://rgbacolorpicker.com/hex-to-rgba

---

## Need Help?

- Colors not applying? Check browser console for errors
- Want more themes? You can add more theme objects to `themeConfig`
- Questions? Check the theme store: `src/stores/theme.js`
