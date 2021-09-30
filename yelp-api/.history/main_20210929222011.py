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
    table = dynamodb.Table('coms4111_hw1_yelp_restaurants')

    # Print out some data about the table.
    # This will cause a request to be made to DynamoDB and its attribute
    # values will be set based on the response.
    print(table.creation_date_time)
    #batch insert 
    with table.batch_writer(iverwrute_by_pkeys=['business_id', 'created_at']) as batch:
        for row in data['businesses']:
            batch.put_item(
                Item=row
            )


def get_data():
    client_id = os.environ['YELP_API_CLIENT_ID']
    api_key = os.environ['YELP_API_KEY']
    api = YelpApi.YelpApi(client_id, api_key)
    res = api.get_business_search({
            "term": "restaurants",
            "location": "New York City",
            "limit": 10,
            "offset": 0
        }, count=10)
    print(len(res['businesses']))
    print(res['businesses'])

get_data()
