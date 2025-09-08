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

### AI Voice Calling Layer (New):
- **AWS Connect or Twilio Voice API**: Voice calling infrastructure
- **Amazon Transcribe**: Real-time speech-to-text with bilingual support
- **Amazon Polly**: Text-to-speech for bilingual conversations
- **Call Management System**: Session routing and state management

### LLM Assessment Layer (New):
- **Amazon Bedrock**: Claude/GPT integration for assessment analysis
- **Custom Prompt Engineering**: Skills-specific conversation flows
- **Response Analysis**: Scoring algorithms and qualification determination
- **Conversation Flow Management**: Interview logic and state transitions

## Design Patterns in Use

### Template Configuration Pattern:
- **Central Config System**: `project.config.ts` as single source of truth
- **Resource Name Generation**: `generateResourceName()`, `generateFunctionName()`, `generateBucketName()`
- **Stage-Aware Deployment**: dev/staging/production with environment-specific settings
- **Never hardcode**: All project-specific values flow through configuration

### Event-Driven Architecture:
- **S3 Event Triggers**: Lambda functions triggered by file uploads to `input/` prefix
- **SQS Processing**: Asynchronous workflow for long-running assessments
- **Webhook Callbacks**: External voice service integration points
- **State Management**: DynamoDB for persistent workflow state

### Microservices Pattern:
- **Specialized Handlers**: `assessment_handler.py`, `voice_handler.py`, `integration_handler.py`
- **Service Layer**: `voice_service.py`, `llm_service.py`, `assessment_service.py`, `resume_service.py`
- **Model Layer**: `worker.py`, `skill.py`, `assessment.py` for data validation
- **Utility Layer**: Language, compliance, and integration utilities

## Data Flow

### Assessment Workflow:
1. **Initiation**: Worker skill application triggers assessment via `/api/assessments/initiate`
2. **Scheduling**: System schedules AI interview call via voice service integration
3. **Conversation**: Real-time voice call with AI agent conducting structured interview
4. **Processing**: Transcript analysis through LLM for skills evaluation and scoring
5. **Results**: Qualification determination and resume generation
6. **Integration**: Results posted back to Gravy Work platform with audit trail

### Call Session Flow:
1. **Session Creation**: CallSessions DynamoDB record with scheduled time and skill IDs
2. **Call Initiation**: Voice service places call to worker phone number
3. **Real-time Processing**: Transcribe converts speech, LLM generates responses, Polly speaks responses
4. **State Persistence**: Conversation state maintained in DynamoDB throughout call
5. **Completion**: Final assessment scoring and qualification determination

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
