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
    /* Cache buster: 2025-07-02-14:30 - Force CSS reload */
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
    
    /* Sidebar styling delegated to main.py */
    
    .main {
        max-width: 800px;
        margin: 0 auto;
        padding: 2rem;
    }
    
    .stMarkdown {
        text-align: justify;
    }
    
    h1 {
        color: #8b5cf6;
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
- **MongoDB** (for user-generated content and accounts details)

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
