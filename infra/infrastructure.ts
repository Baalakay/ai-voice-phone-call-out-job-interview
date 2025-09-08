import * as aws from "@pulumi/aws";
import { projectConfig, generateBucketName } from "../project.config";

export function InfrastructureStack() {
  // Get current stage
  const stage = $app.stage;
  
  // S3 Bucket for all assets (PDFs, images, processed outputs)
  // Can reference existing bucket or create new one based on configuration
  const bucket = projectConfig.resources.bucket.useExisting
    ? aws.s3.BucketV2.get(
        "ProjectBucket",
        projectConfig.resources.bucket.existingName
      )
    : new sst.aws.Bucket("ProjectBucket");

  // SQS Queue for processing
  const processingQueue = new sst.aws.Queue("ProcessingQueue", {
    visibilityTimeout: projectConfig.resources.queue.visibilityTimeout,
  });

  // DynamoDB Table for tracking processing status (optional - can be removed if not needed)
  const dataTable = new sst.aws.Dynamo("DataTable", {
    fields: {
      id: "string",
      status: "string",
      timestamp: "string",
    },
    primaryIndex: { hashKey: "id" },
  });

  return {
    bucket,
    processingQueue,
    dataTable,
  };
}
