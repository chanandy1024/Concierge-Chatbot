import json
import boto3
import requests
from requests_aws4auth import AWS4Auth
from boto3.dynamodb.conditions import Key

region = 'us-west-2'
service='es'
os_host = 'https://search-yelp-restaurants-es-fvux5m65jstc4uowq222ula33m.us-west-2.es.amazonaws.com'
session = boto3.Session()
def search_es(query):
    '''
    Source: https://docs.aws.amazon.com/opensearch-service/latest/developerguide/search-example.html
    '''
    
    credentials = session.get_credentials()
    
    awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)
   
    # Put the user query into the query DSL for more accurate search results.
    # Note that certain fields are boosted (^).
    query = {
        "size": 3,
        "query": {
            "multi_match": {
              "query":"japanese",
              "fields" : ["categories.alias", "categories.title"] 
            }
        }
    }

    # Elasticsearch 6.x requires an explicit Content-Type header
    headers = { "Content-Type": "application/json" }

    # Make the signed HTTP request
    r = requests.get(os_host+'/yelp-restaurants/_search', auth=awsauth, headers=headers, data=json.dumps(query))
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
    #{'statusCode': 200, 'headers': {'Access-Control-Allow-Origin': '*'}, 'isBase64Encoded': False, 'body': '{"took":14,"timed_out":false,"_shards":{"total":5,"successful":5,"skipped":0,"failed":0},"hits":{"total":{"value":32,"relation":"eq"},"max_score":3.9371014,"hits":[{"_index":"yelp-restaurants","_type":"_doc","_id":"69","_score":3.9371014,"_source":{"business_id": "FYWwW5lcxKzaA98Xgw8bqA", "categories": [{"title": "Japanese", "alias": "japanese"}, {"title": "Noodles", "alias": "noodles"}]}},{"_index":"yelp-restaurants","_type":"_doc","_id":"310","_score":3.9371014,"_source":{"business_id": "kesYSgOJW5krU6L8n9qQ4Q", "categories": [{"title": "Japanese", "alias": "japanese"}, {"title": "Steakhouses", "alias": "steak"}]}},{"_index":"yelp-restaurants","_type":"_doc","_id":"88","_score":3.7308528,"_source":{"business_id": "YC-wGlO0oOkEIaCEDZv-ag", "categories": [{"title": "Japanese", "alias": "japanese"}]}}]}}'}

    #format response body
    
    results = []
    for each in json.loads(response['body'])['hits'].get('hits', []):
        results.append({
            'business_id' : each['_source']['business_id'],
            'categories' : each['_source']['categories']
        })
    
    return results

def query_db(business_id, dynamodb=None):
    if not dynamodb:
        dynamodb = session.client('dynamodb')
    # get item based on business_id
    response = dynamodb.get_item(
        TableName='yelp_restaurants',
        Key={
            'business_id': {
                'S' : business_id
            }
        },
        # use '#' to dereference reserved words
        ProjectionExpression='#restaurantName, #restaurantLocation.display_address, phone, price, rating, review_count, #restaurantUrl',
        ExpressionAttributeNames={
            "#restaurantName": "name",
            "#restaurantLocation": "location",
            "#restaurantUrl": "url"
        }
    )
    return response['Item']


def receive_message():
    sqs_client = boto3.client("sqs", region_name="us-west-2")
    response = sqs_client.receive_message(
        QueueUrl="https://sqs.us-west-2.amazonaws.com/164008855428/diningQueue.fifo",
        MaxNumberOfMessages=1,
        WaitTimeSeconds=10,
    )

    print(f"Number of messages received: {len(response.get('Messages', []))}")
    results = []
    for message in response.get("Messages", []):
        message_body = json.loads(message["Body"])
        #print(f"Receipt Handle: {message['ReceiptHandle']}")
        message_body['search_results'] = search_es(query=message_body['Cuisine'].lower())
        results.append(message_body)
    return results
    
def lambda_handler(event, context):
    try:
        #poll queue
        query_result = receive_message()
        print(query_result)
        #query dynamodb for each restaurant
        for message in query_result:
            for restaurant in message['search_results']:
                print(query_db(restaurant['business_id']))
        
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
    
