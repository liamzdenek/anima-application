#!/bin/bash

# Navigate to the UI directory
cd src/ui

# Check if node_modules exists, if not, install dependencies
if [ ! -d "node_modules" ]; then
  echo "Installing dependencies..."
  npm install
fi

# Start the development server
echo "Starting UI development server..."
npm run dev