"""
Terms & Conditions Page for AI Loom
"""
import streamlit as st

# --- Get Cookie Manager from Session State for Consistency ---
cookies = st.session_state.get('cookies')
if cookies is None:
    # Try fallback initialization
    try:
        from cookie_fallback import ensure_cookie_manager
        if ensure_cookie_manager():
            cookies = st.session_state.get('cookies')
        else:
            # Don't stop - just continue without cookies
            cookies = None
    except (ImportError, RuntimeError, ValueError):
        cookies = None

# Custom CSS for stylingerms and Conditions Page for AI Loom
"""
import streamlit as st

# Custom CSS for styling
st.markdown("""
<style>
    /* Hide cookie manager component that takes up horizontal space */
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
    
    /* Hide any empty custom components that might be taking space */
    .stCustomComponentV1:has(iframe[height="0"]) {
        display: none !important;
    }
    
    /* Hide custom components with cookie manager */
    .st-emotion-cache-8atqhb:has(iframe[src*="cookie_manager"]) {
        display: none !important;
    }
    
    /* Consistent sidebar styling (from main.py) */
    .stSidebar > div {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.05), rgba(255, 255, 255, 0.02)) !important;
        backdrop-filter: blur(20px) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.1) !important;
    }
    
    /* Sidebar buttons */
    .stSidebar .stButton > button {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1)) !important;
        color: #e2e8f0 !important;
        border: 1px solid rgba(102, 126, 234, 0.2) !important;
        border-radius: 12px !important;
        padding: 8px 16px !important;
        font-weight: 500 !important;
        transition: all 0.3s ease !important;
    }
    
    .stSidebar .stButton > button:hover {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.2), rgba(118, 75, 162, 0.2)) !important;
        border-color: rgba(102, 126, 234, 0.4) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2) !important;
    }
    
    /* Sidebar popover buttons (Logout, Reset Password) */
    .stSidebar .stPopover .stButton > button {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1)) !important;
        color: #e2e8f0 !important;
        border: 1px solid rgba(102, 126, 234, 0.2) !important;
        border-radius: 12px !important;
        padding: 8px 16px !important;
        font-weight: 500 !important;
        transition: all 0.3s ease !important;
    }
    
    .stSidebar .stPopover .stButton > button:hover {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.2), rgba(118, 75, 162, 0.2)) !important;
        border-color: rgba(102, 126, 234, 0.4) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2) !important;
    }
    
    /* Override any general button styling for sidebar popover */
    .stSidebar [data-testid="stPopover"] .stButton > button {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1)) !important;
        color: #e2e8f0 !important;
        border: 1px solid rgba(102, 126, 234, 0.2) !important;
    }
    
    .main {
        max-width: 800px;
        margin: 0 auto;
        padding: 2rem;
    }
    
    .stMarkdown {
        text-align: justify;
    }
    
    h1 {
        color: #667eea;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .terms-container {
        background: rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 24px;
        padding: 2.5rem;
        margin: 2rem 0;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    }
</style>
""", unsafe_allow_html=True)

# Main content
st.title("📜 Terms & Conditions – AI Loom ")

st.markdown(""" 
**Last Updated:** June 30, 2025  

By using **AI Loom** (the app), you agree to these Terms. We’ll keep it simple and clear — no legal jargon.

---

## 1. What AI Loom Does  

AI Loom is an AI-powered tool that helps you turn notes or slides into personalized learning content like lessons, quizzes, and more.  
It’s currently in **beta**, so expect rapid updates, new features, and the occasional bug.

---

## 2. Your Responsibilities  

When using AI Loom, you agree to:
- Use it respectfully and for its intended purpose  
- Not upload harmful, illegal, or copyrighted content  
- Not try to break, reverse-engineer, or misuse the app  
- Follow our community rules if you join our Discord server

---

## 3. Beta Disclaimer  

This is an early version of the product.  
Features may change, break, or be removed.  
You’re helping shape the final version — and we really appreciate your feedback.

---

## 4. Accounts & Data  

- You’re responsible for keeping your login secure  
- We don’t sell your data — see our [Privacy Policy](https://ailoom.me/privacy-policy) 
- All your data may be deleted in future updates 
- You can request deletion of your account and data at any time

---

## 5. Termination  

We reserve the right to suspend or delete accounts if users abuse the platform, spam, or violate these terms.

---

## 6. No Guarantees  

AI Loom is provided “as is.”  
We’ll do our best to keep it running smoothly, but we can’t promise perfection.  
Use it at your own risk.

---

Thanks for using AI Loom — you're helping us build something awesome.
""")

# Navigation back to home
col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    if st.button("🏠 Back to Home", use_container_width=True):
        st.switch_page("pages/1_🏠_Home.py")
