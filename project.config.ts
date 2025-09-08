/**
 * Project Configuration
 * 
 * 🎯 CENTRAL CONFIGURATION FOR SST TEMPLATE
 * 
 * This is the SINGLE SOURCE OF TRUTH for all project-specific settings.
 * All infrastructure files (infra/*.ts) reference this configuration.
 * 
 * 🚀 FOR NEW PROJECTS: Run ./init-new-project.sh to configure automatically
 * 🤖 FOR AI AGENTS: This is the PRIMARY file to modify for project settings
 * 
 * ⚠️  NEVER hardcode project values in infrastructure files - use this config!
 */

export const projectConfig = {
  // 🏷️ Project identification (MODIFY THESE)
  projectName: "gravy-work", // AI Skills Assessment Platform for Gig Work Staffing
  description: "AI Voice Agent for automated worker skills assessment and screening", // Brief project description
  
  // 🌍 AWS configuration
  aws: {
    region: "us-east-1", // AWS region for all resources
    profile: "default", // AWS CLI profile to use for deployment
  },
  
  // 🛠️ Resource configuration (usually no changes needed)
  resources: {
    // 🪣 S3 Bucket configuration
    bucket: {
      useExisting: false, // true = reference existing bucket, false = create new
      existingName: "", // Only required if useExisting = true
      // 📝 New bucket naming: {orgPrefix}-{projectName}-bucket-{stage}
    },
    
    // 🐍 Lambda function configuration
    lambda: {
      runtime: "python3.12" as const, // Python runtime version
      timeout: "10 minutes", // Function timeout
      memory: "1024 MB", // Allocated memory
      architecture: "x86_64" as const, // CPU architecture
      handler: "functions/src/handlers/index.handler", // Path to handler function
    },
    
    // 📬 SQS Queue configuration  
    queue: {
      visibilityTimeout: "5 minutes", // How long messages remain invisible after being received
    },
  },
  
  // 🏢 Organization/environment prefixes (MODIFY THESE)
  naming: {
    orgPrefix: "gravywork", // Organization prefix for all resource names
  },
  
  // 🚀 Stage-specific configuration (usually no changes needed)
  stages: {
    dev: {
      protect: false, // No deletion protection
      removal: "remove" as const, // Remove resources when stack is deleted
    },
    staging: {
      protect: false, // No deletion protection
      removal: "remove" as const, // Remove resources when stack is deleted
    },
    production: {
      protect: true, // Prevent accidental deletion
      removal: "retain" as const, // Keep resources even if stack is deleted
    },
  },
} as const;

// Helper functions for consistent naming
export const generateResourceName = (resourceType: string, stage: string) => {
  return `${projectConfig.naming.orgPrefix}-${projectConfig.projectName}-${resourceType}-${stage}`;
};

export const generateFunctionName = (stage: string) => {
  return `${projectConfig.projectName}-${stage}`;
};

export const generateBucketName = (stage: string) => {
  if (projectConfig.resources.bucket.useExisting) {
    return projectConfig.resources.bucket.existingName;
  }
  return generateResourceName("bucket", stage);
};

// Type exports for better TypeScript support
export type ProjectConfig = typeof projectConfig;
export type Stage = keyof typeof projectConfig.stages;
