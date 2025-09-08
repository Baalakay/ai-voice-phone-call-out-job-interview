# Gravy Work AI Skills Assessment Platform - POC

## 🎯 Business Use Case

**Gravy Work** is a gig work/staffing platform that connects workers with hospitality and service jobs. The current worker onboarding system creates a significant barrier to entry, resulting in poor conversion rates and competitive disadvantage.

## 🚨 Core Problem Statement

### Current "Willow" System Issues:
- **60% candidate drop-off rate** due to poor user experience with video interviews
- **High barrier to entry** requiring upfront completion of:
  - Video skill assessments
  - Background checks
  - I-9 verification
  - Multiple screening steps
- **Manual processing bottleneck** for high-volume skill assessments
- **Competitive disadvantage** - competitors have simpler onboarding flows

### Business Impact:
- Reduced worker acquisition and retention
- Increased cost per successful onboarding
- Operational inefficiency in skill verification
- Poor user experience affecting brand perception

## 💡 Proposed Solution: AI Voice-Based Skills Assessment

Replace the current video interview system with an **AI Voice Agent** that conducts phone-based skills assessments, enabling a lower-friction onboarding experience.

### Core Functionality:
1. **Automated Phone Interviews** - AI calls workers for 3-5 minute skill assessments
2. **Multi-Skill Assessment** - Single call can assess multiple related skills
3. **Bilingual Support** - English and Spanish language capability
4. **Resume Generation** - Automatically capture and structure work history
5. **Skills Hierarchy** - Auto-approve related skills based on qualifications

### Assessment Categories:

#### High-Priority Skills (Customer-Facing/High-Risk):
- **Bartender** - Drink knowledge, customer service, certification verification
- **Host/Hostess** - Communication skills, English proficiency, customer interaction
- **Grill Cook** - Food safety, cooking techniques, English for order communication
- **Line Cook** - Professional kitchen experience, teamwork, food preparation

#### High-Volume Skills:
- **Banquet Server** - Service experience, event coordination
- **Food Runner** - Restaurant operations, communication skills

### Technical Assessment Requirements:

#### 1. **Technical Skill Competency**
- Job-specific knowledge verification
- Experience validation through structured questioning
- Practical scenario-based assessment

#### 2. **English Language Proficiency**
- **Requirement varies by role:**
  - Customer-facing positions: Conversational English required
  - Kitchen/back-of-house: Basic communication sufficient
- **Assessment approach:** Conduct interview in English for qualifying roles
- **Fallback:** Support Spanish-speaking candidates for non-customer-facing roles

#### 3. **Work History Capture**
- Structured collection of previous relevant experience
- Automatic resume generation from interview responses
- Employment verification data collection

#### 4. **Certification Verification**
- State-specific requirements (TIPS alcohol service, food handling)
- Document upload integration for certification proof
- Binary qualification flags for compliant roles

## 🏗️ Implementation Architecture

### Current Infrastructure:
- **AWS-based** (S3, RDS, existing data storage)
- **No current AI/ML implementation**
- **Existing user management and skill tracking systems**

### Integration Points:
- Worker profile management system
- Skill application workflow
- Scheduling and notification systems
- Compliance and audit trail requirements

## 📊 Success Metrics

### Primary KPIs:
- **Conversion Rate Improvement** - Reduce drop-off from 60% baseline
- **Time to Skill Approval** - Reduce from current manual process time
- **Assessment Accuracy** - Validate skill predictions against job performance
- **User Satisfaction** - Worker experience ratings improvement

### Secondary Metrics:
- **Cost per Assessment** - Operational efficiency vs manual screening
- **Scalability** - Volume capacity compared to current bottlenecks
- **Compliance** - Audit trail and bias prevention measures

## 🚀 POC Scope & Deliverables

### Phase 1 - Core Voice Assessment:
- AI voice calling capability for 3-5 priority skills
- English language assessment integration
- Basic work history capture
- Integration with existing worker profile system

### Phase 2 - Enhanced Features:
- Bilingual (Spanish) support implementation
- Multi-skill assessment in single call
- Automated resume generation
- Skills hierarchy and auto-approval logic

### Phase 3 - Production Readiness:
- Full skill set coverage (30+ skills)
- Advanced scheduling and notification system
- Comprehensive audit and compliance features
- Performance analytics and optimization

## 💼 Business Value Proposition

1. **Improved Worker Acquisition** - Lower barrier to entry increases conversion rates
2. **Operational Efficiency** - Automated assessment reduces manual processing
3. **Better User Experience** - Convenient phone-based vs video interview system
4. **Competitive Advantage** - Match or exceed competitor onboarding simplicity
5. **Scalability** - Handle volume growth without proportional staff increases
6. **Data Quality** - Structured collection improves matching and performance tracking

---

**Project Timeline:** 4-week POC development with AWS integration
**Primary Stakeholder:** Bobby Sherwood, Gravy Work
**Technical Partner:** Extension/Blake McDonald (AI/ML Implementation)