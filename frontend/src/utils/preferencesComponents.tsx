/**
 * User Preferences and Settings Management Components
 * React components for preferences and settings UI
 */

import React, { useReducer, useEffect } from 'react';
import { useToast } from './errorHandlingUtils';
import { PreferencesContext, usePreferences } from './preferencesHook';
import {
  type PreferencesContextType,
  type Theme,
  type Language,
  type NotificationPreferences,
  type AccessibilityPreferences,
  type PrivacySettings,
  type LearningPreferences,
  defaultPreferences,
  preferencesReducer,
  PreferencesStorage,
  themeUtils
} from './preferencesUtils';

/**
 * Preferences Provider Component
 */
export const PreferencesProvider: React.FC<{ children: React.ReactNode }> = ({
  children
}) => {
  const [preferences, dispatch] = useReducer(preferencesReducer, defaultPreferences);
  const [isLoading, setIsLoading] = React.useState(true);
  const [lastSaved, setLastSaved] = React.useState<string | null>(null);
  const { addToast } = useToast();

  // Load preferences on mount
  useEffect(() => {
    const loadPreferences = async () => {
      try {
        setIsLoading(true);

        // Try to load from server first
        const serverPreferences = await PreferencesStorage.loadFromServer();
        if (serverPreferences) {
          dispatch({ type: 'LOAD_PREFERENCES', payload: serverPreferences });
        } else {
          // Fallback to local storage
          const localPreferences = PreferencesStorage.load();
          dispatch({ type: 'LOAD_PREFERENCES', payload: localPreferences });
        }
      } catch (error) {
        console.error('Failed to load preferences:', error);
        addToast({
          type: 'warning',
          title: 'Settings Loading Failed',
          message: 'Using default settings. Your preferences will be saved when you make changes.'
        });
      } finally {
        setIsLoading(false);
      }
    };

    loadPreferences();
  }, [addToast]);

  // Apply theme changes to document
  useEffect(() => {
    themeUtils.applyTheme(preferences.theme);

    // Listen for system theme changes
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    const handleChange = () => {
      if (preferences.theme === 'system') {
        themeUtils.applyTheme(preferences.theme);
      }
    };

    mediaQuery.addEventListener('change', handleChange);
    return () => mediaQuery.removeEventListener('change', handleChange);
  }, [preferences.theme]);

  // Apply accessibility preferences
  useEffect(() => {
    themeUtils.applyAccessibilityPreferences(preferences.accessibility);
  }, [preferences.accessibility]);

  const savePreferences = React.useCallback(async () => {
    try {
      await PreferencesStorage.save(preferences);
      setLastSaved(new Date().toISOString());
      addToast({
        type: 'success',
        title: 'Settings Saved',
        message: 'Your preferences have been saved successfully.'
      });
    } catch (error) {
      addToast({
        type: 'error',
        title: 'Save Failed',
        message: 'Failed to save your preferences. Please try again.'
      });
      throw error;
    }
  }, [preferences, addToast]);

  const contextValue: PreferencesContextType = {
    preferences,
    updateTheme: (theme: Theme) => dispatch({ type: 'SET_THEME', payload: theme }),
    updateLanguage: (language: Language) => dispatch({ type: 'SET_LANGUAGE', payload: language }),
    updateNotifications: (notifications: Partial<NotificationPreferences>) =>
      dispatch({ type: 'UPDATE_NOTIFICATIONS', payload: notifications }),
    updateAccessibility: (accessibility: Partial<AccessibilityPreferences>) =>
      dispatch({ type: 'UPDATE_ACCESSIBILITY', payload: accessibility }),
    updatePrivacy: (privacy: Partial<PrivacySettings>) =>
      dispatch({ type: 'UPDATE_PRIVACY', payload: privacy }),
    updateLearning: (learning: Partial<LearningPreferences>) =>
      dispatch({ type: 'UPDATE_LEARNING', payload: learning }),
    resetPreferences: () => dispatch({ type: 'RESET_PREFERENCES' }),
    savePreferences,
    isLoading,
    lastSaved
  };

  return (
    <PreferencesContext.Provider value={contextValue}>
      {children}
    </PreferencesContext.Provider>
  );
};

