"""
Minimal AWS Lambda handler for testing deployment.
This is a simplified version that doesn't rely on heavy dependencies.
"""

import json

def handler(event, context):
    """
    Simple Lambda handler that returns a success response.
    """
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({
            'message': 'Lambda function deployed successfully!',
            'api_status': 'This is a minimal test handler. The full API will be implemented in the next iteration.',
            'event': event
        })
    }