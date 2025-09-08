import * as aws from "@pulumi/aws";
import { projectConfig, generateFunctionName } from "../project.config";

export function ApplicationStack(infrastructure: ReturnType<typeof import("./infrastructure").InfrastructureStack>) {
  // Get current stage
  const stage = $app.stage;
  
  // Main Processing Function - configurable for any project!
  const processingFunction = new sst.aws.Function("ProcessingFunction", {
    name: generateFunctionName(stage),
    handler: projectConfig.resources.lambda.handler,
    runtime: projectConfig.resources.lambda.runtime,
    timeout: projectConfig.resources.lambda.timeout,
    memory: projectConfig.resources.lambda.memory,
    architecture: projectConfig.resources.lambda.architecture,
    // No additional layers needed for basic setup
    layers: [],
    environment: {
      ENVIRONMENT: stage,
      DATA_TABLE: infrastructure.dataTable.name,
      QUEUE_URL: infrastructure.processingQueue.url,
      OUTPUT_BUCKET: (infrastructure.bucket as any).bucket || (infrastructure.bucket as any).id,
      PROJECT_NAME: projectConfig.projectName,
      
      // Twilio configuration for AI Skills Assessment
      TWILIO_AUTH_TOKEN: stage === "production" ? process.env.TWILIO_AUTH_TOKEN_PROD || "" : process.env.TWILIO_AUTH_TOKEN_DEV || "",
      TWILIO_WEBHOOK_URL: stage === "dev" ? "https://placeholder-dev.execute-api.us-east-1.amazonaws.com" : "https://placeholder-prod.execute-api.us-east-1.amazonaws.com",
    },
    permissions: [
      {
        actions: ["s3:*"],
        resources: [infrastructure.bucket.arn, `${infrastructure.bucket.arn}/*`],
      },
      {
        actions: ["dynamodb:*"],
        resources: [infrastructure.dataTable.arn],
      },
      {
        actions: ["sqs:*"],
        resources: [infrastructure.processingQueue.arn],
      },
      {
        actions: [
          "bedrock:InvokeModel",
          "bedrock:InvokeModelWithResponseStream",
          "logs:CreateLogGroup",
          "logs:CreateLogStream", 
          "logs:PutLogEvents"
        ],
        resources: ["*"],
      },
    ],
  });

  // S3 Event notification to trigger Lambda on file upload
  new aws.s3.BucketNotification("ProjectBucketNotifications", {
    bucket: (infrastructure.bucket as any).bucket || (infrastructure.bucket as any).id,
    lambdaFunctions: [
      {
        lambdaFunctionArn: processingFunction.arn,
        events: ["s3:ObjectCreated:*"],
        filterPrefix: "input/", // More generic prefix
        // Remove specific file filter for flexibility
      },
    ],
  });

  // Allow S3 bucket to invoke the Lambda function
  new aws.lambda.Permission("ProjectBucketInvokePermission", {
    action: "lambda:InvokeFunction",
    function: processingFunction.arn,
    principal: "s3.amazonaws.com",
    sourceArn: infrastructure.bucket.arn,
  });

  // HTTP API for Twilio webhooks (AI Skills Assessment)
  const assessmentApi = new sst.aws.ApiGatewayV2("AssessmentWebhookApi");
  
  // Webhook endpoints for AI Skills Assessment
  assessmentApi.route("POST /webhook", processingFunction.arn);
  assessmentApi.route("POST /webhook/status", processingFunction.arn);
  assessmentApi.route("POST /question/{questionId}", processingFunction.arn);
  assessmentApi.route("POST /complete/{assessmentId}", processingFunction.arn);
  assessmentApi.route("POST /initiate", processingFunction.arn);

  return {
    processingFunction,
    assessmentApi,
  };
}
