"""
Cookie Manager Fallback Initialization
This module provides a fallback cookie manager initialization for pages that might be accessed directly
"""

import streamlit as st
import os

def ensure_cookie_manager():
    """Ensure cookie manager is available in session state, with fallback initialization"""
    
    if 'cookies' not in st.session_state or st.session_state.cookies is None:
        # Try to initialize cookie manager as fallback
        try:
            from streamlit_cookies_manager import EncryptedCookieManager
            
            # Use environment variable or secrets, with a generated default for development
            cookie_key = (
                os.environ.get("COOKIE_ENCRYPTION_KEY") or 
                st.secrets.get("COOKIE_ENCRYPTION_KEY") or 
                "learnify-secure-key-2024-change-for-production"
            )
            
            cookie_manager = EncryptedCookieManager(
                password=cookie_key,
                prefix="learnify/auth",
            )
            
            st.session_state.cookies = cookie_manager
            st.warning("⚠️ Initializing session... Some features may be limited initially.")
            
        except Exception as e:
            st.error(f"Could not initialize cookie manager: {e}")
            st.session_state.cookies = None
            return False
    
    # Check if we have a cookie manager now (could be None if initialization failed)
    return st.session_state.cookies is not None
