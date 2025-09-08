#!/bin/bash

# Project Template Initialization Script
# 
# This script helps initialize a new project from this SST template.
# Run this script when starting a new project to set up the configuration.

set -e

echo "🚀 SST Project Template Initialization"
echo "======================================"
echo

# Get project information from user
read -p "Enter project name (lowercase, no spaces, use dashes): " PROJECT_NAME
read -p "Enter project description: " PROJECT_DESCRIPTION
read -p "Enter organization prefix (default: yourorg): " ORG_PREFIX
ORG_PREFIX=${ORG_PREFIX:-yourorg}

read -p "Enter AWS region (default: us-east-1): " AWS_REGION
AWS_REGION=${AWS_REGION:-us-east-1}

read -p "Enter AWS profile (default: default): " AWS_PROFILE
AWS_PROFILE=${AWS_PROFILE:-default}

echo
echo "Configuration:"
echo "- Project Name: $PROJECT_NAME"
echo "- Description: $PROJECT_DESCRIPTION" 
echo "- Organization: $ORG_PREFIX"
echo "- AWS Region: $AWS_REGION"
echo "- AWS Profile: $AWS_PROFILE"
echo

read -p "Continue with this configuration? (y/N): " CONFIRM
if [[ ! $CONFIRM =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 1
fi

echo
echo "📝 Updating project configuration..."

# Update project.config.ts
cat > project.config.ts << EOF
/**
 * Project Configuration
 * 
 * Central configuration file for SST project templating.
 * Update these values when starting a new project from this template.
 */

export const projectConfig = {
  // Project identification
  projectName: "$PROJECT_NAME",
  description: "$PROJECT_DESCRIPTION",
  
  // AWS configuration
  aws: {
    region: "$AWS_REGION",
    profile: "$AWS_PROFILE",
  },
  
  // Resource naming configuration
  resources: {
    // S3 Bucket configuration
    bucket: {
      // Use existing bucket or create new one
      useExisting: false, // Set to true if referencing existing bucket
      existingName: "", // Only used if useExisting is true
      // Bucket name will be auto-generated as: {orgPrefix}-{projectName}-bucket-{stage}
    },
    
    // Lambda function configuration
    lambda: {
      runtime: "python3.12" as const,
      timeout: "10 minutes",
      memory: "1024 MB",
      architecture: "x86_64" as const,
      handler: "functions/src/handlers/index.handler", // Path to your handler
    },
    
    // Queue configuration
    queue: {
      visibilityTimeout: "5 minutes",
    },
  },
  
  // Organization/environment prefixes
  naming: {
    orgPrefix: "$ORG_PREFIX", // Organization prefix for resources
  },
  
  // Stage-specific configuration
  stages: {
    dev: {
      protect: false,
      removal: "remove" as const,
    },
    staging: {
      protect: false,
      removal: "remove" as const,
    },
    production: {
      protect: true,
      removal: "retain" as const,
    },
  },
} as const;

// Helper functions for consistent naming
export const generateResourceName = (resourceType: string, stage: string) => {
  return \`\${projectConfig.naming.orgPrefix}-\${projectConfig.projectName}-\${resourceType}-\${stage}\`;
};

export const generateFunctionName = (stage: string) => {
  return \`\${projectConfig.projectName}-\${stage}\`;
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
EOF

echo "✅ Updated project.config.ts"

# Update package.json name
echo "📦 Updating package.json..."
if command -v jq > /dev/null 2>&1; then
    jq --arg name "$PROJECT_NAME" '.name = $name' package.json > package.json.tmp && mv package.json.tmp package.json
    echo "✅ Updated package.json name"
else
    echo "⚠️  jq not found. Please manually update the 'name' field in package.json to '$PROJECT_NAME'"
fi

# Update function pyproject.toml
echo "🐍 Updating functions/pyproject.toml..."
sed -i.bak "s/name = \"functions\"/name = \"$PROJECT_NAME-functions\"/" functions/pyproject.toml
rm -f functions/pyproject.toml.bak
echo "✅ Updated functions/pyproject.toml"

# Update root pyproject.toml
echo "🐍 Updating root pyproject.toml..."
sed -i.bak "s/name = \"app\"/name = \"$PROJECT_NAME\"/" pyproject.toml
rm -f pyproject.toml.bak
echo "✅ Updated root pyproject.toml"

echo
echo "🎉 Project initialization complete!"
echo
echo "Next steps:"
echo "1. Review and customize the generated configuration in project.config.ts"
echo "2. Modify functions/src/handlers/index.py for your specific use case"
echo "3. Install dependencies: npm install"
echo "4. Deploy to dev: sst deploy --stage dev"
echo "5. Test your deployment"
echo
echo "📚 For more information, see README.md"
echo

# Optional: Remove this script after initialization
read -p "Remove this initialization script? It's no longer needed. (y/N): " REMOVE_SCRIPT
if [[ $REMOVE_SCRIPT =~ ^[Yy]$ ]]; then
    rm "$0"
    echo "✅ Initialization script removed"
fi

echo "Happy coding! 🚀"
