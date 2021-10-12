import json
from decimal import Decimal
import boto3
import requests
from requests_aws4auth import AWS4Auth
from boto3.dynamodb.conditions import Key
from dynamodb_json import json_util
import operator
from datetime import datetime
import random
from time import time
from dotenv import load_dotenv
import os
load_dotenv()
region = 'us-west-2'
service='es'
os_host = 'https://search-yelp-restaurants-es-fvux5m65jstc4uowq222ula33m.us-west-2.es.amazonaws.com'
session = boto3.Session()

def search_es(category):
    '''
    Source: https://docs.aws.amazon.com/opensearch-service/latest/developerguide/search-example.html
    '''
    
    credentials = session.get_credentials()
    
    awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)
   
    # Put the user query into the query DSL for more accurate search results.
    query = {
        #"size": 200,
        "query": {
            "multi_match": {
              "query":category,
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
    #select 3 at random
    hits = json.loads(response['body'])['hits'].get('hits', [])
    selected_idx = random.sample(range(0, len(hits)), 3)
    #format response body
    results = []
    for each in [hits[i] for i in selected_idx]:
        results.append({
            'business_id' : each['_source']['business_id'],
            'categories' : each['_source']['categories']
        })
    
    return results

def publish_message(phone_number, message, sns=None):
    if not sns:
        sns = session.client('sns')
    # Create the topic if it doesn't exist (this is idempotent)
    topic = sns.create_topic(Name="coms6998-concierge-topic")
    topic_arn = topic['TopicArn']  # get its Amazon Resource Name
    
    # subscribe to topic
    sns.subscribe(
        TopicArn=topic_arn,
        Protocol='sms',
        Endpoint=phone_number
    )
    
    # Publish a message.
    sns.publish(Message=message, TopicArn=topic_arn)
    print("Message sent!")
    
def save_search(data, dynamodb=None):
    if not dynamodb:
        dynamodb = session.client('dynamodb')
    # insert item to suggestions
    #data = json.loads(json.dumps(data), parse_float=Decimal)
    data['created_at'] = time()
    data['search_results'] = json.dumps(data['search_results'])
    dynamodb.put_item(
        TableName='yelp_restaurants_suggestions',
        Item=json.loads(json_util.dumps(data))
    )
    print("Saved search in DB")

def build_sns_message(messages):
    #format date
    reservation_date = datetime.strptime(messages['Date'], '%Y-%m-%d').strftime('%m/%d/%Y')
    message_formatted = f"Hello! Here are your {messages['Cuisine']} restaurant suggestions for {messages['Attendees']}, for {reservation_date} at {messages['Time']}.\n"
    #sort results
    messages['search_results'].sort(key=operator.itemgetter('rating'), reverse=True)
    messages['search_results'].sort(key=operator.itemgetter('review_count'), reverse=True)
    for idx, restaurant in enumerate(messages['search_results']):
        message_formatted += f"{idx+1}. {restaurant['name']} ({restaurant.get('price', 'NA')}), located at {', '.join(restaurant['location']['display_address'])}. Rated {restaurant['rating']}/5 with {restaurant['review_count']} reviews.\n"
    return message_formatted

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
    return json_util.loads(response['Item'])

def receive_message():
    #when triggered, will poll SQS and retrieve a message, if not empty
    sqs_client = boto3.client("sqs", region_name="us-west-2")
    response = sqs_client.receive_message(
        QueueUrl="https://sqs.us-west-2.amazonaws.com/164008855428/diningQueue.fifo",
        MaxNumberOfMessages=1,
        WaitTimeSeconds=10,
    )

    print(f"Number of messages received: {len(response.get('Messages', []))}")
    return response.get('Messages', [])

def get_suggestions(messages):
    results = []
    for message in messages:
        #print(f"Receipt Handle: {message['ReceiptHandle']}")
        message['search_results'] = search_es(category=message['Cuisine'].lower())
        results.append(message)
    return results
    
def lambda_handler(event, context):
    try:
        
        # query_result = receive_message() 
        
        # get query result from SQS trigger
        query_result = [json.loads(x['body']) for x in event['Records']]

        #query dynamodb for each restaurant
        all_messages = []
        for message in get_suggestions(query_result):
            for restaurant in message['search_results']:
                restaurant.update(query_db(restaurant['business_id']))
            save_search(message.copy())
            all_messages.append(build_sns_message(message))

        for idx, each_message in enumerate(all_messages):
            publish_message(phone_number=query_result[idx]['PhoneNumber'], message=each_message)
            
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
    