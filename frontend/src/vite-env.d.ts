/// <reference types="vite/client" />

// Extend Vite's ImportMetaEnv with custom environment variables
declare module 'vite/client' {
  interface ImportMetaEnv {
    readonly VITE_API_BASE_URL: string;
    readonly VITE_ANALYTICS_ID: string;
    readonly VITE_APP_TITLE: string;
    readonly VITE_MAX_FILE_SIZE: string;
    readonly VITE_SUPPORTED_FILE_TYPES: string;
    readonly VITE_ENABLE_ANALYTICS: string;
    readonly VITE_ENABLE_PWA: string;
    readonly VITE_DEBUG_MODE: string;
  }
}

// Global type augmentations
declare global {
  interface Window {
    // Google Analytics
    gtag?: (
      command: 'config' | 'event' | 'exception' | 'page_view' | 'purchase' | 'refund' | 'select_content' | 'share' | 'sign_up' | 'timing_complete',
      targetId: string,
      config?: Record<string, unknown>
    ) => void;
    
    // Error reporting
    __APP_ERROR_HANDLER__?: (error: Error, context?: Record<string, unknown>) => void;
    
    // Development tools
    __REACT_DEVTOOLS_GLOBAL_HOOK__?: unknown;
    __REDUX_DEVTOOLS_EXTENSION__?: unknown;
  }
  
  // File API extensions
  interface File {
    webkitRelativePath?: string;
  }
  
  // Drag and Drop API extensions
  interface DataTransfer {
    effectAllowed: 'none' | 'copy' | 'copyLink' | 'copyMove' | 'link' | 'linkMove' | 'move' | 'all' | 'uninitialized';
    dropEffect: 'none' | 'copy' | 'link' | 'move';
  }
}

// Module declarations for assets
declare module '*.svg' {
  import * as React from 'react';
  export const ReactComponent: React.FunctionComponent<React.SVGProps<SVGSVGElement> & { title?: string }>;
  const src: string;
  export default src;
}

declare module '*.png' {
  const src: string;
  export default src;
}

declare module '*.jpg' {
  const src: string;
  export default src;
}

declare module '*.jpeg' {
  const src: string;
  export default src;
}

declare module '*.gif' {
  const src: string;
  export default src;
}

declare module '*.webp' {
  const src: string;
  export default src;
}

declare module '*.ico' {
  const src: string;
  export default src;
}

declare module '*.bmp' {
  const src: string;
  export default src;
}

// CSS Modules
declare module '*.module.css' {
  const classes: { readonly [key: string]: string };
  export default classes;
}

declare module '*.module.scss' {
  const classes: { readonly [key: string]: string };
  export default classes;
}

declare module '*.module.sass' {
  const classes: { readonly [key: string]: string };
  export default classes;
}

// JSON modules
declare module '*.json' {
  const value: unknown;
  export default value;
}

// Text files
declare module '*.txt' {
  const content: string;
  export default content;
}

// Worker modules
declare module '*?worker' {
  const WorkerFactory: new () => Worker;
  export default WorkerFactory;
}

declare module '*?worker&inline' {
  const WorkerFactory: new () => Worker;
  export default WorkerFactory;
}

// URL modules
declare module '*?url' {
  const url: string;
  export default url;
}

// Raw modules
declare module '*?raw' {
  const content: string;
  export default content;
}

// Inline modules
declare module '*?inline' {
  const content: string;
  export default content;
}

export {};