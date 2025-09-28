"""
Streamlit Performance Monitoring Component
Add this to your main app to monitor performance metrics
"""
import streamlit as st
import time
import psutil
import threading
from datetime import datetime

class PerformanceMonitor:
    def __init__(self):
        self.start_time = time.time()
        self.metrics = {
            'page_loads': 0,
            'avg_load_time': 0,
            'memory_usage': 0,
            'cpu_usage': 0
        }
    
    def track_page_load(self):
        """Track page load performance"""
        if 'load_start' not in st.session_state:
            st.session_state.load_start = time.time()
        
        load_time = time.time() - st.session_state.load_start
        self.metrics['page_loads'] += 1
        
        # Update average load time
        if self.metrics['avg_load_time'] == 0:
            self.metrics['avg_load_time'] = load_time
        else:
            self.metrics['avg_load_time'] = (
                self.metrics['avg_load_time'] + load_time
            ) / 2
        
        return load_time
    
    def get_system_metrics(self):
        """Get current system performance metrics"""
        try:
            self.metrics['memory_usage'] = psutil.virtual_memory().percent
            self.metrics['cpu_usage'] = psutil.cpu_percent()
        except ImportError:
            # psutil not available
            self.metrics['memory_usage'] = 0
            self.metrics['cpu_usage'] = 0
        
        return self.metrics
    
    def display_performance_widget(self):
        """Display a collapsible performance monitoring widget"""
        with st.expander("🔍 Performance Monitor", expanded=False):
            col1, col2, col3 = st.columns(3)
            
            metrics = self.get_system_metrics()
            load_time = self.track_page_load()
            
            with col1:
                st.metric(
                    "Load Time", 
                    f"{load_time:.2f}s",
                    delta=f"Target: <2.5s"
                )
            
            with col2:
                st.metric(
                    "Memory Usage", 
                    f"{metrics['memory_usage']:.1f}%"
                )
            
            with col3:
                st.metric(
                    "Page Loads", 
                    metrics['page_loads']
                )
            
            # Performance recommendations
            if load_time > 2.5:
                st.warning("⚠️ Page load time is slower than recommended (>2.5s)")
                st.info("💡 Try refreshing or check your internet connection")
            elif load_time > 1.0:
                st.info("ℹ️ Page load time is acceptable but could be improved")
            else:
                st.success("✅ Excellent page load performance!")

# Initialize global performance monitor
if 'perf_monitor' not in st.session_state:
    st.session_state.perf_monitor = PerformanceMonitor()

def add_performance_monitoring():
    """Add performance monitoring to any Streamlit page"""
    st.session_state.perf_monitor.display_performance_widget()

def inject_performance_css():
    """Inject CSS for better performance visualization"""
    st.markdown("""
    <style>
    /* Performance optimizations */
    .stApp {
        /* Improve rendering performance */
        will-change: transform;
        transform: translateZ(0);
    }
    
    /* Optimize metric display */
    [data-testid="metric-container"] {
        transition: all 0.3s ease;
    }
    
    /* Loading state improvements */
    .stSpinner > div {
        border-color: #ff6b6b !important;
    }
    
    /* Reduce layout shift */
    .main .block-container {
        min-height: 100vh;
    }
    
    /* Performance indicator colors */
    .performance-excellent { color: #28a745; }
    .performance-good { color: #ffc107; }
    .performance-poor { color: #dc3545; }
    </style>
    """, unsafe_allow_html=True)

# JavaScript for client-side performance monitoring
performance_js = """
<script>
(function() {
    // Monitor Core Web Vitals
    function getCLS(callback) {
        let clsValue = 0;
        let clsEntries = [];
        
        const observer = new PerformanceObserver((entryList) => {
            for (const entry of entryList.getEntries()) {
                if (!entry.hadRecentInput) {
                    clsValue += entry.value;
                    clsEntries.push(entry);
                }
            }
            callback(clsValue);
        });
        
        observer.observe({type: 'layout-shift', buffered: true});
    }
    
    function getLCP(callback) {
        const observer = new PerformanceObserver((entryList) => {
            const entries = entryList.getEntries();
            const lastEntry = entries[entries.length - 1];
            callback(lastEntry.startTime);
        });
        
        observer.observe({type: 'largest-contentful-paint', buffered: true});
    }
    
    function getFID(callback) {
        const observer = new PerformanceObserver((entryList) => {
            for (const entry of entryList.getEntries()) {
                callback(entry.processingStart - entry.startTime);
            }
        });
        
        observer.observe({type: 'first-input', buffered: true});
    }
    
    // Log performance metrics after page load
    window.addEventListener('load', function() {
        setTimeout(function() {
            getLCP(function(lcp) {
                console.log('LCP:', lcp + 'ms');
                if (lcp > 2500) console.warn('LCP is slower than recommended');
            });
            
            getCLS(function(cls) {
                console.log('CLS:', cls);
                if (cls > 0.1) console.warn('CLS is higher than recommended');
            });
            
            getFID(function(fid) {
                console.log('FID:', fid + 'ms');
                if (fid > 100) console.warn('FID is slower than recommended');
            });
            
            // Log navigation timing
            const navigation = performance.getEntriesByType('navigation')[0];
            console.log('Page Load Time:', navigation.loadEventEnd - navigation.fetchStart + 'ms');
        }, 1000);
    });
})();
</script>
"""