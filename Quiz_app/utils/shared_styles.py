"""
Shared CSS styles for consistent theming across the application.
This module consolidates all CSS styling to reduce duplication and improve maintainability.
"""

# Common color variables
COLORS = {
    'primary_gradient': 'linear-gradient(135deg, #06b6d4, #0ea5e9)',
    'background_gradient': 'linear-gradient(135deg, #0f0f23 0%, #1a1a2e 50%, #16213e 100%)',
    'sidebar_gradient': 'linear-gradient(135deg, rgba(15, 23, 42, 0.9), rgba(30, 41, 59, 0.8))',
    'card_bg': 'rgba(255, 255, 255, 0.08)',
    'border_color': 'rgba(6, 182, 212, 0.2)',
    'text_primary': '#e2e8f0',
    'accent_blue': '#06b6d4',
    'accent_purple': '#9d00ff',
}

# Base CSS that should be applied to all pages
BASE_CSS = """
<style>
    /* Import modern fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global styling */
    .stApp {
        background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 50%, #16213e 100%);
        font-family: 'Inter', sans-serif;
        color: #e2e8f0;
    }
    
    /* Hide Streamlit default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Ensure all text is light colored */
    .stMarkdown, .stText, p, div, span, label, h1, h2, h3, h4, h5, h6 {
        color: #e2e8f0 !important;
    }
    
    /* Dark theme for Streamlit form elements */
    .stSelectbox > div > div > div,
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background-color: rgba(255, 255, 255, 0.1) !important;
        color: #e2e8f0 !important;
    }
    
    /* Hide cookie manager components that take up space */
    iframe[title*="cookie_manager"], 
    iframe[src*="cookie_manager"],
    .stCustomComponentV1:has(iframe[src*="cookie_manager"]),
    .stCustomComponentV1[data-testid="stCustomComponentV1"]:has(iframe[height="0"]) {
        display: none !important;
        width: 0 !important;
        height: 0 !important;
        visibility: hidden !important;
    }
    
    /* Modern button styling */
    .stButton > button {
        background: linear-gradient(135deg, rgba(6, 182, 212, 0.1), rgba(14, 165, 233, 0.1));
        color: #e2e8f0 !important;
        border: 1px solid rgba(6, 182, 212, 0.3);
        border-radius: 12px;
        padding: 8px 16px;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, rgba(6, 182, 212, 0.2), rgba(14, 165, 233, 0.2));
        border-color: rgba(6, 182, 212, 0.5);
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(6, 182, 212, 0.3);
    }
    
    /* Modern card styling */
    .modern-card {
        background: rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 20px;
        padding: 2rem;
        margin: 1rem 0;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
    }
    
    /* File uploader styling */
    .stFileUploader {
        background: rgba(255, 255, 255, 0.03);
        border: 2px dashed #9d00ff;
        border-radius: 20px;
        padding: 2rem;
        text-align: center;
        transition: all 0.3s ease;
        margin: 1rem 0;
    }
    
    .stFileUploader:hover {
        border-color: #ff6b6b;
        background: rgba(255, 255, 255, 0.06);
        transform: translateY(-2px);
    }
    
    /* Progress bar styling */
    .stProgress > div > div {
        background: linear-gradient(135deg, #06b6d4, #0ea5e9) !important;
    }
    
    /* Alert styling */
    .stSuccess {
        background: linear-gradient(135deg, rgba(34, 197, 94, 0.2), rgba(22, 163, 74, 0.2));
        border: 1px solid rgba(34, 197, 94, 0.4);
        border-radius: 12px;
        backdrop-filter: blur(20px);
    }
    
    .stError {
        background: linear-gradient(135deg, rgba(245, 101, 101, 0.2), rgba(229, 62, 62, 0.2));
        border: 1px solid rgba(245, 101, 101, 0.4);
        border-radius: 12px;
        backdrop-filter: blur(20px);
    }
    
    .stInfo {
        background: linear-gradient(135deg, rgba(6, 182, 212, 0.2), rgba(14, 165, 233, 0.2));
        border: 1px solid rgba(6, 182, 212, 0.4);
        border-radius: 12px;
        backdrop-filter: blur(20px);
    }
</style>
"""

# Sidebar-specific CSS
SIDEBAR_CSS = """
<style>
    /* Modern sidebar styling */
    .stSidebar > div {
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.9), rgba(30, 41, 59, 0.8));
        backdrop-filter: blur(20px);
        border-right: 1px solid rgba(6, 182, 212, 0.2);
    }
    
    /* Sidebar button styling */
    .stSidebar button,
    .stSidebar .stButton > button,
    [data-testid="stSidebar"] button {
        background: linear-gradient(135deg, rgba(6, 182, 212, 0.1), rgba(14, 165, 233, 0.1)) !important;
        color: #e2e8f0 !important;
        border: 1px solid rgba(6, 182, 212, 0.3) !important;
        border-radius: 12px !important;
        padding: 8px 16px !important;
        font-weight: 500 !important;
        transition: all 0.3s ease !important;
    }
    
    .stSidebar button:hover,
    .stSidebar .stButton > button:hover,
    [data-testid="stSidebar"] button:hover {
        background: linear-gradient(135deg, rgba(6, 182, 212, 0.2), rgba(14, 165, 233, 0.2)) !important;
        border-color: rgba(6, 182, 212, 0.5) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(6, 182, 212, 0.3) !important;
    }
    
    /* Hide navigation links when authenticated */
    .hide-nav-when-auth [data-testid="stSidebarNav"] a[href*="/Login"] {
        display: none !important;
    }
</style>
"""

# Tab styling
TAB_CSS = """
<style>
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 25px;
        padding: 5px;
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        color: #94a3b8;
        border-radius: 20px;
        padding: 10px 20px;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(6, 182, 212, 0.1);
        color: #06b6d4;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #06b6d4, #0ea5e9) !important;
        color: white !important;
    }
</style>
"""

# Course-specific styling
COURSE_CSS = """
<style>
    /* Progress bar container */
    .progress-container {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        z-index: 999;
        background: rgba(13, 18, 32, 0.95);
        backdrop-filter: blur(20px);
        border-bottom: 1px solid rgba(6, 182, 212, 0.2);
        padding: 15px 20px;
    }
    
    /* Question card styling */
    .question-card {
        background: linear-gradient(135deg, rgba(6, 182, 212, 0.1), rgba(8, 145, 178, 0.1));
        border: 1px solid rgba(6, 182, 212, 0.3);
        border-radius: 20px;
        padding: 2rem;
        margin: 2rem 0;
        backdrop-filter: blur(20px);
    }
    
    /* Section navigation */
    .section-nav {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 15px;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
"""

def get_base_css():
    """Get the base CSS that should be applied to all pages."""
    return BASE_CSS

def get_sidebar_css():
    """Get sidebar-specific CSS."""
    return SIDEBAR_CSS

def get_tab_css():
    """Get tab-specific CSS."""
    return TAB_CSS

def get_course_css():
    """Get course page-specific CSS."""
    return COURSE_CSS

def get_combined_css(*css_types):
    """Combine multiple CSS types into a single string."""
    css_map = {
        'base': BASE_CSS,
        'sidebar': SIDEBAR_CSS,
        'tabs': TAB_CSS,
        'course': COURSE_CSS,
    }
    
    combined = ""
    for css_type in css_types:
        if css_type in css_map:
            combined += css_map[css_type]
    
    return combined