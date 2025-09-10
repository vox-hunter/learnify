"""
Lightweight base UI module for Learnify.
Provides minimal CSS injection and session state management to replace
heavy CSS blocks that were causing performance issues.
"""
import streamlit as st


def ensure_base_ui():
    """
    Inject minimal base CSS and initialize session state once per session.
    Guards against redundant injections that slow down reruns.
    """
    # Guard against redundant CSS injection
    if not st.session_state.get('_base_css_injected', False):
        inject_minimal_css()
        st.session_state['_base_css_injected'] = True
    
    # Initialize session state with guards
    init_session_state()


def inject_minimal_css():
    """Inject minimal, essential CSS - target < 60 lines total."""
    st.markdown("""
    <style>
        /* Essential base styling - minimal and performance-focused */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
        
        /* Hide Streamlit default elements */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* Global styling */
        .stApp {
            background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 50%, #16213e 100%);
            font-family: 'Inter', sans-serif;
            color: #e2e8f0;
        }
        
        /* Modern sidebar */
        .stSidebar > div {
            background: linear-gradient(135deg, rgba(15, 23, 42, 0.9), rgba(30, 41, 59, 0.8));
            backdrop-filter: blur(10px);
            border-right: 1px solid rgba(6, 182, 212, 0.2);
        }
        
        /* Button styling - flat design */
        .stButton > button {
            background: linear-gradient(135deg, #06b6d4, #0891b2);
            color: white;
            border: none;
            border-radius: 8px;
            padding: 0.5rem 1rem;
            font-weight: 500;
            transition: all 0.2s ease;
        }
        
        .stButton > button:hover {
            background: linear-gradient(135deg, #0891b2, #0e7490);
            transform: translateY(-1px);
        }
        
        /* Hide specific navigation links */
        a[data-testid="stSidebarNavLink"][href$="/Course"],
        a[data-testid="stSidebarNavLink"][href$="/Privacy"], 
        a[data-testid="stSidebarNavLink"][href$="/Terms"] {
            display: none !important;
        }
        
        /* Text elements */
        .stMarkdown, .stText, p, div, span, label {
            color: #e2e8f0 !important;
        }
        
        /* Form elements */
        .stSelectbox > div > div > div {
            background-color: rgba(255, 255, 255, 0.1) !important;
            color: #e2e8f0 !important;
        }
        
        /* Truncate long titles */
        .course-title-truncated {
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            max-width: 200px;
        }
    </style>
    """, unsafe_allow_html=True)


def init_session_state():
    """Initialize session state variables with guards to prevent redundant operations."""
    
    # Authentication state
    if 'authenticated' not in st.session_state:
        st.session_state['authenticated'] = False
    
    if 'user_id' not in st.session_state:
        st.session_state['user_id'] = None
    
    if 'user_name' not in st.session_state:
        st.session_state['user_name'] = None
    
    # Application state
    if 'app_loading_complete' not in st.session_state:
        st.session_state['app_loading_complete'] = True
    
    # Course generation state
    if 'current_job_id' not in st.session_state:
        st.session_state['current_job_id'] = None
    
    if 'generated_course' not in st.session_state:
        st.session_state['generated_course'] = None
    
    # Navigation state
    if 'last_page_visit' not in st.session_state:
        st.session_state['last_page_visit'] = {}
    
    # Performance tracking
    if 'performance_logging' not in st.session_state:
        import os
        st.session_state['performance_logging'] = os.getenv('LEARNIFY_PERFORMANCE_LOG', 'false').lower() == 'true'


def truncate_course_name(course_name: str, max_words: int = 4) -> tuple[str, bool]:
    """
    Truncate course name to specified number of words, adding ellipsis if needed.
    Returns a tuple of (truncated_name, is_truncated)
    """
    if not course_name:
        return "Untitled Course", False
    
    words = course_name.split()
    if len(words) <= max_words:
        return course_name, False
    
    truncated_result = " ".join(words[:max_words]) + "..."
    return truncated_result, True


def log_performance(operation: str, duration: float = None):
    """Log performance metrics if logging is enabled."""
    if st.session_state.get('performance_logging', False):
        if duration is not None:
            st.write(f"⏱️ {operation}: {duration:.2f}s")
        else:
            st.write(f"🔄 {operation}")