# Technical Context: Gravy Work AI Skills Assessment Platform
*Version: 1.0*
*Created: 2025-01-26*
*Last Updated: 2025-01-26*

## Technology Stack

- **Frontend**: N/A (Voice-only interface, API integration with existing Gravy Work platform)
- **Backend**: Python 3.12 Lambda functions on AWS with SST framework
- **Database**: DynamoDB (NoSQL) for assessment data + S3 for recordings/transcripts
- **Infrastructure**: AWS SST v3 with TypeScript, Pulumi backend (not CDK)
- **AI Services**: Amazon Bedrock (Claude/GPT), Amazon Transcribe, Amazon Polly
- **Voice Services**: AWS Connect or Twilio Voice API for outbound calling
- **Caching/Sessions**: ElastiCache Redis for real-time call state management

## Development Environment Setup

**Base Requirements:**
- Node.js (for SST framework and TypeScript infrastructure code)
- Python 3.12 (Lambda runtime environment)  
- AWS CLI configured with appropriate profile
- UV package manager for Python dependency management
- Docker and VS Code with devcontainer support

**SST-Specific Setup:**
```bash
# Install dependencies
npm install

# Deploy to development
sst deploy --stage dev

# Local development with live Lambda updates
sst dev
```

**Python Environment:**
```bash
cd functions
uv sync  # Install dependencies
uv run python -m pytest  # Run tests
```

## Dependencies

### Runtime Dependencies (`requirements.txt`):
- **boto3>=1.34.0** - Enhanced AWS SDK with latest Bedrock features
- **botocore>=1.34.0** - Core AWS functionality
- **amazon-textract-prettyprinter>=0.1.10** - Document processing (existing template)
- **twilio>=8.0.0** - Voice calling service (if using Twilio over AWS Connect)
- **langchain>=0.1.0** - LLM workflow and prompt management
- **pydantic>=2.0.0** - Data validation and parsing for assessment models
- **phonenumbers>=8.13.0** - Phone number validation and formatting
- **textblob>=0.17.1** - Language detection for bilingual support

### Development Dependencies (`requirements-dev.txt`):
- **pytest>=7.0.0** - Testing framework
- **black>=23.0.0** - Code formatting
- **flake8>=6.0.0** - Linting
- **mypy>=1.0.0** - Type checking

## Technical Constraints

- **SST Template Preservation**: Must maintain generic template structure and central configuration system
- **AWS Region Limitation**: us-east-1 required for optimal Bedrock and voice service availability  
- **Bilingual Processing**: Real-time language detection and switching adds complexity to conversation flows
- **PII Data Compliance**: Call recordings and transcripts require encryption at rest and lifecycle management
- **Real-Time Performance**: Voice conversations demand <200ms response times for natural interaction
- **Integration Dependencies**: Existing Gravy Work platform APIs and worker profile system constraints

## Build and Deployment

- **Build Process**: SST handles TypeScript compilation and Python packaging automatically
- **Deployment Procedure**: `sst deploy --stage [dev|staging|production]` with stage-specific configuration
- **CI/CD**: GitHub Actions recommended with SST-specific deployment workflows

**Stage Configuration:**
- **dev**: Remove resources on destroy, no deletion protection
- **staging**: Remove resources on destroy, no deletion protection  
- **production**: Retain resources on destroy, deletion protection enabled

## Testing Approach

- **Unit Testing**: pytest for individual Lambda functions and service classes
- **Integration Testing**: Mock voice service calls and LLM responses for end-to-end assessment flows
- **E2E Testing**: Actual voice calls with test numbers for complete workflow validation
- **Load Testing**: Concurrent call handling and transcript processing performance validation

## AI/ML Specific Considerations

**LLM Integration:**
- **Amazon Bedrock**: Primary service for Claude/GPT access without external dependencies
- **Prompt Engineering**: Standardized templates per skill type stored in DynamoDB SkillTemplates
- **Response Parsing**: Structured outputs using Pydantic models for consistent assessment scoring
- **Context Management**: Conversation state maintained across multi-turn voice interactions

**Voice Processing:**
- **Real-time Transcription**: Amazon Transcribe streaming API with custom vocabulary for hospitality terms
- **Text-to-Speech**: Amazon Polly with SSML for natural conversation flow and bilingual support
- **Language Detection**: Runtime switching between English and Spanish assessment templates

## Integration Architecture

**Existing Gravy Work Platform Integration:**
- **Worker Profile APIs**: RESTful integration for profile updates and skill approvals
- **Webhook Endpoints**: Status updates and assessment completion notifications
- **Authentication**: Existing JWT/OAuth system for secure API access

**Voice Service Integration:**
- **Outbound Calling**: Programmatic call initiation with worker phone numbers
- **Real-time Events**: WebSocket or callback handling for call status updates
- **Recording Management**: Automatic storage with compliance-appropriate retention policies

---

*This document describes the technologies and technical constraints specific to transforming the SST template into an AI-powered workforce assessment platform.*
