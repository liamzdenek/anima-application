#!/bin/bash
set -e

# Deploy script for the Active Patient Follow-Up Alert Dashboard
# This script deploys the application to AWS using CDK with the lz-demos profile

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# AWS profile to use
AWS_PROFILE="lz-demos"

echo -e "${YELLOW}Starting deployment of Anima Application to AWS using profile ${AWS_PROFILE}...${NC}"

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo -e "${RED}AWS CLI is not installed. Please install it first.${NC}"
    exit 1
fi

# Check if AWS profile exists
if ! aws configure list-profiles | grep -q "${AWS_PROFILE}"; then
    echo -e "${RED}AWS profile '${AWS_PROFILE}' does not exist. Please create it first.${NC}"
    exit 1
fi

# Check if AWS profile is configured correctly
if ! aws sts get-caller-identity --profile ${AWS_PROFILE} &> /dev/null; then
    echo -e "${RED}AWS profile '${AWS_PROFILE}' is not configured correctly. Please check credentials.${NC}"
    exit 1
fi

# Export AWS profile for all commands
export AWS_PROFILE="${AWS_PROFILE}"

# Build the UI first
echo -e "${YELLOW}Building UI...${NC}"
./build-ui.sh "${API_ENDPOINT:-}"

# Navigate to the CDK directory
cd "$(dirname "$0")/cdk"

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}Installing CDK dependencies...${NC}"
    npm install
fi

# Build the CDK app
echo -e "${YELLOW}Building CDK app...${NC}"
npm run build

# Bootstrap CDK (if needed)
echo -e "${YELLOW}Bootstrapping CDK...${NC}"
npx cdk bootstrap

# Deploy the stacks
echo -e "${YELLOW}Deploying CDK stacks using profile ${AWS_PROFILE}...${NC}"
npx cdk deploy --all --require-approval never --profile ${AWS_PROFILE} --concurrency 4

echo -e "${GREEN}Deployment completed successfully!${NC}"
echo -e "${YELLOW}Note: It may take a few minutes for the CloudFront distribution to fully deploy.${NC}"

# Get the outputs
echo -e "${YELLOW}Getting deployment outputs...${NC}"
API_ENDPOINT=$(aws cloudformation describe-stacks --stack-name AnimaBackendStack --query "Stacks[0].Outputs[?OutputKey=='ApiEndpoint'].OutputValue" --output text --profile ${AWS_PROFILE})
CLOUDFRONT_URL=$(aws cloudformation describe-stacks --stack-name AnimaFrontendStack --query "Stacks[0].Outputs[?OutputKey=='CloudFrontURL'].OutputValue" --output text --profile ${AWS_PROFILE})

echo -e "${GREEN}Deployment URLs:${NC}"
echo -e "API Endpoint: ${YELLOW}${API_ENDPOINT}${NC}"
echo -e "Frontend URL: ${YELLOW}${CLOUDFRONT_URL}${NC}"

exit 0