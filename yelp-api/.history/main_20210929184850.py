import YelpApi
import os
from dotenv import load_dotenv
import pandas
load_dotenv()

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

get_data()
