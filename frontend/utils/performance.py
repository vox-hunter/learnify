"""
Performance optimizations for Streamlit app
This module contains functions to improve app performance
"""
import streamlit as st

def inject_performance_optimizations():
    """Inject performance optimizations directly into the Streamlit app"""
    
    # Performance-optimized CSS and JavaScript
    performance_code = """
    <style>
    /* Performance optimizations */
    .stApp {
        /* Improve rendering performance */
        will-change: auto;
        contain: layout style paint;
    }
    
    /* Reduce layout shift */
    .main .block-container {
        min-height: 100vh;
        padding-top: 1rem;
    }
    
    /* Optimize images */
    img {
        loading: lazy;
        decoding: async;
    }
    
    /* Improve font loading */
    body {
        font-display: swap;
    }
    
    /* Reduce unnecessary repaints */
    .stSelectbox > div > div {
        will-change: auto;
    }
    
    /* Loading states */
    .stSpinner > div {
        border-color: #ff6b6b transparent transparent transparent !important;
    }
    
    /* Hide Streamlit menu and footer for better performance */
    #MainMenu {visibility: visible;}
    .stDeployButton {display:none;}
    footer {visibility: hidden;}
    
    /* Optimize metric cards */
    [data-testid="metric-container"] {
        transition: transform 0.2s ease;
    }
    </style>
    
    <!-- Performance optimized Google Analytics -->
    <script>
    (function() {
        // Initialize dataLayer
        window.dataLayer = window.dataLayer || [];
        function gtag(){dataLayer.push(arguments);}
        gtag('js', new Date());
        
        // Configure GA with performance optimizations
        gtag('config', 'G-B30T0B78LK', {
            'send_page_view': false,
            'transport_type': 'beacon',
            'allow_google_signals': false,
            'allow_ad_personalization_signals': false,
            'optimize_id': null
        });
        
        // Load GA script asynchronously after critical resources
        function loadGA() {
            if (document.readyState === 'complete') {
                setTimeout(function() {
                    var script = document.createElement('script');
                    script.async = true;
                    script.src = 'https://www.googletagmanager.com/gtag/js?id=G-B30T0B78LK';
                    script.onload = function() {
                        gtag('config', 'G-B30T0B78LK');
                        gtag('event', 'page_view', {
                            'page_title': document.title,
                            'page_location': window.location.href
                        });
                    };
                    document.head.appendChild(script);
                }, 500); // Delay to ensure critical rendering path is complete
            } else {
                window.addEventListener('load', loadGA);
            }
        }
        
        // Start loading process
        loadGA();
        
        // Performance monitoring
        if ('performance' in window) {
            window.addEventListener('load', function() {
                setTimeout(function() {
                    var navigation = performance.getEntriesByType('navigation')[0];
                    if (navigation) {
                        var loadTime = navigation.loadEventEnd - navigation.fetchStart;
                        gtag('event', 'page_load_time', {
                            'value': Math.round(loadTime),
                            'metric_id': 'page_load_time'
                        });
                    }
                }, 1000);
            });
        }
    })();
    </script>
    
    <!-- Resource hints for better loading -->
    <link rel="preconnect" href="https://www.googletagmanager.com">
    <link rel="dns-prefetch" href="https://analytics.google.com">
    <link rel="dns-prefetch" href="https://webhooks.fivetran.com">
    """
    
    st.markdown(performance_code, unsafe_allow_html=True)

def add_page_caching():
    """Add aggressive caching for better performance"""
    
    # Enable Streamlit's experimental caching features
    if hasattr(st, 'cache_data'):
        # Use new caching API if available
        cache_config = {
            'ttl': 300,  # 5 minutes
            'max_entries': 1000,
            'show_spinner': False
        }
    else:
        # Fallback for older versions
        cache_config = {}
    
    return cache_config

def optimize_session_state():
    """Optimize session state for better performance"""
    
    # Clean up old session state entries
    keys_to_remove = []
    for key in st.session_state:
        if key.startswith('temp_') or key.startswith('old_'):
            keys_to_remove.append(key)
    
    for key in keys_to_remove:
        del st.session_state[key]

def add_loading_performance():
    """Add loading performance improvements"""
    
    # Add a performance monitoring widget in development
    if st.secrets.get("environment", "production") == "development":
        with st.expander("🔍 Performance Monitor", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Session State Keys", len(st.session_state))
            with col2:
                import sys
                st.metric("Python Objects", len(gc.get_objects()) if 'gc' in sys.modules else 0)

def setup_performance():
    """Main function to set up all performance optimizations"""
    
    # Apply optimizations
    inject_performance_optimizations()
    optimize_session_state()
    
    # Add performance monitoring in development
    try:
        add_loading_performance()
    except Exception:
        pass  # Fail silently in production