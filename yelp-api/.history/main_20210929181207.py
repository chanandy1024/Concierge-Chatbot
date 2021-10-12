import YelpApi
import os

def get_data():
    print(os.environ['YELP_API_CLIENT_ID'])
    print(os.environ['YELP_API_KEY'])

get_data()
# api = YelpApi()