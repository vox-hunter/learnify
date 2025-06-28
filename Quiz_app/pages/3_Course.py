import streamlit as st
import json
import sys # Add sys import
import os # Add os import
import random
import time
import datetime

# Add the parent directory (Quiz app) to sys.path to allow imports from it
# __file__ is pages/3_📚_Course.py -> dirname is pages -> dirname is Quiz app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Ensure loading UI is cleaned up
try:
    from streamlit_loading import ensure_loading_cleanup
    ensure_loading_cleanup()
except ImportError:
    pass

try:
    from st_fill_in_the_blanks import fill_in_the_blanks_input
    FILL_IN_BLANKS_AVAILABLE = True
except ImportError:
    FILL_IN_BLANKS_AVAILABLE = False
    fill_in_the_blanks_input = None
    st.warning("Fill-in-the-blanks component not available - using fallback text input")
    
try:
    import local_backend
except ImportError:
    local_backend = None
    st.warning("Local backend not available for AI validation")

try:
    from mongo_course_manager import get_course_manager, get_session_id
    MONGO_AVAILABLE = True
except ImportError:
    MONGO_AVAILABLE = False

# Initialize session state function
def initialize_session_state():
    """Initialize all session state variables"""
    if "current_section_index" not in st.session_state:  
        st.session_state.current_section_index = 0
    if "user_answers" not in st.session_state:
        st.session_state.user_answers = {}
    if "checked_answers" not in st.session_state:
        st.session_state.checked_answers = {}
    if "current_score" not in st.session_state:
        st.session_state.current_score = 0
    if "total_questions_in_course" not in st.session_state:
        st.session_state.total_questions_in_course = 0
    if "scored_correctly_keys" not in st.session_state:
        st.session_state.scored_correctly_keys = set()
    if "feedback" not in st.session_state:
        st.session_state.feedback = {}
    if "course_history" not in st.session_state:
        st.session_state.course_history = []
    if "current_course_id" not in st.session_state:
        st.session_state.current_course_id = None
    if "course_finished" not in st.session_state:
        st.session_state.course_finished = False
    if "start_time" not in st.session_state:
        st.session_state.start_time = time.time()

def reset_course_session_state():
    """Reset course-specific session state when starting a new course"""
    # Reset course progress data
    st.session_state.current_section_index = 0
    st.session_state.user_answers = {}
    st.session_state.checked_answers = {}
    st.session_state.current_score = 0
    st.session_state.total_questions_in_course = 0
    st.session_state.scored_correctly_keys = set()
    st.session_state.feedback = {}
    st.session_state.course_finished = False
    st.session_state.start_time = time.time()
    
    # Clear any cached question counts
    keys_to_remove = [key for key in st.session_state.keys() if str(key).startswith('total_questions_')]
    for key in keys_to_remove:
        del st.session_state[key]

# Initialize session state
initialize_session_state()

def is_localhost():
    """Check if the app is running on localhost."""
    try:
        # Get the server address from Streamlit's config
        server_address = st.get_option('server.address')
        
        # Check if the address is localhost or the local IP
        if server_address in ['localhost', '127.0.0.1', '0.0.0.0']:
            return True
            
        # Fallback for other local IPs
        import socket
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        
        return server_address == local_ip
    except Exception:
        # If any error occurs, assume it's not localhost for safety
        return False

def is_admin_user():
    """Check if admin features should be enabled for specific admin users."""
    username = st.session_state.get('username', '')
    email = st.session_state.get('email', '')
    
    admin_usernames = ["vox"]
    admin_emails = ["vidyutsanthosh4@gmail.com"]
    
    return username in admin_usernames or email in admin_emails

def mark_all_section_questions_correct(course_data, section_index, course_id):
    """Mark all questions in a section as correct (admin function)"""
    if section_index >= len(course_data):
        return False
    
    section_key = f"course_{course_id}_sec_{section_index}"
    section_data = course_data[section_index]
    
    # Mark main section questions as correct
    _mark_section_questions_correct_recursive(section_data, section_key)
    
    return True

def _mark_section_questions_correct_recursive(section_data, section_key):
    """Recursively mark all questions in a section and its subsections as correct"""
    # Check if section_data is a Pydantic model or dict
    is_pydantic_model = hasattr(section_data, '__dict__') and not hasattr(section_data, 'get')
    
    if is_pydantic_model:
        questions = getattr(section_data, "quiz", [])
        subsections = getattr(section_data, "subsections", [])
    else:
        questions = section_data.get('quiz', section_data.get('questions', []))
        subsections = section_data.get('subsections', [])
    
    # Handle None values
    if questions is None:
        questions = []
    if subsections is None:
        subsections = []
    
    # Mark main section questions as correct
    if questions:
        for i, _ in enumerate(questions):
            question_key = f"{section_key}_q_{i}"
            
            # Mark as answered correctly
            st.session_state.checked_answers[question_key] = True
            st.session_state.user_answers[question_key] = "Admin Override"
            
            # Add to score tracking if not already counted
            if question_key not in st.session_state.scored_correctly_keys:
                st.session_state.current_score += 1
                st.session_state.scored_correctly_keys.add(question_key)
            
            # Add feedback
            st.session_state.feedback[question_key] = "Correct! (Admin Override)"
    
    # Mark subsection questions as correct
    if subsections:
        for sub_idx, subsection in enumerate(subsections):
            subsection_key = f"{section_key}_sub_{sub_idx}"
            _mark_section_questions_correct_recursive(subsection, subsection_key)

