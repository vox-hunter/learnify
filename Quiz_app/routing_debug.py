"""
Debug helper for routing functionality
Add ?debug_routing=true to URL to see routing information
"""

import streamlit as st

def show_routing_debug():
    """Display routing debug information"""
    if st.query_params.get('debug_routing') == 'true':
        st.sidebar.markdown("---")
        st.sidebar.subheader("🔧 Routing Debug")
        
        # Current URL info
        st.sidebar.write("**Current URL:**")
        st.sidebar.code(f"Path: {st.context.headers.get('x-forwarded-uri', 'N/A')}")
        
        # Query parameters
        st.sidebar.write("**Query Parameters:**")
        for key, value in st.query_params.items():
            st.sidebar.code(f"{key}: {value}")
        
        # Navigation pages
        st.sidebar.write("**Available Routes:**")
        routes = ["/privacy", "/terms", "/course", "/login"]
        for route in routes:
            st.sidebar.code(route)
        
        # Test links
        st.sidebar.write("**Test Direct Access:**")
        base_url = "http://localhost:8501"  # Update for production
        for route in routes:
            st.sidebar.markdown(f"[{route}]({base_url}{route})")
        
        # Instructions
        st.sidebar.info("""
        **Routing Test Instructions:**
        1. Click internal navigation (should work)
        2. Try direct URL access in new tab
        3. Check if server configuration is needed
        4. Review DEPLOYMENT_GUIDE.md for platform-specific fixes
        """)

# Add this to main.py after navigation setup
if __name__ == "__main__":
    show_routing_debug()