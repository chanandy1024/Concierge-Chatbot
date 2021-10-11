import boto3
from dynamodb_json import json_util as json
import pandas as pd
from elasticsearch import Elasticsearch, RequestsHttpConnection

import requests
from requests_aws4auth import AWS4Auth
from tabulate import tabulate
client = boto3.client('dynamodb')

def get_table(table_name):
    results = []
    last_evaluated_key = None
    while True:
        if last_evaluated_key:
            response = client.scan(
                TableName=table_name,
                ExclusiveStartKey=last_evaluated_key
            )
        else: 
            response = client.scan(TableName=table_name)
        last_evaluated_key = response.get('LastEvaluatedKey')
        
        results.extend(response['Items'])
        break
        if not last_evaluated_key:
            break
    return results


def dump_table(data):
    # build file
    # The action_and_metadata portion of the bulk file
    bulk_file = ''
    for index in data:
        bulk_file += '{ "index" : { "_index" : "site", "_type" : "_doc", "_id" : "' + str(id) + '" } }\n'
        # The optional_document portion of the bulk file
        bulk_file += json.dumps(index) + '\n'
    print(bulk_file)
    host = '' # For example, my-test-domain.us-east-1.es.amazonaws.com
    region = '' # e.g. us-west-1

    service = 'es'
    credentials = boto3.Session().get_credentials()
    awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)

    es = Elasticsearch(
        hosts = [{'host': host, 'port': 443}],
        http_auth = awsauth,
        use_ssl = True,
        verify_certs = True,
        connection_class = RequestsHttpConnection
    )

    document = {
        "title": "Moneyball",
        "director": "Bennett Miller",
        "year": "2011"
    }

    es.bulk(index="movies", doc_type="_doc", id="5", body=document)
    print(es.get(index="movies", doc_type="_doc", id="5"))

# Usage
data = get_table('coms6998_hw1_yelp_restaurants')
# do something with data
df = pd.DataFrame(json.loads(data))
df = df[['business_id', 'categories']]
print(tabulate(df.head()))