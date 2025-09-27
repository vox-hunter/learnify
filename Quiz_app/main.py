"""
AI Quiz and Course Generator - Simplified Main Entry Point
"""

import streamlit as st
import os
import sys
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

# Simple page navigation without st.navigation (which might not be available)
st.sidebar.title("🧠 AI Course Generator")

# Authentication status in sidebar
if st.session_state.get('authentication_status'):
    st.sidebar.success(f"Welcome {st.session_state.get('name', 'User')}!")
    
    # Account button
    display_name = st.session_state.get('name', st.session_state.get('username'))
    if st.sidebar.button(f"👤 {display_name}", use_container_width=True):
        st.switch_page("pages/2_🔐_Login.py")
else:
    if st.sidebar.button("Sign up / Login", use_container_width=True):
        st.switch_page("pages/2_🔐_Login.py")

# Main content area
st.title("🧠 AI Course Generator")
st.write("Welcome to the simplified AI Course Generator!")

# Navigation buttons
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🏠 Home", use_container_width=True):
        st.switch_page("pages/1_🏠_Home.py")

with col2:
    if st.button("🔐 Login", use_container_width=True):
        st.switch_page("pages/2_🔐_Login.py")

with col3:
    if st.button("📚 Course", use_container_width=True):
        st.switch_page("pages/3_Course.py")

# Instructions
st.markdown("""
### Getting Started
1. **Login** or create an account to get started
2. **Upload a PDF** or provide a URL to generate a course
3. **Take the quiz** and track your progress

### Features
- ✅ PDF processing and course generation
- ✅ Interactive quizzes with multiple question types
- ✅ Progress tracking
- ✅ Secure authentication
""")

# Mark app as fully loaded
st.session_state['app_fully_loaded'] = True