#!/usr/bin/env python3

import os
import boto3
from twilio.rest import Client

# Get environment variables (same as Lambda)
def get_twilio_config():
    """Get Twilio configuration from environment."""
    return {
        'account_sid': os.environ.get('TWILIO_ACCOUNT_SID', 'AC4e658dd5cf5c6e36514e5bae7f4c1bf7'),
        'auth_token': os.environ.get('TWILIO_AUTH_TOKEN', 'db19869a6764956183410a5169a41ab0'),
        'phone_number': os.environ.get('TWILIO_PHONE_NUMBER', '+14722368895'),
        'webhook_url': os.environ.get('TWILIO_WEBHOOK_URL', 'https://eih1khont2.execute-api.us-east-1.amazonaws.com')
    }

def main():
    print("🔍 Twilio Account Debug Information")
    print("=" * 50)
    
    config = get_twilio_config()
    
    print(f"Account SID: {config['account_sid']}")
    print(f"Phone Number: {config['phone_number']}")
    print(f"Webhook URL: {config['webhook_url']}")
    
    try:
        # Initialize Twilio client
        client = Client(config['account_sid'], config['auth_token'])
        
        # Get account info
        account = client.api.accounts(config['account_sid']).fetch()
        print(f"Account Status: {account.status}")
        print(f"Account Type: {account.type}")
        
        # List verified caller IDs
        print("\n📞 Verified Caller IDs:")
        verified_numbers = client.outgoing_caller_ids.list()
        
        if verified_numbers:
            for number in verified_numbers:
                print(f"  - {number.phone_number} (Friendly Name: {number.friendly_name})")
        else:
            print("  No verified caller IDs found")
            
    except Exception as e:
        print(f"❌ Error accessing Twilio account: {str(e)}")

if __name__ == "__main__":
    main()
