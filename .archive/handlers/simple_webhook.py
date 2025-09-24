#!/usr/bin/env python3
"""
Simplified Assessment Handler for POC Testing

This is a minimal working version to test the infrastructure.
"""

import json
import os
import boto3
import logging
from datetime import datetime

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):
    """Simplified handler for testing."""
    
    logger.info(f"Received event: {json.dumps(event, default=str)}")
    
    try:
        # Get request path
        path = event.get('rawPath', event.get('requestContext', {}).get('http', {}).get('path', ''))
        method = event.get('requestContext', {}).get('http', {}).get('method', 'POST')
        
        logger.info(f"Path: {path}, Method: {method}")
        
        # Simple routing
        if path == '/webhook':
            return handle_webhook_test()
        elif path == '/initiate':
            return handle_initiate_test()
        elif path.startswith('/question/'):
            return handle_question_test()
        else:
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'text/xml'},
                'body': '''<?xml version="1.0" encoding="UTF-8"?>
                <Response>
                    <Say>AI Skills Assessment POC is working. This is a test response.</Say>
                    <Hangup/>
                </Response>'''
            }
    
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'text/xml'},
            'body': '''<?xml version="1.0" encoding="UTF-8"?>
            <Response>
                <Say>There was an error processing your request.</Say>
                <Hangup/>
            </Response>'''
        }

def handle_webhook_test():
    """Handle webhook test."""
    
    # Simple TwiML response for testing
    twiml = '''<?xml version="1.0" encoding="UTF-8"?>
    <Response>
        <Say voice="alice">Welcome to AI Skills Assessment. This is a test call. Thank you for calling.</Say>
        <Hangup/>
    </Response>'''
    
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'text/xml',
            'Cache-Control': 'no-cache'
        },
        'body': twiml
    }

def handle_initiate_test():
    """Handle initiate test."""
    
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps({
            'success': True,
            'message': 'Assessment initiation endpoint is working',
            'timestamp': datetime.utcnow().isoformat()
        })
    }

def handle_question_test():
    """Handle question test."""
    
    twiml = '''<?xml version="1.0" encoding="UTF-8"?>
    <Response>
        <Say voice="alice">This is a test question response. The system is working correctly.</Say>
        <Hangup/>
    </Response>'''
    
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'text/xml',
            'Cache-Control': 'no-cache'
        },
        'body': twiml
    }
