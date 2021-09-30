import YelpApi
import os

def get_data():
    print(os.environ['YELP_API_CLIENT_ID'])
    print(os.environ['YELP_API_KEY'])

if __name__ == __main__:
    get_data()
    # api = YelpApi()