import json
from datetime import datetime
import boto3
import uuid
from datetime import datetime

def lambda_handler(event, context):
    client = boto3.client('lex-runtime', region_name='us-west-2')
    #load event body 
    event_body = json.loads(event['body'])
    
    response = client.post_text(
        botName='DiningConcierge',
        botAlias='TestDining',
        userId=event_body['messages'][0]['unstructured']['user_id'],
        inputText=event_body['messages'][0]['unstructured']['text']
    )
    response_text = response['message']
    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        },
        'body': json.dumps({    
            'messages': [
                {
                  'type': 'unstructured',
                  'unstructured': {
                    'id': event_body['messages'][0]['unstructured']['user_id'],
                    'text': response_text,
                    'timestamp': datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                  }
                }
            ]
        })
    }
    

