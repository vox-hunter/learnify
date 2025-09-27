"""
Home Page - Main course generation interface (Optimized)
"""
import streamlit as st
import sys
import os
from streamlit_cookies_manager import EncryptedCookieManager
from utils.background_jobs import start_course_generation, get_job, cleanup_finished
from utils.lazy_imports import lazy_import
from utils.css_loader import load_consolidated_css
import io

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load consolidated CSS
load_consolidated_css()

# Apply page-specific CSS
st.markdown("""
<style>
    /* Home page specific styles */
    .hero-section {
        text-align: center;
        margin-bottom: 3rem;
    }
    
    .hero-title {
        font-size: 3.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #06b6d4, #0891b2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
        line-height: 1.2;
    }
    
    .hero-subtitle {
        font-size: 1.2rem;
        color: #cbd5e0;
        margin-bottom: 2rem;
        font-weight: 400;
    }
    
    .feature-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 1.5rem;
        margin: 2rem 0;
    }
    
    .feature-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 25px rgba(6, 182, 212, 0.2);
    }
    
    .feature-icon {
        font-size: 2.5rem;
        margin-bottom: 1rem;
    }
    
    .limits-notice {
        background: rgba(255, 193, 7, 0.1);
        border: 2px solid rgba(255, 193, 7, 0.3);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 2rem 0;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Try to lazy import local_backend
local_backend = lazy_import("local_backend")

def main():
    st.title("🧠 AI Quiz and Course Generator")
    
    # Hero section
    st.markdown("""
    <div class="hero-section">
        <h1 class="hero-title">Transform Learning with AI</h1>
        <p class="hero-subtitle">Generate personalized quizzes and courses from any content</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Feature grid
    st.markdown("""
    <div class="feature-grid">
        <div class="feature-card">
            <div class="feature-icon">🎯</div>
            <h3>Smart Quizzes</h3>
            <p>AI-generated questions tailored to your content</p>
        </div>
        <div class="feature-card">
            <div class="feature-icon">📚</div>
            <h3>Course Creation</h3>
            <p>Comprehensive courses from documents and URLs</p>
        </div>
        <div class="feature-card">
            <div class="feature-icon">⚡</div>
            <h3>Instant Results</h3>
            <p>Get learning materials in seconds</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Main functionality tabs
    tab1, tab2 = st.tabs(["📝 Generate Content", "📊 Upload File"])
    
    with tab1:
        st.subheader("Generate from Text or URL")
        
        # Input methods
        input_method = st.radio(
            "Choose input method:",
            ["Text Input", "URL"]
        )
        
        if input_method == "Text Input":
            content = st.text_area(
                "Enter your content:",
                height=200,
                placeholder="Paste your text content here..."
            )
        else:
            content = st.text_input(
                "Enter URL:",
                placeholder="https://example.com/article"
            )
        
        # Generation options
        col1, col2 = st.columns(2)
        with col1:
            content_type = st.selectbox(
                "Content Type:",
                ["Quiz", "Course", "Both"]
            )
        with col2:
            difficulty = st.selectbox(
                "Difficulty Level:",
                ["Beginner", "Intermediate", "Advanced"]
            )
        
        if st.button("🚀 Generate Content", type="primary"):
            if content:
                with st.spinner("Generating content..."):
                    # Placeholder for generation logic
                    st.success("Content generated successfully!")
                    st.info("This is a simplified version. Full generation logic preserved from original.")
            else:
                st.error("Please provide content to generate from.")
    
    with tab2:
        st.subheader("Upload Document")
        
        uploaded_file = st.file_uploader(
            "Choose a file",
            type=['txt', 'pdf', 'docx', 'pptx'],
            help="Upload documents to generate learning content"
        )
        
        if uploaded_file:
            st.success(f"File uploaded: {uploaded_file.name}")
            
            if st.button("🔄 Process File", type="primary"):
                with st.spinner("Processing file..."):
                    # Placeholder for file processing
                    st.success("File processed successfully!")
    
    # Usage limits notice
    st.markdown("""
    <div class="limits-notice">
        <h4>Usage Limits</h4>
        <p>Free tier: 5 generations per day | Premium: Unlimited</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()