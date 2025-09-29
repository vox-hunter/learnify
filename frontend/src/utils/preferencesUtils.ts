/**
 * Preferences Utilities
 * Separated utilities for Fast Refresh compatibility
 */

import React from 'react';

/**
 * Theme Configuration
 */
export type Theme = 'light' | 'dark' | 'system';
export type Language = 'en' | 'es' | 'fr' | 'de' | 'zh' | 'ja';
export type FontSize = 'small' | 'medium' | 'large' | 'extra-large';
export type ReducedMotion = 'auto' | 'reduce';

/**
 * Notification Preferences
 */
export interface NotificationPreferences {
  email: {
    enabled: boolean;
    frequency: 'immediate' | 'daily' | 'weekly';
    types: {
      courseUpdates: boolean;
      quizReminders: boolean;
      achievements: boolean;
      marketing: boolean;
    };
  };
  push: {
    enabled: boolean;
    types: {
      courseUpdates: boolean;
      quizReminders: boolean;
      achievements: boolean;
    };
  };
  inApp: {
    enabled: boolean;
    sound: boolean;
    types: {
      courseUpdates: boolean;
      quizReminders: boolean;
      achievements: boolean;
      social: boolean;
    };
  };
}

/**
 * Accessibility Preferences
 */
export interface AccessibilityPreferences {
  highContrast: boolean;
  reducedMotion: ReducedMotion;
  screenReader: boolean;
  keyboardNavigation: boolean;
  focusIndicators: boolean;
  fontSize: FontSize;
  audioDescriptions: boolean;
  captions: boolean;
}

/**
 * Privacy Settings
 */
export interface PrivacySettings {
  profileVisibility: 'public' | 'private' | 'friends';
  dataCollection: {
    analytics: boolean;
    performance: boolean;
    marketing: boolean;
  };
  sharing: {
    progress: boolean;
    achievements: boolean;
    courses: boolean;
  };
  cookies: {
    essential: boolean;
    functional: boolean;
    analytics: boolean;
    marketing: boolean;
  };
}

/**
 * Learning Preferences
 */
export interface LearningPreferences {
  difficulty: 'beginner' | 'intermediate' | 'advanced' | 'adaptive';
  pace: 'slow' | 'normal' | 'fast' | 'self-paced';
  reminders: {
    enabled: boolean;
    time: string; // HH:mm format
    frequency: 'daily' | 'weekdays' | 'custom';
    customDays: number[]; // 0-6 (Sunday-Saturday)
  };
  autoplay: {
    videos: boolean;
    audio: boolean;
  };
  captions: {
    enabled: boolean;
    language: Language;
  };
}

/**
 * Complete User Preferences
 */
export interface UserPreferences {
  theme: Theme;
  language: Language;
  notifications: NotificationPreferences;
  accessibility: AccessibilityPreferences;
  privacy: PrivacySettings;
  learning: LearningPreferences;
  lastUpdated: string;
  version: number;
}

/**
 * Default Preferences
 */
export const defaultPreferences: UserPreferences = {
  theme: 'system',
  language: 'en',
  notifications: {
    email: {
      enabled: true,
      frequency: 'daily',
      types: {
        courseUpdates: true,
        quizReminders: true,
        achievements: true,
        marketing: false
      }
    },
    push: {
      enabled: false,
      types: {
        courseUpdates: true,
        quizReminders: true,
        achievements: true
      }
    },
    inApp: {
      enabled: true,
      sound: true,
      types: {
        courseUpdates: true,
        quizReminders: true,
        achievements: true,
        social: true
      }
    }
  },
  accessibility: {
    highContrast: false,
    reducedMotion: 'auto',
    screenReader: false,
    keyboardNavigation: true,
    focusIndicators: true,
    fontSize: 'medium',
    audioDescriptions: false,
    captions: false
  },
  privacy: {
    profileVisibility: 'private',
    dataCollection: {
      analytics: true,
      performance: true,
      marketing: false
    },
    sharing: {
      progress: false,
      achievements: false,
      courses: false
    },
    cookies: {
      essential: true,
      functional: true,
      analytics: true,
      marketing: false
    }
  },
  learning: {
    difficulty: 'adaptive',
    pace: 'normal',
    reminders: {
      enabled: false,
      time: '09:00',
      frequency: 'daily',
      customDays: [1, 2, 3, 4, 5] // Weekdays
    },
    autoplay: {
      videos: false,
      audio: false
    },
    captions: {
      enabled: false,
      language: 'en'
    }
  },
  lastUpdated: new Date().toISOString(),
  version: 1
};

