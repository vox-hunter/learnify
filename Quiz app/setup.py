#!/usr/bin/env python3
"""
Setup script for AI Quiz and Course Generator
"""

import os
import subprocess
import sys
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error during {description}:")
        print(f"Command: {command}")
        print(f"Error: {e.stderr}")
        return False

def check_requirements():
    """Check if all requirements are installed"""
    print("\n📋 Checking requirements...")
    try:
        import streamlit
        import google.genai
        import pydantic
        import requests
        import dotenv
        print("✅ All Python dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        return False

def check_env_file():
    """Check if .env file exists and has API key"""
    env_path = Path(".env")
    if not env_path.exists():
        print("\n⚠️  .env file not found")
        print("Please create a .env file with your GEMINI_API_KEY")
        print("Example:")
        print("GEMINI_API_KEY=your_api_key_here")
        return False
    
    with open(env_path, 'r') as f:
        content = f.read()
    
    if "GEMINI_API_KEY=" not in content:
        print("\n⚠️  GEMINI_API_KEY not found in .env file")
        return False
    
    print("✅ .env file configured")
    return True

def build_component():
    """Build the custom Streamlit component"""
    component_path = Path("st_fill_in_the_blanks/frontend")
    if not component_path.exists():
        print("❌ Custom component source not found")
        return False
    
    print("\n🔨 Building custom component...")
    original_dir = os.getcwd()
    try:
        os.chdir(component_path)
        
        # Check if node_modules exists
        if not Path("node_modules").exists():
            if not run_command("npm install", "Installing npm dependencies"):
                return False
        
        # Build the component
        if not run_command("npm run build", "Building React component"):
            return False
        
        print("✅ Custom component built successfully")
        return True
    
    finally:
        os.chdir(original_dir)

def main():
    print("🚀 AI Quiz and Course Generator Setup")
    print("=" * 50)
    
    # Install Python dependencies
    if not run_command("pip install -r requirements.txt", "Installing Python dependencies"):
        print("❌ Failed to install Python dependencies")
        return False
    
    # Check if all requirements are properly installed
    if not check_requirements():
        print("❌ Some requirements are missing. Please check the installation.")
        return False
    
    # Check .env file
    if not check_env_file():
        print("❌ Please configure your .env file before running the application")
        return False
    
    # Build custom component
    if not build_component():
        print("❌ Failed to build custom component")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 Setup completed successfully!")
    print("\nTo run the application:")
    print("  streamlit run main.py")
    print("\nThe application will open in your browser at http://localhost:8501")

if __name__ == "__main__":
    main()
