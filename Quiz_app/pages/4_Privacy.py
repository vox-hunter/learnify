"""
Privacy Policy Page for AI Loom
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
    
    .privacy-container {
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
st.title("🛡️ Privacy Policy – AI Loom ")

st.markdown("""
**Last Updated:** June 30, 2025  

Welcome to **AI Loom**! We respect your privacy and are committed to being transparent about how we collect, use, and protect your data.

---

## 1. What We Collect  

We may collect the following basic data:
- **Email address** (for login or communication)  
- **App usage data** (how often you use the app, which features you use)  
- **Feedback you provide** (bug reports, feature requests)  
- **Optional content uploads** (notes or slides for course generation)

---

## 2. How We Use Your Data  

We use your information to:
- Let you log in and use the app  
- Improve app features and user experience  
- Understand how the platform is being used  
- Respond to your feedback or support requests  
- Send notes or slides you upload to our AI provider for course generation

---

## 3. How Your Data is Stored  

Your data is securely stored in:
- **Supabase** (for authentication)  
- **MongoDB** (for user-generated content and course data)

We do **not** sell, rent, or share your data with third parties. However, we may share **anonymized usage data** with our AI provider to improve course generation features.

---

## 4. Cookies & Analytics  

We may use basic cookies or tools like **Google Analytics** to understand usage patterns.  
No personal information is tracked unless you've logged in.

---

## 5. Your Choices  

- You can request your data be deleted at any time by deleting your account at the "Account" page.
- We remove your data from our systems within **30 days** of account deletion.

---

## 6. Community & Feedback  

By joining our [Discord server](https://discord.gg/HNZ96dSdtn), you agree to follow community rules.  
Any feedback you submit may be used to improve the product.
""")

# Navigation back to home
col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    if st.button("🏠 Back to Home", use_container_width=True):
        st.switch_page("pages/1_🏠_Home.py")
