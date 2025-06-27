"""
Native Streamlit loading screen using st.empty() container.
This approach uses Streamlit's native rendering system.
"""

import streamlit as st
import time

def show_streamlit_loading():
    """
    Show loading screen using Streamlit's native components.
    This approach avoids iframe issues entirely.
    """
    
    # Create a container that fills the entire page
    loading_container = st.empty()
    
    # Add CSS to make the loading screen full-page
    st.markdown("""
    <style>
        /* Hide the main app content initially */
        .main .block-container {
            display: none;
        }
        
        /* Style the loading container */
        .loading-fullscreen {
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
        
        .loading-spinner-native {
            width: 60px;
            height: 60px;
            border: 3px solid rgba(157, 0, 255, 0.3);
            border-top: 3px solid #9d00ff;
            border-radius: 50%;
            animation: nativeSpinAnimation 1s linear infinite;
            margin-bottom: 20px;
            box-shadow: 0 0 20px rgba(157, 0, 255, 0.4);
        }
        
        @keyframes nativeSpinAnimation {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .loading-title-native {
            font-size: 2rem;
            font-weight: bold;
            color: #9d00ff;
            margin-bottom: 10px;
            text-shadow: 0 0 20px rgba(157, 0, 255, 0.5);
            animation: nativeGlowAnimation 2s ease-in-out infinite;
        }
        
        @keyframes nativeGlowAnimation {
            0% { text-shadow: 0 0 20px rgba(157, 0, 255, 0.5); }
            50% { text-shadow: 0 0 30px rgba(157, 0, 255, 0.8); }
            100% { text-shadow: 0 0 20px rgba(157, 0, 255, 0.5); }
        }
        
        .loading-message-native {
            font-size: 1.1rem;
            opacity: 0.8;
            text-align: center;
            margin-bottom: 20px;
        }
        
        .loading-progress-native {
            width: 250px;
            height: 4px;
            background: rgba(157, 0, 255, 0.2);
            border-radius: 2px;
            overflow: hidden;
            margin-bottom: 15px;
        }
        
        .loading-progress-bar-native {
            height: 100%;
            background: linear-gradient(90deg, #9d00ff, #ff6b6b, #9d00ff);
            border-radius: 2px;
            animation: nativeProgressAnimation 3s ease-in-out infinite;
        }
        
        @keyframes nativeProgressAnimation {
            0% { width: 0%; transform: translateX(-100%); }
            50% { width: 100%; transform: translateX(0%); }
            100% { width: 100%; transform: translateX(100%); }
        }
        
        .loading-subtext-native {
            font-size: 0.9rem;
            opacity: 0.6;
            text-align: center;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Fill the container with loading screen content
    with loading_container.container():
        st.markdown("""
        <div class="loading-fullscreen">
            <div class="loading-spinner-native"></div>
            <div class="loading-title-native">AI Loom</div>
            <div class="loading-message-native">Loading your intelligent learning platform...</div>
            <div class="loading-progress-native">
                <div class="loading-progress-bar-native"></div>
            </div>
            <div class="loading-subtext-native">Setting up components and authentication...</div>
        </div>
        """, unsafe_allow_html=True)
    
    return loading_container

def hide_streamlit_loading(loading_container):
    """
    Hide the loading screen and show the main app
    """
    if loading_container:
        loading_container.empty()
    
    # Show the main content
    st.markdown("""
    <style>
        .main .block-container {
            display: block !important;
            animation: fadeInContent 1s ease-in-out;
        }
        
        @keyframes fadeInContent {
            from { opacity: 0; }
            to { opacity: 1; }
        }
    </style>
    """, unsafe_allow_html=True)
