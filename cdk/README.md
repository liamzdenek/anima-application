# AWS CDK Deployment for Anima Application

This directory contains the AWS Cloud Development Kit (CDK) infrastructure code for deploying the Active Patient Follow-Up Alert Dashboard to AWS.

## Architecture

The deployment consists of two main stacks:

### Backend Stack (`AnimaBackendStack`)

- **AWS Lambda**: Hosts the FastAPI application
- **API Gateway**: Provides HTTP endpoints for the Lambda function
- **IAM Roles**: Necessary permissions for Lambda execution

### Frontend Stack (`AnimaFrontendStack`)

- **S3 Bucket**: Stores the static assets built with Vite
- **CloudFront Distribution**: Serves the frontend with global caching
- **Origin Access Identity**: Secures access to the S3 bucket

## Prerequisites

- AWS CLI installed and configured
- Node.js 16+ and npm
- AWS CDK CLI installed (`npm install -g aws-cdk`)

## Deployment

The easiest way to deploy is using the provided script:

```bash
./deploy.sh
```

This script will:
1. Install dependencies
2. Build the CDK app
3. Bootstrap the CDK environment (if needed)
4. Deploy both stacks using the "lz-demos" AWS profile
5. Output the deployment URLs

**Note**: The deployment script is configured to use the "lz-demos" AWS profile. Make sure this profile is properly configured in your AWS credentials.

## Manual Deployment

If you prefer to deploy manually:

1. Install dependencies:
   ```bash
   cd cdk
   npm install
   ```

2. Build the CDK app:
   ```bash
   npm run build
   ```

3. Bootstrap the CDK environment (first time only):
   ```bash
   npx cdk bootstrap --profile lz-demos
   ```

4. Deploy the stacks:
   ```bash
   npx cdk deploy --all --profile lz-demos
   ```

## Configuration

The deployment uses the following configuration:

- **Region**: Uses the default AWS region from your AWS CLI configuration
- **Account**: Uses the default AWS account from your AWS CLI configuration
- **Environment Variables**: The frontend build receives the API endpoint as an environment variable

## Customization

To customize the deployment:

1. Edit `cdk/bin/cdk.ts` to modify stack names or add tags
2. Edit `cdk/lib/backend-stack.ts` to customize the Lambda or API Gateway
3. Edit `cdk/lib/frontend-stack.ts` to customize the S3 bucket or CloudFront distribution

## Cleanup

To remove all deployed resources:

```bash
cd cdk
npx cdk destroy --all --profile lz-demos
```

**Note**: This will delete all resources created by the CDK stacks, including the S3 bucket and its contents.