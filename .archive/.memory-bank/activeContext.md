# Active Context: Gravy Work AI Skills Assessment Platform
*Version: 1.0*
*Created: 2025-01-26*
*Last Updated: 2025-01-26*
*Current RIPER Mode: START_PHASE*

## Current Focus

**Project Initialization Phase**: Transforming the generic SST AWS template into a specialized AI voice assessment platform for Gravy Work's hospitality worker screening. The template provides solid infrastructure foundation (S3, SQS, DynamoDB, Lambda) that needs AI voice capabilities and assessment logic.

## Recent Changes

- **2025-01-26**: CursorRIPER Framework initialized with complete memory bank setup
- **2025-01-26**: Project requirements documentation analyzed from .prd folder
- **2025-01-26**: Template architecture assessed for AI voice integration compatibility

## Active Decisions

- **SST Template Foundation**: APPROVED - Keep existing infrastructure stack as base, extend with AI components
- **Voice Service Selection**: PENDING - AWS Connect vs Twilio evaluation needed for outbound calling
- **LLM Service Choice**: PROPOSED - Amazon Bedrock for AWS-native integration and data sovereignty

## Next Steps

1. **Complete START Phase**: Finalize memory bank initialization and transition to RESEARCH mode
2. **Voice Service Evaluation**: Research AWS Connect vs Twilio for outbound calling requirements
3. **LLM Integration Design**: Plan Bedrock integration with conversation flow management
4. **Database Schema Design**: Extend DynamoDB with assessment tracking and skill templates
5. **Priority Skills Selection**: Define initial 3 skills for POC (bartender, host/hostess, grill cook)

## Current Challenges

- **Template Preservation vs Customization**: Balance keeping generic template structure while adding specialized AI assessment capabilities
- **Real-Time Voice Processing**: Achieve <200ms response times for natural conversation flow with LLM analysis
- **Bilingual Implementation**: Design conversation management that seamlessly switches between English/Spanish mid-call

## Implementation Progress

- [✓] **CursorRIPER Framework Setup**: Core framework files loaded and state management active
- [✓] **Project Requirements Analysis**: All .prd documents parsed and synthesized into memory bank
- [✓] **Template Architecture Review**: Existing SST infrastructure assessed for AI extensions
- [ ] **Voice Service Integration Plan**: Research and select calling service provider
- [ ] **LLM Conversation Design**: Design assessment conversation flows and prompt templates
- [ ] **Database Schema Extensions**: Add assessment tracking and skills template tables
- [ ] **Priority Skills Definition**: Create assessment templates for initial 3 hospitality skills
- [ ] **Integration API Design**: Plan webhooks and APIs for Gravy Work platform connection

## Template State Notes

**Files Safe to Customize:**
- `project.config.ts` - Update for Gravy Work specific settings and AI service configurations
- `functions/src/handlers/index.py` - Replace with assessment orchestration logic
- `requirements.txt` - Add AI/ML dependencies (Bedrock SDK, language processing libs)
- New modules in functions/src/ - Add assessment, voice, and integration services

**Files to Preserve (Template Structure):**
- `infra/infrastructure.ts` - Keep generic, config-driven resource definitions
- `infra/application.ts` - Extend but maintain template patterns for Lambda configuration  
- `sst.config.ts` - Preserve template structure, reference from central config
- `init-new-project.sh` - Keep for future template usage

---

*This document captures the current state of transforming the SST template into the Gravy Work AI Skills Assessment platform.*
