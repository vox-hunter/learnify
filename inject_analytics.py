"""
Post-install script to inject Google Analytics into Streamlit
This script runs after pip install to modify the Streamlit static files
"""
import os
import sys
import streamlit as st

def inject_google_analytics():
    """Inject Google Analytics into Streamlit's index.html"""
    
    # Get Streamlit installation directory
    streamlit_dir = os.path.dirname(st.__file__)
    index_file = os.path.join(streamlit_dir, 'static', 'index.html')
    
    print(f"Streamlit directory: {streamlit_dir}")
    print(f"Index file: {index_file}")
    
    if not os.path.exists(index_file):
        print(f"Error: Streamlit index.html not found at {index_file}")
        return False
    
    # Read the current file
    with open(index_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if Google Analytics is already injected
    if 'gtag' in content:
        print("Google Analytics already injected")
        return True
    
    # Google Analytics code to inject
    ga_code = '''    <!-- Google tag (gtag.js) -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-B30T0B78LK"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){dataLayer.push(arguments);}
      gtag('js', new Date());
      gtag('config', 'G-B30T0B78LK');
    </script>
    
'''
    
    # Inject after <head> tag
    modified_content = content.replace('<head>', f'<head>\n{ga_code}')
    
    # Write back to file
    with open(index_file, 'w', encoding='utf-8') as f:
        f.write(modified_content)
    
    print("Google Analytics injected successfully!")
    return True

if __name__ == "__main__":
    print("Injecting Google Analytics into Streamlit...")
    success = inject_google_analytics()
    sys.exit(0 if success else 1)
