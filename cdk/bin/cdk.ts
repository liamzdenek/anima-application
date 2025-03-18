#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { FrontendStack } from '../lib/frontend-stack';
import { BackendStack } from '../lib/backend-stack';

const app = new cdk.App();

// Environment configuration
// Use the AWS profile specified in the environment or command line
const env = {
  account: process.env.CDK_DEFAULT_ACCOUNT,
  region: process.env.CDK_DEFAULT_REGION || 'us-east-1'
};

// Add context value for the AWS profile
const awsProfile = process.env.AWS_PROFILE || 'lz-demos';
cdk.Tags.of(app).add('AwsProfile', awsProfile);

// Create the backend stack first
const backendStack = new BackendStack(app, 'AnimaBackendStack', {
  env,
  description: 'Backend infrastructure for the Active Patient Follow-Up Alert Dashboard',
});

// Create the frontend stack with a reference to the backend API URL
const frontendStack = new FrontendStack(app, 'AnimaFrontendStack', {
  env,
  description: 'Frontend infrastructure for the Active Patient Follow-Up Alert Dashboard',
  apiEndpoint: backendStack.apiEndpoint,
});

// Add tags to all resources
cdk.Tags.of(app).add('Project', 'AnimaApplication');
cdk.Tags.of(app).add('Environment', 'Production');