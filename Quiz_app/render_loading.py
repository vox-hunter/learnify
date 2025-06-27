"""
Ultra-simple loading screen for Render deployment.
This version uses minimal JavaScript and relies on CSS animations and timers.
"""

import streamlit as st
import streamlit.components.v1 as components

def inject_render_loading_screen():
    """
    Ultra-simple loading screen optimized for Render.
    Uses only CSS animations and a simple timer.
    """
    render_loading_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            #render-loading {
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
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                color: white;
                transition: opacity 1s ease-out;
            }
            
            .spinner {
                width: 60px;
                height: 60px;
                border: 3px solid rgba(157, 0, 255, 0.3);
                border-top: 3px solid #9d00ff;
                border-radius: 50%;
                animation: spin 1s linear infinite;
                margin-bottom: 20px;
            }
            
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            
            .logo {
                font-size: 2rem;
                font-weight: bold;
                color: #9d00ff;
                margin-bottom: 10px;
                text-shadow: 0 0 20px rgba(157, 0, 255, 0.5);
            }
            
            .message {
                font-size: 1.1rem;
                opacity: 0.8;
                text-align: center;
                margin-bottom: 20px;
            }
            
            .progress {
                width: 250px;
                height: 4px;
                background: rgba(157, 0, 255, 0.2);
                border-radius: 2px;
                overflow: hidden;
            }
            
            .progress-bar {
                height: 100%;
                background: #9d00ff;
                border-radius: 2px;
                animation: progress 4s ease-in-out infinite;
            }
            
            @keyframes progress {
                0% { width: 0%; }
                50% { width: 70%; }
                100% { width: 100%; }
            }
            
            .hidden {
                opacity: 0;
                pointer-events: none;
            }
        </style>
    </head>
    <body>
        <div id="render-loading">
            <div class="spinner"></div>
            <div class="logo">AI Loom</div>
            <div class="message">Loading your intelligent learning platform...</div>
            <div class="progress">
                <div class="progress-bar"></div>
            </div>
        </div>
        
        <script>
            console.log('Render loading screen started');
            
            // Simple timer-based hiding (most reliable for Render)
            setTimeout(function() {
                console.log('Hiding loading screen after timer');
                var loading = document.getElementById('render-loading');
                if (loading) {
                    loading.classList.add('hidden');
                    setTimeout(function() {
                        if (loading.parentNode) {
                            loading.parentNode.removeChild(loading);
                        }
                    }, 1000);
                }
            }, 6000); // Show for 6 seconds
            
            // Backup: Hide when page is fully loaded
            window.addEventListener('load', function() {
                setTimeout(function() {
                    console.log('Hiding loading screen on window load');
                    var loading = document.getElementById('render-loading');
                    if (loading && !loading.classList.contains('hidden')) {
                        loading.classList.add('hidden');
                        setTimeout(function() {
                            if (loading.parentNode) {
                                loading.parentNode.removeChild(loading);
                            }
                        }, 1000);
                    }
                }, 2000);
            });
        </script>
    </body>
    </html>
    """
    
    # Inject the loading screen
    components.html(render_loading_html, height=0, scrolling=False)

def add_loading_css():
    """
    Add loading CSS directly to Streamlit
    """
    st.markdown("""
    <style>
        /* Ensure loading screen appears above everything */
        #render-loading {
            position: fixed !important;
            top: 0 !important;
            left: 0 !important;
            width: 100vw !important;
            height: 100vh !important;
            z-index: 999999 !important;
        }
        
        /* Hide Streamlit content during initial load */
        .stApp {
            opacity: 0;
            animation: fadeInApp 1s ease-in-out 6s forwards;
        }
        
        @keyframes fadeInApp {
            from { opacity: 0; }
            to { opacity: 1; }
        }
    </style>
    """, unsafe_allow_html=True)
