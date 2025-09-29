/**
 * Accessibility Utilities and Components
 * Comprehensive ARIA support, keyboard navigation, and screen reader compatibility
 */

import React from 'react';

/**
 * ARIA Live Region for dynamic content announcements
 */
export const LiveRegion: React.FC<{
  children: React.ReactNode;
  politeness?: 'polite' | 'assertive' | 'off';
  atomic?: boolean;
  relevant?: 'additions' | 'removals' | 'text' | 'all' | 'additions text' | 'additions removals' | 'removals additions' | 'removals text' | 'text additions' | 'text removals';
  className?: string;
}> = ({ 
  children, 
  politeness = 'polite', 
  atomic = false, 
  relevant = 'additions text',
  className = '' 
}) => (
  <div
    aria-live={politeness}
    aria-atomic={atomic}
    aria-relevant={relevant}
    className={`sr-only ${className}`}
  >
    {children}
  </div>
);

/**
 * Skip Navigation Link
 */
export const SkipLink: React.FC<{
  href: string;
  children: React.ReactNode;
}> = ({ href, children }) => (
  <a
    href={href}
    className="skip-link"
    onFocus={(e) => e.currentTarget.classList.add('skip-link--visible')}
    onBlur={(e) => e.currentTarget.classList.remove('skip-link--visible')}
  >
    {children}
  </a>
);

/**
 * Accessible Modal Dialog
 */
export const AccessibleModal: React.FC<{
  isOpen: boolean;
  onClose: () => void;
  children: React.ReactNode;
  title: string;
  description?: string;
  closeOnEscape?: boolean;
  closeOnOverlay?: boolean;
}> = ({ 
  isOpen, 
  onClose, 
  children, 
  title, 
  description,
  closeOnEscape = true,
  closeOnOverlay = true 
}) => {
  const modalRef = React.useRef<HTMLDivElement>(null);
  const previousActiveElement = React.useRef<Element | null>(null);

  // Focus management
  React.useEffect(() => {
    if (isOpen) {
      previousActiveElement.current = document.activeElement;
      modalRef.current?.focus();
    } else {
      (previousActiveElement.current as HTMLElement)?.focus();
    }
  }, [isOpen]);

  // Keyboard navigation
  React.useEffect(() => {
    if (!isOpen) return;

    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape' && closeOnEscape) {
        onClose();
      }

      // Trap focus within modal
      if (event.key === 'Tab') {
        const focusableElements = modalRef.current?.querySelectorAll(
          'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );
        
        if (focusableElements && focusableElements.length > 0) {
          const firstElement = focusableElements[0] as HTMLElement;
          const lastElement = focusableElements[focusableElements.length - 1] as HTMLElement;

          if (event.shiftKey && document.activeElement === firstElement) {
            event.preventDefault();
            lastElement.focus();
          } else if (!event.shiftKey && document.activeElement === lastElement) {
            event.preventDefault();
            firstElement.focus();
          }
        }
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, closeOnEscape, onClose]);

  if (!isOpen) return null;

  return (
    <div
      className="modal-overlay"
      onClick={closeOnOverlay ? onClose : undefined}
      role="presentation"
    >
      <div
        ref={modalRef}
        className="modal-dialog"
        role="dialog"
        aria-modal="true"
        aria-labelledby="modal-title"
        aria-describedby={description ? "modal-description" : undefined}
        tabIndex={-1}
        onClick={(e) => e.stopPropagation()}
      >
        <div className="modal-header">
          <h2 id="modal-title" className="modal-title">
            {title}
          </h2>
          <button
            className="modal-close"
            onClick={onClose}
            aria-label="Close modal"
          >
            ✕
          </button>
        </div>
        
        {description && (
          <p id="modal-description" className="modal-description">
            {description}
          </p>
        )}
        
        <div className="modal-content">
          {children}
        </div>
      </div>
    </div>
  );
};

/**
 * Accessible Form Field with proper labeling and error handling
 */
export const AccessibleField: React.FC<{
  id: string;
  label: string;
  children: React.ReactNode;
  error?: string;
  required?: boolean;
  description?: string;
  className?: string;
}> = ({ id, label, children, error, required, description, className = '' }) => (
  <div className={`field ${error ? 'field--error' : ''} ${className}`}>
    <label htmlFor={id} className="field-label">
      {label}
      {required && <span className="field-required" aria-label="required">*</span>}
    </label>
    
    {description && (
      <div id={`${id}-description`} className="field-description">
        {description}
      </div>
    )}
    
    <div className="field-input">
      {React.cloneElement(children as React.ReactElement, {
        id,
        'aria-describedby': [
          description ? `${id}-description` : '',
          error ? `${id}-error` : ''
        ].filter(Boolean).join(' ') || undefined,
        'aria-invalid': error ? 'true' : undefined,
        'aria-required': required
      })}
    </div>
    
    {error && (
      <div id={`${id}-error`} className="field-error" role="alert">
        {error}
      </div>
    )}
  </div>
);

/**
 * Accessible Tabs Component
 */
export const AccessibleTabs: React.FC<{
  tabs: Array<{ id: string; label: string; content: React.ReactNode; disabled?: boolean }>;
  activeTab: string;
  onTabChange: (tabId: string) => void;
  className?: string;
}> = ({ tabs, activeTab, onTabChange, className = '' }) => {
  const tabRefs = React.useRef<Record<string, HTMLButtonElement | null>>({});

  const handleKeyDown = (event: React.KeyboardEvent, tabId: string) => {
    const currentIndex = tabs.findIndex(tab => tab.id === tabId);
    let nextIndex = currentIndex;

    switch (event.key) {
      case 'ArrowRight':
        nextIndex = (currentIndex + 1) % tabs.length;
        break;
      case 'ArrowLeft':
        nextIndex = (currentIndex - 1 + tabs.length) % tabs.length;
        break;
      case 'Home':
        nextIndex = 0;
        break;
      case 'End':
        nextIndex = tabs.length - 1;
        break;
      default:
        return;
    }

    event.preventDefault();
    const nextTab = tabs[nextIndex];
    if (!nextTab.disabled) {
      onTabChange(nextTab.id);
      tabRefs.current[nextTab.id]?.focus();
    }
  };

  return (
    <div className={`tabs ${className}`}>
      <div className="tabs-list" role="tablist">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            ref={(el) => { tabRefs.current[tab.id] = el; }}
            role="tab"
            aria-selected={activeTab === tab.id}
            aria-controls={`panel-${tab.id}`}
            id={`tab-${tab.id}`}
            tabIndex={activeTab === tab.id ? 0 : -1}
            disabled={tab.disabled}
            className={`tab ${activeTab === tab.id ? 'tab--active' : ''}`}
            onClick={() => !tab.disabled && onTabChange(tab.id)}
            onKeyDown={(e) => handleKeyDown(e, tab.id)}
          >
            {tab.label}
          </button>
        ))}
      </div>
      
      {tabs.map((tab) => (
        <div
          key={tab.id}
          id={`panel-${tab.id}`}
          role="tabpanel"
          aria-labelledby={`tab-${tab.id}`}
          hidden={activeTab !== tab.id}
          className="tab-panel"
        >
          {activeTab === tab.id && tab.content}
        </div>
      ))}
    </div>
  );
};

