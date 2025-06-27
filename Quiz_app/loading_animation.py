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
        /* Global Loading Animation - Render optimized */
        .app-loading-overlay {
            position: fixed !important;
            top: 0 !important;
            left: 0 !important;
            width: 100vw !important;
            height: 100vh !important;
            background: linear-gradient(135deg, #0a0014 0%, #1a0033 50%, #0a0014 100%) !important;
            display: flex !important;
            flex-direction: column !important;
            justify-content: center !important;
            align-items: center !important;
            z-index: 999999 !important;
            transition: opacity 0.8s ease-in-out, visibility 0.8s ease-in-out !important;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
        }

        .app-loading-overlay.hide {
            opacity: 0 !important;
            visibility: hidden !important;
            pointer-events: none !important;
        }

        /* Ensure content is hidden during loading */
        body.app-loading .stApp > div:not(#app-loading-overlay):not(.app-loading-overlay) {
            opacity: 0 !important;
            pointer-events: none !important;
        }

        /* Smooth transition when loading is complete */
        body.app-loaded .stApp > div {
            opacity: 1 !important;
            transition: opacity 0.5s ease-in-out !important;
        }

        /* Loading spinner */
        .loading-spinner {
            width: 80px !important;
            height: 80px !important;
            border: 4px solid rgba(157, 0, 255, 0.1) !important;
            border-top: 4px solid #9d00ff !important;
            border-radius: 50% !important;
            animation: loadingSpinAnimation 1s linear infinite !important;
            margin-bottom: 24px !important;
            box-shadow: 0 0 30px rgba(157, 0, 255, 0.3) !important;
        }

        @keyframes loadingSpinAnimation {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        /* Loading text */
        .loading-text {
            color: #9d00ff !important;
            font-size: 1.8rem !important;
            font-weight: 700 !important;
            margin-bottom: 16px !important;
            text-align: center !important;
            text-shadow: 0 0 20px rgba(157, 0, 255, 0.5) !important;
            animation: loadingPulseAnimation 2s ease-in-out infinite !important;
            font-family: inherit !important;
        }

        .loading-subtext {
            color: #ffffff !important;
            font-size: 1.1rem !important;
            font-weight: 400 !important;
            text-align: center !important;
            opacity: 0.8 !important;
            margin-bottom: 32px !important;
            font-family: inherit !important;
        }

        /* Progress bar */
        .loading-progress {
            width: 300px !important;
            height: 6px !important;
            background: rgba(157, 0, 255, 0.2) !important;
            border-radius: 3px !important;
            overflow: hidden !important;
            margin-bottom: 16px !important;
        }

        .loading-progress-bar {
            height: 100% !important;
            background: linear-gradient(90deg, #9d00ff, #ff6b6b, #9d00ff) !important;
            border-radius: 3px !important;
            animation: loadingProgressAnimation 3s ease-in-out infinite !important;
        }

        @keyframes loadingProgressAnimation {
            0% { width: 0%; transform: translateX(-100%); }
            50% { width: 100%; transform: translateX(0%); }
            100% { width: 100%; transform: translateX(100%); }
        }

        /* Floating particles */
        .loading-particles {
            position: absolute !important;
            width: 100% !important;
            height: 100% !important;
            overflow: hidden !important;
            pointer-events: none !important;
        }

        .particle {
            position: absolute !important;
            background: #9d00ff !important;
            border-radius: 50% !important;
            opacity: 0.6 !important;
            animation: loadingFloatAnimation 6s ease-in-out infinite !important;
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

        @keyframes loadingFloatAnimation {
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

        @keyframes loadingPulseAnimation {
            0% { text-shadow: 0 0 20px rgba(157, 0, 255, 0.5); }
            50% { text-shadow: 0 0 30px rgba(157, 0, 255, 0.8); }
            100% { text-shadow: 0 0 20px rgba(157, 0, 255, 0.5); }
        }

        /* Prevent scrolling during loading */
        body.app-loading {
            overflow: hidden !important;
        }
    </style>
    
    <script>
        // Robust loading screen management for Render deployment
        let loadingHidden = false;
        
        function hideLoadingScreen() {
            if (loadingHidden) return;
            loadingHidden = true;
            
            const overlay = document.getElementById('app-loading-overlay');
            if (overlay) {
                overlay.classList.add('hide');
                // Remove from DOM after animation
                setTimeout(() => {
                    if (overlay && overlay.parentNode) {
                        overlay.parentNode.removeChild(overlay);
                    }
                    if (document.body) {
                        document.body.classList.remove('app-loading');
                        document.body.classList.add('app-loaded');
                    }
                }, 800);
            }
        }

        // Safer check for loaded state
        function checkIfLoaded() {
            try {
                // Check if basic Streamlit elements exist
                const streamlitApp = document.querySelector('.stApp');
                if (!streamlitApp) return false;
                
                // Check for Streamlit test elements (more reliable)
                const streamlitElements = document.querySelectorAll('[data-testid]');
                const hasStreamlitContent = streamlitElements.length > 5; // Need substantial content
                
                // Check for main content areas
                const mainContent = document.querySelector('[data-testid="stAppViewContainer"]') || 
                                  document.querySelector('.main') ||
                                  document.querySelector('#main-content');
                
                // Check if content is actually visible
                const hasVisibleContent = streamlitApp.offsetHeight > 100;
                
                return hasStreamlitContent && mainContent && hasVisibleContent;
            } catch (error) {
                console.log('Loading check error:', error);
                return false;
            }
        }

        // More robust monitoring with multiple fallbacks
        let checkCount = 0;
        const maxChecks = 75; // Maximum 15 seconds
        const checkInterval = 200;
        
        function monitorLoading() {
            checkCount++;
            
            // Primary check - is everything loaded?
            if (checkIfLoaded()) {
                setTimeout(hideLoadingScreen, 1000); // Wait 1 second after detection
                return;
            }
            
            // Fallback checks
            if (checkCount >= maxChecks) {
                console.log('Loading timeout reached, hiding screen');
                hideLoadingScreen();
                return;
            }
            
            // Continue monitoring
            setTimeout(monitorLoading, checkInterval);
        }

        // Multiple initialization strategies for different environments
        function initializeLoading() {
            // Add loading class to body if it exists
            if (document.body) {
                document.body.classList.add('app-loading');
            }
            
            // Start monitoring immediately
            setTimeout(monitorLoading, 500);
            
            // Additional fallback timers
            setTimeout(() => {
                if (!loadingHidden) {
                    console.log('5 second fallback triggered');
                    hideLoadingScreen();
                }
            }, 5000);
            
            setTimeout(() => {
                if (!loadingHidden) {
                    console.log('10 second hard fallback triggered');
                    hideLoadingScreen();
                }
            }, 10000);
        }

        // Initialize based on document state
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', initializeLoading);
        } else if (document.readyState === 'interactive') {
            setTimeout(initializeLoading, 100);
        } else {
            initializeLoading();
        }

        // Window load fallback for slow connections
        window.addEventListener('load', () => {
            setTimeout(() => {
                if (!loadingHidden) {
                    console.log('Window load fallback triggered');
                    hideLoadingScreen();
                }
            }, 1000);
        });

        // Streamlit-specific event listeners (if available)
        if (window.streamlit) {
            window.streamlit.addEventListener('ready', () => {
                setTimeout(hideLoadingScreen, 500);
            });
        }
    </script>
    """
    
    # Inject the loading screen
    components.html(loading_html, height=0, scrolling=False)

def inject_simple_loading_screen():
    """
    Simpler loading screen that's more reliable on Render.
    Uses a timer-based approach instead of DOM detection.
    """
    simple_loading_html = """
    <div id="simple-loading-overlay" style="
        position: fixed !important;
        top: 0 !important;
        left: 0 !important;
        width: 100vw !important;
        height: 100vh !important;
        background: linear-gradient(135deg, #0a0014 0%, #1a0033 50%, #0a0014 100%) !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: center !important;
        align-items: center !important;
        z-index: 999999 !important;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
    ">
        <div style="
            width: 80px;
            height: 80px;
            border: 4px solid rgba(157, 0, 255, 0.1);
            border-top: 4px solid #9d00ff;
            border-radius: 50%;
            animation: simpleSpinAnimation 1s linear infinite;
            margin-bottom: 24px;
            box-shadow: 0 0 30px rgba(157, 0, 255, 0.3);
        "></div>
        
        <div style="
            color: #9d00ff;
            font-size: 1.8rem;
            font-weight: 700;
            margin-bottom: 16px;
            text-align: center;
            text-shadow: 0 0 20px rgba(157, 0, 255, 0.5);
        ">AI Loom</div>
        
        <div style="
            color: #ffffff;
            font-size: 1.1rem;
            font-weight: 400;
            text-align: center;
            opacity: 0.8;
            margin-bottom: 32px;
        ">Loading your intelligent learning experience...</div>
        
        <div style="
            width: 300px;
            height: 6px;
            background: rgba(157, 0, 255, 0.2);
            border-radius: 3px;
            overflow: hidden;
            margin-bottom: 16px;
        ">
            <div style="
                height: 100%;
                background: linear-gradient(90deg, #9d00ff, #ff6b6b, #9d00ff);
                border-radius: 3px;
                animation: simpleProgressAnimation 3s ease-in-out infinite;
            "></div>
        </div>
        
        <div style="
            color: #ffffff;
            font-size: 0.9rem;
            text-align: center;
            opacity: 0.6;
        ">Setting up components and authentication...</div>
    </div>
    
    <style>
        @keyframes simpleSpinAnimation {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        @keyframes simpleProgressAnimation {
            0% { width: 0%; transform: translateX(-100%); }
            50% { width: 100%; transform: translateX(0%); }
            100% { width: 100%; transform: translateX(100%); }
        }
    </style>
    
    <script>
        console.log('Simple loading screen initialized');
        
        // Hide loading screen after a fixed time (more reliable for Render)
        setTimeout(function() {
            console.log('Hiding simple loading screen');
            var overlay = document.getElementById('simple-loading-overlay');
            if (overlay) {
                overlay.style.opacity = '0';
                overlay.style.transition = 'opacity 0.8s ease-in-out';
                setTimeout(function() {
                    if (overlay && overlay.parentNode) {
                        overlay.parentNode.removeChild(overlay);
                    }
                }, 800);
            }
        }, 8000); // Show for 8 seconds
        
        // Additional check for when Streamlit content appears
        var checkCount = 0;
        var checkInterval = setInterval(function() {
            checkCount++;
            try {
                var streamlitContent = document.querySelector('.stApp');
                var hasContent = streamlitContent && streamlitContent.children.length > 0;
                
                if (hasContent || checkCount > 40) { // 8 seconds max
                    console.log('Streamlit content detected or timeout reached');
                    clearInterval(checkInterval);
                    var overlay = document.getElementById('simple-loading-overlay');
                    if (overlay) {
                        overlay.style.opacity = '0';
                        overlay.style.transition = 'opacity 0.8s ease-in-out';
                        setTimeout(function() {
                            if (overlay && overlay.parentNode) {
                                overlay.parentNode.removeChild(overlay);
                            }
                        }, 800);
                    }
                }
            } catch (error) {
                console.log('Check error:', error);
            }
        }, 200);
    </script>
    """
    
    # Inject the simple loading screen
    components.html(simple_loading_html, height=0, scrolling=False)

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
