# Cursor AI Agent Rules for SST AWS Project Template

## 🎯 PROJECT OVERVIEW
This is a **reusable AWS SST template** for serverless applications, not a specific project. The goal is to maintain a clean, configurable template that can be used to initialize new projects.

## 🏗️ TEMPLATE ARCHITECTURE
- **Infrastructure Stack** (`infra/infrastructure.ts`): Core AWS resources (S3, SQS, DynamoDB)
- **Application Stack** (`infra/application.ts`): Lambda functions and event triggers
- **Central Configuration** (`project.config.ts`): Single source of truth for all project settings
- **Lambda Handler** (`functions/src/handlers/index.py`): Customizable Python function template
- **LLM Integration** (`functions/src/config/llm_config.py` + `functions/src/functions/bedrock_service.py`): Optional Bedrock integration

## ⚙️ CONFIGURATION SYSTEM
- **PRIMARY CONFIG**: `project.config.ts` - Controls ALL project-specific settings
- **NEVER hardcode** project names, regions, or resource names in infra files
- Use helper functions: `generateResourceName()`, `generateFunctionName()`, `generateBucketName()`
- Environment-specific settings in `projectConfig.stages`

## 🚫 CRITICAL: DO NOT MODIFY THESE TEMPLATE FILES
Unless explicitly requested, preserve the template structure:
- `infra/infrastructure.ts` - Keep generic, config-driven
- `infra/application.ts` - Keep generic, config-driven  
- `sst.config.ts` - Template structure
- `init-new-project.sh` - Initialization script
- `.cursorrules` - This file

## ✅ SAFE TO CUSTOMIZE
- `project.config.ts` - Primary configuration (but explain changes)
- `functions/src/handlers/index.py` - Lambda function logic
- `functions/src/config/llm_config.py` - LLM settings
- `requirements.txt` / `requirements-dev.txt` - Dependencies
- `README.md` - Documentation

## 🛠️ DEVELOPMENT WORKFLOW
1. **New Projects**: Run `./init-new-project.sh` first
2. **Deploy**: `sst deploy --stage dev|staging|production`
3. **Development**: Use devcontainer environment
4. **Dependencies**: Use `uv` for Python package management

## 📁 KEY FILE PURPOSES
- `project.config.ts` - Central configuration, modify this for project settings
- `infra/infrastructure.ts` - Shared AWS resources (S3, SQS, DynamoDB)
- `infra/application.ts` - Lambda functions and event triggers
- `functions/src/handlers/index.py` - Main Lambda handler (customize business logic here)
- `functions/src/config/llm_config.py` - LLM/Bedrock configuration
- `init-new-project.sh` - Project initialization script
- `requirements.txt` - Runtime dependencies only
- `requirements-dev.txt` - Development/testing tools

## 🎨 CODING PREFERENCES
- **TypeScript**: Use for infrastructure code
- **Python 3.12**: Lambda runtime
- **SST Framework**: Not AWS CDK (we migrated away from CDK)
- **Configuration-driven**: No hardcoded values
- **Environment variables**: Use for runtime overrides
- **Type safety**: Maintain TypeScript types in config

## 🔧 SST SPECIFIC NOTES
- Uses SST v3 (not CDK)
- Pulumi-based under the hood
- `sst.aws.Bucket` not `aws.s3.Bucket` for new resources
- `aws.s3.BucketV2.get()` for referencing existing buckets
- Stage-aware resource naming

## 🚨 COMMON MISTAKES TO AVOID
- Don't add hardcoded resource names to infrastructure files
- Don't modify the initialization script without understanding impact
- Don't change the central config structure without updating helper functions
- Don't add development dependencies to requirements.txt
- Don't remove the template's flexibility for project-specific needs

## 🤝 WHEN HELPING WITH THIS TEMPLATE
1. **Always ask** what type of project they're building before suggesting changes
2. **Preserve template nature** - don't make it project-specific
3. **Use configuration system** - show how to modify project.config.ts
4. **Explain the template approach** when making suggestions
5. **Test suggestions** against multiple use cases
6. **Document changes** in README.md if they affect template usage

## 💡 TEMPLATE PHILOSOPHY
This template provides:
- **Consistency** across projects
- **Best practices** out of the box
- **Flexibility** through configuration
- **Easy initialization** for new projects
- **DevContainer ready** development environment
- **Stage-aware** deployment (dev/staging/production)

When in doubt, preserve the template's generic nature and show users how to configure it rather than hard-coding project-specific details.