# Apply modern CSS styling
st.markdown("""
<style>
    /* Global styles */
    .stApp {
        background: linear-gradient(135deg, #0a0014 0%, #1a0033 100%);
    }
    
    /* Course container */
    .course-container {
        max-width: 1000px;
        margin: 0 auto;
        padding: 1rem;
    }
    
    /* Course title */
    .course-title {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #9d00ff, #ff6b6b);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
        text-align: center;
    }
    
    /* Section title */
    .section-title {
        font-size: 1.8rem;
        font-weight: 600;
        color: #9d00ff;
        margin-bottom: 1rem;
    }
    
    /* Navigation buttons */
    .nav-buttons {
        display: flex;
        justify-content: space-between;
        margin: 2rem 0;
    }
    
    /* Pill button styling */
    .stButton > button {
        background: linear-gradient(135deg, #9d00ff, #7a00cc);
        color: white;
        border: none;
        border-radius: 50px;
        padding: 12px 30px;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(157, 0, 255, 0.3);
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #7a00cc, #5c0099);
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(157, 0, 255, 0.4);
    }
    
    .stButton > button:disabled {
        background: #444;
        transform: none;
        box-shadow: none;
    }
    
    /* Score display */
    .score-container {
        background: linear-gradient(135deg, rgba(157, 0, 255, 0.1), rgba(255, 107, 107, 0.1));
        border-radius: 20px;
        padding: 1.5rem;
        text-align: center;
        margin: 2rem 0;
        border: 1px solid rgba(157, 0, 255, 0.3);
    }
    
    .score-container h3 {
        color: #9d00ff;
        margin-bottom: 0.5rem;
    }
    
    .score-container h2 {
        background: linear-gradient(135deg, #9d00ff, #ff6b6b);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2rem;
        margin: 0;
    }
    
    /* Question container styling */
    .question-container {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(157, 0, 255, 0.3);
        border-radius: 20px;
        padding: 2rem;
        margin: 1.5rem 0;
        transition: all 0.3s ease;
    }
    
    .question-container:hover {
        border-color: rgba(255, 107, 107, 0.5);
        background: rgba(255, 255, 255, 0.05);
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(157, 0, 255, 0.2);
    }
    
    /* Radio button styling */
    .stRadio > div {
        background: rgba(255, 255, 255, 0.02);
        border-radius: 15px;
        padding: 1rem;
    }
    
    /* Text inputs */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background: rgba(255, 255, 255, 0.05);
        border: 2px solid #9d00ff;
        border-radius: 15px;
        color: white;
        padding: 15px;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #ff6b6b;
        box-shadow: 0 0 15px rgba(157, 0, 255, 0.3);
    }
    
    /* Success and error messages */
    .stSuccess {
        background: rgba(0, 255, 0, 0.1);
        border: 1px solid #00ff00;
        border-radius: 10px;
    }
    
    .stError {
        background: rgba(255, 0, 0, 0.1);
        border: 1px solid #ff0000;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Cache for course data to avoid repeated database calls
@st.cache_data(ttl=300)  # Cache for 5 minutes
def _load_course_from_mongo(course_id, user_identifier, session_id):
    """Cached function to load course data from MongoDB"""
    if not MONGO_AVAILABLE:
        return None, "MongoDB not available"
    
    try:
        course_manager = get_course_manager()
        
        # Check if user can access this course
        can_access, access_error = course_manager.can_access_course(
            course_id=course_id,
            user_identifier=user_identifier,
            session_id=session_id
        )
        
        if not can_access:
            return None, access_error
        
        # Load course from MongoDB
        course_doc, load_error = course_manager.get_course(course_id)
        
        if course_doc and not load_error:
            return course_doc['content'], None  # Return the course content
        elif load_error:
            return None, load_error
        else:
            return None, "Course not found"
    except (ImportError, AttributeError, ConnectionError) as e:
        return None, f"Error accessing course database: {e}"

def optimize_session_state():
    """Optimize session state by batching updates and reducing unnecessary flags"""
    # Clear temporary flags that might cause unnecessary reruns
    flags_to_clear = ['privacy_updated', 'fitb_answered', 'match_submitted', 'course_changed']
    for flag in flags_to_clear:
        if flag in st.session_state:
            del st.session_state[flag]

def main():
    # Optimize session state and clear temporary flags
    optimize_session_state()
    
    # Sidebar navigation is now handled by main.py
    
    # Get current course ID from URL or session state
    course_id = get_current_course_id()
    
    if course_id is None:
        st.error("❌ No course selected. Please go back to home and generate a course.")
        if st.button("🏠 Go to Home"):
            st.switch_page("app_pages/1_🏠_Home.py")
        return
    
    # Check if this is a new course (different from the last one)
    if st.session_state.get('last_course_id') != course_id:
        reset_course_session_state()
        st.session_state.last_course_id = course_id
    
    # Load course data (now with caching)
    course_data = load_course_data(course_id)
    
    if not course_data:
        st.error("❌ Course not found. It may have been deleted.")
        if st.button("🏠 Go to Home"):
            st.switch_page("app_pages/1_🏠_Home.py")
        return

    if st.session_state.get('course_finished', False):
        display_course_completion_stats(course_data, course_id)
        return
      # Main course container
    st.markdown('<div class="course-container">', unsafe_allow_html=True)
    
    # Course title and info - handle both MongoDB and session data
    course_title = "📚 Course"  # Default title
    
    # Try to get title from MongoDB first
    if MONGO_AVAILABLE and isinstance(course_id, str) and len(course_id) == 24:
        try:
            course_manager = get_course_manager()
            course_doc, _ = course_manager.get_course(course_id)
            if course_doc:
                course_title = course_doc.get('title', '📚 Course')
        except (ImportError, AttributeError, ConnectionError) as e:
            st.error(f"An error occurred while fetching the course title from MongoDB: {e}")
    
    # Fall back to session state
    if course_title == "📚 Course" and 'course_history' in st.session_state:
        try:
            course_id_int = int(course_id)
            if course_id_int < len(st.session_state.course_history):
                course_title = st.session_state.course_history[course_id_int]['title']
        except (ValueError, TypeError):
            pass
    
    st.markdown(f'<h1 class="course-title">{course_title}</h1>', unsafe_allow_html=True)
    
    # Course metadata
    total_sections = len(course_data)
    current_section = st.session_state.get('current_section_index', 0)
    st.markdown(f"**📚 Section {current_section + 1} of {total_sections}**")
    
    # Score display
    show_score_display(course_data)
    
    # Admin controls (enabled on localhost or for admin users)
    if is_admin_user():
        st.markdown("---")
        
        # Show localhost indicator
        if is_localhost():
            st.markdown("### 🔧 Admin Controls (Localhost Mode)")
            st.info("💻 Admin features are enabled because you're running on localhost")
        else:
            st.markdown("### 🔧 Admin Controls")
        
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            if st.button("✅ Mark Current Section Complete", key="admin_mark_section"):
                success = mark_all_section_questions_correct(course_data, current_section, course_id)
                if success:
                    st.success(f"✅ Marked all questions in Section {current_section + 1} as correct!")
                    st.rerun()
                else:
                    st.error("❌ Failed to mark section complete")
        
        with col2:
            if st.button("✅ Mark All Sections Complete", key="admin_mark_all"):
                for section_idx in range(len(course_data)):
                    mark_all_section_questions_correct(course_data, section_idx, course_id)
                
                st.session_state.course_finished = True
                st.success("✅ Marked all sections as complete and finished the course!")
                st.rerun()
        
        with col3:
            if st.button("🔄 Reset Course Progress", key="admin_reset"):
                reset_course_session_state()
                st.success("✅ Course progress reset!")
                st.rerun()
        
        st.markdown("---")
    
    # Course navigation
    show_course_navigation(course_data, course_id)
    
    # Display current section
    display_current_section(course_data, course_id)
    
    st.markdown('</div>', unsafe_allow_html=True)

def get_current_course_id():
    """Get the current course ID from URL params or session state"""
    # First check URL parameters for course_id
    if "course_id" in st.query_params:
        course_id = st.query_params["course_id"]
        # Cache the course_id in session state to avoid repeated URL param reads
        if st.session_state.get('current_course_id') != course_id:
            st.session_state.current_course_id = course_id
        return course_id
    
    # Check URL for section parameter and update session state
    if "section" in st.query_params:
        try:
            section_idx = int(st.query_params["section"])
            if st.session_state.get('current_section_index') != section_idx:
                st.session_state.current_section_index = section_idx
        except (ValueError, TypeError):
            pass
    
    # Check if we have a shared course ID in session state (from redirect)
    if 'shared_course_id' in st.session_state:
        shared_id = st.session_state.shared_course_id
        # Clear it after use to avoid confusion
        del st.session_state.shared_course_id
        st.session_state.current_course_id = shared_id
        return shared_id
    
    # Try to get from session state (for backward compatibility)
    if 'current_course_id' in st.session_state:
        return st.session_state.current_course_id
    
    # If not available, return None
    return None

def load_course_data(course_id):
    """Load course data by ID from MongoDB or session state"""
    # First try to load from MongoDB if available
    if MONGO_AVAILABLE and isinstance(course_id, str) and len(course_id) == 24:  # MongoDB ObjectId is 24 chars
        # Check if user can access this course
        user_identifier = st.session_state.get('username')
        session_id = get_session_id() if not user_identifier else None
        
        # Use cached function to avoid repeated database calls
        course_content, error = _load_course_from_mongo(course_id, user_identifier, session_id)
        
        if course_content and not error:
            return course_content
        elif error:
            st.error(f"❌ Error loading course: {error}")
            return None
    
    # Fall back to session state for backward compatibility
    if 'course_history' not in st.session_state:
        return None
    
    try:
        course_id_int = int(course_id)
        if course_id_int >= len(st.session_state.course_history):
            return None
        
        return st.session_state.course_history[course_id_int]['data']
    except (ValueError, TypeError):
        return None

def show_score_display(course_data):
    """Display color-coded progress bar showing correct (green) and incorrect (red) answers"""
    total_questions = count_total_questions(course_data)
    
    if total_questions > 0:
        # Get current stats
        correct_answers = st.session_state.get('current_score', 0)
        answered_questions = len(st.session_state.get('checked_answers', {}))
        incorrect_answers = answered_questions - correct_answers
        unanswered_questions = total_questions - answered_questions
        
        # Calculate percentages
        correct_pct = (correct_answers / total_questions) * 100
        incorrect_pct = (incorrect_answers / total_questions) * 100
        unanswered_pct = (unanswered_questions / total_questions) * 100
        
        # Create color-coded progress bar using HTML and CSS
        progress_html = f"""
        <div style="
            width: 100%;
            height: 25px;
            background-color: #4a148c;
            border-radius: 12px;
            border: 1px solid #6a1b9a;
            display: flex;
            overflow: hidden;
            margin: 10px 0;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        ">
            <div style="
                width: {correct_pct}%;
                background: linear-gradient(90deg, #28a745, #20c997);
                height: 100%;
                transition: width 0.3s ease;
            "></div>
            <div style="
                width: {incorrect_pct}%;
                background: linear-gradient(90deg, #dc3545, #e74c3c);
                height: 100%;
                transition: width 0.3s ease;
            "></div>
            <div style="
                width: {unanswered_pct}%;
                background-color: #4a148c;
                height: 100%;
                transition: width 0.3s ease;
            "></div>
        </div>
        """
        
        st.markdown(progress_html, unsafe_allow_html=True)
    else:
        # Show empty progress bar if no questions
        st.markdown("""
        <div style="
            width: 100%;
            height: 25px;
            background-color: #4a148c;
            border-radius: 12px;
            border: 1px solid #6a1b9a;
            margin: 10px 0;
        "></div>
        <div style="
            text-align: center;
            font-size: 12px;
            color: #666;
            margin-top: 5px;
        ">No questions available</div>
        """, unsafe_allow_html=True)

def count_total_questions(course_data):
    """Count total questions in course - optimized version"""
    if not course_data:
        return 0
    
    # Use cached count if available
    cache_key = f"total_questions_{hash(str(course_data))}"
    if cache_key in st.session_state:
        return st.session_state[cache_key]
    
    total = 0
    for section in course_data:
        if 'quiz' in section or 'questions' in section:
            questions = section.get('quiz', section.get('questions', []))
            total += len(questions)
        # Count subsection questions
        if 'subsections' in section and section['subsections']:
            for subsection in section['subsections']:
                if 'quiz' in subsection or 'questions' in subsection:
                    sub_questions = subsection.get('quiz', subsection.get('questions', []))
                    total += len(sub_questions)
    
    # Cache the result
    st.session_state[cache_key] = total
    return total

def are_all_questions_in_section_answered(course_data, section_index):
    """Check if all questions in the current section are answered."""
    if section_index >= len(course_data):
        return False

    # Get the course ID to construct proper question keys
    course_id = st.session_state.get('current_course_id', 'unknown')
    section_key = f"course_{course_id}_sec_{section_index}"
    
    # Check if all questions in this section (and its subsections) are answered
    return _check_section_questions_answered(course_data[section_index], section_key)

def _check_section_questions_answered(section_data, section_key):
    """Recursively check if all questions in a section and its subsections are answered."""
    # Check if section_data is a Pydantic model or dict
    is_pydantic_model = hasattr(section_data, '__dict__') and not hasattr(section_data, 'get')
    
    if is_pydantic_model:
        questions = getattr(section_data, "quiz", [])
        subsections = getattr(section_data, "subsections", [])
    else:
        questions = section_data.get('quiz', section_data.get('questions', []))
        subsections = section_data.get('subsections', [])
    
    # Handle None values
    if questions is None:
        questions = []
    if subsections is None:
        subsections = []
    
    # Check main section questions
    if questions:
        for i, _ in enumerate(questions):
            question_key = f"{section_key}_q_{i}"
            is_answered = question_key in st.session_state.get('checked_answers', {})
            if not is_answered:
                return False
    
    # Check subsection questions
    if subsections:
        for sub_idx, subsection in enumerate(subsections):
            subsection_key = f"{section_key}_sub_{sub_idx}"
            if not _check_section_questions_answered(subsection, subsection_key):
                return False
    
    return True

def show_course_navigation(course_data, course_id=None):
    """Show section navigation"""
    total_sections = len(course_data)
    current_section = st.session_state.get('current_section_index', 0)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        if current_section > 0:
            if st.button("⬅️ Previous Section", key="prev_section_btn"):
                st.session_state.current_section_index = current_section - 1
                st.query_params.section = str(current_section - 1)
                st.rerun()
        else:
            st.button("⬅️ Previous Section", disabled=True, key="prev_section_btn_disabled")
    
    with col2:
        st.markdown(f"**Section {current_section + 1} of {total_sections}**")
    
    with col3:
        all_answered = are_all_questions_in_section_answered(course_data, current_section)
        
        # Temporary debug to see why button is disabled
        if not all_answered:
            with st.expander("🔍 Debug: Why is Next Section disabled?"):
                course_id = st.session_state.get('current_course_id', 'unknown')
                section_key = f"course_{course_id}_sec_{current_section}"
                st.write(f"**Section:** {current_section} (displayed as Section {current_section + 1})")
                st.write(f"**Section key:** {section_key}")
                st.write(f"**All checked answers:** {list(st.session_state.get('checked_answers', {}).keys())}")
                
                # Show expected vs actual
                section_data = course_data[current_section]
                is_pydantic_model = hasattr(section_data, '__dict__') and not hasattr(section_data, 'get')
                if is_pydantic_model:
                    questions = getattr(section_data, "quiz", [])
                else:
                    questions = section_data.get('quiz', section_data.get('questions', []))
                
                if questions:
                    st.write(f"**Expected question keys:**")
                    for i, _ in enumerate(questions):
                        expected_key = f"{section_key}_q_{i}"
                        is_answered = expected_key in st.session_state.get('checked_answers', {})
                        st.write(f"- {expected_key} → {'✅' if is_answered else '❌'}")
        
        if current_section < total_sections - 1:
            if st.button("Next Section ➡️", key="next_section_btn", disabled=not all_answered):
                st.session_state.current_section_index = current_section + 1
                st.query_params.section = str(current_section + 1)
                st.rerun()
        else:
            if st.button("🏁 Finish Course", key="finish_course_btn", disabled=not all_answered):
                st.session_state.course_finished = True
                st.rerun()

def display_course_completion_stats(course_data, course_id):
    """Displays the course completion statistics."""
    
    st.markdown('<div class="course-container">', unsafe_allow_html=True)
    st.markdown('<h1 class="course-title">Course Completed!</h1>', unsafe_allow_html=True)

    # --- Score Percentage ---
    total_questions = count_total_questions(course_data)
    correct_answers = st.session_state.get('current_score', 0)
    score_percentage = (correct_answers / total_questions) * 100 if total_questions > 0 else 0

    if score_percentage >= 95:
        st.balloons()

    # Message based on score
    if score_percentage == 100:
        message = "🎉 Perfect Score! You're a master! 🎉"
    elif score_percentage >= 95:
        message = "🎊 Outstanding! You've nearly perfected it! 🎊"
    elif score_percentage >= 70:
        message = "👍 Great job! You have a solid understanding."
    elif score_percentage >= 40:
        message = "🙂 Good effort. A little more practice will make a big difference."
    else:
        message = "💪 Keep practicing! Every attempt is a step forward."

    # Animation for score
    st.markdown(f"""
    <div class="score-container">
        <h3>Your Score</h3>
        <h2 style="font-size: 3rem;">{score_percentage:.2f}%</h2>
        <p style="font-size: 1.2rem;">{message}</p>
    </div>
    """, unsafe_allow_html=True)

    # --- Memory Strength ---
    if MONGO_AVAILABLE and isinstance(course_id, str) and len(course_id) == 24:
        course_manager = get_course_manager()
        course_doc, _ = course_manager.get_course(course_id)

        if course_doc:
            memory_strength = course_doc.get('memory_strength', 0)
            last_attempt_timestamp = course_doc.get('last_attempt_timestamp')
            
            update_strength = False
            new_strength = memory_strength

            if last_attempt_timestamp is None:
                update_strength = True
                new_strength = 1
            else:
                # Handle timezone issues - ensure both datetimes have the same timezone info
                current_time = datetime.datetime.now(datetime.timezone.utc)
                
                # If last_attempt_timestamp is timezone-naive, make it UTC
                if last_attempt_timestamp.tzinfo is None:
                    last_attempt_timestamp = last_attempt_timestamp.replace(tzinfo=datetime.timezone.utc)
                
                time_since_last_attempt = current_time - last_attempt_timestamp
                if time_since_last_attempt >= datetime.timedelta(hours=24):
                    update_strength = True
                    new_strength = min(memory_strength + 1, 5)
            
            if update_strength:
                time_spent = time.time() - st.session_state.start_time
                course_manager.update_course_memory_strength(course_id, new_strength, time_spent)
                memory_strength = new_strength

            st.markdown("<h3>Memory Strength</h3>", unsafe_allow_html=True)
            lit_icons = "⚡" * memory_strength
            unlit_icons = "⚪" * (5 - memory_strength)
            st.markdown(f"<div style='font-size: 2rem;'>{lit_icons}{unlit_icons}</div>", unsafe_allow_html=True)

            if memory_strength < 5:
                st.info("Re-attempt this course after 24 hours to increase your memory strength!")

    st.markdown('</div>', unsafe_allow_html=True)

    if st.button("Go back to Home"):
        # Use session state to prevent double processing
        if "going_home" not in st.session_state:
            st.session_state["going_home"] = True
            st.session_state.course_finished = False
            for key in list(st.session_state.keys()):
                if key not in ['username', 'course_history', 'logged_in', 'going_home']:
                    del st.session_state[key]
            initialize_session_state()
            st.switch_page("pages/1_🏠_Home.py")

def display_current_section(course_data, course_id):
    """Display the current section content"""
    current_section_index = st.session_state.get('current_section_index', 0)
    
    if current_section_index >= len(course_data):
        st.error("Section not found")
        return
    
    current_section = course_data[current_section_index]
    section_key = f"course_{course_id}_sec_{current_section_index}"
      # Display section title
    # Check if current_section is a Pydantic model (it has __dict__ but no get method)
    is_pydantic_model = hasattr(current_section, '__dict__') and not hasattr(current_section, 'get')
    
    if is_pydantic_model:
        # For Pydantic models, access the attribute directly
        section_title = getattr(current_section, "section_title", f'Section {current_section_index + 1}')
    else:
        # For dictionaries, use get method
        section_title = current_section.get('section_title', current_section.get('section', f'Section {current_section_index + 1}'))
    
    st.markdown(f'<h2 class="section-title">{section_title}</h2>', unsafe_allow_html=True)
    
    # Display section content
    display_section_content(current_section, section_key)

def display_section_content(section_data, section_key):
    """Display section content including explanation and questions"""
    # Check if section_data is a Pydantic model (it has __dict__ but no get method)
    is_pydantic_model = hasattr(section_data, '__dict__') and not hasattr(section_data, 'get')
    
    if is_pydantic_model:
        # For Pydantic models, access the attribute directly
        explanation = getattr(section_data, "explanation", "")
        questions = getattr(section_data, "quiz", [])
        subsections = getattr(section_data, "subsections", [])
    else:
        # For dictionaries, use get method
        explanation = section_data.get('explanation', '')
        questions = section_data.get('quiz', section_data.get('questions', []))
        subsections = section_data.get('subsections', [])
    
    # Display explanation
    if explanation:
        st.markdown(f"**{explanation}**")
    
    # Display questions
    if questions:
        st.markdown("---")
        for idx, question_item in enumerate(questions):
            display_question(question_item, section_key, idx)
    
    # Display subsections if they exist
    if subsections:
        for sub_idx, subsection in enumerate(subsections):
            subsection_key = f"{section_key}_sub_{sub_idx}"
            
            # Check if subsection is a Pydantic model
            is_sub_pydantic_model = hasattr(subsection, '__dict__') and not hasattr(subsection, 'get')
            
            if is_sub_pydantic_model:
                # For Pydantic models, access the attribute directly
                sub_title = getattr(subsection, "section_title", f'Subsection {sub_idx + 1}')
            else:
                # For dictionaries, use get method
                sub_title = subsection.get('section_title', subsection.get('section', f'Subsection {sub_idx + 1}'))
            
            st.markdown(f"### {sub_title}")
            
            # Display subsection content recursively
            display_section_content(subsection, subsection_key)

def display_question(question_item, section_key, question_idx):
    """Display a single question using the proper logic from frontend.py"""
    import re  # Import for this function only
    # Check if question_item is a Pydantic model
    is_pydantic_model = hasattr(question_item, '__dict__') and not hasattr(question_item, 'get')
    
    if is_pydantic_model:
        # For Pydantic models, access attributes directly
        question_type = getattr(question_item, "type", "unknown").lower()
        question_text_full = getattr(question_item, "question", "No question text provided.")
        # Try both 'choices' and 'options' for flexibility
        choices = getattr(question_item, "choices", None) or getattr(question_item, "options", None)
        answer = getattr(question_item, "answer", None)
    else:
        # For dictionaries, use get method
        question_type = question_item.get("type", "unknown").lower()
        question_text_full = question_item.get("question", "No question text provided.")
        # Try both 'choices' and 'options' for flexibility
        choices = question_item.get('choices', None) or question_item.get('options', None)
        answer = question_item.get('answer', None)
    
    question_key = f"{section_key}_q_{question_idx}"
    is_answered = st.session_state.checked_answers.get(question_key, False)    # Store question text in session state for AI validation
    st.session_state[f"{question_key}_question"] = question_text_full

    # Only display the question text here if it's NOT a fill-in-the-blank handled by the custom component
    if question_type not in ["fill_in_the_blank", "fill in the blank"]:
        st.markdown(f"**{question_idx+1}. ({question_type.replace('_', ' ').title()})**: {question_text_full}")
    elif question_type in ["fill_in_the_blank", "fill in the blank"]:
        # For fill-in-the-blank, we still want the question number and type, but not the text itself here.
        st.markdown(f"**{question_idx+1}. ({question_type.replace('_', ' ').title()})**:")

    if question_type in ["multiple_choice", "multiple choice"]:
        options = choices  # Use the already extracted choices
        
        # Debug information (can be removed in production)
        if options is None:
            st.warning(f"Debug: Multiple choice question has options=None. Question data: {dict(question_item) if hasattr(question_item, 'items') else 'Pydantic model'}")
        
        if options is not None:
            if not options:
                st.error("Multiple choice question has no options provided.")
                return
            st.radio(
                "Your choice:", options, 
                key=question_key, 
                label_visibility="collapsed",
                on_change=handle_answer_submission,
                args=(question_key, answer, question_type, None),
                disabled=is_answered,
                index=None
            )
        else:
            st.warning(f"Multiple choice question '{question_text_full}': No options provided.")
            
    elif question_type in ["fill_in_the_blank", "fill in the blank"]:
        # For fill-in-the-blank, we need the full question text and the answer to blank out
        correct_answer_for_blank = str(answer) if answer is not None else ""
        component_instance_key = f"fitb_{question_key}" # Key for the custom component's state        # Store question text in session state for AI validation (if applicable, though not used by FITB directly)
        st.session_state[f"{question_key}_question"] = question_text_full
        
        # Display question number only (not type for fill-in-the-blank to avoid duplication)
        st.markdown(f"**{question_idx+1}.**")
        
        if not question_text_full or not correct_answer_for_blank:
            st.warning(f"Fill in the blank question (key: {question_key}) is missing full text or the correct answer. Using standard input.")
            # Fallback to standard text input, which uses question_key for its state
            st.text_input("Your answer:",
                          key=question_key,
                          on_change=handle_answer_submission,
                          args=(question_key, correct_answer_for_blank, question_type, None),
                          disabled=is_answered
                          )
        # Check if the question_text_full contains underscores (e.g., '___')
        elif not re.search(r'_{3,}', question_text_full):
            st.warning(f"Question text for fill-in-the-blank (key: {question_key}) does not contain '___'. Using standard input. Question: '{question_text_full}'")
            # Fallback to standard text input
            st.text_input("Your answer:",
                          key=question_key,
                          on_change=handle_answer_submission,
                          args=(question_key, correct_answer_for_blank, question_type, None),
                          disabled=is_answered
                          )
        else:
            # Use the custom component
            # Initialize component's specific state if not present
            if component_instance_key not in st.session_state:
                st.session_state[component_instance_key] = ""

            # Initialize session state variables if not present
            if "answers" not in st.session_state:
                st.session_state.answers = {}
            if "feedback" not in st.session_state:
                st.session_state.feedback = {}            # Check if this question has been answered correctly
            answer_data = st.session_state.answers.get(question_key, {})
            is_correct = answer_data.get("is_correct", False)
            is_answered = bool(answer_data)  # True if question has been answered (correctly or incorrectly)
              # Process the answer to ensure it's a string
            correct_answer_for_component = answer
            if isinstance(answer, list) and len(answer) > 0:
                correct_answer_for_component = str(answer[0])
            else:
                correct_answer_for_component = str(answer)
              # Add debug output for component data
            # Process the answer to ensure it's a string
            user_input = None
            component_error = None            
            
            if not FILL_IN_BLANKS_AVAILABLE or fill_in_the_blanks_input is None:
                st.info("🔄 Fill-in-the-blanks component not available - using fallback text input")
                # Fallback to standard text input
                fallback_key = f"{component_instance_key}_fallback"
                user_input = st.text_input(
                    f"Fill in the blank: {question_text_full.replace('___', '_____')}",
                    key=fallback_key,
                    disabled=is_answered,
                    help=f"Correct answer: {correct_answer_for_component}" if is_answered else None
                )
            else:
                try:
                    user_input = fill_in_the_blanks_input(
                        question_text_full=question_text_full, 
                        correctAnswer=correct_answer_for_component,
                        key=component_instance_key,
                        disabled=is_answered  # Disable input if question has been answered
                    )
                except (ImportError, ModuleNotFoundError, AttributeError, TypeError) as e:
                    component_error = str(e)
                    st.error(f"❌ Fill-in-the-blanks component error: {component_error}")
                    st.info("🔄 Using fallback text input")
                    # Fallback to standard text input
                    fallback_key = f"{component_instance_key}_fallback"
                    user_input = st.text_input(
                        f"Fill in the blank: {question_text_full.replace('___', '_____')}",
                        key=fallback_key,
                        disabled=is_answered,
                        help=f"Correct answer: {correct_answer_for_component}" if is_answered else None
                    )
              # Handle both string input and object input (for enhanced component behavior)
            current_answer = ""
            is_give_up_action = False
            is_correct_action = False
            # is_wrong_action = False  # Removed unused variable
              # Early exit if question is already answered to prevent infinite loops
            if is_answered:
                # Question already answered, don't process any new input
                current_answer = ""
                action = ""
                is_give_up_action = False
                is_completed_wrong = False
                is_correct_action = False
                # is_wrong_action = False  # Removed unused variable
            elif isinstance(user_input, dict):
                # Handle enhanced component return format
                raw_value = user_input.get("value", "")
                # Handle both string and list values from component
                if isinstance(raw_value, list):
                    current_answer = raw_value[0] if len(raw_value) > 0 else ""
                else:
                    current_answer = str(raw_value)
                
                action = user_input.get("action", "")
                component_says_correct = user_input.get("isCorrect", False)
                is_give_up_action = action == "give_up"
                is_completed_wrong = action == "question_complete" and not component_says_correct
                is_correct_action = (action == "correct_answer" or action == "question_complete") and component_says_correct
                # Note: isWrong flag is available but not used in current logic
                
                # Debug info
                # if action:  # Only show if there's an action
                #     st.write(f"🔍 Debug: Action={action}, Raw Value={raw_value}, Answer='{current_answer}', Correct={user_input.get('isCorrect', False)}")
            elif isinstance(user_input, str):
                # Fallback for standard text input or when component returns string
                current_answer = user_input
                action = ""
                is_give_up_action = False
                is_completed_wrong = False
                is_correct_action = False
                is_wrong_action = False
            elif user_input is None:
                current_answer = ""
                action = ""
                is_give_up_action = False
                is_completed_wrong = False
                is_correct_action = False
                is_wrong_action = False
            else:
                st.warning(f"⚠️ Unexpected input type: {type(user_input)}, value: {user_input}")
                current_answer = str(user_input) if user_input is not None else ""
                action = ""
                is_give_up_action = False
                is_completed_wrong = False
                is_correct_action = False
                is_wrong_action = False
            
            # Real-time checking as user types or on specific actions
            if current_answer is not None and isinstance(current_answer, str):
                current_answer = current_answer.strip()
                
                # Handle answer format - extract from list if needed
                correct_answer_str = answer
                if isinstance(answer, list) and len(answer) > 0:
                    correct_answer_str = str(answer[0])  # Take first element if it's a list                else:
                    correct_answer_str = str(answer)
                
                answer_matches = False
                if isinstance(current_answer, str) and isinstance(correct_answer_str, str):
                    answer_matches = current_answer.lower() == correct_answer_str.lower()
                
                # Only process specific component actions to avoid infinite loops
                should_process = (isinstance(user_input, dict) and 
                                action in ["give_up", "correct_answer", "question_complete"]) or isinstance(user_input, str)
                
                # If answer is correct and not already processed
                if should_process and (answer_matches or is_correct_action) and not is_correct:
                    # Mark as correct
                    if "answers" not in st.session_state:
                        st.session_state.answers = {}
                    if "feedback" not in st.session_state:
                        st.session_state.feedback = {}
                    
                    st.session_state.answers[question_key] = {
                        "user_answer": current_answer,
                        "is_correct": True,
                        "question_type": question_type
                    }
                    st.session_state.feedback[question_key] = "Correct! 🎉"
                    st.session_state.fitb_answered = True
                    
                    # IMPORTANT: Also mark in checked_answers for navigation system
                    st.session_state.checked_answers[question_key] = True
                    st.session_state.user_answers[question_key] = current_answer
                    
                    # Update score tracking
                    if question_key not in st.session_state.scored_correctly_keys:
                        st.session_state.current_score += 1
                        st.session_state.scored_correctly_keys.add(question_key)
                    
                      # Also update the local is_correct variable for immediate UI update
                    is_correct = True
                    st.rerun()  # Immediate rerun for correct answers to update UI                # Handle give up action or completed wrong answer
                elif should_process and (is_give_up_action or is_completed_wrong) and not is_correct:
                    if "answers" not in st.session_state:
                        st.session_state.answers = {}
                    if "feedback" not in st.session_state:
                        st.session_state.feedback = {}
                    
                    st.session_state.answers[question_key] = {
                        "user_answer": current_answer,
                        "is_correct": False,
                        "question_type": question_type
                    }
                    st.session_state.feedback[question_key] = f"The correct answer is: {answer}"
                    st.session_state.fitb_answered = True
                    
                    # IMPORTANT: Also mark in checked_answers for navigation system
                    st.session_state.checked_answers[question_key] = True
                    st.session_state.user_answers[question_key] = current_answer
                    
                    st.rerun()  # Rerun to update UI and disable component              # Display feedback for fill-in-the-blank questions
            answer_data = st.session_state.answers.get(question_key, {})
            if answer_data:  # If there's any answer data (correct or incorrectly)
                feedback_text = st.session_state.feedback.get(question_key)
                if feedback_text:
                    # Mark that feedback has been displayed for this question to prevent duplicate display
                    feedback_displayed_key = f"{question_key}_feedback_displayed"
                    if feedback_displayed_key not in st.session_state:
                        st.session_state[feedback_displayed_key] = True
                        if "Correct!" in feedback_text:
                            st.success(f"✅ {feedback_text}")
                        else:
                            st.error(f"❌ {feedback_text}")
    
    elif question_type == "match":
        # Get the matching items from the question's answer
        match_data = answer  # Use the already extracted answer
        
        # Convert to dictionary format if it's an array of objects with "premise" and "response" fields
        match_dict = {}
        if isinstance(match_data, list):
            try:
                # Handle array format with objects that have premise/response fields
                for item in match_data:
                    if isinstance(item, dict):
                        # Direct premise/response format
                        if "premise" in item and "response" in item:
                            match_dict[item["premise"]] = item["response"]
                        # Indexed format like [0:{...}, 1:{...}]
                        elif len(item) == 1 and isinstance(list(item.values())[0], dict):
                            inner_item = list(item.values())[0]
                            if "premise" in inner_item and "response" in inner_item:
                                match_dict[inner_item["premise"]] = inner_item["response"]
                
                # If we successfully converted at least one item, use the dictionary
                if match_dict:
                    match_data = match_dict
                    st.success("Successfully converted match data format.")
            except Exception as e:
                st.error(f"Error processing match data: {e}")
                st.json(match_data)  # Show the problematic data
        
        # If match_data is still not a dict, try to parse it as JSON string or fix formatting issues
        elif not isinstance(match_data, dict):
            if isinstance(match_data, str):
                # Try to parse as JSON string
                fixed_data = fix_json_format(match_data)
                if fixed_data:
                    match_data = fixed_data
                    st.success("Successfully fixed JSON formatting in match question.")
                else:
                    # Try to parse as standard JSON first
                    try:
                        match_data = json.loads(match_data)
                        st.success("Successfully parsed JSON string.")
                    except json.JSONDecodeError:
                        st.error(f"Could not parse match data as JSON: {match_data}")
            else:
                # Convert to string and try to fix
                data_str = str(match_data)
                fixed_data = fix_json_format(data_str)
                if fixed_data:
                    match_data = fixed_data
                    st.success("Successfully parsed match question data.")
                else:
                    # Try to parse as standard JSON first
                    try:
                        match_data = json.loads(data_str)
                        st.success("Successfully parsed match question data.")
                    except json.JSONDecodeError:
                        # Show more detailed error information
                        raw_data_str = str(match_data)
                        if '"' in raw_data_str and '":' in raw_data_str and '","' not in raw_data_str and '}' in raw_data_str:
                            st.error("""
                            **JSON Formatting Error Detected in Match Question!**
                            
                            The match question answer appears to be missing commas between key-value pairs.
                            
                            **Expected format:** `{"key1": "value1", "key2": "value2", "key3": "value3"}`
                            
                            **Current format appears to be:** Missing commas like `{"key1": "value1" "key2": "value2"}`
                            
                            This has been automatically detected and should be handled, but parsing failed.
                            Please try regenerating the course content.
                            """)
                        else:
                            st.warning("Matching question data is not in the expected format. Expected a dictionary of left-right pairs.")
                        # Show the problematic data for debugging
                        st.json(match_data)
                        # Now proceed with match question processing if we have a valid dictionary
        
        # Check if we have a proper match format (dictionary mapping left items to right items)
        if isinstance(match_data, dict) and match_data:
            left_items = list(match_data.keys())
            right_items = list(match_data.values())
            
            # Shuffle the right items to make it more challenging
            # We'll use a fixed seed based on the question key to ensure
            # the order is consistent on reruns but different for each question
            r = random.Random(question_key)
            shuffled_right = right_items.copy()
            r.shuffle(shuffled_right)
            
            # Create a container for the matching UI
            match_container = st.container()
            
            # Initialize user's matches in session state if not already done
            match_answers_key = f"{question_key}_matches"
            if match_answers_key not in st.session_state:
                st.session_state[match_answers_key] = {}
            
            with match_container:
                st.write("Match the items on the left with the correct items on the right:")
                
                # Create two columns for left and right items
                left_col, right_col = st.columns(2)
                
                with left_col:
                    for i, item in enumerate(left_items):
                        st.markdown(f"**{i+1}.** {item}")
                
                with right_col:
                    # Display shuffled right items as labels for the dropdowns
                    # This part is mostly for visual reference if needed, actual matching is via dropdowns
                    pass # Not strictly needed to list them again if dropdowns show options
                
                # Create dropdowns for matching
                user_matches_for_ui = {} # To store selections from dropdowns in the current render
                for i, left_item in enumerate(left_items):
                    # Use a unique key for each dropdown based on left_item and question_key
                    # to preserve its state across reruns if not submitted.
                    dropdown_key = f"match_select_{question_key}_{i}"
                    
                    # Get the current selection for this dropdown from session state (user's ongoing attempt)
                    current_selection_for_left_item = st.session_state[match_answers_key].get(left_item)

                    selected_right_item = st.selectbox(
                        f"Match for '{left_item}'",
                        options=[""] + shuffled_right,  # Add a blank option
                        index=(shuffled_right.index(current_selection_for_left_item) + 1) if current_selection_for_left_item and current_selection_for_left_item in shuffled_right else 0,
                        key=dropdown_key,
                        label_visibility="collapsed",
                        disabled=is_answered 
                    )
                    if selected_right_item: # Only add to matches if something is selected
                        user_matches_for_ui[left_item] = selected_right_item
                
                # Update session state with current selections from UI
                # This happens on every rerun if a dropdown changes
                st.session_state[match_answers_key] = user_matches_for_ui
                
                # Submit button for matching questions
                # The button is active if not answered and all left items have a selection.
                # We check user_matches_for_ui which reflects the current state of dropdowns.
                all_items_matched_in_ui = len(user_matches_for_ui) == len(left_items)

                if not is_answered and all_items_matched_in_ui:
                    if st.button("Submit Matches", key=f"submit_match_{question_key}"):
                        # On button click, the user_matches_for_ui (from current dropdowns)
                        # has already been stored in st.session_state[match_answers_key].
                        # We use that value from session_state for submission.
                        user_selections_to_submit = st.session_state.get(match_answers_key, {})
                        st.session_state[question_key] = json.dumps(user_selections_to_submit)
                        # Ensure match_data (correct answers) is a dict before dumping and handling submission
                        if isinstance(correct_answer, dict):
                            correct_answer_json = json.dumps(correct_answer)
                            handle_answer_submission(question_key, correct_answer_json, "match", None)
                        else:
                            st.error("Internal error: Correct answer data for matching is not in the expected dictionary format.")
                            st.session_state.checked_answers[question_key] = True
                            st.session_state.user_answers[question_key] = json.dumps(user_selections_to_submit)
                            st.session_state.feedback[question_key] = "Error: Could not process the correct answer data."
                        
                        # Use a flag instead of immediate rerun for performance
                        st.session_state.match_submitted = True
                elif not is_answered:
                    # If not all items are matched, show a disabled-like message or a disabled button
                    # For simplicity, we can just not show the button or show it disabled.
                    # Here, if all_items_matched_in_ui is false, the button above is not rendered.
                    # We can add a placeholder or a disabled button if desired.                    st.button("Submit Matches", key=f"submit_match_{question_key}_disabled", disabled=True)
                    if not all_items_matched_in_ui and len(left_items) > 0 : # only show if there are items to match
                        st.caption("Please select a match for all items on the left.")

        else:
            # This block handles cases where match_data was not a dictionary initially.
            # Try one more time to fix the JSON format before giving up
            if not isinstance(match_data, dict):
                # Final attempt with more aggressive parsing
                # st.warning("Matching question data is malformed. Attempting to fix...") # Optional warning
                fixed_match_data = None
                if isinstance(match_data, str):
                    fixed_match_data = fix_json_format(match_data)
                
                if isinstance(fixed_match_data, dict) and fixed_match_data:
                    # If fixed, we could try to re-render the match UI, but that's complex.
                    # For now, just log that it was fixed and fall back.
                    # st.info("Successfully parsed malformed match data, but UI fell back to text input for this attempt.")
                    pass # Fall through to text area

            # Fallback to text area for malformed match questions or if fixing failed
            st.error("Unable to display matching question due to data format issues. Please answer as a JSON string or contact support.")
            st.text_area("Your answer (as JSON, e.g., {\\\"premise1\\\": \\\"responseA\\\", ...}):",
                        key=question_key,
                        on_change=handle_answer_submission,
                        args=(question_key, answer, question_type, None), # answer here is the original, possibly malformed, answer
                        disabled=is_answered
                        )
    
    elif question_type in ["short_answer", "short answer"]:
        st.text_area("Your answer:",
                    key=question_key,
                    on_change=handle_answer_submission,
                    args=(question_key, answer, question_type, None),
                    disabled=is_answered
                    )
    elif question_type in ["true_false", "true false", "true or false"]:
        tf_options = ["True", "False"]
        st.radio("Your choice:", tf_options,
                 key=question_key,
                 label_visibility="collapsed",
                 on_change=handle_answer_submission,
                 args=(question_key, answer, question_type, None),
                 disabled=is_answered
                 )      # Display feedback if answered
    if is_answered: # This relies on checked_answers[question_key] being True
        # Check if feedback has already been displayed (e.g., by fill-in-the-blank component)
        feedback_displayed_key = f"{question_key}_feedback_displayed"
        if feedback_displayed_key not in st.session_state:
            feedback_text = st.session_state.feedback.get(question_key)
            if feedback_text: # Check if feedback text exists and is not empty
                if "Correct!" in feedback_text:
                    st.success(f"✅ {feedback_text}")
                elif feedback_text.startswith("Incorrect."):
                    # Extract the part after "Incorrect. " to check for errors vs. partial scores
                    detailed_feedback = feedback_text[len("Incorrect. "):]
                    if any(err_keyword in detailed_feedback.lower() for err_keyword in ["error", "unexpected", "invalid", "malformed"]):
                        st.error(f"❌ {feedback_text}") # e.g., "Incorrect. Error: Malformed data."
                    else:
                        # For partial scores or simple incorrect messages without specific error keywords
                        st.info(f"ℹ️ {feedback_text}") # e.g., "Incorrect. You matched 2 out of 3." or "Incorrect. Your answer: X, Correct answer: Y"
                elif any(err_keyword in feedback_text.lower() for err_keyword in ["error", "unexpected", "invalid", "malformed"]):
                    # For direct error messages not prepended with "Incorrect."
                    st.error(f"❌ {feedback_text}")
                else:
                    # Fallback for any other non-empty feedback, treat as informational
                    # This could catch custom feedback messages that don't fit the patterns above
                    st.info(f"ℹ️ {feedback_text}")
        # else: No feedback message was found in session state for this question_key.
        # If is_answered is True but feedback_text is None or empty, nothing will be shown here.
        # This would be a state inconsistency if it occurs.

def fix_json_format(data_str):
    """
    Fix common JSON formatting issues in match question data, specifically missing commas.
    
    Args:
        data_str (str): String representation of JSON-like data
        
    Returns:
        dict or None: Parsed dictionary if successful, None if failed
    """
    import re  # Import for this function only
    try:
        # First try normal JSON parsing
        return json.loads(data_str)
    except json.JSONDecodeError:
        try:
            # Clean up the string for common issues
            cleaned = str(data_str).strip()
            
            # Handle case 1: Remove any trailing commas before closing braces/brackets
            cleaned = re.sub(r',\s*}', '}', cleaned)
            cleaned = re.sub(r',\s*]', ']', cleaned)
            
            # Handle case 2: Missing opening/closing braces
            if not cleaned.startswith('{'):
                cleaned = '{' + cleaned
            if not cleaned.endswith('}'):
                cleaned = cleaned + '}'
            
            # Handle case 3: Missing commas between key-value pairs
            # Pattern for "value" followed directly by whitespace/newline and then "key":
            cleaned = re.sub(r'("\s*)\s*\n?\s*"([^"]+)":', r'\1, "\2":', cleaned)
            
            # Also handle cases where there's no space: "value""key":
            cleaned = re.sub(r'(")\s*"([^"]+)":', r'\1, "\2":', cleaned)
            
            # Handle case 4: Missing commas after closing quotes
            # Look for }" followed by "key without comma
            cleaned = re.sub(r'"\s*\n?\s*"([^"]+)":', r'", "\1":', cleaned)
            
            # Clean up any double commas that might have been created
            cleaned = re.sub(r',\s*,', ',', cleaned)
            
            # Remove any leading comma that might have been added after opening brace
            cleaned = re.sub(r'{\s*,', '{', cleaned)
            
            # Try parsing the fixed JSON
            result = json.loads(cleaned)
            return result
            
        except (json.JSONDecodeError, ValueError, TypeError):
            # If regex approach fails, try manual key-value extraction
            try:
                # Extract key-value pairs using a more robust approach
                # First try to handle the Key='Value' format specifically
                pattern_single_quotes = r"([A-Za-z0-9\s]+)='([^']*)'"
                matches = re.findall(pattern_single_quotes, str(data_str))
                
                if matches:
                    result_dict = {}
                    for key, value in matches:
                        # Clean up the key by removing extra whitespace
                        key = key.strip()
                        result_dict[key] = value
                    return result_dict
                
                # Pattern to match key-value pairs with various spacing and line breaks
                # This pattern looks for "key":"value" patterns regardless of spacing
                pattern = r'"([^"]+)"\s*:\s*"([^"]*)"'
                matches = re.findall(pattern, str(data_str))
                
                if matches:
                    result_dict = {}
                    for key, value in matches:
                        result_dict[key] = value
                    return result_dict
                
                # Try alternative pattern for unquoted values
                pattern2 = r'"([^"]+)"\s*:\s*([^"{}]+?)(?=\s*(?:"[^"]*"\s*:|}))'
                matches2 = re.findall(pattern2, str(data_str))
                
                if matches2:
                    result_dict = {}
                    for key, value in matches2:
                        # Clean up the value by removing extra whitespace and quotes
                        value = value.strip().strip('"').strip()
                        result_dict[key] = value
                    return result_dict
                
            except (json.JSONDecodeError, ValueError, TypeError):
                pass    
    return None

def handle_answer_submission(question_key, correct_answer, question_type, selected_match_key=None, submitted_answer=None):
    # Initialize session state for answer tracking if not already present
    if "answers" not in st.session_state:
        st.session_state.answers = {}
      # For fill-in-the-blank, skip this function as it's handled by dedicated component logic
    if question_type == "fill_in_the_blank":
        return # Let the custom component handle all fill-in-the-blank logic# For other question types, proceed with existing logic
    user_answer = st.session_state.get(question_key)
    
    if user_answer is None: 
        # If it's a new question, it might be None if not initialized by the input element yet.
        # For fill-in-the-blank custom component, it's initialized to "".
        # For standard inputs, if not touched, it might be None.
        # Let's allow submission to proceed; empty/None answers will be marked by is_answer_correct.
        pass # Allow None to be processed by is_answer_correct, which handles str(user_answer)

    # For match questions, check if a blank/placeholder option was selected
    # Match questions use "" as placeholder in dropdowns
    if question_type == "match" and user_answer and isinstance(user_answer, str):
        try:
            # Parse the user answer JSON to check for empty selections
            user_selections = json.loads(user_answer)
            if isinstance(user_selections, dict):
                # Check if any selection is empty (placeholder)
                for _left_item, right_selection in user_selections.items():
                    if not right_selection or right_selection == "":
                        return  # Don't process submission if placeholder is selected
        except (json.JSONDecodeError, TypeError):
            pass  # Continue with normal processing if JSON parsing fails

    st.session_state.checked_answers[question_key] = True 
    st.session_state.user_answers[question_key] = user_answer

    is_correct_locally = False
    feedback_message = ""

    if question_type in ["true_false", "true false", "true or false"]:
        correct_answer_bool = str(correct_answer).lower() == "true"
        user_answer_bool = str(user_answer).lower() == "true"
        if user_answer_bool == correct_answer_bool:
            is_correct_locally = True
        feedback_message = f"Your answer: {user_answer}, Correct answer: {correct_answer}"

    # AI-powered validation for short answer questions
    elif question_type in ["short_answer", "short answer"]:
        if user_answer is None: # Explicitly handle None for short answer if it makes sense
            user_answer = "" # Or handle as an error/incomplete submission
        # First try AI validation
        try:
            # Get the original question text from session state
            question_text = st.session_state.get(f"{question_key}_question", "")
            
            # Use AI validation if available
            if local_backend is not None:
                ai_result, ai_explanation = local_backend.validate_short_answer_with_ai(
                    question_text, user_answer, correct_answer
                )
                
                if ai_result is not None: # AI validation was successful               
                    is_correct_locally = ai_result
                    feedback_message = ai_explanation # AI explanation is the full feedback
                else: # AI validation failed or returned None, fallback to simple check               
                    is_correct_locally = is_answer_correct(user_answer, correct_answer, question_type)
                    display_answer = correct_answer[0] if isinstance(correct_answer, list) else correct_answer
                    if is_correct_locally:
                        feedback_message = f"Correct! Your answer: {user_answer}, Expected: {display_answer}. (AI validation was skipped)"
                    else:
                        feedback_message = f"Your answer: {user_answer}, Expected: {display_answer}. (AI validation was skipped)"
            else:
                # Local backend not available, use simple validation
                is_correct_locally = is_answer_correct(user_answer, correct_answer, question_type)
                display_answer = correct_answer[0] if isinstance(correct_answer, list) else correct_answer
                if is_correct_locally:
                    feedback_message = f"Correct! Your answer: {user_answer}, Expected: {display_answer} (AI validation unavailable)"
                else:
                    feedback_message = f"Your answer: {user_answer}, Expected: {display_answer} (AI validation unavailable)"
                
        except Exception as e:
            # Fallback to simple string comparison if AI validation fails
            is_correct_locally = is_answer_correct(user_answer, correct_answer, question_type)
            display_answer = correct_answer[0] if isinstance(correct_answer, list) else correct_answer
            if is_correct_locally:
                feedback_message = f"Correct! Your answer: {user_answer}, Expected: {display_answer} (AI validation error: {str(e)})"
            else:
                feedback_message = f"Your answer: {user_answer}, Expected: {display_answer} (AI validation error: {str(e)})"

    # For match questions, we have JSON strings representing dictionaries
    elif question_type == "match":
        if isinstance(user_answer, str): # Ensure user_answer is a string before json.loads
            try:
                # user_answer is st.session_state.get(question_key), a JSON string of user's matches.
                # correct_answer is a JSON string of the correct matches, passed from display_question.
                user_matches_dict = json.loads(user_answer)
                correct_matches_dict = json.loads(correct_answer) # Assuming correct_answer is always a valid JSON string here

                # Validate that both parsed objects are dictionaries
                if not isinstance(user_matches_dict, dict) or not isinstance(correct_matches_dict, dict):
                    is_correct_locally = False
                    feedback_message = "Error: Match data is not in the expected dictionary format after parsing."
                else:
                    # Compare the dictionaries for logical equality
                    is_correct_locally = (user_matches_dict == correct_matches_dict)
                    
                    # Calculate partial score for feedback message
                    correct_count = 0
                    # Iterate through the keys in the user's submitted matches
                    for item_key in user_matches_dict:
                        # Check if the item exists in correct answers and if the user's match for it is correct
                        if item_key in correct_matches_dict and user_matches_dict[item_key] == correct_matches_dict[item_key]:
                            correct_count += 1
                
                total_items_to_match = len(correct_matches_dict) # Total number of items that should be matched

                if is_correct_locally:
                    feedback_message = f"Correct! You matched all {total_items_to_match} items."
                else:
                    if total_items_to_match > 0:
                        feedback_message = f"You matched {correct_count} out of {total_items_to_match} items correctly."
                    else: # Should not happen with well-formed question data
                        feedback_message = "Could not determine the number of items to match, or there were no items to match."
            
            except json.JSONDecodeError:
                is_correct_locally = False
                feedback_message = "Error processing your selections: the answer format was unexpected. Please ensure your selections are valid."
            except Exception as e: # Catch any other unexpected error during match processing
                is_correct_locally = False
                feedback_message = f"An unexpected error occurred while checking your match answer: {str(e)}"
        else:
            # Handle cases where user_answer is None or not a string (e.g. if not answered)
            is_correct_locally = False
            feedback_message = "No answer submitted or answer is in an invalid format for matching."

    # For other text-based answers (multiple_choice, fill_in_the_blank)
    elif is_answer_correct(user_answer, correct_answer, question_type):
        is_correct_locally = True
        # Display first acceptable answer if multiple exist
        display_answer = correct_answer[0] if isinstance(correct_answer, list) else correct_answer
        feedback_message = f"Your answer: {user_answer}, Correct answer: {display_answer}"
    else: # Default case for incorrect non-boolean, non-short-answer
        is_correct_locally = False # Ensure this is set if not already by other branches
        # Display first acceptable answer if multiple exist
        display_answer = correct_answer[0] if isinstance(correct_answer, list) else correct_answer
        feedback_message = f"Your answer: {user_answer}, Correct answer: {display_answer}"

    if is_correct_locally:
        # For "match" and "short_answer" (with AI), feedback_message is already the complete success message.
        # For "true_false", and other types like MC/FITB, we might want to prepend "Correct!" if not already there.
        if question_type == "match":
            st.session_state.feedback[question_key] = feedback_message # e.g., "Correct! You matched all X items."
        elif question_type in ["short_answer", "short answer"] and feedback_message:
            # Assuming ai_explanation (feedback_message) is a full sentence like "Correct, because..." or "That's right..."
            st.session_state.feedback[question_key] = feedback_message
        elif question_type in ["true_false", "true false", "true or false"] and feedback_message:
            # feedback_message for TF correct is "Your answer: X, Correct answer: X"
            st.session_state.feedback[question_key] = f"Correct! {feedback_message}"
        else: # Default for MC, FITB if correct (feedback_message is "Your answer: X, Correct: X")
            st.session_state.feedback[question_key] = f"Correct! {feedback_message}"
        
        if question_key not in st.session_state.scored_correctly_keys:
            st.session_state.current_score += 1
            st.session_state.scored_correctly_keys.add(question_key)
    else:
        # For incorrect answers, feedback_message should contain the reason/details.
        # Prepend "Incorrect." to this detailed message.
        st.session_state.feedback[question_key] = f"Incorrect. {feedback_message}"

def is_answer_correct(user_answer, correct_answer, question_type=None):
    """Check if user answer matches any acceptable answer"""
    user_clean = str(user_answer).strip().lower()
    
    # Handle multiple acceptable answers
    if isinstance(correct_answer, list):
        acceptable_answers = [str(ans).strip().lower() for ans in correct_answer]
        return user_clean in acceptable_answers
    else:
        # Single answer (backward compatibility)
        return user_clean == str(correct_answer).strip().lower()

if __name__ == "__main__":
    main()
