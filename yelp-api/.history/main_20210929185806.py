import YelpApi
import os
from dotenv import load_dotenv
import pandas
import boto3

load_dotenv()


def import_data(data):
    dynamodb = boto3.resource('dynamodb')
    # Instantiate a table resource object without actually
    # creating a DynamoDB table. Note that the attributes of this table
    # are lazy-loaded: a request is not made nor are the attribute
    # values populated until the attributes
    # on the table resource are accessed or its load() method is called.
    table = dynamodb.Table('users')

    # Print out some data about the table.
    # This will cause a request to be made to DynamoDB and its attribute
    # values will be set based on the response.
    print(table.creation_date_time)

def get_data():
    client_id = os.environ['YELP_API_CLIENT_ID']
    api_key = os.environ['YELP_API_KEY']
    api = YelpApi.YelpApi(client_id, api_key)
    res = api.get_business_search({
            "term": "restaurants",
            "location": "New York City",
            "limit": 50,
            "offset": 0
        }, count=50)
    print(res)

import_data()