// usePreferences hook is imported from preferencesHook.ts

/**
 * Settings Panel Components
 */
export interface SettingsPanelProps {
  className?: string;
}

export const ThemeSettings: React.FC<SettingsPanelProps> = ({ className }) => {
  const { preferences, updateTheme } = usePreferences();

  return (
    <div className={className}>
      <h3>Theme Settings</h3>
      <div className="settings-group">
        <label>
          <input
            type="radio"
            name="theme"
            value="light"
            checked={preferences.theme === 'light'}
            onChange={() => updateTheme('light')}
          />
          Light Theme
        </label>
        <label>
          <input
            type="radio"
            name="theme"
            value="dark"
            checked={preferences.theme === 'dark'}
            onChange={() => updateTheme('dark')}
          />
          Dark Theme
        </label>
        <label>
          <input
            type="radio"
            name="theme"
            value="system"
            checked={preferences.theme === 'system'}
            onChange={() => updateTheme('system')}
          />
          System Default
        </label>
      </div>
    </div>
  );
};

export const NotificationSettings: React.FC<SettingsPanelProps> = ({ className }) => {
  const { preferences, updateNotifications } = usePreferences();

  return (
    <div className={className}>
      <h3>Notification Settings</h3>
      <div className="settings-group">
        <label>
          <input
            type="checkbox"
            checked={preferences.notifications.email.enabled}
            onChange={(e) => updateNotifications({
              email: { ...preferences.notifications.email, enabled: e.target.checked }
            })}
          />
          Email Notifications
        </label>
        <label>
          <input
            type="checkbox"
            checked={preferences.notifications.push.enabled}
            onChange={(e) => updateNotifications({
              push: { ...preferences.notifications.push, enabled: e.target.checked }
            })}
          />
          Push Notifications
        </label>
        <label>
          <input
            type="checkbox"
            checked={preferences.notifications.inApp.enabled}
            onChange={(e) => updateNotifications({
              inApp: { ...preferences.notifications.inApp, enabled: e.target.checked }
            })}
          />
          In-App Notifications
        </label>
      </div>
    </div>
  );
};

export const AccessibilitySettings: React.FC<SettingsPanelProps> = ({ className }) => {
  const { preferences, updateAccessibility } = usePreferences();

  return (
    <div className={className}>
      <h3>Accessibility Settings</h3>
      <div className="settings-group">
        <label>
          <input
            type="checkbox"
            checked={preferences.accessibility.highContrast}
            onChange={(e) => updateAccessibility({
              highContrast: e.target.checked
            })}
          />
          High Contrast Mode
        </label>
        <label>
          <input
            type="checkbox"
            checked={preferences.accessibility.reducedMotion === 'reduce'}
            onChange={(e) => updateAccessibility({
              reducedMotion: e.target.checked ? 'reduce' : 'auto'
            })}
          />
          Reduce Motion
        </label>
        <label>
          Font Size:
          <select
            value={preferences.accessibility.fontSize}
            onChange={(e) => updateAccessibility({
              fontSize: e.target.value as 'small' | 'medium' | 'large' | 'extra-large'
            })}
          >
            <option value="small">Small</option>
            <option value="medium">Medium</option>
            <option value="large">Large</option>
            <option value="extra-large">Extra Large</option>
          </select>
        </label>
      </div>
    </div>
  );
};

export const PrivacySettingsPanel: React.FC<SettingsPanelProps> = ({ className }) => {
  const { preferences, updatePrivacy } = usePreferences();

  return (
    <div className={className}>
      <h3>Privacy Settings</h3>
      <div className="settings-group">
        <label>
          Profile Visibility:
          <select
            value={preferences.privacy.profileVisibility}
            onChange={(e) => updatePrivacy({
              profileVisibility: e.target.value as 'public' | 'private' | 'friends'
            })}
          >
            <option value="public">Public</option>
            <option value="friends">Friends Only</option>
            <option value="private">Private</option>
          </select>
        </label>
        <label>
          <input
            type="checkbox"
            checked={preferences.privacy.dataCollection.analytics}
            onChange={(e) => updatePrivacy({
              dataCollection: {
                ...preferences.privacy.dataCollection,
                analytics: e.target.checked
              }
            })}
          />
          Analytics Data Collection
        </label>
        <label>
          <input
            type="checkbox"
            checked={preferences.privacy.dataCollection.marketing}
            onChange={(e) => updatePrivacy({
              dataCollection: {
                ...preferences.privacy.dataCollection,
                marketing: e.target.checked
              }
            })}
          />
          Marketing Data Collection
        </label>
      </div>
    </div>
  );
};

