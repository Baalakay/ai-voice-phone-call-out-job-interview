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

### AI Voice Calling Layer - PRODUCTION IMPLEMENTATION:
- **Twilio Voice API**: Advanced outbound calls with sophisticated TwiML flow control
- **ElevenLabs Audio Files**: Professional "Rachel" voice for all 31 assessment questions
- **Complex Call Flow**: Multi-question sequences with state management, timeout handling, repeat functionality
- **Interactive Controls**: Star (*) key for question repeat, pound (#) key for answer submission

### LLM Assessment Layer - PRODUCTION IMPLEMENTATION:
- **Amazon Bedrock**: Integrated transcript analysis with assessment scoring (operational)
- **Advanced Webhook Processing**: Complex state management across multiple Lambda invocations
- **Sophisticated Scoring**: Multi-criteria evaluation with role-specific assessment templates
- **S3 Result Storage**: Comprehensive JSON-based storage with error recovery and state persistence

## Design Patterns in Use

### Template Configuration Pattern:
- **Central Config System**: `project.config.ts` as single source of truth
- **Resource Name Generation**: `generateResourceName()`, `generateFunctionName()`, `generateBucketName()`
- **Stage-Aware Deployment**: dev/staging/production with environment-specific settings
- **Never hardcode**: All project-specific values flow through configuration

### Production Event-Driven Architecture:
- **Advanced Lambda Triggers**: Sophisticated webhook handling with state management
- **Twilio Webhooks**: Multiple callback URLs for different call states and user interactions
- **S3 File Storage**: Professional audio assets, assessment results, web UI hosting
- **Persistent State Management**: Stateful functions with S3-based session persistence

### Production Handler Pattern:
- **Comprehensive Handler**: `webhook_simple.py` with complete assessment logic and flow control
- **Integrated Services**: Advanced Twilio API integration, ElevenLabs TTS, AWS services
- **Complex Data Structures**: Sophisticated state management, assessment templates, error handling
- **Utility Integration**: Full-featured logic with proper error recovery and user guidance

## Data Flow

### Production Assessment Workflow:
1. **Web Initiation**: User selects role and enters phone number via S3-hosted web interface
2. **Lambda Call**: Advanced Twilio integration places outbound call with proper error handling
3. **Interactive Q&A**: Professional ElevenLabs audio with star (*) repeat and pound (#) submission controls
4. **State Management**: Sophisticated session persistence across multiple webhook calls
5. **Analysis**: Real-time transcript processing with role-specific evaluation criteria
6. **Storage**: Comprehensive assessment results with proper error recovery
7. **Completion**: Graceful call termination with user feedback and result availability

### Production Call Session Flow:
1. **Advanced Call Setup**: Lambda triggers Twilio with complex TwiML flow and webhook routing
2. **Professional Audio**: ElevenLabs "Rachel" voice files served from S3 with proper permissions
3. **Interactive Collection**: Advanced <Record> and <Gather> with timeout handling and user controls
4. **Persistent State**: Robust session management across multiple Lambda invocations
5. **Real-time Processing**: Continuous state updates with proper error handling and recovery

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
