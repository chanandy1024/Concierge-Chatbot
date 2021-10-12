import json
import boto3
from boto3.dynamodb.conditions import Key
from dynamodb_json import json_util

region = 'us-west-2'
session = boto3.Session()

def query_db(user_id, dynamodb=None):
    if not dynamodb:
        dynamodb = session.client('dynamodb')
    
    response = dynamodb.query(
        TableName='yelp_restaurants_suggestions',
        Limit = 1,
        ScanIndexForward = False, #sorted by created_at desc
        KeyConditionExpression="user_id = :userId",
        ExpressionAttributeValues={
            ":userId" : {
                'S' : user_id
            }
        }
    )
    return response['Items'][0]

def lambda_handler(event, context):
    try:
        #user_id = 'kulpmiyezaljf6smc8g'
        user_id = event['queryStringParameters']['user_id']
        response = query_db(user_id=user_id)
        #parse json
        if (response):
            response = json_util.loads(response);
            return {
                'statusCode': 200,
                'headers': {
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
                },
                'body': json.dumps(response)
            }
        else:
            return {
                'statusCode': 403,
                'headers': {
                        'Access-Control-Allow-Headers': 'Content-Type',
                        'Access-Control-Allow-Origin': '*',
                        'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
                    },
                'body': json.dumps('Could not find previous suggestions')
            }
    except Exception as e:
        print(e)
        return {
            'statusCode': 403,
            'headers': {
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            },
            'body': json.dumps('Error getting data!')
        }
    

