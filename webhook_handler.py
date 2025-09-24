"""
Simple webhook handler for Twilio - no complex imports needed.
"""
import json
import logging

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):
    """
    Simple Lambda handler for Twilio webhooks.
    Returns TwiML response without complex imports.
    """
    try:
        logger.info(f"Received webhook event: {json.dumps(event, default=str)}")
        
        # Return simple TwiML response
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'text/xml',
            },
            'body': '''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice">Hello from GravyWork AI Skills Assessment! This webhook is working perfectly.</Say>
    <Hangup/>
</Response>'''
        }
        
    except Exception as e:
        logger.error(f"Error in webhook handler: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal server error'})
        }
