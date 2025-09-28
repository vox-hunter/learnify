"""
Centralized CSS styles for the Learnify application.
This module eliminates CSS duplication across pages and provides consistent theming.
"""

def get_base_styles():
    """Return base CSS styles used across all pages"""
    return """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Global styling */
    .stApp {
        background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 50%, #16213e 100%);
        font-family: 'Inter', sans-serif;
        color: #e2e8f0;
    }
    
    /* Hide default Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Hide cookie manager components */
    iframe[title*="cookie_manager"], 
    iframe[src*="cookie_manager"],
    iframe[title*="streamlit_cookies_manager"],
    iframe[src*="streamlit_cookies_manager"] {
        display: none !important;
        width: 0 !important;
        height: 0 !important;
        visibility: hidden !important;
        position: absolute !important;
        left: -9999px !important;
    }
    
    .stCustomComponentV1:has(iframe[src*="cookie_manager"]) {
        display: none !important;
    }
    
    /* Text and elements */
    .stMarkdown, .stText, p, div, span, label, h1, h2, h3, h4, h5, h6 {
        color: #e2e8f0 !important;
    }
    
    /* Form elements */
    .stSelectbox > div > div > div,
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background-color: rgba(255, 255, 255, 0.1) !important;
        color: #e2e8f0 !important;
    }
    
    /* Main content container */
    .main-container {
        background: rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 20px;
        padding: 2rem;
        margin: 1rem auto;
        max-width: 1000px;
    }
    
    /* Button styling */
    .main .stButton > button,
    .stMain .stButton > button {
        background: linear-gradient(135deg, #06b6d4, #0891b2);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 12px 24px;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .main .stButton > button:hover,
    .stMain .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(6, 182, 212, 0.4);
    }
    
    /* Alert styling */
    .stSuccess {
        background: linear-gradient(135deg, rgba(34, 197, 94, 0.2), rgba(22, 163, 74, 0.2));
        border: 1px solid rgba(34, 197, 94, 0.4);
        border-radius: 12px;
    }
    
    .stError {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.2), rgba(220, 38, 38, 0.2));
        border: 1px solid rgba(239, 68, 68, 0.4);
        border-radius: 12px;
    }
    
    .stWarning {
        background: linear-gradient(135deg, rgba(245, 158, 11, 0.2), rgba(217, 119, 6, 0.2));
        border: 1px solid rgba(245, 158, 11, 0.4);
        border-radius: 12px;
    }
    
    .stInfo {
        background: linear-gradient(135deg, rgba(6, 182, 212, 0.2), rgba(14, 165, 233, 0.2));
        border: 1px solid rgba(6, 182, 212, 0.4);
        border-radius: 12px;
    }
    </style>
    """

def get_sidebar_styles():
    """Return sidebar-specific CSS styles"""
    return """
    <style>
    .stSidebar {
        background: rgba(10, 14, 39, 0.9);
        backdrop-filter: blur(20px);
    }
    
    .stSidebar *[role="button"],
    .stSidebar button {
        background: linear-gradient(135deg, rgba(6, 182, 212, 0.1), rgba(14, 165, 233, 0.1)) !important;
        border: 1px solid rgba(6, 182, 212, 0.3) !important;
        color: #e2e8f0 !important;
        border-radius: 12px !important;
        padding: 8px 16px !important;
        font-weight: 500 !important;
        transition: all 0.3s ease !important;
    }
    
    .stSidebar *[role="button"]:hover,
    .stSidebar button:hover {
        background: linear-gradient(135deg, rgba(6, 182, 212, 0.2), rgba(14, 165, 233, 0.2)) !important;
        border-color: rgba(6, 182, 212, 0.4) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(6, 182, 212, 0.2) !important;
    }
    </style>
    """

def hide_navigation_links():
    """Return CSS to hide specific navigation links"""
    return """
    <style>
    /* Hide specific navigation links */
    a[data-testid="stSidebarNavLink"][href$="/Course"] {
        display: none;
    }
    
    a[data-testid="stSidebarNavLink"][href$="/Privacy"] {
        display: none !important;
    }
    
    a[data-testid="stSidebarNavLink"][href$="/Terms"] {
        display: none !important;
    }
    
    [data-testid="stSidebarNav"] a[href*="/Login"] {
        display: none !important;
    }
    </style>
    """

def apply_common_styles():
    """Apply all common styles to the current page"""
    import streamlit as st
    st.markdown(get_base_styles(), unsafe_allow_html=True)
    st.markdown(get_sidebar_styles(), unsafe_allow_html=True)