"""
Simple CSS-only loading screen for Streamlit.
This version uses pure CSS and gets injected before any other content.
"""

import streamlit as st

def inject_css_loading():
    """
    Inject a pure CSS loading screen that covers the page.
    """
    st.markdown("""
    <style>
        /* Create a loading overlay that covers everything */
        body::before {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background: linear-gradient(135deg, #0a0014 0%, #1a0033 50%, #0a0014 100%);
            z-index: 999999;
            animation: hideOverlay 1s ease-out 5s forwards;
        }
        
        /* Loading content */
        body::after {
            content: '';
            position: fixed;
            top: 50%;
            left: 50%;
            width: 60px;
            height: 60px;
            margin: -30px 0 0 -30px;
            border: 3px solid rgba(157, 0, 255, 0.3);
            border-top: 3px solid #9d00ff;
            border-radius: 50%;
            animation: loadingSpin 1s linear infinite, hideSpinner 1s ease-out 5s forwards;
            z-index: 9999999;
        }
        
        @keyframes loadingSpin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        @keyframes hideOverlay {
            to {
                opacity: 0;
                visibility: hidden;
            }
        }
        
        @keyframes hideSpinner {
            to {
                opacity: 0;
                visibility: hidden;
            }
        }
        
        /* Hide Streamlit content initially */
        .stApp {
            opacity: 0;
            animation: showApp 1s ease-in-out 5s forwards;
        }
        
        @keyframes showApp {
            to {
                opacity: 1;
            }
        }
    </style>
    """, unsafe_allow_html=True)

def inject_advanced_css_loading():
    """
    Advanced CSS loading screen with text and better styling.
    """
    st.markdown("""
    <div id="css-loading-screen">
        <div class="css-loading-content">
            <div class="css-spinner"></div>
            <div class="css-title">AI Loom</div>
            <div class="css-message">Loading...</div>
        </div>
    </div>
    
    <style>
        #css-loading-screen {
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background: linear-gradient(135deg, #0a0014 0%, #1a0033 50%, #0a0014 100%);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 999999;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            color: white;
            animation: cssHideLoading 1s ease-out 5s forwards;
        }
        
        .css-loading-content {
            text-align: center;
        }
        
        .css-spinner {
            width: 60px;
            height: 60px;
            border: 3px solid rgba(157, 0, 255, 0.3);
            border-top: 3px solid #9d00ff;
            border-radius: 50%;
            animation: cssSpinAnimation 1s linear infinite;
            margin: 0 auto 20px auto;
            box-shadow: 0 0 20px rgba(157, 0, 255, 0.4);
        }
        
        .css-title {
            font-size: 2rem;
            font-weight: bold;
            color: #9d00ff;
            margin-bottom: 10px;
            text-shadow: 0 0 20px rgba(157, 0, 255, 0.5);
        }
        
        .css-message {
            font-size: 1.1rem;
            opacity: 0.8;
        }
        
        @keyframes cssSpinAnimation {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        @keyframes cssHideLoading {
            to {
                opacity: 0;
                visibility: hidden;
                pointer-events: none;
            }
        }
        
        /* Hide main app initially */
        .stApp {
            opacity: 0;
            animation: cssShowApp 1s ease-in-out 5s forwards;
        }
        
        @keyframes cssShowApp {
            to {
                opacity: 1;
            }
        }
    </style>
    
    <script>
        // Backup JavaScript to remove loading screen
        setTimeout(function() {
            var loadingScreen = document.getElementById('css-loading-screen');
            if (loadingScreen) {
                loadingScreen.style.display = 'none';
            }
            
            var app = document.querySelector('.stApp');
            if (app) {
                app.style.opacity = '1';
            }
        }, 5000);
    </script>
    """, unsafe_allow_html=True)
