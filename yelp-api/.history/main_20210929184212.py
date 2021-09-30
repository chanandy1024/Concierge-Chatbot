import YelpApi
import os
from dotenv import load_dotenv

load_dotenv()

def get_data():
    client_id = os.environ['YELP_API_CLIENT_ID']
    api_key = os.environ['YELP_API_KEY']
    api = YelpApi.YelpApi(client_id, api_key)
    api.get_business_search({
        "term": "restaurants",
        "location": "New York City",
        "limit": 50,
        "offset": 0
    }, count=50)
get_data()
