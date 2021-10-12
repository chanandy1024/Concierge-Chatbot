import boto3
from dynamodb_json import json_util
import json
from dotenv import load_dotenv
import os
import pandas as pd
from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
from tabulate import tabulate
from boto3.dynamodb.types import TypeDeserializer
load_dotenv()

deserializer = TypeDeserializer()
session = boto3.session.Session(profile_name='ccbd', region_name='us-west-2')

client = session.client('dynamodb')

def get_table(table_name):
    results = []
    last_evaluated_key = None
    while True:
        if last_evaluated_key:
            response = client.scan(
                TableName=table_name,
                ExclusiveStartKey=last_evaluated_key,
                AttributesToGet=['business_id', 'categories']
            )
        else: 
            response = client.scan(TableName=table_name, AttributesToGet=['business_id', 'categories'])
        last_evaluated_key = response.get('LastEvaluatedKey')
        #print(response['LastEvaluatedKey'])
        results.extend(response['Items'])
        if not last_evaluated_key:
            break
    return results

def dump_table(data):
    # build file
    # The action_and_metadata portion of the bulk file
    bulk_file = ''
    for idx, index in enumerate(data):
        bulk_file += '{ "index" : { "_index" : "yelp-restaurants", "_type" : "_doc", "_id" : "' + str(idx+1) + '" } }\n'
        # The optional_document portion of the bulk file
        bulk_file += json.dumps(index) + '\n'
    
    host = os.environ['AWS_OS_HOST']
    region = 'us-west-2' 
    service = 'es'
    credentials = session.get_credentials()
    awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service)

    aos = Elasticsearch(
        hosts = [{'host': host, 'port': 443}],
        http_auth = awsauth,
        use_ssl = True,
        verify_certs = True,
        connection_class = RequestsHttpConnection
    )

    aos.bulk(bulk_file)
    
    print(aos.search(q='some test query'))

# Usage
data = get_table('yelp_restaurants')
# do something with data
deserialized = json_util.loads(data)
df = pd.DataFrame(deserialized)[['business_id', 'categories']]
df.to_csv('db_scan.csv')
dump_table(df.to_dict(orient='records'))