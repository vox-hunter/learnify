"""
Direct HTML injection loading screen for Streamlit.
This version injects the loading screen directly into the main page HTML.
"""

import streamlit as st

def inject_page_loading_screen():
    """
    Inject loading screen directly into the page using st.markdown.
    This avoids iframe sandbox issues.
    """
    
    # Inject the loading screen HTML and CSS directly into the page
    st.markdown("""
    <div id="page-loading-overlay" style="
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
    ">
        <div style="
            width: 60px;
            height: 60px;
            border: 3px solid rgba(157, 0, 255, 0.3);
            border-top: 3px solid #9d00ff;
            border-radius: 50%;
            animation: pageSpinAnimation 1s linear infinite;
            margin-bottom: 20px;
            box-shadow: 0 0 20px rgba(157, 0, 255, 0.4);
        "></div>
        
        <div style="
            font-size: 2rem;
            font-weight: bold;
            color: #9d00ff;
            margin-bottom: 10px;
            text-shadow: 0 0 20px rgba(157, 0, 255, 0.5);
            animation: pageGlowAnimation 2s ease-in-out infinite;
        ">AI Loom</div>
        
        <div style="
            font-size: 1.1rem;
            opacity: 0.8;
            text-align: center;
            margin-bottom: 20px;
        ">Loading your intelligent learning platform...</div>
        
        <div style="
            width: 250px;
            height: 4px;
            background: rgba(157, 0, 255, 0.2);
            border-radius: 2px;
            overflow: hidden;
        ">
            <div style="
                height: 100%;
                background: linear-gradient(90deg, #9d00ff, #ff6b6b, #9d00ff);
                border-radius: 2px;
                animation: pageProgressAnimation 3s ease-in-out infinite;
            "></div>
        </div>
        
        <div style="
            font-size: 0.9rem;
            opacity: 0.6;
            margin-top: 15px;
            text-align: center;
        ">Setting up components and authentication...</div>
    </div>
    
    <style>
        @keyframes pageSpinAnimation {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        @keyframes pageProgressAnimation {
            0% { width: 0%; transform: translateX(-100%); }
            50% { width: 100%; transform: translateX(0%); }
            100% { width: 100%; transform: translateX(100%); }
        }
        
        @keyframes pageGlowAnimation {
            0% { text-shadow: 0 0 20px rgba(157, 0, 255, 0.5); }
            50% { text-shadow: 0 0 30px rgba(157, 0, 255, 0.8); }
            100% { text-shadow: 0 0 20px rgba(157, 0, 255, 0.5); }
        }
        
        /* Hide the main Streamlit content initially */
        .stApp > div:not(#page-loading-overlay) {
            opacity: 0;
            transition: opacity 1s ease-in-out;
        }
        
        /* Show content after loading */
        .content-loaded .stApp > div:not(#page-loading-overlay) {
            opacity: 1;
        }
        
        /* Hide loading overlay */
        #page-loading-overlay.hidden {
            opacity: 0;
            visibility: hidden;
            pointer-events: none;
            transition: opacity 0.8s ease-out, visibility 0.8s ease-out;
        }
    </style>
    
    <script>
        console.log('Page loading screen initialized');
        
        // Function to hide loading screen
        function hidePageLoading() {
            var overlay = document.getElementById('page-loading-overlay');
            if (overlay && !overlay.classList.contains('hidden')) {
                console.log('Hiding page loading screen');
                overlay.classList.add('hidden');
                document.body.classList.add('content-loaded');
                
                // Remove overlay after animation
                setTimeout(function() {
                    if (overlay && overlay.parentNode) {
                        overlay.parentNode.removeChild(overlay);
                    }
                }, 800);
            }
        }
        
        // Hide after 6 seconds
        setTimeout(hidePageLoading, 6000);
        
        // Also check for content load
        var checkCount = 0;
        var checkInterval = setInterval(function() {
            checkCount++;
            
            // Look for Streamlit content
            var streamlitContent = document.querySelector('.stApp');
            var hasContent = streamlitContent && streamlitContent.children.length > 2;
            
            if (hasContent || checkCount > 30) { // 6 seconds max
                clearInterval(checkInterval);
                hidePageLoading();
            }
        }, 200);
        
        // Fallback on window load
        window.addEventListener('load', function() {
            setTimeout(hidePageLoading, 1000);
        });
    </script>
    """, unsafe_allow_html=True)

def add_streamlit_loading_css():
    """
    Add additional CSS to ensure proper loading behavior
    """
    st.markdown("""
    <style>
        /* Ensure loading overlay is always on top */
        #page-loading-overlay {
            position: fixed !important;
            top: 0 !important;
            left: 0 !important;
            width: 100vw !important;
            height: 100vh !important;
            z-index: 999999 !important;
        }
        
        /* Initially hide all Streamlit content */
        .stApp {
            opacity: 0;
            animation: fadeInStreamlit 1s ease-in-out 6s forwards;
        }
        
        @keyframes fadeInStreamlit {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        
        /* Override when content is loaded */
        .content-loaded .stApp {
            opacity: 1 !important;
            animation: none !important;
        }
    </style>
    """, unsafe_allow_html=True)
