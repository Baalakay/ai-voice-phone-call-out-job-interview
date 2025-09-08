# System Patterns: Gravy Work AI Skills Assessment Platform
*Version: 1.0*
*Created: 2025-01-26*
*Last Updated: 2025-01-26*

## Architecture Overview

The system is built on an AWS SST (Serverless Stack) foundation, extending a reusable template to create specialized AI-powered workforce assessment capabilities. The architecture follows a microservices approach with event-driven processing and real-time voice interaction.

**Base Infrastructure**: S3 storage + SQS queuing + DynamoDB + Python Lambda functions
**AI Extensions**: Voice calling (AWS Connect/Twilio) + Speech services (Transcribe/Polly) + LLM integration (Bedrock)

## Key Components

- **Assessment Orchestrator**: Lambda function managing the complete assessment lifecycle from initiation to completion
- **Voice Call Handler**: Real-time conversation management with speech recognition and AI response generation
- **Skills Evaluation Engine**: LLM-based transcript analysis and scoring with qualification determination
- **Integration Layer**: Webhooks and APIs connecting to existing Gravy Work worker platform
- **Bilingual Processing**: Language detection and switching with multilingual prompt templates
- **Compliance System**: Audit trails, recording retention, and bias prevention monitoring

## Design Patterns in Use

- **Central Configuration Pattern**: Single source of truth in `project.config.ts` for all environment-specific settings
- **Infrastructure + Application Stack Separation**: Core resources isolated from application-specific Lambda functions
- **Stage-Aware Deployment**: Environment-specific resource naming and protection policies (dev/staging/production)
- **Event-Driven Processing**: S3 triggers → SQS queuing → Lambda processing for scalable async workflows
- **Template Preservation**: Generic SST template structure maintained while adding specialized functionality
- **Resource Helper Functions**: Consistent naming conventions via `generateResourceName()`, `generateFunctionName()`, `generateBucketName()`

## Data Flow

```
1. Worker applies for skill → Assessment initiated via API
2. Call scheduled → Voice service places call to worker
3. AI conversation → Real-time transcript generation
4. Assessment complete → LLM analyzes responses and scores skills  
5. Results processed → Resume generated + skill approval/rejection
6. Platform integration → Worker profile updated with new qualifications
7. Audit trail → Recording and transcript stored for compliance
```

## Key Technical Decisions

- **SST v3 over AWS CDK**: Modern serverless framework with better TypeScript integration and Pulumi backend
- **Python 3.12 Lambda Runtime**: Optimal performance for AI/ML workloads with latest language features
- **DynamoDB for Assessment Data**: NoSQL flexibility for varied skill assessment schemas and real-time access patterns
- **Bedrock for LLM Integration**: AWS-native AI service avoiding external API dependencies and data sovereignty concerns
- **Bilingual Architecture First**: Core system designed for multi-language from start rather than retrofitted
- **Template-Based Assessment**: Standardized question sets per skill type ensuring consistent evaluation and bias reduction

## Component Relationships

**Assessment Initiation**: API Gateway → Assessment Orchestrator → Call Scheduler → Voice Service
**Real-Time Processing**: Voice Handler ↔ Transcribe Service ↔ LLM Service ↔ Polly Service  
**Data Pipeline**: Assessment Results → Skills Evaluator → Resume Generator → Platform Integration
**Storage Layer**: Call recordings/transcripts → S3 | Assessment data → DynamoDB | Audit logs → CloudWatch
**Configuration Flow**: project.config.ts → Infrastructure Stack → Application Stack → Lambda Environment Variables

## Infrastructure Extensions for AI Voice

### New Components Added to Base Template:
- **Voice Calling Infrastructure**: AWS Connect contact flows or Twilio Voice API integration
- **Speech Processing Stack**: Amazon Transcribe (real-time) + Amazon Polly (multilingual)
- **LLM Integration Layer**: Bedrock service with Claude/GPT conversation management
- **Enhanced Data Storage**: Call recordings with lifecycle policies + assessment transcripts + worker skill profiles
- **Real-Time Session Management**: ElastiCache Redis for call state + WebSocket API for live updates

### Database Schema Extensions:
- **WorkerSkillAssessments**: Assessment lifecycle tracking with transcript/recording references
- **SkillTemplates**: Standardized assessment questions and evaluation criteria per skill type
- **CallSessions**: Real-time call state management with multi-skill support per session

---

*This document captures the system architecture and design patterns that transform the generic SST template into a specialized workforce assessment platform.*
