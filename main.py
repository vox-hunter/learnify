"""
AI Quiz and Course Generator - Main Entry Point for Deployment
This script serves as the entry point for the Learnify app when deployed to platforms like Render.
It redirects to the actual main application file in the Quiz_app directory.
"""

import streamlit as st
import os
import sys

# Add the Quiz_app directory to the path
quiz_app_path = os.path.join(os.path.dirname(__file__), "Quiz_app")
sys.path.insert(0, quiz_app_path)

# Change working directory to Quiz_app so relative imports work correctly
os.chdir(quiz_app_path)

# Import and run the main application
import importlib.util

# Load the main application module
main_path = os.path.join(quiz_app_path, "main.py")
print(f"Looking for main.py at: {main_path}")
print(f"File exists: {os.path.exists(main_path)}")

if not os.path.exists(main_path):
    st.error(f"Cannot find main.py at {main_path}")
    st.stop()

spec = importlib.util.spec_from_file_location("main_app", main_path)
main_app = importlib.util.module_from_spec(spec)

# Execute the main application
sys.modules["main_app"] = main_app
spec.loader.exec_module(main_app)
