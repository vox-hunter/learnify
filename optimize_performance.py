"""
Performance optimization script for Learnify Streamlit app
This script implements several performance improvements to reduce load times
"""
import os
import sys
import streamlit as st

def optimize_analytics_loading():
    """Optimize Google Analytics to load asynchronously"""
    
    streamlit_dir = os.path.dirname(st.__file__)
    index_file = os.path.join(streamlit_dir, 'static', 'index.html')
    
    if not os.path.exists(index_file):
        print(f"Error: Streamlit index.html not found at {index_file}")
        return False
    
    # Read the current file
    with open(index_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if already optimized
    if 'Performance Optimized GA' in content:
        print("Google Analytics already optimized")
        return True
    
    # Remove existing GA code if present
    if 'gtag' in content:
        # Remove old GA code
        lines = content.split('\n')
        new_lines = []
        skip_ga = False
        
        for line in lines:
            if 'Google tag (gtag.js)' in line or 'gtag.js?id=' in line:
                skip_ga = True
            elif skip_ga and '</script>' in line:
                skip_ga = False
                continue
            elif not skip_ga:
                new_lines.append(line)
        
        content = '\n'.join(new_lines)
    
    # Optimized Google Analytics code - loads after page load
    optimized_ga_code = '''    <!-- Performance Optimized GA -->
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){dataLayer.push(arguments);}
      gtag('js', new Date());
      
      // Configure GA but don't load script yet
      gtag('config', 'G-B30T0B78LK', {
        'send_page_view': false,
        'transport_type': 'beacon'
      });
      
      // Load GA script after page is fully loaded to avoid blocking render
      window.addEventListener('load', function() {
        setTimeout(function() {
          var script = document.createElement('script');
          script.async = true;
          script.src = 'https://www.googletagmanager.com/gtag/js?id=G-B30T0B78LK';
          script.onload = function() {
            gtag('config', 'G-B30T0B78LK');
            gtag('event', 'page_view');
          };
          document.head.appendChild(script);
        }, 100); // Small delay to ensure everything else loads first
      });
    </script>
    
    <!-- Preconnect to improve loading -->
    <link rel="preconnect" href="https://www.googletagmanager.com">
    <link rel="dns-prefetch" href="https://analytics.google.com">
    
'''
    
    # Inject after <head> tag
    modified_content = content.replace('<head>', f'<head>\n{optimized_ga_code}')
    
    # Write back to file
    try:
        with open(index_file, 'w', encoding='utf-8') as f:
            f.write(modified_content)
        print("✅ Google Analytics optimized for better performance")
        return True
    except Exception as e:
        print(f"Error writing optimized analytics: {e}")
        return False

def add_performance_hints():
    """Add performance hints to HTML head"""
    
    streamlit_dir = os.path.dirname(st.__file__)
    index_file = os.path.join(streamlit_dir, 'static', 'index.html')
    
    if not os.path.exists(index_file):
        return False
    
    with open(index_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if 'Performance Hints Added' in content:
        print("Performance hints already added")
        return True
    
    # Performance optimization hints
    perf_hints = '''    <!-- Performance Hints Added -->
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    
    <!-- Resource hints for faster loading -->
    <link rel="dns-prefetch" href="//webhooks.fivetran.com">
    
    <!-- Optimize font loading -->
    <style>
      /* Prevent font loading delays */
      body { font-display: swap; }
      
      /* Reduce layout shift during loading */
      .stApp > header { display: none; }
      
      /* Optimize spinner display */
      .stSpinner > div > div { 
        border-color: #ff6b6b transparent transparent transparent !important;
      }
    </style>
    
'''
    
    # Add after existing head content
    modified_content = content.replace('<head>', f'<head>\n{perf_hints}')
    
    try:
        with open(index_file, 'w', encoding='utf-8') as f:
            f.write(modified_content)
        print("✅ Performance hints added")
        return True
    except Exception as e:
        print(f"Error adding performance hints: {e}")
        return False

def create_streamlit_config():
    """Create optimized Streamlit configuration"""
    
    config_content = '''[server]
# Optimize server settings for better performance
maxUploadSize = 200
maxMessageSize = 200
enableWebsocketCompression = true
enableXsrfProtection = true

[browser]
# Optimize browser settings
gatherUsageStats = false
showErrorDetails = false

[theme]
# Optimize theme for faster rendering
base = "light"
primaryColor = "#ff6b6b"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"

[client]
# Optimize client settings
caching = true
displayEnabled = true
toolbarMode = "minimal"

[runner]
# Optimize script runner
magicEnabled = false
installTracer = false
fixMatplotlib = false

[logger]
# Optimize logging
level = "ERROR"
messageFormat = "%(asctime)s %(message)s"
'''
    
    config_dir = os.path.expanduser('~/.streamlit')
    os.makedirs(config_dir, exist_ok=True)
    config_file = os.path.join(config_dir, 'config.toml')
    
    try:
        with open(config_file, 'w') as f:
            f.write(config_content)
        print(f"✅ Optimized Streamlit config created at {config_file}")
        return True
    except Exception as e:
        print(f"Error creating config: {e}")
        return False

def main():
    """Run all performance optimizations"""
    print("🚀 Starting Learnify Performance Optimization...")
    print("=" * 50)
    
    success_count = 0
    
    if optimize_analytics_loading():
        success_count += 1
    
    if add_performance_hints():
        success_count += 1
        
    if create_streamlit_config():
        success_count += 1
    
    print("=" * 50)
    print(f"✅ Performance optimization complete: {success_count}/3 optimizations applied")
    print("\n📋 Next Steps:")
    print("1. Restart your Streamlit application")
    print("2. Test the performance improvements")
    print("3. Monitor Core Web Vitals in production")
    print("\n🎯 Expected improvements:")
    print("- Faster initial page load (reduced LCP)")
    print("- Less layout shift (improved CLS)")
    print("- Better user experience overall")

if __name__ == "__main__":
    main()