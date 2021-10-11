import requests
import json
from concurrent.futures import ThreadPoolExecutor

class YelpApi():
    def __init__(self, client_id, api_key):
        self._api_key = api_key
        self._client_id = client_id
        self._base_url = 'https://api.yelp.com/v3'

    def _search(self, args):
        print(args)
        url = f"{self._base_url}/businesses/search"
        try:
            response = requests.get(url, 
                params=args,
                headers={
                "Authorization" : f"Bearer {self._api_key}"
                }
            )
            res_json = response.json()
            return res_json
        except Exception as e:
            print(e)
            return []
        

    def get_business_search(self, args, count=50):
        chunk_size = 50
        arg_list = []
        for i in range(0, count, chunk_size):
            args['offset'] = i
            args['limit'] = 50 if count > 50 else args['limit']
            # deep copy
            arg_list.append(args.copy())
        data = []
        with ThreadPoolExecutor(max_workers=5) as executor:
            data.extend(list(executor.map(self._search, arg_list)))
        merged = []
        for x in data:
            if x.get('businesses'):
                merged.extend(x['businesses'])
        return merged