export const LearningSettings: React.FC<SettingsPanelProps> = ({ className }) => {
  const { preferences, updateLearning } = usePreferences();

  return (
    <div className={className}>
      <h3>Learning Preferences</h3>
      <div className="settings-group">
        <label>
          Difficulty Level:
          <select
            value={preferences.learning.difficulty}
            onChange={(e) => updateLearning({
              difficulty: e.target.value as 'beginner' | 'intermediate' | 'advanced' | 'adaptive'
            })}
          >
            <option value="beginner">Beginner</option>
            <option value="intermediate">Intermediate</option>
            <option value="advanced">Advanced</option>
            <option value="adaptive">Adaptive</option>
          </select>
        </label>
        <label>
          Learning Pace:
          <select
            value={preferences.learning.pace}
            onChange={(e) => updateLearning({
              pace: e.target.value as 'slow' | 'normal' | 'fast' | 'self-paced'
            })}
          >
            <option value="slow">Slow</option>
            <option value="normal">Normal</option>
            <option value="fast">Fast</option>
            <option value="self-paced">Self-Paced</option>
          </select>
        </label>
        <label>
          <input
            type="checkbox"
            checked={preferences.learning.reminders.enabled}
            onChange={(e) => updateLearning({
              reminders: {
                ...preferences.learning.reminders,
                enabled: e.target.checked
              }
            })}
          />
          Daily Learning Reminders
        </label>
      </div>
    </div>
  );
};

/**
 * Complete Settings Panel Component
 */
export const SettingsPanel: React.FC<SettingsPanelProps> = ({ className }) => {
  const { savePreferences, isLoading, lastSaved } = usePreferences();
  const [activeTab, setActiveTab] = React.useState('general');

  const handleSave = async () => {
    try {
      await savePreferences();
    } catch (error) {
      console.error('Failed to save preferences:', error);
    }
  };

  if (isLoading) {
    return <div className={className}>Loading preferences...</div>;
  }

  return (
    <div className={className}>
      <div className="settings-header">
        <h2>Settings</h2>
        {lastSaved && (
          <p className="last-saved">
            Last saved: {new Date(lastSaved).toLocaleString()}
          </p>
        )}
      </div>

      <div className="settings-tabs">
        <button
          className={activeTab === 'general' ? 'active' : ''}
          onClick={() => setActiveTab('general')}
        >
          General
        </button>
        <button
          className={activeTab === 'notifications' ? 'active' : ''}
          onClick={() => setActiveTab('notifications')}
        >
          Notifications
        </button>
        <button
          className={activeTab === 'accessibility' ? 'active' : ''}
          onClick={() => setActiveTab('accessibility')}
        >
          Accessibility
        </button>
        <button
          className={activeTab === 'privacy' ? 'active' : ''}
          onClick={() => setActiveTab('privacy')}
        >
          Privacy
        </button>
        <button
          className={activeTab === 'learning' ? 'active' : ''}
          onClick={() => setActiveTab('learning')}
        >
          Learning
        </button>
      </div>

      <div className="settings-content">
        {activeTab === 'general' && <ThemeSettings />}
        {activeTab === 'notifications' && <NotificationSettings />}
        {activeTab === 'accessibility' && <AccessibilitySettings />}
        {activeTab === 'privacy' && <PrivacySettingsPanel />}
        {activeTab === 'learning' && <LearningSettings />}
      </div>

      <div className="settings-actions">
        <button onClick={handleSave} className="save-button">
          Save Settings
        </button>
      </div>
    </div>
  );
};