/**
 * Preferences Actions
 */
export type PreferencesAction =
  | { type: 'SET_THEME'; payload: Theme }
  | { type: 'SET_LANGUAGE'; payload: Language }
  | { type: 'UPDATE_NOTIFICATIONS'; payload: Partial<NotificationPreferences> }
  | { type: 'UPDATE_ACCESSIBILITY'; payload: Partial<AccessibilityPreferences> }
  | { type: 'UPDATE_PRIVACY'; payload: Partial<PrivacySettings> }
  | { type: 'UPDATE_LEARNING'; payload: Partial<LearningPreferences> }
  | { type: 'RESET_PREFERENCES' }
  | { type: 'LOAD_PREFERENCES'; payload: UserPreferences };

/**
 * Preferences Reducer
 */
export const preferencesReducer = (
  state: UserPreferences,
  action: PreferencesAction
): UserPreferences => {
  const updatedState = (() => {
    switch (action.type) {
      case 'SET_THEME':
        return { ...state, theme: action.payload };
      case 'SET_LANGUAGE':
        return { ...state, language: action.payload };
      case 'UPDATE_NOTIFICATIONS':
        return {
          ...state,
          notifications: { ...state.notifications, ...action.payload }
        };
      case 'UPDATE_ACCESSIBILITY':
        return {
          ...state,
          accessibility: { ...state.accessibility, ...action.payload }
        };
      case 'UPDATE_PRIVACY':
        return {
          ...state,
          privacy: { ...state.privacy, ...action.payload }
        };
      case 'UPDATE_LEARNING':
        return {
          ...state,
          learning: { ...state.learning, ...action.payload }
        };
      case 'RESET_PREFERENCES':
        return { ...defaultPreferences };
      case 'LOAD_PREFERENCES':
        return action.payload;
      default:
        return state;
    }
  })();

  return {
    ...updatedState,
    lastUpdated: new Date().toISOString(),
    version: updatedState.version + (action.type !== 'LOAD_PREFERENCES' ? 1 : 0)
  };
};

/**
 * Storage Manager
 */
export class PreferencesStorage {
  private static readonly STORAGE_KEY = 'learnify_preferences';
  private static readonly BACKUP_KEY = 'learnify_preferences_backup';

  static async save(preferences: UserPreferences): Promise<void> {
    try {
      // Create backup of current preferences
      const existing = localStorage.getItem(this.STORAGE_KEY);
      if (existing) {
        localStorage.setItem(this.BACKUP_KEY, existing);
      }

      // Save new preferences
      localStorage.setItem(this.STORAGE_KEY, JSON.stringify(preferences));

      // Also attempt to save to server if authenticated
      if (this.isAuthenticated()) {
        await this.saveToServer(preferences);
      }
    } catch (error) {
      console.error('Failed to save preferences:', error);
      throw new Error('Failed to save preferences');
    }
  }

  static load(): UserPreferences {
    try {
      const stored = localStorage.getItem(this.STORAGE_KEY);
      if (stored) {
        const parsed = JSON.parse(stored) as UserPreferences;
        return this.migratePreferences(parsed);
      }
    } catch (error) {
      console.error('Failed to load preferences:', error);
      // Try to load backup
      try {
        const backup = localStorage.getItem(this.BACKUP_KEY);
        if (backup) {
          return JSON.parse(backup) as UserPreferences;
        }
      } catch (backupError) {
        console.error('Failed to load backup preferences:', backupError);
      }
    }
    return defaultPreferences;
  }

