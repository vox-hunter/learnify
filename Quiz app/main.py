"""
AI Quiz and Course Generator - Main Entry Point
This script serves as the main entry point for the AI Quiz and Course Generator application.
"""

import streamlit as st
from frontend import main as run_frontend, initialize_session_state

# Ensure session state is initialized
initialize_session_state()

if __name__ == "__main__":
    # Run the frontend application
    run_frontend()
