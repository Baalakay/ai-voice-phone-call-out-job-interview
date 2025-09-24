import * as aws from "@pulumi/aws";
import { projectConfig, generateFunctionName, getTwilioConfig } from "../project.config";

export function ApplicationStack(infrastructure: ReturnType<typeof import("./infrastructure").InfrastructureStack>) {
  // Get current stage
  const stage = $app.stage;
  const twilioConfig = getTwilioConfig(stage);
  
  // HTTP API for Twilio webhooks (AI Skills Assessment) - define first for URL reference
  const assessmentApi = new sst.aws.ApiGatewayV2("AssessmentWebhookApi");
  
  // Main Processing Function - configurable for any project!
  const processingFunction = new sst.aws.Function("ProcessingFunction", {
    name: generateFunctionName(stage),
    handler: "functions/src/functions/webhook_simple.handler",
    runtime: "python3.12",
    timeout: projectConfig.resources.lambda.timeout,
    memory: projectConfig.resources.lambda.memory,
    architecture: projectConfig.resources.lambda.architecture,
    // No additional layers needed for basic setup
    layers: [],
    environment: {
      ENVIRONMENT: stage,
      // DATA_TABLE: removed for simplified S3-based storage
      QUEUE_URL: infrastructure.processingQueue.url,
      OUTPUT_BUCKET: (infrastructure.bucket as any).bucket || (infrastructure.bucket as any).id,
      PROJECT_NAME: projectConfig.projectName,
      S3_BUCKET_NAME: (infrastructure.bucket as any).bucket || (infrastructure.bucket as any).id,
      
      // Twilio configuration for AI Skills Assessment - from centralized config
      TWILIO_ACCOUNT_SID: twilioConfig.accountSid,
      TWILIO_AUTH_TOKEN: twilioConfig.authToken,
      TWILIO_PHONE_NUMBER: twilioConfig.phoneNumber,
      TWILIO_WEBHOOK_URL: assessmentApi.url,
    },
    permissions: [
      {
        actions: ["s3:*"],
        resources: ["*"],
      },
      {
        actions: ["sqs:*"],
        resources: ["*"],
      },
      {
        actions: [
          "bedrock:InvokeModel",
          "bedrock:InvokeModelWithResponseStream",
          "transcribe:StartTranscriptionJob",
          "transcribe:GetTranscriptionJob",
          "transcribe:ListTranscriptionJobs",
          "lambda:InvokeFunction",
          "logs:CreateLogGroup",
          "logs:CreateLogStream", 
          "logs:PutLogEvents"
        ],
        resources: ["*"],
      },
    ],
  });

  // Assessment Processing Function - handles post-call LLM analysis
  const assessmentProcessor = new sst.aws.Function("AssessmentProcessor", {
    name: `${projectConfig.projectName}-${stage}-assessment-processor`,
    handler: "functions/src/functions/assessment_processor_simple.lambda_handler",
    runtime: "python3.12",
    timeout: "15 minutes", // Longer timeout for transcription + LLM processing
    memory: "1024 MB",
    architecture: projectConfig.resources.lambda.architecture,
    layers: [],
    environment: {
      ENVIRONMENT: stage,
      OUTPUT_BUCKET: (infrastructure.bucket as any).bucket || (infrastructure.bucket as any).id,
      S3_BUCKET_NAME: (infrastructure.bucket as any).bucket || (infrastructure.bucket as any).id,
      PROJECT_NAME: projectConfig.projectName,
      
      // Twilio credentials for downloading recordings
      TWILIO_ACCOUNT_SID: twilioConfig.accountSid,
      TWILIO_AUTH_TOKEN: twilioConfig.authToken,
      TWILIO_WEBHOOK_URL: assessmentApi.url,
    },
    permissions: [
      {
        actions: ["s3:*"],
        resources: ["*"],
      },
      {
        actions: [
          "bedrock:InvokeModel",
          "bedrock:InvokeModelWithResponseStream",
          "bedrock:Converse",
          "transcribe:StartTranscriptionJob",
          "transcribe:GetTranscriptionJob",
          "transcribe:ListTranscriptionJobs",
          "logs:CreateLogGroup",
          "logs:CreateLogStream", 
          "logs:PutLogEvents"
        ],
        resources: ["*"],
      },
    ],
  });

  // LLM Comparison processor for testing multiple models (temporarily disabled for bucket fix)
  // const llmComparisonProcessor = new sst.aws.Function("LLMComparisonProcessor", {
  //   handler: "functions/src/functions/llm_comparison_processor.lambda_handler",
  //   timeout: "15 minutes",
  //   memory: "2048 MB",
  //   environment: {
  //     OUTPUT_BUCKET: (infrastructure.bucket as any).bucket || (infrastructure.bucket as any).id,
  //   },
  //   permissions: [
  //     {
  //       actions: ["s3:GetObject", "s3:PutObject", "s3:DeleteObject", "s3:ListBucket"],
  //       resources: [infrastructure.bucket.arn, $interpolate`${infrastructure.bucket.arn}/*`],
  //     },
  //     {
  //       actions: ["bedrock:InvokeModel", "bedrock:Converse"],
  //       resources: ["*"],
  //     },
  //   ],
  // });

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

  // Webhook endpoints for AI Skills Assessment
  assessmentApi.route("POST /webhook", processingFunction.arn);
  assessmentApi.route("POST /webhook/recording", processingFunction.arn);
  assessmentApi.route("POST /webhook/gather", processingFunction.arn);
  assessmentApi.route("POST /webhook/status", processingFunction.arn);
  assessmentApi.route("POST /question/{questionId}", processingFunction.arn);
  assessmentApi.route("POST /complete/{assessmentId}", processingFunction.arn);
  assessmentApi.route("POST /initiate", processingFunction.arn);

  return {
    processingFunction,
    assessmentProcessor,
    // llmComparisonProcessor,  // Temporarily disabled for bucket fix
    assessmentApi,
  };
}
