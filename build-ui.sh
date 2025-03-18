#!/bin/bash
set -e

# Build script for the UI
# This script builds the UI and prepares it for deployment

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Building UI for deployment...${NC}"

# Navigate to the UI directory
cd "$(dirname "$0")/src/ui"

# Install dependencies
echo -e "${YELLOW}Installing dependencies...${NC}"
npm ci

# Build the UI
echo -e "${YELLOW}Building UI...${NC}"
VITE_API_ENDPOINT="${1:-https://kzyl5zwgnd.execute-api.us-west-2.amazonaws.com/prod}" npm run build

echo -e "${GREEN}UI build completed successfully!${NC}"
echo -e "${YELLOW}Built assets are in src/ui/dist/${NC}"

exit 0