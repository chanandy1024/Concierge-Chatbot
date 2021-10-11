import json
import boto3
import requests
from requests_aws4auth import AWS4Auth

region = 'us-west-2'
service='es'
os_host = 'https://search-yelp-restaurants-es-fvux5m65jstc4uowq222ula33m.us-west-2.es.amazonaws.com'

def search_es(query, fields=['business_id']):
    session = boto3.Session()
    credentials = session.get_credentials()
    
    awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)
   
    # Put the user query into the query DSL for more accurate search results.
    # Note that certain fields are boosted (^).
    query = {
        "size": 25,
        "query": {
            "multi_match": {
                "query": "italian",
                "fields": ["business_id", "categories"]
            }
        }
    }

    # Elasticsearch 6.x requires an explicit Content-Type header
    headers = { "Content-Type": "application/json" }
    print(awsauth)
    response = requests.get(os_host,
                        auth=awsauth)
    print(response.content)
    '''
    # Make the signed HTTP request
    r = requests.get(os_host, auth=awsauth, headers=headers, data=json.dumps(query))
    print(r.text)
    # Create the response and add some extra content to support CORS
    response = {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Origin": '*'
        },
        "isBase64Encoded": False
    }

    # Add the search results to the response
    response['body'] = r.text
    print(response)
    
    '''

def receive_message():
    sqs_client = boto3.client("sqs", region_name="us-west-2")
    response = sqs_client.receive_message(
        QueueUrl="https://sqs.us-west-2.amazonaws.com/164008855428/diningQueue.fifo",
        MaxNumberOfMessages=1,
        WaitTimeSeconds=10,
    )

    print(f"Number of messages received: {len(response.get('Messages', []))}")
    #Message body: {'City': 'Manhattan', 'Cuisine': 'Mexican', 'Attendees': '1', 'Date': '2022-10-23', 'Time': '7pm', 'PhoneNumber': '7347095631'}
    for message in response.get("Messages", []):
        message_body = json.loads(message["Body"])
        #print(f"Receipt Handle: {message['ReceiptHandle']}")
        search_es(query=message_body['Cuisine'].lower(), fields=['business_id', 'categories'])
        
def lambda_handler(event, context):
    try:
        #poll queue
        receive_message()
        return {
            'statusCode': 200,
            'body': json.dumps('Success! Finding restaurants')
        }
    except Exception as e:
        print(e)
        return {
            'statusCode': 500,
            'body': json.dumps('Error getting data!')
        }
    
