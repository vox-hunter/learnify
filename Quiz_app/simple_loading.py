"""
Simple inline loading for Streamlit that works reliably.
This shows a loading message while the app initializes.
"""

import streamlit as st
import time

class StreamlitLoader:
    def __init__(self):
        self.loading_placeholder = None
        self.content_placeholder = None
        
    def show_loading(self):
        """Show loading screen using Streamlit placeholders"""
        
        # Add CSS to style the loading
        st.markdown("""
        <style>
            .loading-container {
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                min-height: 80vh;
                background: linear-gradient(135deg, #0a0014 0%, #1a0033 50%, #0a0014 100%);
                border-radius: 10px;
                padding: 40px;
                text-align: center;
                color: white;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            }
            
            .loading-spinner-simple {
                width: 60px;
                height: 60px;
                border: 3px solid rgba(157, 0, 255, 0.3);
                border-top: 3px solid #9d00ff;
                border-radius: 50%;
                animation: simpleSpinAnimation 1s linear infinite;
                margin-bottom: 20px;
                box-shadow: 0 0 20px rgba(157, 0, 255, 0.4);
            }
            
            @keyframes simpleSpinAnimation {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            
            .loading-title-simple {
                font-size: 2.5rem;
                font-weight: bold;
                color: #9d00ff;
                margin-bottom: 10px;
                text-shadow: 0 0 20px rgba(157, 0, 255, 0.5);
            }
            
            .loading-message-simple {
                font-size: 1.2rem;
                opacity: 0.9;
                margin-bottom: 20px;
            }
            
            .loading-submessage-simple {
                font-size: 1rem;
                opacity: 0.7;
            }
        </style>
        """, unsafe_allow_html=True)
        
        # Create placeholder for loading content
        self.loading_placeholder = st.empty()
        
        # Show loading screen
        with self.loading_placeholder.container():
            st.markdown("""
            <div class="loading-container">
                <div class="loading-spinner-simple"></div>
                <div class="loading-title-simple">🧠 AI Loom</div>
                <div class="loading-message-simple">Loading your intelligent learning platform...</div>
                <div class="loading-submessage-simple">Setting up components, authentication, and courses...</div>
            </div>
            """, unsafe_allow_html=True)
        
        return self
    
    def hide_loading(self):
        """Hide loading screen and show main content"""
        if self.loading_placeholder:
            self.loading_placeholder.empty()
    
    def update_message(self, message):
        """Update loading message"""
        if self.loading_placeholder:
            with self.loading_placeholder.container():
                st.markdown(f"""
                <div class="loading-container">
                    <div class="loading-spinner-simple"></div>
                    <div class="loading-title-simple">🧠 AI Loom</div>
                    <div class="loading-message-simple">Loading your intelligent learning platform...</div>
                    <div class="loading-submessage-simple">{message}</div>
                </div>
                """, unsafe_allow_html=True)

def show_simple_loading():
    """
    Show a simple loading screen that works reliably in Streamlit
    """
    loader = StreamlitLoader()
    loader.show_loading()
    return loader
