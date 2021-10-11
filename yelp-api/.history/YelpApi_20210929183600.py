import requests
import json
from concurrent.futures import ThreadPoolExecutor

class YelpApi():
    def __init__(self, client_id, api_key):
        self._api_key = api_key
        self._client_id = client_id
        self._base_url = 'https://api.yelp.com/v3'

    def _search(args):
        url = f"{self._base_url}/businesses/search"
        requests.get(url, header={
            "Authorization" : f"Bearer {self._api_key}"
        })

    def get_business_search(self, args, count):
        
        data = []
        with ThreadPoolExecutor(max_workers=5) as executor:
            data.extend(list(executor.map(self._search, args)))


