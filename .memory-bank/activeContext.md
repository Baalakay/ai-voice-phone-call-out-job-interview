# Active Context: Gravy Work AI Skills Assessment Platform
*Version: 1.0*
*Created: $(date)*
*Last Updated: $(date)*
*Current RIPER Mode: INITIALIZING*

## Current Focus
Setting up the foundational AI Skills Assessment platform by extending the SST AWS Project Template. The template provides S3 bucket, Lambda functions, DynamoDB, and SQS infrastructure - we need to add voice calling, LLM integration, and bilingual assessment capabilities.

## Template State Assessment

### Template Foundation (✅ Available):
- **Infrastructure Stack**: S3, SQS, DynamoDB, Lambda framework established
- **Configuration System**: `project.config.ts` for centralized project settings
- **Deployment Pipeline**: SST v3 with dev/staging/production stages
- **Development Environment**: VS Code devcontainer with Python 3.12 and Node.js
- **Basic LLM Integration**: `llm_config.py` and `bedrock_service.py` foundation exists

### Template Characteristics:
- **Generic Nature**: Currently configured for general AWS serverless applications
- **Configuration-Driven**: All project-specific settings flow through `project.config.ts`
- **Stage-Aware**: Different behavior for dev/staging/production deployments
- **DevContainer Ready**: Includes AWS CLI, Python, Node.js development tools

## Files Safe to Customize vs. Preserve

### 🛠️ SAFE TO CUSTOMIZE:
- **`project.config.ts`**: Primary configuration file - modify for voice and AI services
- **`functions/src/handlers/index.py`**: Main Lambda handler - customize for assessment logic
- **`functions/src/config/llm_config.py`**: LLM configuration - extend for assessment prompts
- **`requirements.txt`**: Runtime dependencies - add AI/voice service libraries
- **`requirements-dev.txt`**: Development dependencies - add testing tools
- **`README.md`**: Project documentation

### 🚫 PRESERVE TEMPLATE STRUCTURE:
- **`infra/infrastructure.ts`**: Keep generic, config-driven infrastructure
- **`infra/application.ts`**: Preserve Lambda and S3 trigger patterns
- **`sst.config.ts`**: SST framework configuration
- **`init-new-project.sh`**: Project initialization script
- **`.cursorrules`**: Template guidelines and rules

## Recent Changes
- **Framework Initialization**: CursorRIPER Framework installed with START phase active
- **Project Requirements Review**: Analyzed 4 PRD documents for project context
- **Memory Bank Creation**: Established comprehensive project knowledge base
- **Template Analysis**: Evaluated existing SST template capabilities for AI assessment use case

## Active Decisions

### Voice Service Provider:
- **Status**: PENDING - Need to decide between AWS Connect vs Twilio
- **AWS Connect**: Native AWS integration, potentially better Transcribe/Polly integration
- **Twilio**: Mature voice API, extensive documentation, proven call quality
- **Recommendation**: Start with AWS Connect for tighter AWS ecosystem integration

### Assessment Architecture:
- **Status**: PLANNED - Extend existing Lambda handler pattern
- **Approach**: Create specialized handlers (assessment, voice, integration)
- **Services**: Add voice_service.py, assessment_service.py, resume_service.py
- **Models**: Add worker.py, skill.py, assessment.py for data validation

### Bilingual Implementation:
- **Status**: RESEARCH NEEDED - Language detection and switching strategies
- **Language Detection**: TextBlob vs AWS Comprehend vs user preference
- **Dynamic Switching**: Call flow changes based on detected/preferred language
- **Prompt Engineering**: Separate prompt templates for English/Spanish assessments

## Next Steps

### Immediate (Week 1-2 - Phase 1):
1. **Configure Voice Service Integration**: Choose and implement AWS Connect or Twilio
2. **Extend Lambda Handlers**: Add assessment_handler.py, voice_handler.py modules
3. **Set Up LLM Assessment Logic**: Extend existing Bedrock integration for skills evaluation
4. **Create DynamoDB Schema**: Add WorkerSkillAssessments, SkillTemplates, CallSessions tables
5. **Build Basic Assessment Flow**: End-to-end test with 1-2 priority skills (English only)

### Near-term (Week 3 - Phase 2):
1. **Implement Bilingual Support**: Spanish language integration for Transcribe/Polly
2. **Add Resume Generation**: Service to create structured resumes from assessment data
3. **Multi-skill Assessment**: Logic to assess multiple related skills in single call
4. **Gravy Work Integration**: API endpoints for existing platform communication

### Medium-term (Week 4 - Phase 3):
1. **Full Skill Template Coverage**: Expand from 3-5 skills to broader assessment capability
2. **Enhanced Compliance**: Audit trails, bias prevention, call recording management
3. **Performance Optimization**: Concurrent call handling, response time improvement
4. **Production Deployment**: Staging validation and production readiness

## Current Challenges

### Technical Integration:
- **Real-time Voice Processing**: Achieving sub-second response times for natural conversation
- **Bilingual Switching**: Seamless language detection and response generation
- **Assessment Accuracy**: Balancing thoroughness with 3-5 minute call duration limit

### Template Extension:
- **Preserve Generic Nature**: Adding AI capabilities while maintaining template reusability
- **Configuration Complexity**: Managing voice service, AI service, and bilingual settings
- **Infrastructure Scaling**: Voice service capacity planning and cost optimization

### Business Integration:
- **Existing Platform APIs**: Understanding Gravy Work's current worker management system
- **Compliance Requirements**: EEOC guidelines, call recording consent, bias prevention
- **Skills Definition**: Translating job requirements into assessable conversation flows

## Implementation Progress

### ✅ Completed:
- [✓] CursorRIPER Framework initialization and START phase setup
- [✓] Project requirements analysis from PRD documents
- [✓] Memory bank establishment with comprehensive project knowledge
- [✓] Template foundation assessment and customization planning

### 🔄 In Progress:
- [ ] Voice service provider selection and integration setup
- [ ] Lambda handler architecture design and initial implementation
- [ ] DynamoDB schema design for assessment data structures

### 📋 Pending:
- [ ] AI assessment prompt engineering for hospitality skills
- [ ] Bilingual conversation flow design and implementation  
- [ ] Gravy Work platform API integration points
- [ ] Compliance and audit trail implementation
- [ ] End-to-end testing with real assessment scenarios

---

*This document captures the current state of work and immediate next steps for extending the SST template into an AI-powered skills assessment platform.*
