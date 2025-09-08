# System Patterns: Gravy Work AI Skills Assessment Platform
*Version: 1.0*
*Created: $(date)*
*Last Updated: $(date)*

## Architecture Overview
The system extends the SST AWS Project Template to create a specialized AI-powered workforce assessment platform. Core architecture includes Infrastructure Stack (S3, SQS, DynamoDB), Application Stack (Lambda functions with AI integrations), and a central configuration system for project customization.

## Key Components

### Infrastructure Layer (Based on SST Template):
- **S3 Bucket**: Call recordings, transcripts, resumes storage with lifecycle policies
- **SQS Queue**: Async processing workflow for assessment pipeline  
- **DynamoDB**: Worker profiles, assessment data, skill templates
- **Lambda Functions**: Python 3.12 runtime with specialized handlers

### AI Voice Calling Layer - SIMPLIFIED FOR POC:
- **Twilio Voice API**: Outbound calls + built-in STT via <Gather> verb
- **Pre-recorded Audio Files**: Static questions stored in S3 (no TTS needed)
- **Simple Call Flow**: Linear Q&A sequence with no complex state management

### LLM Assessment Layer - SIMPLIFIED FOR POC:
- **Amazon Bedrock**: Claude/GPT integration for transcript analysis (already exists)
- **Direct API Calls**: Simple prompt/response pattern, no complex workflow management
- **Basic Scoring**: Simple qualification determination (approved/rejected/needs_review)
- **S3 Result Storage**: JSON files instead of complex database schemas

## Design Patterns in Use

### Template Configuration Pattern:
- **Central Config System**: `project.config.ts` as single source of truth
- **Resource Name Generation**: `generateResourceName()`, `generateFunctionName()`, `generateBucketName()`
- **Stage-Aware Deployment**: dev/staging/production with environment-specific settings
- **Never hardcode**: All project-specific values flow through configuration

### Simplified Event-Driven Architecture (POC):
- **Direct Lambda Triggers**: Simple function calls, no complex event handling
- **Twilio Webhooks**: Single callback URL for call completion status
- **S3 File Storage**: JSON results and audio files, no event triggers needed
- **No Persistent State**: Stateless functions, call data stored in S3

### Simplified Handler Pattern (POC):
- **Single Handler**: `assessment_handler.py` for all assessment logic
- **Minimal Services**: Direct Twilio API calls, direct Bedrock API calls
- **Basic Data Structures**: Python dicts and JSON files, no complex models
- **No Utility Layer**: Inline logic sufficient for POC scope

## Data Flow

### Simplified Assessment Workflow (POC):
1. **Initiation**: Lambda function triggered with worker phone number and skill type
2. **Call**: Twilio immediately places outbound call to worker
3. **Static Q&A**: Pre-recorded questions played, worker responses collected via STT
4. **Analysis**: Combined transcript sent to Bedrock for skills evaluation
5. **Storage**: Assessment results saved as JSON file to S3
6. **Complete**: Simple success/failure response, no complex integration

### Simplified Call Session Flow (POC):
1. **Direct Call**: Lambda triggers Twilio call with pre-built TwiML flow
2. **Audio Playback**: S3-hosted audio files played via Twilio <Play> verb
3. **Speech Collection**: <Gather speech="true"> collects and transcribes responses
4. **No State Management**: Simple linear flow, no persistent session state
5. **Immediate Processing**: All responses collected, sent to Bedrock at call end

## Key Technical Decisions

### SST Framework Selection:
- **Rationale**: Migrated from AWS CDK to SST v3 for better developer experience
- **Implementation**: Pulumi-based infrastructure with `sst.aws.Bucket` patterns
- **Benefits**: Simplified deployment, better local development, improved configuration management

### Python Lambda Runtime:
- **Rationale**: Python 3.12 for AI/ML ecosystem compatibility (LangChain, boto3, ML libraries)
- **Implementation**: Modular handler structure with specialized services
- **Benefits**: Rich AI library ecosystem, rapid development for assessment logic

### DynamoDB for State Management:
- **Rationale**: NoSQL flexibility for varied assessment data structures
- **Implementation**: Multiple tables for WorkerSkillAssessments, SkillTemplates, CallSessions
- **Benefits**: Scalable, stage-aware, integrated with SST template patterns

### Amazon Bedrock for LLM:
- **Rationale**: Managed service with enterprise compliance and multiple model support
- **Implementation**: Integrated through existing `llm_service.py` pattern from template
- **Benefits**: Compliance-ready, multi-model flexibility, AWS native integration

### Bilingual Architecture:
- **Rationale**: Support English and Spanish for wider worker accessibility
- **Implementation**: Language detection, dynamic Transcribe/Polly model switching, multilingual prompts
- **Benefits**: Increased conversion rates, competitive advantage in Hispanic markets

## Component Relationships

### Template Integration Pattern:
- **Preserve**: Core SST template structure (`infra/*.ts`, `sst.config.ts`)
- **Extend**: Lambda handlers with specialized assessment logic
- **Configure**: `project.config.ts` modified for voice calling and AI services
- **Safe Customization**: Handler business logic, dependencies, configuration values

### Assessment Flow Dependencies:
- **Voice Service → Transcribe**: Real-time audio stream processing
- **Transcribe → LLM Service**: Transcript analysis and response generation  
- **LLM Service → Polly**: Text-to-speech response delivery
- **Assessment Results → Integration APIs**: Results posting to Gravy Work platform

### Data Storage Relationships:
- **S3**: Immutable storage for recordings, transcripts, generated resumes
- **DynamoDB**: Mutable state for ongoing assessments, worker profiles, skill templates
- **SQS**: Decoupled processing for assessment analysis and result generation

---

*This document captures the system architecture and design patterns used in the project, extending the SST template for AI-powered workforce assessment.*
