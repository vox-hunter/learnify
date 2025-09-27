"""
Consolidated CSS loader for frontend optimization.
Loads all common styles from a single file to reduce bloat.
"""
import streamlit as st
import os
from pathlib import Path

def load_consolidated_css():
    """Load the consolidated CSS file and inject it into Streamlit."""
    css_path = Path(__file__).parent.parent / "assets" / "styles.css"
    
    if css_path.exists():
        with open(css_path, 'r', encoding='utf-8') as f:
            css_content = f.read()
        
        st.markdown(f"""
        <style>
        {css_content}
        </style>
        """, unsafe_allow_html=True)
        return True
    else:
        st.warning("CSS file not found - using fallback styles")
        return False

def apply_page_specific_css(page_css: str):
    """Apply additional page-specific CSS styles."""
    if page_css:
        st.markdown(f"""
        <style>
        {page_css}
        </style>
        """, unsafe_allow_html=True)