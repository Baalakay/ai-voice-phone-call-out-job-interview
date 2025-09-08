# Technical Context: Gravy Work AI Skills Assessment Platform
*Version: 1.0*
*Created: $(date)*
*Last Updated: $(date)*

## Technology Stack

### Infrastructure & Deployment:
- **SST Framework v3**: Serverless deployment (migrated from AWS CDK)
- **Pulumi**: Underlying infrastructure as code
- **TypeScript**: Infrastructure configuration and type safety
- **AWS**: Primary cloud platform (us-east-1 region)

### Backend & Runtime:
- **Python 3.12**: Lambda runtime with AI/ML ecosystem support
- **Lambda Functions**: Serverless compute with configurable timeout/memory
- **Amazon Bedrock**: Managed LLM service (Claude/GPT integration)
- **FastAPI**: API framework for HTTP endpoints
- **Celery + Redis**: Task queue management for async processing

### AI & Voice Services:
- **Amazon Transcribe**: Real-time speech-to-text (English/Spanish)
- **Amazon Polly**: Text-to-speech synthesis (bilingual support)
- **AWS Connect or Twilio**: Voice calling infrastructure  
- **LangChain**: LLM workflow management and prompt engineering

### Data Storage:
- **S3**: Call recordings, transcripts, resumes (with lifecycle policies)
- **DynamoDB**: Worker profiles, assessments, skill templates, call sessions
- **SQS**: Async message processing queue
- **ElastiCache Redis**: Caching and session management

### Development Environment:
- **VS Code DevContainer**: Consistent development environment
- **Python UV**: Package management (`uv sync` for dependencies)
- **Node.js**: Required for SST framework and TypeScript
- **AWS CLI**: Pre-configured for deployment

## Development Environment Setup

### Prerequisites:
```bash
# Container includes all tools, or install locally:
- Python 3.12+
- Node.js 18+ with npm
- AWS CLI with configured credentials
- Docker (for devcontainer)
```

### Initial Setup:
```bash
# 1. Run project initialization (for new projects)
./init-new-project.sh

# 2. Install dependencies
npm install                # SST/TypeScript dependencies
cd functions && uv sync    # Python dependencies

# 3. Configure AWS credentials (if not using devcontainer)
aws configure
```

### Development Workflow:
```bash
# Deploy to development
sst deploy --stage dev

# Local function testing
cd functions && python -m pytest

# Deploy to staging/production
sst deploy --stage staging
sst deploy --stage production  # Protected stage
```

## Dependencies

### Runtime Dependencies (`requirements.txt`):
- **boto3>=1.34.0**: Enhanced AWS SDK features
- **twilio>=8.0.0**: Voice calling service (if using Twilio)
- **amazon-transcribe-streaming**: Real-time transcription
- **langchain>=0.1.0**: LLM workflow management
- **pydantic>=2.0.0**: Data validation models
- **phonenumbers>=8.13.0**: Phone number validation
- **textblob>=0.17.1**: Language detection
- **fastapi>=0.100.0**: API framework
- **celery>=5.3.0**: Task queue management
- **redis>=5.0.0**: Caching and session management

### Development Dependencies (`requirements-dev.txt`):
- **pytest**: Testing framework
- **black**: Code formatting
- **mypy**: Type checking
- **pytest-asyncio**: Async testing support

### Infrastructure Dependencies (TypeScript/npm):
```json
{
  "sst": "^3.0.0",
  "@types/node": "^20.0.0", 
  "typescript": "^5.0.0"
}
```

## Technical Constraints

### SST Template Constraints:
- **Template Nature**: Must preserve generic, configurable structure
- **Configuration-Driven**: No hardcoded values in infrastructure files
- **Resource Naming**: Must use helper functions for consistent naming
- **Stage Awareness**: dev/staging/production deployment differences

### AI Service Constraints:
- **Bedrock Limits**: Model availability, rate limits, token constraints
- **Transcribe Limits**: Real-time processing capabilities, language model availability
- **Polly Limits**: Character limits, voice selection, language support
- **Voice Service Limits**: Concurrent call capacity, geographic restrictions

### Compliance Constraints:
- **Call Recording**: Retention policies and consent requirements
- **PII Protection**: Encryption at rest, secure data handling
- **Bias Prevention**: Standardized assessments, audit trail requirements
- **Data Residency**: AWS region compliance (us-east-1)

### Integration Constraints:
- **Existing Gravy Work APIs**: Authentication, rate limits, data format requirements
- **Phone System Integration**: Number validation, carrier compatibility
- **Real-time Requirements**: Sub-second response times for voice interaction

## Build and Deployment

### Build Process:
- **TypeScript Compilation**: Infrastructure code compiled by SST
- **Python Packaging**: Lambda layers and function bundles created by SST
- **Configuration Validation**: `project.config.ts` type checking
- **Resource Generation**: Dynamic naming based on stage and config

### Deployment Procedure:
```bash
# Stage-specific deployments
sst deploy --stage dev      # No resource protection
sst deploy --stage staging  # Resource protection enabled
sst deploy --stage production  # Full protection, manual approval

# Teardown (dev/staging only)
sst remove --stage dev
```

### CI/CD Integration:
- **GitHub Actions**: Automated deployment on branch merge
- **Stage Promotion**: dev → staging → production workflow
- **Environment Variables**: AWS credentials and stage-specific configs
- **Testing Pipeline**: Unit tests, integration tests, deployment validation

## Testing Approach

### Unit Testing:
- **Python Functions**: pytest for handler and service logic
- **Mock Dependencies**: AWS services, LLM APIs, voice services
- **Data Validation**: Pydantic model testing
- **Assessment Logic**: Skills evaluation algorithm testing

### Integration Testing:
- **API Endpoints**: FastAPI testing client
- **AWS Services**: LocalStack for local AWS simulation
- **Voice Integration**: Mock voice service callbacks
- **End-to-end Workflows**: Assessment pipeline testing

### Load Testing:
- **Concurrent Calls**: Voice service capacity testing
- **DynamoDB Performance**: High-volume assessment data
- **Lambda Concurrency**: Auto-scaling behavior validation

## Template-Specific Configuration

### Primary Config File (`project.config.ts`):
```typescript
export const projectConfig = {
  projectName: "gravy-work-ai-assessment",  // Modified for project
  description: "AI Skills Assessment Platform",
  
  aws: {
    region: "us-east-1",
    profile: "default"
  },
  
  resources: {
    lambda: {
      runtime: "python3.12",
      timeout: "10 minutes",        // Extended for voice calls
      memory: "1024 MB",            // Increased for AI processing
    }
  },
  
  // Custom sections for voice and AI services
  voiceService: {
    provider: "aws-connect",        // or "twilio"
    bilingual: true
  },
  
  aiServices: {
    llm: "bedrock-claude",
    transcribe: "enhanced",
    polly: "neural"
  }
}
```

### Environment Variables Available:
- **Standard Template**: `ENVIRONMENT`, `DATA_TABLE`, `QUEUE_URL`, `OUTPUT_BUCKET`, `PROJECT_NAME`
- **AI Services**: `BEDROCK_MODEL_ID`, `TRANSCRIBE_REGION`, `POLLY_VOICE_ID`
- **Voice Integration**: `VOICE_SERVICE_API_KEY`, `CALLBACK_URL`

---

*This document describes the technologies used in the project and how they're configured, extending the SST template for AI-powered assessment capabilities.*
