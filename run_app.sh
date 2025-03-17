#!/bin/bash

# Start the inference API in the background
echo "Starting inference API..."
python -m src.inference.app &
API_PID=$!

# Wait a moment for the API to start
sleep 2

# Navigate to the UI directory
cd src/ui

# Check if node_modules exists, if not, install dependencies
if [ ! -d "node_modules" ]; then
  echo "Installing UI dependencies..."
  npm install
fi

# Start the UI development server
echo "Starting UI development server..."
npm run dev

# When the UI server is stopped, also stop the API
echo "Stopping inference API..."
kill $API_PID