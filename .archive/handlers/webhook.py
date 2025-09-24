def handler(event, context):
    """Ultra simple webhook handler for Twilio."""
    
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'text/xml',
        },
        'body': '''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice">Hello from GravyWork AI Skills Assessment! This is working perfectly.</Say>
    <Hangup/>
</Response>'''
    }
