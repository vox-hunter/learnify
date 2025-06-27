"""
Global Loading Animation for Streamlit App
This module provides a comprehensive loading screen that covers the entire app
until all components, pages, and resources are fully loaded.
"""

import streamlit as st
import streamlit.components.v1 as components
import time
import asyncio

def inject_loading_screen():
    """
    Inject the loading screen HTML and CSS into the Streamlit app.
    This should be called at the very beginning of your main app.
    """
    loading_html = """
    <div id="app-loading-overlay" class="app-loading-overlay">
        <div class="loading-particles">
            <div class="particle"></div>
            <div class="particle"></div>
            <div class="particle"></div>
            <div class="particle"></div>
            <div class="particle"></div>
            <div class="particle"></div>
            <div class="particle"></div>
            <div class="particle"></div>
            <div class="particle"></div>
        </div>
        
        <div class="loading-spinner"></div>
        
        <div class="loading-text">AI Loom</div>
        <div class="loading-subtext">Initializing your intelligent learning experience...</div>
        
        <div class="loading-progress">
            <div class="loading-progress-bar"></div>
        </div>
        
        <div class="loading-subtext" style="font-size: 0.9rem; margin-top: 16px;">
            Loading components, authentication, and courses...
        </div>
    </div>
    
    <style>
        /* Global Loading Animation */
        .app-loading-overlay {
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
            z-index: 9999;
            transition: opacity 0.8s ease-in-out, visibility 0.8s ease-in-out;
        }

        .app-loading-overlay.hide {
            opacity: 0;
            visibility: hidden;
            pointer-events: none;
        }

        /* Loading spinner */
        .loading-spinner {
            width: 80px;
            height: 80px;
            border: 4px solid rgba(157, 0, 255, 0.1);
            border-top: 4px solid #9d00ff;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin-bottom: 24px;
            box-shadow: 0 0 30px rgba(157, 0, 255, 0.3);
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        /* Loading text */
        .loading-text {
            color: #9d00ff;
            font-size: 1.8rem;
            font-weight: 700;
            margin-bottom: 16px;
            text-align: center;
            text-shadow: 0 0 20px rgba(157, 0, 255, 0.5);
            animation: pulse 2s ease-in-out infinite;
        }

        .loading-subtext {
            color: #ffffff;
            font-size: 1.1rem;
            font-weight: 400;
            text-align: center;
            opacity: 0.8;
            margin-bottom: 32px;
        }

        /* Progress bar */
        .loading-progress {
            width: 300px;
            height: 6px;
            background: rgba(157, 0, 255, 0.2);
            border-radius: 3px;
            overflow: hidden;
            margin-bottom: 16px;
        }

        .loading-progress-bar {
            height: 100%;
            background: linear-gradient(90deg, #9d00ff, #ff6b6b, #9d00ff);
            border-radius: 3px;
            animation: loadingProgress 3s ease-in-out infinite;
        }

        @keyframes loadingProgress {
            0% { width: 0%; transform: translateX(-100%); }
            50% { width: 100%; transform: translateX(0%); }
            100% { width: 100%; transform: translateX(100%); }
        }

        /* Floating particles */
        .loading-particles {
            position: absolute;
            width: 100%;
            height: 100%;
            overflow: hidden;
            pointer-events: none;
        }

        .particle {
            position: absolute;
            background: #9d00ff;
            border-radius: 50%;
            opacity: 0.6;
            animation: float 6s ease-in-out infinite;
        }

        .particle:nth-child(1) { width: 8px; height: 8px; left: 10%; animation-delay: 0s; }
        .particle:nth-child(2) { width: 12px; height: 12px; left: 20%; animation-delay: 1s; }
        .particle:nth-child(3) { width: 6px; height: 6px; left: 30%; animation-delay: 2s; }
        .particle:nth-child(4) { width: 10px; height: 10px; left: 40%; animation-delay: 0.5s; }
        .particle:nth-child(5) { width: 8px; height: 8px; left: 50%; animation-delay: 1.5s; }
        .particle:nth-child(6) { width: 14px; height: 14px; left: 60%; animation-delay: 3s; }
        .particle:nth-child(7) { width: 6px; height: 6px; left: 70%; animation-delay: 2.5s; }
        .particle:nth-child(8) { width: 10px; height: 10px; left: 80%; animation-delay: 4s; }
        .particle:nth-child(9) { width: 8px; height: 8px; left: 90%; animation-delay: 1.2s; }

        @keyframes float {
            0%, 100% { 
                transform: translateY(100vh) scale(0); 
                opacity: 0; 
            }
            10% { 
                opacity: 0.6; 
                transform: translateY(90vh) scale(1); 
            }
            90% { 
                opacity: 0.6; 
                transform: translateY(-10vh) scale(1); 
            }
        }

        /* Hide main app content while loading */
        .app-loading .stApp > div:not(.app-loading-overlay) {
            opacity: 0;
            pointer-events: none;
        }

        /* Smooth transition when loading is complete */
        .app-loaded .stApp > div {
            opacity: 1;
            transition: opacity 0.5s ease-in-out;
        }

        @keyframes pulse {
            0% { text-shadow: 0 0 20px rgba(157, 0, 255, 0.5); }
            50% { text-shadow: 0 0 30px rgba(157, 0, 255, 0.8); }
            100% { text-shadow: 0 0 20px rgba(157, 0, 255, 0.5); }
        }
    </style>
    
    <script>
        // Hide loading screen after everything is loaded
        function hideLoadingScreen() {
            const overlay = document.getElementById('app-loading-overlay');
            if (overlay) {
                // Add a minimum display time for better UX
                setTimeout(() => {
                    overlay.classList.add('hide');
                    // Remove from DOM after animation
                    setTimeout(() => {
                        if (overlay.parentNode) {
                            overlay.parentNode.removeChild(overlay);
                        }
                        document.body.classList.remove('app-loading');
                        document.body.classList.add('app-loaded');
                    }, 800);
                }, 2000); // Show for at least 2 seconds
            }
        }

        // Check if everything is loaded
        function checkIfLoaded() {
            // Check if Streamlit is fully loaded
            const streamlitElements = document.querySelectorAll('[data-testid]');
            const hasStreamlitContent = streamlitElements.length > 0;
            
            // Check if sidebar and main content are present
            const sidebar = document.querySelector('[data-testid="stSidebar"]');
            const mainContent = document.querySelector('[data-testid="stAppViewContainer"]');
            
            // Check if custom CSS has been applied
            const hasCustomStyling = document.querySelector('.stApp').style.backgroundColor !== '';
            
            return hasStreamlitContent && sidebar && mainContent;
        }

        // Monitor loading progress
        let checkCount = 0;
        const maxChecks = 50; // Maximum 10 seconds of checking
        
        function monitorLoading() {
            checkCount++;
            
            if (checkIfLoaded() || checkCount >= maxChecks) {
                hideLoadingScreen();
            } else {
                setTimeout(monitorLoading, 200); // Check every 200ms
            }
        }

        // Start monitoring when DOM is ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => {
                setTimeout(monitorLoading, 500); // Give a small delay for Streamlit to start
            });
        } else {
            setTimeout(monitorLoading, 500);
        }

        // Also hide on window load as fallback
        window.addEventListener('load', () => {
            setTimeout(hideLoadingScreen, 1500);
        });

        // Add loading class to body
        document.body.classList.add('app-loading');
    </script>
    """
    
    # Inject the loading screen
    components.html(loading_html, height=0, scrolling=False)

