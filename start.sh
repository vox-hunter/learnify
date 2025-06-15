#!/bin/bash

# Build the custom Streamlit component
echo "Building st_fill_in_the_blanks component..."
cd "Quiz app/st_fill_in_the_blanks/frontend"

# Install dependencies
npm install

# Build the component
npm run build

echo "Component build completed!"

# Go back to root directory
cd ../../../

# Start the Streamlit app
streamlit run "Quiz app/main.py"
