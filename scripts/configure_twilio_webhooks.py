#!/usr/bin/env python3
"""
Automated Twilio Webhook Configuration

This script programmatically configures your Twilio phone number webhooks
to point to the deployed API Gateway.
"""

from twilio.rest import Client
import sys
import os

def configure_twilio_webhooks():
    """Configure Twilio phone number webhooks."""
    
    # Twilio credentials - from your Twilio console
    account_sid = "AC4e658dd5cf5c6e36514e5bae7f4c1bf7"  # Your Live Account SID
    auth_token = "db19869a6764956183410a5169a41ab0"
    phone_number = "+14722368895"
    
    # Webhook URLs
    webhook_url = "https://eih1khont2.execute-api.us-east-1.amazonaws.com/webhook"
    status_callback_url = "https://eih1khont2.execute-api.us-east-1.amazonaws.com/webhook/status"
    
    print("🔧 Configuring Twilio Webhooks")
    print("=" * 50)
    print(f"📞 Phone Number: {phone_number}")
    print(f"🔗 Webhook URL: {webhook_url}")
    print(f"📊 Status Callback: {status_callback_url}")
    
    try:
        # Initialize Twilio client
        client = Client(account_sid, auth_token)
        
        # Find the phone number resource
        phone_numbers = client.incoming_phone_numbers.list(phone_number=phone_number)
        
        if not phone_numbers:
            print(f"❌ Phone number {phone_number} not found in your Twilio account")
            return False
        
        phone_number_resource = phone_numbers[0]
        
        # Update webhook configuration
        phone_number_resource.update(
            voice_url=webhook_url,
            voice_method='POST',
            status_callback=status_callback_url,
            status_callback_method='POST'
        )
        
        print("✅ Webhook configuration updated successfully!")
        
        # Verify configuration
        updated_number = client.incoming_phone_numbers(phone_number_resource.sid).fetch()
        print(f"\n📋 Current Configuration:")
        print(f"   Voice URL: {updated_number.voice_url}")
        print(f"   Voice Method: {updated_number.voice_method}")
        print(f"   Status Callback: {updated_number.status_callback}")
        print(f"   Status Method: {updated_number.status_callback_method}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error configuring webhooks: {str(e)}")
        print(f"\nManual Configuration:")
        print(f"1. Login to Twilio Console: https://console.twilio.com")
        print(f"2. Go to Phone Numbers → Manage → Active numbers")
        print(f"3. Click on {phone_number}")
        print(f"4. Set Voice Webhook: {webhook_url}")
        print(f"5. Set Status Callback: {status_callback_url}")
        return False

def test_twilio_connection():
    """Test Twilio API connection."""
    
    account_sid = "AC4e658dd5cf5c6e36514e5bae7f4c1bf7"  # Your Live Account SID
    auth_token = "db19869a6764956183410a5169a41ab0"
    
    print("\n🧪 Testing Twilio Connection...")
    
    try:
        client = Client(account_sid, auth_token)
        
        # Test connection by fetching account info
        account = client.api.accounts(account_sid).fetch()
        print(f"✅ Connected to Twilio account: {account.friendly_name}")
        
        # List phone numbers
        phone_numbers = client.incoming_phone_numbers.list()
        print(f"📞 Found {len(phone_numbers)} phone number(s):")
        
        for number in phone_numbers:
            print(f"   {number.phone_number} ({number.friendly_name})")
        
        return True
        
    except Exception as e:
        print(f"❌ Twilio connection failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🎯 AI Skills Assessment - Twilio Configuration")
    print("=" * 60)
    
    # Test connection first
    if not test_twilio_connection():
        print("\n⚠️  Please check your Twilio credentials")
        sys.exit(1)
    
    # Configure webhooks
    success = configure_twilio_webhooks()
    
    if success:
        print("\n🚀 SUCCESS! Your Twilio phone number is now configured.")
        print("You can now call (472) 236-8895 to test the AI Skills Assessment!")
        print("\n📝 Next steps:")
        print("1. Deploy the latest Lambda function: npm run deploy")
        print("2. Test by calling (472) 236-8895")
        print("3. Check CloudWatch logs for debugging")
    else:
        print("\n⚠️  Webhook configuration failed. Please configure manually.")