  static async loadFromServer(): Promise<UserPreferences | null> {
    if (!this.isAuthenticated()) {
      return null;
    }

    try {
      const response = await fetch('/api/user/preferences', {
        headers: {
          'Authorization': `Bearer ${this.getAuthToken()}`
        }
      });

      if (response.ok) {
        const serverPreferences = await response.json();
        return this.migratePreferences(serverPreferences);
      }
    } catch (error) {
      console.error('Failed to load preferences from server:', error);
    }

    return null;
  }

  private static async saveToServer(preferences: UserPreferences): Promise<void> {
    const response = await fetch('/api/user/preferences', {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.getAuthToken()}`
      },
      body: JSON.stringify(preferences)
    });

    if (!response.ok) {
      throw new Error('Failed to save preferences to server');
    }
  }

  private static migratePreferences(preferences: unknown): UserPreferences {
    // Handle version migrations
    const prefs = preferences as Record<string, unknown>;
    if (!prefs.version || (prefs.version as number) < defaultPreferences.version) {
      return {
        ...defaultPreferences,
        ...prefs,
        version: defaultPreferences.version
      } as UserPreferences;
    }

    return prefs as unknown as UserPreferences;
  }

  private static isAuthenticated(): boolean {
    return !!localStorage.getItem('auth_token');
  }

  private static getAuthToken(): string | null {
    return localStorage.getItem('auth_token');
  }
}

/**
 * Preferences Context Type
 */
export interface PreferencesContextType {
  preferences: UserPreferences;
  updateTheme: (theme: Theme) => void;
  updateLanguage: (language: Language) => void;
  updateNotifications: (notifications: Partial<NotificationPreferences>) => void;
  updateAccessibility: (accessibility: Partial<AccessibilityPreferences>) => void;
  updatePrivacy: (privacy: Partial<PrivacySettings>) => void;
  updateLearning: (learning: Partial<LearningPreferences>) => void;
  resetPreferences: () => void;
  savePreferences: () => Promise<void>;
  isLoading: boolean;
  lastSaved: string | null;
}

/**
 * Theme application utilities
 */
export const themeUtils = {
  applyTheme: (theme: Theme) => {
    const root = document.documentElement;
    
    if (theme === 'system') {
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      root.setAttribute('data-theme', prefersDark ? 'dark' : 'light');
    } else {
      root.setAttribute('data-theme', theme);
    }
  },

  applyAccessibilityPreferences: (accessibility: AccessibilityPreferences) => {
    const root = document.documentElement;

    root.style.setProperty('--font-size-multiplier', 
      accessibility.fontSize === 'small' ? '0.875' :
      accessibility.fontSize === 'large' ? '1.125' :
      accessibility.fontSize === 'extra-large' ? '1.25' : '1'
    );

    if (accessibility.reducedMotion === 'reduce') {
      root.style.setProperty('--animation-duration', '0.01ms');
      root.style.setProperty('--transition-duration', '0.01ms');
    } else {
      root.style.removeProperty('--animation-duration');
      root.style.removeProperty('--transition-duration');
    }

    root.setAttribute('data-high-contrast', accessibility.highContrast.toString());
    root.setAttribute('data-focus-indicators', accessibility.focusIndicators.toString());
  }
};

/**
 * Hook for using preferences (will be re-exported from main file)
 */
export const createUsePreferences = (context: React.Context<PreferencesContextType | undefined>) => {
  return () => {
    const contextValue = React.useContext(context);
    if (contextValue === undefined) {
      throw new Error('usePreferences must be used within a PreferencesProvider');
    }
    return contextValue;
  };
};