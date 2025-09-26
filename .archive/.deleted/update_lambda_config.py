#!/usr/bin/env python3
"""
Update Lambda Environment Variables for Twilio Integration

This script updates the deployed Lambda function with the correct Twilio 
configuration and API Gateway webhook URLs.
"""

import boto3
import json

def update_lambda_environment():
    """Update Lambda function environment variables."""
    
    # Initialize Lambda client
    lambda_client = boto3.client('lambda')
    
    # Lambda function name (from our deployment)
    function_name = "gravywork-processor-dev"
    
    # Get current environment variables
    try:
        response = lambda_client.get_function(FunctionName=function_name)
        current_env = response['Configuration']['Environment']['Variables']
        print(f"📋 Current Lambda environment variables:")
        for key, value in current_env.items():
            if 'TWILIO' in key:
                print(f"   {key}: {value}")
    except Exception as e:
        print(f"❌ Error getting Lambda function: {str(e)}")
        return False
    
    # Updated environment variables
    updated_env = current_env.copy()
    updated_env.update({
        'TWILIO_WEBHOOK_URL': 'https://eih1khont2.execute-api.us-east-1.amazonaws.com',
        # Note: TWILIO_AUTH_TOKEN should be set manually for security
    })
    
    print(f"\n🔧 Updating Lambda environment variables...")
    
    try:
        lambda_client.update_function_configuration(
            FunctionName=function_name,
            Environment={'Variables': updated_env}
        )
        
        print(f"✅ Lambda environment updated successfully!")
        print(f"\n📝 Updated variables:")
        print(f"   TWILIO_WEBHOOK_URL: https://eih1khont2.execute-api.us-east-1.amazonaws.com")
        print(f"\n⚠️  MANUAL STEP REQUIRED:")
        print(f"   You need to manually set TWILIO_AUTH_TOKEN in the AWS Lambda console")
        print(f"   Go to: AWS Lambda → {function_name} → Configuration → Environment variables")
        print(f"   Add: TWILIO_AUTH_TOKEN = [your Twilio Auth Token]")
        
        return True
        
    except Exception as e:
        print(f"❌ Error updating Lambda: {str(e)}")
        return False

def create_twilio_webhook_guide():
    """Create guide for configuring Twilio webhooks."""
    
    guide = """
🎯 TWILIO WEBHOOK CONFIGURATION GUIDE
====================================

📞 Phone Number: (472) 236-8895
🔗 API Gateway URL: https://eih1khont2.execute-api.us-east-1.amazonaws.com

WEBHOOK CONFIGURATION STEPS:
1. Login to your Twilio Console (https://console.twilio.com)
2. Go to Phone Numbers → Manage → Active numbers
3. Click on (472) 236-8895
4. In "Voice Configuration" section:
   - Webhook: https://eih1khont2.execute-api.us-east-1.amazonaws.com/webhook
   - HTTP Method: POST
5. In "Status Callback" section:
   - URL: https://eih1khont2.execute-api.us-east-1.amazonaws.com/webhook/status
   - Method: POST
6. Click "Save Configuration"

WEBHOOK ENDPOINTS:
- /webhook           → Initial call handler
- /webhook/status    → Call status updates
- /question/{id}     → Question flow
- /complete/{id}     → Assessment completion
- /initiate          → Start new assessment

TESTING:
After configuration, you can:
1. Call (472) 236-8895 to test the assessment flow
2. Use /initiate endpoint to trigger outbound calls
3. Check S3 bucket for assessment results

TROUBLESHOOTING:
- Check AWS Lambda logs in CloudWatch
- Verify S3 audio files are accessible
- Confirm Twilio Auth Token is set in Lambda environment
"""
    
    with open('twilio_webhook_setup_guide.txt', 'w') as f:
        f.write(guide)
    
    print(guide)
    
    return True

if __name__ == "__main__":
    print("🔧 AI Skills Assessment POC - Final Configuration")
    print("=" * 60)
    
    # Update Lambda environment
    lambda_updated = update_lambda_environment()
    
    print("\n" + "=" * 60)
    
    # Create webhook guide
    guide_created = create_twilio_webhook_guide()
    
    if lambda_updated and guide_created:
        print("\n🚀 CONFIGURATION READY!")
        print("Complete the manual Twilio Auth Token step and webhook configuration.")
        print("Then your AI Skills Assessment POC will be fully operational!")
    else:
        print("\n⚠️  Some configuration steps failed. Please check the errors above.")
