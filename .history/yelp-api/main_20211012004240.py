import YelpApi
import os
from dotenv import load_dotenv
import pandas as pd
import boto3
from time import time, sleep
from decimal import Decimal
import json
load_dotenv()
session = boto3.session.Session(profile_name='ccbd', region_name='us-west-2')

def insert_to_db(data):
    
    dynamodb = session.resource('dynamodb')
    # Instantiate a table resource object without actually
    # creating a DynamoDB table. Note that the attributes of this table
    # are lazy-loaded: a request is not made nor are the attribute
    # values populated until the attributes
    # on the table resource are accessed or its load() method is called.
    table = dynamodb.Table('yelp_restaurants')

    # Print out some data about the table.
    # This will cause a request to be made to DynamoDB and its attribute
    # values will be set based on the response.
    print("Connected to dynamodb:", table.creation_date_time)
    print("Inserting", len(data), "records")
    #batch insert 
    with table.batch_writer(overwrite_by_pkeys=['business_id']) as batch:
        # Float types must be converted to decimal
        for row in json.loads(json.dumps(data), parse_float=Decimal):
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
            "term": "food",
            "location": "New York",
            "limit": limit,
            "offset": 0,
            "radius": 40000,
            "categories": category,
            "sort_by": 'review_count',
        }, count=limit)

if __name__ == '__main__':
    categories = [
        'afghani',
        'african',
        'newamerican',
        'tradamerican',
        'bangladeshi',
        'andulusian',
        'arabian',
        'argentine',
        'armenian',
        'asianfusion',
        'australian',
        'baguettes',
        'belgian',
        'bbq',
        'basque',
        'beergarden',
        'bistros',
        'brazilian',
        'british',
        'burgers',
        'cafeteria',
        'cajun',
        'cambodian',
        'newcanadian',
        'newcanadian',
        'cheesesteaks',
        'chickenshop',
        'caribbean',
        'chinese',
        'dumplings',
        'eastern_european',
        'ethiopian',
        'hotdogs',
        'filipino',
        'foodstands',
        'french',
        'german',
        'gluten_free',
        'greek',
        'halal',
        'himalayan',
        'italian',
        'khcafe',
        'indian',
        'indonesian',
        'irish',
        'jewish',
        'kebab',
        'latin',
        'japanese',
        'korean',
        'mediterranean',
        'mexican',
        'mongolian',
        'mideastern',
        'pakistani',
        'persian',
        'pizza',
        'portuguese',
        'scandanavian',
        'seafood',
        'singaporean',
        'slovakian',
        'soulfood',
        'spanish',
        'steakhouses',
        'sushi',
        'swedish',
        'taiwanese',
        'tapasmallplates',
        'tex-mex',
        'thai',
        'turkish',
        'vegetarian',
        'vegan',
        'vietnamese',
    ]
    for category in categories:
        result = get_data(category, limit=200)
        if (len(result)):
            pd.DataFrame(result).to_csv('test.csv', index=False)
            insert_to_db(pd.DataFrame(result).drop_duplicates(subset=['id']).to_dict(orient='records'))
            print('successfully inserted:', category)
            sleep(30)
    print("done")
    
