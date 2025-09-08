# Technical Customizations Required for Gravy Work AI Skills Assessment POC

## 🔧 Infrastructure Modifications Needed

### Current SST Template Foundation:
✅ **Keep As-Is:**
- S3 Bucket for data storage (call recordings, transcripts, resumes)  
- SQS Queue for async processing workflow
- DynamoDB for worker profiles and assessment data
- Lambda function framework (Python 3.12)
- AWS CDK/SST infrastructure as code

### 🆕 New Components Required:

#### 1. **AI Voice Calling Infrastructure**
- **AWS Connect** or **Twilio Voice API** integration
- **Amazon Transcribe** for real-time speech-to-text
- **Amazon Polly** for text-to-speech (bilingual support)
- **Call routing and management system**

#### 2. **LLM Integration for Assessment**
- **Amazon Bedrock** for Claude/GPT integration
- **Custom prompt engineering** for skills assessment
- **Conversation flow management** for interview logic
- **Response analysis and scoring algorithms**

#### 3. **Data Storage Extensions**
- **Call recordings** storage in S3 with lifecycle policies
- **Assessment transcripts** for compliance and audit
- **Worker skill profiles** and assessment history
- **Resume generation** templates and storage

#### 4. **Bilingual Support**
- **Language detection** from user preferences
- **Spanish language models** for Transcribe/Polly
- **Multilingual prompt templates** for LLM assessments
- **Dynamic language switching** during interviews

## 🛠️ Lambda Function Customizations

### Primary Handler Updates (`functions/src/handlers/index.py`):

```python
# Current: Generic processing template
# Required: Specialized handlers for:

1. skill_assessment_initiator()
   - Trigger assessment calls from worker skill applications
   - Queue management for call scheduling
   - Integration with existing worker profile system

2. voice_call_handler()
   - Real-time conversation management
   - Speech recognition and response generation
   - Call flow state management
   - Bilingual language handling

3. assessment_evaluator()
   - LLM-based transcript analysis
   - Skills scoring and qualification determination
   - Resume generation from captured work history
   - Skills hierarchy and cross-skill recommendations

4. integration_webhook()
   - Callback handling from voice service providers
   - Status updates to main worker platform
   - Audit trail and compliance logging
```

### 📁 New Module Structure:
```
functions/src/
├── handlers/
│   ├── index.py                 # Main entry points
│   ├── assessment_handler.py    # Skills assessment logic
│   ├── voice_handler.py         # Voice call management
│   └── integration_handler.py   # External system integration
├── services/
│   ├── voice_service.py         # Voice calling abstraction
│   ├── llm_service.py          # LLM interaction (extend existing)
│   ├── assessment_service.py    # Skills evaluation logic
│   └── resume_service.py        # Resume generation
├── models/
│   ├── worker.py               # Worker profile models
│   ├── skill.py                # Skill definition models
│   └── assessment.py           # Assessment result models
└── utils/
    ├── language_utils.py       # Bilingual support utilities
    ├── compliance_utils.py     # Audit and bias prevention
    └── integration_utils.py    # External API helpers
```

## 📊 Database Schema Extensions

### DynamoDB Tables to Add/Modify:

#### 1. **WorkerSkillAssessments** Table
```json
{
  "workerId": "string",
  "skillId": "string", 
  "assessmentDate": "timestamp",
  "status": "pending|in_progress|completed|failed",
  "transcriptS3Key": "string",
  "recordingS3Key": "string",
  "score": "number",
  "qualificationResult": "approved|rejected|needs_review",
  "language": "en|es",
  "duration": "number",
  "assessmentData": {
    "workHistory": [],
    "responses": [],
    "certifications": []
  }
}
```

#### 2. **SkillTemplates** Table
```json
{
  "skillId": "string",
  "skillName": "string",
  "category": "customer_facing|kitchen|general",
  "englishRequired": "boolean",
  "assessmentQuestions": [],
  "evaluationCriteria": {},
  "estimatedDuration": "number",
  "relatedSkills": []
}
```

#### 3. **CallSessions** Table
```json
{
  "sessionId": "string",
  "workerId": "string",
  "skillIds": ["string"],
  "callStatus": "scheduled|active|completed|failed",
  "scheduledTime": "timestamp",
  "actualStartTime": "timestamp",
  "language": "en|es",
  "voiceCallId": "string"
}
```

## 🔗 Integration Points

### External Services Required:
1. **Voice Calling Service** (AWS Connect or Twilio)
2. **Speech Services** (Transcribe + Polly)
3. **LLM Service** (Bedrock with Claude/GPT)
4. **Existing Gravy Work Platform APIs** for:
   - Worker profile management
   - Skill application workflow
   - Notification systems

### API Endpoints to Create:
- `POST /api/assessments/initiate` - Start skill assessment process
- `POST /api/assessments/schedule` - Schedule AI interview call
- `GET /api/assessments/{assessmentId}/status` - Check assessment status
- `POST /api/webhooks/voice-callback` - Handle voice service callbacks
- `GET /api/skills/templates` - Retrieve skill assessment templates

## 🚨 Compliance & Audit Requirements

### Data Handling:
- **Call recording retention** with configurable lifecycle
- **Transcript storage** for bias analysis and appeals
- **Assessment decision audit trails**
- **PII data protection** and encryption at rest

### Bias Prevention:
- **Standardized question sets** per skill type
- **Consistent evaluation criteria** across candidates
- **Language proficiency standards** documentation
- **Statistical monitoring** for demographic bias

## 📦 Additional Dependencies

### Python Requirements (`requirements.txt` additions):
```
boto3>=1.34.0                    # Enhanced AWS SDK features
twilio>=8.0.0                    # Voice calling (if using Twilio)
amazon-transcribe-streaming       # Real-time transcription
langchain>=0.1.0                 # LLM workflow management
pydantic>=2.0.0                  # Data validation models
phonenumbers>=8.13.0             # Phone number validation
textblob>=0.17.1                 # Language detection
fastapi>=0.100.0                 # API framework
celery>=5.3.0                    # Task queue management
redis>=5.0.0                     # Caching and session management
```

### Infrastructure Dependencies:
```typescript
// Additional CDK/SST resources needed in infrastructure files:
- AWS Connect Contact Flow (or Twilio integration)
- API Gateway with WebSocket support for real-time calls  
- ElastiCache Redis for call session management
- CloudWatch Logs with enhanced retention for compliance
- IAM roles for cross-service communication
- Lambda layers for shared utilities and models
```

---

## 🎯 POC Implementation Priority

### Phase 1 (Week 1-2): Core Assessment Engine
1. Basic voice calling integration (single language)
2. Simple skills assessment (3 priority skills)  
3. Transcript analysis and basic scoring
4. Integration with existing worker profiles

### Phase 2 (Week 3): Enhanced Features
1. Bilingual support implementation
2. Resume generation functionality
3. Multi-skill assessment capability
4. Audit trail and compliance features

### Phase 3 (Week 4): Production Polish
1. Full skills template coverage
2. Advanced scheduling and notifications
3. Performance optimization
4. Comprehensive testing and documentation

This technical foundation will transform the generic SST template into a specialized AI-powered workforce assessment platform tailored for Gravy Work's specific business requirements.
