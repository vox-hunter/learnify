"""
Test script to verify the loading animation works correctly.
Run this to test the loading animation independently.
"""

import streamlit as st
import time
from loading_animation import inject_loading_screen, show_loading_status, hide_loading_screen

st.set_page_config(
    page_title="Loading Animation Test",
    page_icon="🧠",
    layout="wide"
)

# Inject loading screen immediately
inject_loading_screen()

# Simulate loading steps
if 'test_started' not in st.session_state:
    st.session_state.test_started = True
    
    # Simulate various loading steps
    show_loading_status("Initializing test...", 10)
    time.sleep(0.5)
    
    show_loading_status("Loading components...", 30)
    time.sleep(0.5)
    
    show_loading_status("Setting up authentication...", 60)
    time.sleep(0.5)
    
    show_loading_status("Finalizing interface...", 90)
    time.sleep(0.5)
    
    show_loading_status("Ready!", 100)
    time.sleep(1)

# Main app content
st.title("🧠 AI Loom - Loading Test")
st.success("Loading animation test completed!")

st.markdown("""
### Loading Animation Features:
- ✅ Beautiful gradient background with AI Loom branding
- ✅ Animated spinner with purple glow effect
- ✅ Floating particles animation
- ✅ Progress bar with loading steps
- ✅ Status messages that update during loading
- ✅ Smooth fade-out transition
- ✅ Automatic detection of when Streamlit is ready

### How it works:
1. The loading screen appears immediately when the page loads
2. It shows various loading stages with progress updates
3. It automatically detects when Streamlit components are ready
4. It fades out smoothly after a minimum display time
5. The main app content appears with a smooth transition

This loading system is perfect for your Render deployment as it will keep users engaged while your app loads all components, authentication, and resources.
""")

if st.button("Test Loading Again"):
    st.session_state.clear()
    st.rerun()
