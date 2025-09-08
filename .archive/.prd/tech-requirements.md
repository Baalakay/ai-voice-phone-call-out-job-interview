# SST AWS Project Template

A reusable template for AWS projects using SST (Serverless Stack) with TypeScript and Python Lambda functions.

## 🏗️ Architecture

This template provides a standardized structure for AWS serverless applications with:

- **Infrastructure Stack**: S3 Bucket, SQS Queue, DynamoDB Table
- **Application Stack**: Lambda Function with proper IAM permissions
- **Configurable**: Central configuration system for easy project customization
- **DevContainer Ready**: Includes VS Code devcontainer support

## 📂 Project Structure

```
├── project.config.ts          # 🔧 Central configuration (MODIFY THIS)
├── sst.config.ts              # SST framework configuration
├── infra/
│   ├── infrastructure.ts      # Core AWS infrastructure
│   └── application.ts         # Application-specific resources
├── functions/
│   └── src/
│       └── handlers/
│           └── index.py       # 🐍 Lambda function handler (CUSTOMIZE)
├── init-new-project.sh        # 🚀 Project initialization script
└── README.md                  # This file
```

## 🚀 Quick Start

### 1. Initialize a New Project

Run the initialization script to configure the template for your specific project:

```bash
./init-new-project.sh
```

This script will:
- Prompt for project name and configuration
- Update `project.config.ts` with your values
- Update package.json and pyproject.toml files
- Remove hardcoded references

### 2. Install Dependencies

```bash
npm install
```

### 3. Deploy to AWS

```bash
# Deploy to development stage
sst deploy --stage dev

# Deploy to production stage
sst deploy --stage production
```

## ⚙️ Configuration

### project.config.ts

The central configuration file that controls all project-specific settings:

```typescript
export const projectConfig = {
  projectName: "your-project-name",        // 🏷️ Change this!
  description: "Your project description",
  
  aws: {
    region: "us-east-1",
    profile: "default"
  },
  
  resources: {
    bucket: {
      useExisting: false,                   // Set true to use existing bucket
      existingName: ""                      // Bucket name if using existing
    },
    lambda: {
      runtime: "python3.12",
      timeout: "10 minutes",
      memory: "1024 MB",
      handler: "functions/src/handlers/index.handler"
    }
  },
  
  naming: {
    orgPrefix: "yourorg"                    // 🏢 Organization prefix
  }
}
```

### Stage Configuration

The template supports multiple deployment stages:

- **dev**: Development environment (removes resources on destroy)
- **staging**: Staging environment (removes resources on destroy) 
- **production**: Production environment (retains resources on destroy, protected)

## 🐍 Lambda Function Customization

The template includes a generic Lambda handler at `functions/src/handlers/index.py`. Customize this for your specific use case:

```python
def handler(event, context):
    # Your custom logic here
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from your project!')
    }
```

### Environment Variables Available:

- `ENVIRONMENT`: Current stage (dev, staging, production)
- `DATA_TABLE`: DynamoDB table name
- `QUEUE_URL`: SQS queue URL
- `OUTPUT_BUCKET`: S3 bucket name
- `PROJECT_NAME`: Your project name from config

## 🔄 S3 Event Triggers

By default, the Lambda function is triggered by S3 uploads to the `input/` prefix. Files uploaded to `s3://your-bucket/input/` will automatically trigger processing.

## 📊 AWS Resources Created

### Development Stage
- S3 Bucket: `yourorg-projectname-bucket-dev`
- Lambda: `projectname-dev`
- SQS Queue: Auto-generated name
- DynamoDB Table: Auto-generated name

### Production Stage  
- S3 Bucket: `yourorg-projectname-bucket-production`
- Lambda: `projectname-production`
- SQS Queue: Auto-generated name (protected)
- DynamoDB Table: Auto-generated name (protected)

## 🛠️ Development Workflow

### Local Development

The project is set up to work with VS Code devcontainers. The devcontainer includes:
- Python 3.12
- Node.js and npm
- AWS CLI
- All necessary development tools

### Testing Locally

```bash
# Install Python dependencies
cd functions
uv sync

# Run local tests (customize as needed)
python -m pytest
```

### Deployment Commands

```bash
# Deploy to dev
sst deploy --stage dev

# Deploy to staging
sst deploy --stage staging

# Deploy to production (protected)
sst deploy --stage production

# Remove dev deployment
sst remove --stage dev
```

## 🔒 Security & Permissions

The Lambda function has the minimum required permissions:

- **S3**: Read/write access to the project bucket
- **DynamoDB**: Read/write access to the data table
- **SQS**: Send/receive messages from the processing queue
- **CloudWatch**: Create log groups and write logs
- **Textract**: Access for document processing (can be removed if not needed)

## 📝 Customization Guide

### Adding New AWS Resources

1. Add to `infra/infrastructure.ts` for shared resources
2. Add to `infra/application.ts` for application-specific resources
3. Update the return statements to expose new resources
4. Reference in your Lambda functions via environment variables

### Changing the Trigger

Currently configured for S3 events. To change:

1. Modify the `BucketNotification` in `infra/application.ts`
2. Or remove it entirely and add different triggers (EventBridge, API Gateway, etc.)

### Using Existing AWS Resources

Set `useExisting: true` in your `project.config.ts` and specify the resource name:

```typescript
resources: {
  bucket: {
    useExisting: true,
    existingName: "my-existing-bucket"
  }
}
```

## 🐳 DevContainer Support

This project includes VS Code devcontainer configuration that provides:

- Consistent development environment
- Pre-installed AWS CLI and tools
- Python and Node.js environments
- Container shares AWS credentials from host

## 🔄 Template Updates

To update this template for future projects:

1. Make changes to the core files
2. Test with a sample deployment
3. Update this README with any new features
4. Version tag the template for reproducibility

## 📚 Additional Resources

- [SST Documentation](https://sst.dev/docs)
- [AWS CDK Documentation](https://docs.aws.amazon.com/cdk/)
- [Pulumi AWS Documentation](https://www.pulumi.com/docs/clouds/aws/)

## 🤝 Contributing

When adding features to this template:

1. Ensure backward compatibility
2. Update the configuration system
3. Update this README
4. Test with multiple stages
5. Consider devcontainer compatibility

## 🤖 AI Agent Guidelines

### For Cursor AI Assistants
When working with this template:

1. **This is a TEMPLATE, not a specific project** - preserve generic, configurable nature
2. **Primary config file**: `project.config.ts` - modify this for project-specific settings
3. **Never hardcode** project names in infrastructure files - use the config system
4. **Template files to preserve**: `infra/*.ts`, `sst.config.ts`, `init-new-project.sh`
5. **Safe to customize**: `functions/src/handlers/index.py`, `project.config.ts`, dependencies
6. **New projects**: Always run `./init-new-project.sh` first
7. **Dependencies**: Runtime deps in `requirements.txt`, dev deps in `requirements-dev.txt`
8. **Architecture**: Infrastructure + Application stacks, always starts with S3 bucket + Lambda

See `.cursorrules` for complete AI agent guidelines.

### Key Principle
**Show users how to configure the template rather than making it project-specific.**

## 📄 License

This template is provided as-is for internal use. Customize according to your organization's requirements.
