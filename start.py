#!/usr/bin/env python3
"""
Startup script for Learnify app on Render
This ensures the app starts from the correct directory
"""

import os
import sys
import subprocess

# Change to the Quiz_app directory
quiz_app_dir = os.path.join(os.path.dirname(__file__), 'Quiz_app')
os.chdir(quiz_app_dir)

# Add the Quiz_app directory to Python path
sys.path.insert(0, quiz_app_dir)

# Run streamlit
if __name__ == "__main__":
    subprocess.run([
        sys.executable, "-m", "streamlit", "run", "main.py",
        "--server.headless", "true",
        "--server.enableCORS", "false", 
        "--server.enableXsrfProtection", "false"
    ])
