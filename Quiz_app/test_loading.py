"""
Test script for the improved native Streamlit loading animation.
Tests sidebar collapse/expand and loading cleanup functionality.
"""

import streamlit as st
from streamlit_loading import show_streamlit_native_loading, ensure_loading_cleanup

st.set_page_config(
    page_title="Improved Loading Test - Streamlit",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed"  # Start collapsed like main app
)

# Ensure loading UI is cleaned up on this page
ensure_loading_cleanup()

st.title("🧠 AI Loom - Improved Loading Test")

col1, col2 = st.columns(2)

with col1:
    if st.button("▶️ Test Loading Animation", use_container_width=True):
        # Reset loading state
        if 'app_loading_complete' in st.session_state:
            del st.session_state['app_loading_complete']
        show_streamlit_native_loading()

with col2:
    if st.button("🔄 Reset Test", use_container_width=True):
        st.session_state.clear()
        st.rerun()

# Show current sidebar state
sidebar_state = "Expanded" if st.session_state.get('sidebar_should_be_expanded', False) else "Collapsed"
loading_complete = st.session_state.get('app_loading_complete', False)

st.info(f"**Current State**: Loading Complete: {loading_complete} | Sidebar: {sidebar_state}")

st.markdown("""
## ✅ **Improved Native Streamlit Loading System**

### **New Features Added:**

#### 🔧 **1. Automatic Sidebar Management:**
- ✅ **Collapses sidebar** during loading for clean full-screen experience
- ✅ **Expands sidebar** automatically when loading completes  
- ✅ **Maintains sidebar state** across page navigation
- ✅ **Smooth transitions** with CSS animations

#### 🧹 **2. Loading UI Cleanup:**
- ✅ **Removes loading UI** from all pages after completion
- ✅ **Prevents loading artifacts** on page navigation
- ✅ **Session state tracking** to avoid re-showing loading
- ✅ **Clean page transitions** without loading remnants

### **How the improvements work:**

#### **During Loading:**
1. **Sidebar automatically collapses** for immersive loading experience
2. **Main content expands** to full width
3. **Loading animation** shows with progress and status
4. **CSS prevents** sidebar visibility during loading

#### **After Loading:**
1. **Sidebar automatically expands** back to normal state
2. **Loading UI completely removed** from DOM
3. **Session state marked** as loading complete
4. **All pages clean up** any loading artifacts

#### **Page Navigation:**
1. **Each page checks** if loading was already completed
2. **Cleanup function ensures** no loading UI remnants
3. **Sidebar stays expanded** on all subsequent pages
4. **No re-loading** on page switches

### **Perfect for Production:**
- 🎯 **One-time loading**: Only shows on initial app startup
- 🎯 **Clean navigation**: No loading artifacts when switching pages
- 🎯 **Consistent sidebar**: Always properly expanded after loading
- 🎯 **Smooth UX**: Professional transitions and state management

### **Render Deployment Ready:**
- ✅ 100% Streamlit native components
- ✅ No iframe or JavaScript dependencies  
- ✅ Reliable sidebar state management
- ✅ Clean page loading and navigation
- ✅ Works with slow network connections

Your app now provides a **complete loading experience** that starts with a collapsed sidebar for focus, shows clear progress, and then seamlessly transitions to your full app with an expanded sidebar! 🚀
""")

# Add sidebar content for testing
with st.sidebar:
    st.header("Test Sidebar")
    st.write("This sidebar should be:")
    st.write("- **Collapsed** during loading")
    st.write("- **Expanded** after loading completes")
    st.write("- **Clean** on all pages (no loading artifacts)")
    
    if st.button("Test Sidebar Button"):
        st.success("Sidebar is working correctly!")
        
st.markdown("---")
st.markdown("💡 **Test Instructions**: Click 'Test Loading Animation' to see the sidebar collapse, then watch it expand automatically when loading completes!")
