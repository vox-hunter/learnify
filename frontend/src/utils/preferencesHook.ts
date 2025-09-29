/**
 * Preferences Hook
 * Separated for Fast Refresh compatibility
 */

import React, { useContext } from 'react';
import type { PreferencesContextType } from './preferencesUtils';

/**
 * Preferences Context (created in components file)
 */
export const PreferencesContext = React.createContext<PreferencesContextType | undefined>(undefined);

/**
 * Hook to use preferences context
 */
export const usePreferences = () => {
  const context = useContext(PreferencesContext);
  if (context === undefined) {
    throw new Error('usePreferences must be used within a PreferencesProvider');
  }
  return context;
};