/**
 * Accessible Dropdown/Combobox
 */
export const AccessibleCombobox: React.FC<{
  id: string;
  label: string;
  options: Array<{ value: string; label: string; disabled?: boolean }>;
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  searchable?: boolean;
  className?: string;
}> = ({ id, label, options, value, onChange, placeholder, searchable = false, className = '' }) => {
  const [isOpen, setIsOpen] = React.useState(false);
  const [searchTerm, setSearchTerm] = React.useState('');
  const [focusedIndex, setFocusedIndex] = React.useState(-1);
  
  const comboboxRef = React.useRef<HTMLDivElement>(null);
  const inputRef = React.useRef<HTMLInputElement>(null);
  const listboxRef = React.useRef<HTMLUListElement>(null);

  const filteredOptions = searchable 
    ? options.filter(option => 
        option.label.toLowerCase().includes(searchTerm.toLowerCase())
      )
    : options;

  const selectedOption = options.find(option => option.value === value);

  const handleKeyDown = (event: React.KeyboardEvent) => {
    switch (event.key) {
      case 'ArrowDown':
        event.preventDefault();
        if (!isOpen) {
          setIsOpen(true);
        } else {
          setFocusedIndex(prev => 
            prev < filteredOptions.length - 1 ? prev + 1 : 0
          );
        }
        break;
      case 'ArrowUp':
        event.preventDefault();
        if (isOpen) {
          setFocusedIndex(prev => 
            prev > 0 ? prev - 1 : filteredOptions.length - 1
          );
        }
        break;
      case 'Enter':
        event.preventDefault();
        if (isOpen && focusedIndex >= 0) {
          onChange(filteredOptions[focusedIndex].value);
          setIsOpen(false);
          setFocusedIndex(-1);
        }
        break;
      case 'Escape':
        setIsOpen(false);
        setFocusedIndex(-1);
        inputRef.current?.focus();
        break;
    }
  };

  return (
    <div ref={comboboxRef} className={`combobox ${className}`}>
      <label htmlFor={id} className="combobox-label">
        {label}
      </label>
      
      <div className="combobox-container">
        <input
          ref={inputRef}
          id={id}
          type="text"
          role="combobox"
          aria-expanded={isOpen}
          aria-haspopup="listbox"
          aria-controls={`${id}-listbox`}
          aria-activedescendant={
            focusedIndex >= 0 ? `${id}-option-${focusedIndex}` : undefined
          }
          value={searchable ? searchTerm : selectedOption?.label || ''}
          onChange={(e) => searchable && setSearchTerm(e.target.value)}
          onFocus={() => setIsOpen(true)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          className="combobox-input"
        />
        
        <button
          type="button"
          aria-label="Toggle options"
          onClick={() => setIsOpen(!isOpen)}
          className="combobox-toggle"
        >
          ▼
        </button>
      </div>

      {isOpen && (
        <ul
          ref={listboxRef}
          id={`${id}-listbox`}
          role="listbox"
          className="combobox-listbox"
        >
          {filteredOptions.map((option, index) => (
            <li
              key={option.value}
              id={`${id}-option-${index}`}
              role="option"
              aria-selected={option.value === value}
              className={`combobox-option ${
                index === focusedIndex ? 'combobox-option--focused' : ''
              } ${option.value === value ? 'combobox-option--selected' : ''}`}
              onClick={() => {
                onChange(option.value);
                setIsOpen(false);
                setFocusedIndex(-1);
              }}
            >
              {option.label}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

// Utility functions moved to accessibilityUtils.ts for Fast Refresh compatibility

export default {
  LiveRegion,
  SkipLink,
  AccessibleModal,
  AccessibleField,
  AccessibleTabs,
  AccessibleCombobox
};