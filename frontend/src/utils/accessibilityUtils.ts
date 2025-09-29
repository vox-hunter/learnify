/**
 * Accessibility Utility Functions
 * Separated from components for Fast Refresh compatibility
 */

/**
 * Accessibility utilities
 */
export const a11yUtils = {
  /**
   * Generate unique ID for form elements
   */
  generateId: (prefix: string = 'element'): string => {
    return `${prefix}-${Math.random().toString(36).substr(2, 9)}`;
  },

  /**
   * Announce content to screen readers
   */
  announce: (message: string, priority: 'polite' | 'assertive' = 'polite'): void => {
    const announcement = document.createElement('div');
    announcement.setAttribute('aria-live', priority);
    announcement.setAttribute('aria-atomic', 'true');
    announcement.className = 'sr-only';
    announcement.textContent = message;
    
    document.body.appendChild(announcement);
    
    setTimeout(() => {
      document.body.removeChild(announcement);
    }, 1000);
  },

  /**
   * Check if element is focusable
   */
  isFocusable: (element: Element): boolean => {
    const focusableSelectors = [
      'button:not([disabled])',
      'input:not([disabled])',
      'select:not([disabled])',
      'textarea:not([disabled])',
      'a[href]',
      '[tabindex]:not([tabindex="-1"])'
    ];
    
    return focusableSelectors.some(selector => element.matches(selector));
  },

  /**
   * Get all focusable elements within a container
   */
  getFocusableElements: (container: Element): Element[] => {
    const focusableSelectors = [
      'button:not([disabled])',
      'input:not([disabled])',
      'select:not([disabled])',
      'textarea:not([disabled])',
      'a[href]',
      '[tabindex]:not([tabindex="-1"])'
    ].join(', ');
    
    return Array.from(container.querySelectorAll(focusableSelectors));
  },

  /**
   * Trap focus within an element
   */
  trapFocus: (container: Element, event: KeyboardEvent): boolean => {
    if (event.key !== 'Tab') return false;
    
    const focusableElements = a11yUtils.getFocusableElements(container);
    if (focusableElements.length === 0) return false;
    
    const firstElement = focusableElements[0] as HTMLElement;
    const lastElement = focusableElements[focusableElements.length - 1] as HTMLElement;
    
    if (event.shiftKey && document.activeElement === firstElement) {
      event.preventDefault();
      lastElement.focus();
      return true;
    }
    
    if (!event.shiftKey && document.activeElement === lastElement) {
      event.preventDefault();
      firstElement.focus();
      return true;
    }
    
    return false;
  },

  /**
   * Keyboard navigation constants
   */
  keys: {
    ENTER: 'Enter',
    SPACE: ' ',
    ESCAPE: 'Escape',
    TAB: 'Tab',
    ARROW_UP: 'ArrowUp',
    ARROW_DOWN: 'ArrowDown',
    ARROW_LEFT: 'ArrowLeft',
    ARROW_RIGHT: 'ArrowRight',
    HOME: 'Home',
    END: 'End'
  } as const,

  /**
   * Common ARIA roles
   */
  roles: {
    BUTTON: 'button',
    TAB: 'tab',
    TABPANEL: 'tabpanel',
    TABLIST: 'tablist',
    DIALOG: 'dialog',
    ALERT: 'alert',
    LISTBOX: 'listbox',
    OPTION: 'option',
    COMBOBOX: 'combobox',
    MENU: 'menu',
    MENUITEM: 'menuitem',
    NAVIGATION: 'navigation',
    MAIN: 'main',
    BANNER: 'banner',
    CONTENTINFO: 'contentinfo'
  } as const,

  /**
   * Screen reader only class helper
   */
  srOnly: 'sr-only',

  /**
   * Focus management utilities
   */
  focus: {
    /**
     * Save current focus and return a function to restore it
     */
    save: (): (() => void) => {
      const activeElement = document.activeElement as HTMLElement;
      return () => {
        if (activeElement && activeElement.focus) {
          activeElement.focus();
        }
      };
    },

    /**
     * Move focus to first focusable element in container
     */
    first: (container: Element): boolean => {
      const focusableElements = a11yUtils.getFocusableElements(container);
      if (focusableElements.length > 0) {
        (focusableElements[0] as HTMLElement).focus();
        return true;
      }
      return false;
    },

    /**
     * Move focus to last focusable element in container
     */
    last: (container: Element): boolean => {
      const focusableElements = a11yUtils.getFocusableElements(container);
      if (focusableElements.length > 0) {
        (focusableElements[focusableElements.length - 1] as HTMLElement).focus();
        return true;
      }
      return false;
    }
  }
};

/**
 * Accessibility validation helpers
 */
export const a11yValidation = {
  /**
   * Check if element has accessible name
   */
  hasAccessibleName: (element: Element): boolean => {
    return !!(
      element.getAttribute('aria-label') ||
      element.getAttribute('aria-labelledby') ||
      element.textContent?.trim() ||
      (element as HTMLInputElement).labels?.length
    );
  },

  /**
   * Check if interactive element is keyboard accessible
   */
  isKeyboardAccessible: (element: Element): boolean => {
    const tabIndex = element.getAttribute('tabindex');
    return tabIndex !== '-1' && (
      a11yUtils.isFocusable(element) ||
      element.hasAttribute('tabindex')
    );
  },

  /**
   * Check if element has proper ARIA attributes
   */
  hasProperAria: (element: Element, requiredAttributes: string[] = []): boolean => {
    return requiredAttributes.every(attr => element.hasAttribute(attr));
  }
};

export default {
  a11yUtils,
  a11yValidation
};