def hide_loading_screen():
    """
    Force hide the loading screen (optional manual trigger)
    """
    hide_script = """
    <script>
        const overlay = document.getElementById('app-loading-overlay');
        if (overlay) {
            overlay.classList.add('hide');
            setTimeout(() => {
                if (overlay.parentNode) {
                    overlay.parentNode.removeChild(overlay);
                }
                document.body.classList.remove('app-loading');
                document.body.classList.add('app-loaded');
            }, 800);
        }
    </script>
    """
    components.html(hide_script, height=0)

def show_loading_status(message="Loading...", progress=None):
    """
    Update loading screen with specific status message
    Args:
        message: Status message to display
        progress: Progress percentage (0-100) - optional
    """
    if 'loading_screen_shown' not in st.session_state:
        return
        
    update_script = f"""
    <script>
        const subtextElements = document.querySelectorAll('.loading-subtext');
        if (subtextElements.length > 1) {{
            subtextElements[1].textContent = '{message}';
        }}
        
        {f'''
        const progressBar = document.querySelector('.loading-progress-bar');
        if (progressBar && {progress} !== null) {{
            progressBar.style.width = '{progress}%';
            progressBar.style.animation = 'none';
        }}
        ''' if progress is not None else ''}
    </script>
    """
    components.html(update_script, height=0)
