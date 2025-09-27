"""
AI Quiz and Course Generator - Simplified Main Entry Point
"""

import streamlit as st
import os
import sys
from utils.lazy_imports import import_optional
from utils.navigation_cache import record_page_visit

# Page Config
st.set_page_config(
    page_title="AI Course Generator",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Minimal CSS only
st.markdown("""
<style>
    .stApp {
        background-color: #1e1e1e;
        color: #ffffff;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stSidebar > div {
        background-color: #2d2d2d;
    }
</style>
""", unsafe_allow_html=True)

# Initialize app state
if 'app_loading_complete' not in st.session_state:
    st.session_state['app_loading_complete'] = True

# Import pages
from pages import (
    home_page,
    login_page,
    course_page
)

# Get current page
pg = st.navigation([
    st.Page(home_page, title="🏠 Home", icon="🏠"),
    st.Page(login_page, title="🔐 Login", icon="🔐"),
    st.Page(course_page, title="📚 Course", icon="📚"),
])

# Record page visit
current_page_title = getattr(pg, 'title', None) or getattr(pg, 'name', None)
if current_page_title:
    record_page_visit(current_page_title)

# Hide login link when authenticated
if st.session_state.get('authentication_status'):
    st.markdown("""
        <style>
        [data-testid="stSidebarNav"] a[href*="/Login"] {display: none !important;}
        </style>
        """, unsafe_allow_html=True)

# Sidebar content
with st.sidebar:
    st.title("🧠 AI Course Generator")
    
    # Authentication status
    if st.session_state.get('authentication_status'):
        st.success(f"Welcome {st.session_state.get('name', 'User')}!")
        
        # Account button
        display_name = st.session_state.get('name', st.session_state.get('username'))
        if st.button(f"👤 {display_name}", use_container_width=True):
            st.switch_page(login_page)
    else:
        if st.button("Sign up / Login", icon="🔐", use_container_width=True):
            st.switch_page(login_page)

# Run the selected page
pg.run()

# Mark app as fully loaded
st.session_state['app_fully_loaded'] = True