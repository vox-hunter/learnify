"""
AI Quiz and Course Generator - Main Entry Point
This script redirects to the home page for the new multi-page structure.
"""

import streamlit as st

# Set page config
st.set_page_config(
    page_title="Learnify",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Redirect to home page
st.switch_page("pages/1_🏠_Home.py")
