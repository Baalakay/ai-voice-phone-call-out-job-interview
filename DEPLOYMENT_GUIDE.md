# Deployment Guide: AI Skills Assessment Platform

## 🔐 How Credentials Work in AWS Deployment

### Credential Flow Overview
```
Your Machine (Environment Variables) 
    ↓
project.config.ts (Build Time)
    ↓  
infra/application.ts (Deployment Time)
    ↓
AWS Lambda Environment Variables (Runtime)
    ↓
Python Functions (os.environ.get)
```

### Step-by-Step Process

#### 1. Set Environment Variables (Your Machine)
```bash
# Option A: Use the setup script
./setup-env.sh

# Option B: Set manually
export TWILIO_ACCOUNT_SID="AC4e658dd5cf5c6e36514e5bae7f4c1bf7"
export TWILIO_AUTH_TOKEN="db19869a6764956183410a5169a41ab0"
```

#### 2. Build Time (project.config.ts)
```typescript
twilio: {
  accountSid: process.env.TWILIO_ACCOUNT_SID || "PLACEHOLDER_ACCOUNT_SID",
  authToken: process.env.TWILIO_AUTH_TOKEN || "PLACEHOLDER_AUTH_TOKEN",
}
```
**What happens**: Node.js reads your environment variables and populates the config.

#### 3. Deployment Time (infra/application.ts)
```typescript
const twilioConfig = getTwilioConfig(stage);

environment: {
  TWILIO_ACCOUNT_SID: twilioConfig.accountSid,  // ← Gets actual credential
  TWILIO_AUTH_TOKEN: twilioConfig.authToken,    // ← Gets actual credential
}
```
**What happens**: SST creates Lambda functions with these environment variables.

#### 4. Runtime (AWS Lambda Functions)
```python
# webhook_simple.py
TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')  # ← Gets actual credential
TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')    # ← Gets actual credential

# assessment_processor_simple.py  
twilio_account_sid = os.environ.get('TWILIO_ACCOUNT_SID')  # ← Gets actual credential
twilio_auth_token = os.environ.get('TWILIO_AUTH_TOKEN')    # ← Gets actual credential
```
**What happens**: Python functions read credentials from Lambda environment variables.

## 🚀 Deployment Commands

### Full Deployment Process
```bash
# 1. Set credentials
./setup-env.sh

# 2. Verify credentials are set
echo "Account SID: $TWILIO_ACCOUNT_SID"
echo "Auth Token: [HIDDEN]"

# 3. Deploy to AWS
npx sst deploy --stage dev

# 4. Verify deployment
curl -X GET "https://your-api-gateway-url.amazonaws.com/health"
```

### Development vs Production
```bash
# Development deployment
export TWILIO_ACCOUNT_SID="AC4e658dd5cf5c6e36514e5bae7f4c1bf7"
export TWILIO_AUTH_TOKEN="db19869a6764956183410a5169a41ab0"
npx sst deploy --stage dev

# Production deployment (if different credentials)
export TWILIO_ACCOUNT_SID="AC_your_prod_account_sid"
export TWILIO_AUTH_TOKEN="your_prod_auth_token"
npx sst deploy --stage production
```

## ✅ Verification Steps

### 1. Check Environment Variables Are Set
```bash
echo "TWILIO_ACCOUNT_SID: ${TWILIO_ACCOUNT_SID}"
echo "TWILIO_AUTH_TOKEN: ${TWILIO_AUTH_TOKEN:0:10}..." # Show first 10 chars
```

### 2. Test Credential Resolution
```bash
node -e "
const { getTwilioConfig } = require('./project.config.ts');
const config = getTwilioConfig('dev');
console.log('AccountSID:', config.accountSid ? 'RESOLVED' : 'MISSING');
console.log('AuthToken:', config.authToken ? 'RESOLVED' : 'MISSING');
"
```

### 3. Verify Lambda Environment Variables (Post-Deployment)
Check AWS Lambda console → Function → Configuration → Environment variables
- `TWILIO_ACCOUNT_SID` should show your actual Account SID
- `TWILIO_AUTH_TOKEN` should show your actual Auth Token

### 4. Test API Calls
```bash
# Test webhook endpoint
curl -X POST "https://your-api-gateway-url.amazonaws.com/webhook" \
  -H "Content-Type: application/json" \
  -d '{"test": "connection"}'
```

## 🔧 Troubleshooting

### Issue: "PLACEHOLDER" credentials in Lambda
**Cause**: Environment variables not set before deployment
**Solution**: 
```bash
./setup-env.sh
npx sst deploy --stage dev
```

### Issue: Lambda function can't authenticate with Twilio
**Cause**: Environment variables not properly passed to Lambda
**Solution**: Check `infra/application.ts` environment section:
```typescript
environment: {
  TWILIO_ACCOUNT_SID: twilioConfig.accountSid,  // Should be actual SID
  TWILIO_AUTH_TOKEN: twilioConfig.authToken,    // Should be actual token
}
```

### Issue: "ValidationException" from Twilio
**Cause**: Invalid credentials or wrong format
**Solution**: Verify credentials in Twilio Console → Account → API Keys & Tokens

## 🔒 Security Notes

- ✅ **No hardcoded secrets** in code repository
- ✅ **Environment variables** used for credential management
- ✅ **AWS Lambda environment variables** encrypted at rest
- ✅ **setup-env.sh** in .gitignore to prevent accidental commits
- ⚠️ **Never commit** actual credentials to git
- ⚠️ **Rotate credentials** periodically for security

## 📋 File Summary

### Files with NO secrets (safe for git):
- `project.config.ts` - Uses `process.env.TWILIO_*`
- `functions/src/config/twilio_config.py` - Contains only placeholders
- `infra/application.ts` - Passes environment variables to Lambda

### Files with secrets (in .gitignore):
- `setup-env.sh` - Contains actual credentials for deployment

### Files that consume credentials:
- `functions/src/functions/webhook_simple.py` - Uses `os.environ.get()`
- `functions/src/functions/assessment_processor_simple.py` - Uses `os.environ.get()`
