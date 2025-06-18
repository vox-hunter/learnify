"""
Home Page - Optimized Main course generation interface
"""
import streamlit as st
import sys
import os
from streamlit_cookies_manager import EncryptedCookieManager

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import local_backend

try:
    from mongo_auth import MongoAuthManager
    from mongo_course_manager import get_course_manager, get_session_id
    MONGO_AVAILABLE = True
except ImportError as e:
    st.error(f"Failed to import MongoAuthManager or MongoCourseManager: {e}")
    MONGO_AVAILABLE = False

# Optimized CSS - Reduced complexity
st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #0a0014 0%, #1a0033 100%); }
    .main-container { max-width: 800px; margin: 0 auto; padding: 2rem; text-align: center; }
    .main-title {
        font-size: 3rem; font-weight: 700;
        background: linear-gradient(135deg, #9d00ff, #ff6b6b);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        margin-bottom: 2rem;
    }
    .stButton > button {
        background: linear-gradient(135deg, #9d00ff, #7a00cc);
        color: white; border: none; border-radius: 50px;
        padding: 12px 30px; font-weight: 600;
        transition: all 0.3s ease; width: 100%; font-size: 1rem;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #7a00cc, #5c0099);
        transform: translateY(-2px);
    }
    .course-card {
        border: 1px solid #9d00ff; border-radius: 15px;
        padding: 1rem; margin-bottom: 1rem;
        background: rgba(157, 0, 255, 0.05);
    }
</style>
""", unsafe_allow_html=True)

# Cookie Manager Initialization
COOKIE_ENCRYPTION_KEY = st.secrets.get("COOKIE_ENCRYPTION_KEY", "YOUR_STRONG_SECRET_PASSWORD_FOR_COOKIES")
cookies = EncryptedCookieManager(password=COOKIE_ENCRYPTION_KEY, prefix="learnify/auth")

AUTH_COOKIE_NAME = "username"
GUEST_COURSES_COOKIE_NAME = "guest_courses_count"

# Optimized session state initialization
@st.cache_data
def get_default_session_state():
    """Get default session state values"""
    return {
        "current_section_index": 0,
        "user_answers": {},
        "checked_answers": {},
        "current_score": 0,
        "total_questions_in_course": 0,
        "scored_correctly_keys": set(),
        "feedback": {},
        "course_data": None,
        "error_message": None,
        "is_generating_course": False,
        "courses_generated": 0,
        "authentication_status": None,
        "name": None,
        "username": None,
        "course_history": [],
        "current_course_id": None
    }

def initialize_session_state():
    """Initialize session state efficiently"""
    defaults = get_default_session_state()
    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

# Authentication functions (simplified)
def get_auth_manager():
    if not MONGO_AVAILABLE:
        return None
    if "auth_manager" not in st.session_state:
        st.session_state.auth_manager = MongoAuthManager()
    return st.session_state.auth_manager

def login_user_session(username, user_data):
    st.session_state['authentication_status'] = True
    st.session_state['username'] = username
    st.session_state['name'] = user_data.get('name')
    st.session_state['email'] = user_data.get('email')
    
    # Transfer guest courses
    if MONGO_AVAILABLE:
        try:
            session_id = get_session_id()
            course_manager = get_course_manager()
            transferred_count, _ = course_manager.transfer_guest_courses(session_id, username)
            if transferred_count > 0:
                st.success(f"✅ {transferred_count} guest course{'s' if transferred_count != 1 else ''} transferred!")
        except Exception:
            pass
    
    reset_guest_course_count()
    st.session_state.courses_generated = 0

def logout_user_session():
    st.session_state['authentication_status'] = False
    st.session_state['username'] = None
    st.session_state['name'] = None
    st.session_state['email'] = None
    st.session_state['logout_just_occurred'] = True
    
    if cookies.ready():
        cookies[AUTH_COOKIE_NAME] = "logged_out"
        cookies.save()

# Guest course tracking (simplified)
def get_guest_course_count():
    if not cookies.ready():
        return 0
    try:
        count = cookies.get(GUEST_COURSES_COOKIE_NAME, 0)
        return int(count) if count else 0
    except:
        return 0

def increment_guest_course_count():
    if not cookies.ready():
        return
    current_count = get_guest_course_count()
    new_count = current_count + 1
    cookies[GUEST_COURSES_COOKIE_NAME] = str(new_count)
    cookies.save()
    return new_count

def reset_guest_course_count():
    if cookies.ready():
        cookies[GUEST_COURSES_COOKIE_NAME] = "0"
        cookies.save()

def check_course_limit():
    if st.session_state.get('authentication_status'):
        return True
    return get_guest_course_count() < 3

def force_login_if_limit_reached():
    if st.session_state.get('authentication_status'):
        return False
    
    if get_guest_course_count() >= 3:
        st.error("🔐 You have generated 3 courses as a guest. Please login to continue.")
        if st.button("🔐 Go to Login", type="primary", key="force_login_btn"):
            st.switch_page("pages/2_🔐_Login.py")
        return True
    return False

# Auto-login function
def auto_login_from_cookie_home():
    manager = get_auth_manager()
    if not manager or st.session_state.get('authentication_status'):
        return

    cookie_username = cookies.get(AUTH_COOKIE_NAME)
    if cookie_username and cookie_username != "logged_out":
        user_data = manager.find_user_by_username(cookie_username)
        if user_data:
            login_user_session(cookie_username, user_data)

# Optimized course generation with better progress tracking
def generate_and_redirect(uploaded_file, pdf_url):
    """Generate course with optimized progress tracking"""
    st.session_state.is_generating_course = True
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    def status_callback(status_message, progress_percent):
        progress_bar.progress(min(progress_percent / 100, 0.95))  # Cap at 95% until complete
        status_text.text(status_message)
    
    try:
        # Generate course
        if uploaded_file:
            uploaded_file.seek(0)
            course_data, error_message = local_backend.generate_course(
                file_content=uploaded_file.read(), 
                status_callback=status_callback
            )
        else:
            course_data, error_message = local_backend.generate_course(
                file_url=pdf_url, 
                status_callback=status_callback
            )
        
        if course_data and not error_message:
            progress_bar.progress(100)
            status_text.text("✅ Course created successfully!")

            # Determine course title
            if uploaded_file:
                course_title = f"📄 {uploaded_file.name.replace('.pdf', '')}"
            else:
                course_title = f"🔗 Course from URL"

            # Save course
            if MONGO_AVAILABLE:
                try:
                    course_manager = get_course_manager()
                    is_guest = not st.session_state.get('authentication_status', False)
                    
                    if is_guest:
                        session_id = get_session_id()
                        creator = session_id
                    else:
                        session_id = None
                        creator = st.session_state.get('username', 'unknown_user')
                    
                    course_id, save_error = course_manager.save_course(
                        course_data=course_data,
                        course_title=course_title,
                        creator=creator,
                        is_guest=is_guest,
                        session_id=session_id,
                        is_public=True 
                    )
                    
                    if course_id and not save_error:
                        st.session_state.current_course_id = course_id
                        
                        if not st.session_state.get('authentication_status'):
                            increment_guest_course_count()
                        
                        # Clear generation state
                        st.session_state.is_generating_course = False
                        st.session_state.current_uploaded_file = None
                        st.session_state.current_pdf_url = None
                        
                        # Redirect to course
                        st.query_params["course_id"] = str(course_id)
                        time.sleep(1)  # Brief pause to show completion
                        st.switch_page("pages/3_Course.py")
                    else:
                        st.error(f"❌ Failed to save course: {save_error}")
                        st.session_state.is_generating_course = False
                        
                except Exception as e:
                    st.error(f"❌ Error saving course: {e}")
                    st.session_state.is_generating_course = False
            else:
                st.warning("⚠️ MongoDB not available. Course generated but not saved.")
                st.session_state.is_generating_course = False
                
        else:
            st.error(f"❌ {error_message}")
            st.session_state.is_generating_course = False
            
    except Exception as e:
        st.error(f"❌ Error generating course: {str(e)}")
        st.session_state.is_generating_course = False

# Optimized course dashboard
@st.cache_data(ttl=60)  # Cache for 1 minute
def get_user_courses_cached(user_identifier, is_guest, session_id=None):
    """Get user courses with caching"""
    if not MONGO_AVAILABLE:
        return [], None
    
    try:
        course_manager = get_course_manager()
        if is_guest:
            return course_manager.get_user_courses(user_identifier=session_id, is_guest=True, session_id=session_id)
        else:
            return course_manager.get_user_courses(user_identifier, is_guest=False)
    except Exception as e:
        return [], str(e)

def show_course_dashboard():
    """Show optimized course dashboard"""
    if not MONGO_AVAILABLE:
        st.markdown("### 🚀 Ready to Get Started?")
        st.info("Upload a PDF or enter a URL below to generate your first course!")
        return
    
    try:
        user_identifier = st.session_state.get('username')
        session_id_val = get_session_id()
        is_guest = not st.session_state.get('authentication_status', False)
        
        # Use cached function
        courses, error = get_user_courses_cached(
            user_identifier if not is_guest else session_id_val,
            is_guest,
            session_id_val if is_guest else None
        )
        
        if courses and not error:
            st.markdown("### 📚 Your Recent Courses")
            
            # Show recent courses in a simple grid
            if len(courses) > 0:
                cols = st.columns(min(3, len(courses)))
                for i, course in enumerate(courses[:6]):
                    with cols[i % 3]:
                        course_title = course.get('title', 'Untitled Course')
                        course_id = course.get('course_id')
                        total_questions = course.get('total_questions', 0)
                        
                        st.markdown(f'''
                        <div class="course-card">
                            <h4>{course_title[:30]}{'...' if len(course_title) > 30 else ''}</h4>
                            <p>📊 {total_questions} questions</p>
                        </div>
                        ''', unsafe_allow_html=True)
                        
                        if st.button(f"▶️ Continue", key=f"course_btn_{course_id}", use_container_width=True):
                            if course_id:
                                st.query_params["course_id"] = str(course_id)
                                st.session_state.current_course_id = str(course_id)
                                st.switch_page("pages/3_Course.py")
        else:
            st.markdown("### 🚀 Ready to Get Started?")
            st.info("Upload a PDF or enter a URL below to generate your first course!")
            
    except Exception as e:
        st.markdown("### 🚀 Ready to Get Started?")
        st.info("Upload a PDF or enter a URL below to generate your first course!")

def main():
    """Optimized main function"""
    # Handle shared course
    shared_course_id = st.query_params.get("course_id")
    if shared_course_id:
        st.session_state.shared_course_id = shared_course_id
        st.query_params["course_id"] = shared_course_id
        st.switch_page("pages/3_Course.py")
        return
    
    initialize_session_state()
    
    # Process logout and auto-login
    just_logged_out = st.session_state.pop('logout_just_occurred', False)
    if not just_logged_out and cookies.ready():
        auto_login_from_cookie_home()
    
    # Top navigation
    col1, col2, col3 = st.columns([6, 1, 1])
    
    with col2:
        if st.session_state.get('authentication_status'):
            display_name = st.session_state.get('name', st.session_state.get('username', 'User'))
            if len(display_name) > 15:
                display_name = display_name[:12] + "..."
            st.markdown(f"<div style='text-align: center; padding: 5px; border: 1px solid #9d00ff; border-radius: 25px; background: rgba(157,0,255,0.1);'>👤 {display_name}</div>", unsafe_allow_html=True)
        elif MONGO_AVAILABLE and cookies.ready():
            if st.button("🔐 Login", key="top_nav_login_btn", use_container_width=True):
                st.switch_page("pages/2_🔐_Login.py")

    with col3:
        if st.session_state.get('authentication_status'):
            if st.button("🚪 Logout", key="top_nav_logout_btn", use_container_width=True):
                logout_user_session()
                st.rerun()

    # Main content
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    st.markdown('<h1 class="main-title">What will you learn today?</h1>', unsafe_allow_html=True)
    
    # Status message
    if st.session_state.get('authentication_status'):
        st.success(f"🎉 Welcome back, {st.session_state.get('name', 'User')}!")
    else:
        if force_login_if_limit_reached():
            return
        guest_count = get_guest_course_count()
        remaining = 3 - guest_count
        if remaining > 0:
            st.info(f"🎯 Guest mode: {remaining} out of 3 free courses remaining")
    
    st.markdown("---")
    
    # Course Dashboard
    show_course_dashboard()
    st.markdown("---")

    # Input tabs
    tab1, tab2 = st.tabs(["📁 Upload File", "🔗 URL"])
    uploaded_file = None
    pdf_url = None
    
    with tab1:
        st.markdown("### Upload your PDF file")
        uploaded_file = st.file_uploader(
            "Choose a PDF file",
            type=["pdf"],
            help="Maximum file size: 10MB, Maximum words: 15,000",
            label_visibility="collapsed"
        )
        if uploaded_file:
            file_size = len(uploaded_file.getvalue())
            file_size_mb = file_size / (1024*1024)
            
            if file_size > 10 * 1024 * 1024:
                st.error(f"❌ File too large ({file_size_mb:.1f} MB). Maximum size is 10MB.")
                uploaded_file = None
            else:
                try:
                    pdf_analysis = local_backend.analyze_pdf_content(uploaded_file.getvalue())
                    word_count = pdf_analysis['word_count']
                    
                    if word_count > 15000:
                        st.error(f"❌ PDF contains too many words ({word_count:,}). Maximum: 15,000 words.")
                        uploaded_file = None
                    elif word_count == 0:
                        st.error("❌ Could not extract text from this PDF.")
                        uploaded_file = None
                    else:
                        st.success(f"📄 File uploaded: {uploaded_file.name} ({file_size_mb:.1f} MB)")
                except Exception as e:
                    st.error(f"❌ Error analyzing PDF: {str(e)}")
                    uploaded_file = None
    
    with tab2:
        st.markdown("### Enter PDF URL")
        pdf_url = st.text_input(
            "PDF URL",
            placeholder="https://example.com/document.pdf",
            help="Enter a direct link to a PDF file",
            label_visibility="collapsed"
        )
        if pdf_url and not pdf_url.startswith(('http://', 'https://')):
            st.warning("⚠️ Please enter a valid URL starting with http:// or https://")
            pdf_url = None
    
    # Generate button
    st.markdown("<br>", unsafe_allow_html=True)
    can_generate = check_course_limit()
    
    if st.session_state.get('is_generating_course', False):
        st.button("🤖 Generating Course...", disabled=True, key="generating_btn")
        # Get file data from session state
        uploaded_file = st.session_state.get('current_uploaded_file')
        pdf_url = st.session_state.get('current_pdf_url')
        if uploaded_file or pdf_url:
            generate_and_redirect(uploaded_file, pdf_url)
    elif can_generate:
        if st.button("✨ Generate Course", type="primary", key="generate_btn"):
            if uploaded_file or pdf_url:
                if not check_course_limit():
                    st.error("🔐 Course limit reached. Please login to continue.")
                    return
                
                # Store file data and set generating state
                st.session_state.current_uploaded_file = uploaded_file
                st.session_state.current_pdf_url = pdf_url
                st.session_state.is_generating_course = True
                st.rerun()
            else:
                st.error("⚠️ Please upload a file or enter a URL first")
    else:
        st.warning("⚠️ You've reached the limit of 3 guest courses.")
        if st.button("🔐 Go to Login", type="primary"):
            st.switch_page("pages/2_🔐_Login.py")
    
    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()