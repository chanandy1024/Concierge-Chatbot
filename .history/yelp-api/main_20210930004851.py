import YelpApi
import os
from dotenv import load_dotenv
import pandas
import boto3
from time import time, sleep
from decimal import Decimal
import json
load_dotenv()

def insert_to_db(data):
    dynamodb = boto3.resource('dynamodb')
    # Instantiate a table resource object without actually
    # creating a DynamoDB table. Note that the attributes of this table
    # are lazy-loaded: a request is not made nor are the attribute
    # values populated until the attributes
    # on the table resource are accessed or its load() method is called.
    table = dynamodb.Table('coms6998_hw1_yelp_restaurants')

    # Print out some data about the table.
    # This will cause a request to be made to DynamoDB and its attribute
    # values will be set based on the response.
    print("Connected to dynamodb:", table.creation_date_time)
    #batch insert 
    with table.batch_writer(overwrite_by_pkeys=['business_id']) as batch:
        # Float types must be converted to decimal
        for row in json.loads(json.dumps(data['businesses']), parse_float=Decimal):
            row['business_id'] = row['id']
            row['created_at'] = Decimal(time())
            batch.put_item(
                Item=row
            )

def get_data(category, limit=50):
    client_id = os.environ['YELP_API_CLIENT_ID']
    api_key = os.environ['YELP_API_KEY']
    api = YelpApi.YelpApi(client_id, api_key)
    return api.get_business_search({
            "term": "restaurants",
            "location": "New York City",
            "limit": limit,
            "offset": 0,
            "category": category
        }, count=limit)

if __name__ == '__main__':
    categories = [
        'african',
        'newamerican',
        'tradamerican',
        'bangladeshi',
        'belgian',
        'brazilian',
        'cambodian',
        'newcanadian',
        'caribbean',
        'chinese',
        'filipino',
        'french',
        'italian',
        'japanese',
        'korean',
        'mediterranean',
        'mexican',
        'mideastern',
        'singaporean',
        'thai',
        'turkish',
        'vietnamese',
    ]
    for category in categories:
        result = get_data(category, limit=1000)
        if (len(result)):
            insert_to_db(result)
            print('successfully inserted:', category)
            #sleep(60)
    print("done")
    
