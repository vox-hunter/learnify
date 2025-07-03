"""
Ultra-simple loading using Streamlit native components.
This approach shows loading while the app actually loads in parallel.
"""

import streamlit as st
import streamlit.components.v1 as components

def start_background_loading():
    """
    Start loading animation that runs while app loads in background.
    """
    
    # Only show loading if not already completed
    if st.session_state.get('app_loading_complete', False):
        return
    
    # Custom CSS for loading state and sidebar control
    st.markdown("""
    <style>
        /* Collapse sidebar during loading */
        [data-testid="stSidebar"] {
            transform: translateX(-100%) !important;
            transition: transform 0.3s ease !important;
        }
        
        /* Expand main content during loading */
        [data-testid="stAppViewContainer"] .main {
            margin-left: 0 !important;
            transition: margin-left 0.3s ease !important;
        }
        
        .loading-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background: linear-gradient(135deg, #0a0014 0%, #1a0033 50%, #0a0014 100%);
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            z-index: 999999;
            color: white;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }
        
        .loading-spinner {
            width: 60px;
            height: 60px;
            border: 3px solid rgba(157, 0, 255, 0.3);
            border-top: 3px solid #9d00ff;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin-bottom: 20px;
            box-shadow: 0 0 20px rgba(157, 0, 255, 0.4);
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .loading-title {
            font-size: 2.5rem;
            font-weight: bold;
            color: #9d00ff;
            text-shadow: 0 0 20px rgba(157, 0, 255, 0.5);
            margin-bottom: 10px;
        }
        
        .loading-message {
            font-size: 1.2rem;
            opacity: 0.9;
            margin-bottom: 20px;
            text-align: center;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Create loading overlay
    loading_container = st.empty()
    
    with loading_container.container():
        st.markdown("""
        <div class="loading-overlay">
            <div class="loading-spinner"></div>
            <div class="loading-title">🧠 AI Loom</div>
            <div class="loading-message">Loading your intelligent learning platform...</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Store loading container in session state for later cleanup
    st.session_state['loading_container'] = loading_container

def show_streamlit_native_loading():
    """
    Legacy function - now just calls start_background_loading for compatibility
    """
    start_background_loading()
    return True

def complete_loading():
    """
    Complete the loading process and show the main app.
    This should be called after all app initialization is done.
    """
    
    # Mark loading as complete first to prevent re-entry
    st.session_state['app_loading_complete'] = True
    
    # Clear loading overlay
    if 'loading_container' in st.session_state:
        try:
            st.session_state['loading_container'].empty()
            del st.session_state['loading_container']
        except (KeyError, AttributeError, RuntimeError):
            pass  # Ignore errors if container is already gone
    
    # Expand sidebar and restore normal layout
    st.markdown("""
    <style>
        /* Restore sidebar with force */
        [data-testid="stSidebar"] {
            transform: translateX(0) !important;
            width: auto !important;
            min-width: 21rem !important;
            max-width: none !important;
            transition: all 0.5s ease !important;
            opacity: 1 !important;
            visibility: visible !important;
        }
        
        /* Restore main content margin */
        [data-testid="stAppViewContainer"] .main {
            margin-left: auto !important;
            transition: margin-left 0.5s ease !important;
        }
        
        /* Remove loading overlay completely */
        .loading-overlay {
            display: none !important;
            opacity: 0 !important;
            visibility: hidden !important;
            pointer-events: none !important;
            transition: all 0.5s ease !important;
        }
        
        /* Force sidebar to be visible and expanded */
        [data-testid="stSidebar"] > div {
            width: 21rem !important;
        }
        
        /* Override any collapsed state */
        [data-testid="collapsedControl"] {
            display: none !important;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Use JavaScript to force sidebar expansion more aggressively
    components.html("""
    <script>
        function expandSidebar() {
            // Remove any loading overlays
            var loadingOverlays = document.querySelectorAll('.loading-overlay');
            loadingOverlays.forEach(function(overlay) {
                overlay.style.display = 'none';
                overlay.remove();
            });
            
            // Multiple attempts to expand sidebar
            setTimeout(function() {
                // Method 1: Look for expand button
                var expandBtn = document.querySelector('[data-testid="collapsedControl"]');
                if (expandBtn) {
                    expandBtn.click();
                }
                
                // Method 2: Force sidebar attributes
                var sidebar = document.querySelector('[data-testid="stSidebar"]');
                if (sidebar) {
                    sidebar.style.transform = 'translateX(0)';
                    sidebar.style.width = 'auto';
                    sidebar.style.minWidth = '21rem';
                    sidebar.style.opacity = '1';
                    sidebar.style.visibility = 'visible';
                }
                
                // Method 3: Trigger resize event
                window.dispatchEvent(new Event('resize'));
                
            }, 100);
            
            // Repeat after delay to ensure it sticks
            setTimeout(expandSidebar, 500);
        }
        
        expandSidebar();
    </script>
    """, height=0)
    
    st.session_state['sidebar_should_be_expanded'] = True

def ensure_loading_cleanup():
    """
    Ensure loading UI is removed from all pages after loading is complete.
    Call this at the beginning of each page.
    """
    if st.session_state.get('app_loading_complete', False):
        # Remove any loading artifacts and ensure sidebar is properly shown
        st.markdown("""
        <style>
            /* Ensure sidebar is visible on all pages after loading */
            [data-testid="stSidebar"] {
                transform: translateX(0) !important;
                opacity: 1 !important;
                visibility: visible !important;
            }
            
            /* Ensure main content has proper spacing */
            [data-testid="stAppViewContainer"] .main {
                margin-left: auto !important;
            }
            
            /* Hide any remaining loading elements */
            .loading-overlay {
                display: none !important;
            }
        </style>
        """, unsafe_allow_html=True)
