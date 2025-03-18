import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as apigateway from 'aws-cdk-lib/aws-apigateway';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as logs from 'aws-cdk-lib/aws-logs';
import * as path from 'path';

export class BackendStack extends cdk.Stack {
  public readonly apiEndpoint: string;
  
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // Create a Lambda function for the API
    const apiLambda = new lambda.Function(this, 'ApiLambda', {
      runtime: lambda.Runtime.PYTHON_3_9,
      handler: 'lambda_handler.handler',
      code: lambda.Code.fromAsset(path.join(__dirname, '../../src/inference'), {
        bundling: {
          image: lambda.Runtime.PYTHON_3_9.bundlingImage,
          command: [
            'bash', '-c', [
              // Install only the required packages, excluding development dependencies
              'pip install --no-cache-dir -r requirements-lambda.txt -t /tmp/asset-output --only-binary=:all: --platform manylinux2014_x86_64 --implementation cp --python-version 3.9 --abi cp39',
              // Copy only the necessary files
              'mkdir -p /asset-output',
              'cp -r /tmp/asset-output/* /asset-output/',
              'cp lambda_handler.py app_lambda.py model_handler.py schemas.py /asset-output/',
              // Remove unnecessary files to reduce package size
              'find /asset-output -type d -name "__pycache__" -exec rm -rf {} +',
              'find /asset-output -type d -name "tests" -exec rm -rf {} +',
              'find /asset-output -type d -name "examples" -exec rm -rf {} +',
              'find /asset-output -type f -name "*.pyc" -delete',
              'find /asset-output -type f -name "*.pyo" -delete',
              'find /asset-output -type f -name "*.pyd" -delete',
              'find /asset-output -type f -name "*.so" | grep -v "\.so\..*" | xargs -r strip --strip-unneeded',
            ].join(' && '),
          ],
        },
      }),
      timeout: cdk.Duration.seconds(30),
      memorySize: 512,
      environment: {
        PYTHONPATH: '/var/task',
      },
    });

    // Create CloudWatch Logs role for API Gateway
    const apiGatewayLogsRole = new iam.Role(this, 'ApiGatewayLogsRole', {
      assumedBy: new iam.ServicePrincipal('apigateway.amazonaws.com'),
      managedPolicies: [
        iam.ManagedPolicy.fromAwsManagedPolicyName('service-role/AmazonAPIGatewayPushToCloudWatchLogs')
      ]
    });

    // Create CloudWatch Log Group for API Gateway
    const apiLogGroup = new logs.LogGroup(this, 'ApiGatewayLogs', {
      retention: logs.RetentionDays.ONE_WEEK,
      removalPolicy: cdk.RemovalPolicy.DESTROY
    });

    // Create an API Gateway REST API
    const api = new apigateway.RestApi(this, 'AnimaApi', {
      restApiName: 'Anima Application API',
      description: 'API for the Active Patient Follow-Up Alert Dashboard',
      defaultCorsPreflightOptions: {
        allowOrigins: apigateway.Cors.ALL_ORIGINS,
        allowMethods: apigateway.Cors.ALL_METHODS,
        allowHeaders: apigateway.Cors.DEFAULT_HEADERS,
        allowCredentials: true,
      },
      deployOptions: {
        stageName: 'prod',
        loggingLevel: apigateway.MethodLoggingLevel.INFO,
        dataTraceEnabled: true,
        accessLogDestination: new apigateway.LogGroupLogDestination(apiLogGroup),
        accessLogFormat: apigateway.AccessLogFormat.jsonWithStandardFields(),
      },
    });

    // Set the CloudWatch role ARN for the account
    const cfnAccount = new apigateway.CfnAccount(this, 'ApiGatewayAccount', {
      cloudWatchRoleArn: apiGatewayLogsRole.roleArn
    });
    
    // Make sure the API depends on the account settings
    api.node.addDependency(cfnAccount);

    // Create a Lambda integration
    const lambdaIntegration = new apigateway.LambdaIntegration(apiLambda, {
      proxy: true,
    });

    // Add a proxy resource to the API
    const proxyResource = api.root.addProxy({
      defaultIntegration: lambdaIntegration,
      anyMethod: true,
    });

    // Store the API endpoint for output
    this.apiEndpoint = api.url;

    // Output the API endpoint
    new cdk.CfnOutput(this, 'ApiEndpoint', {
      value: this.apiEndpoint,
      description: 'The endpoint of the API Gateway',
    });
  }
}