import boto3
from dynamodb_json import json_util as json
import pandas as pd
import requests
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
    headers = {'Content-Type': 'application/x-ndjson'}
    
    r = requests.post("https://ES_HOST/_bulk", auth=awsauth, headers=headers, data=data_as_str)

# Usage
data = get_table('coms6998_hw1_yelp_restaurants')
# do something with data
df = pd.DataFrame(json.loads(data))
df = df[['business_id', 'categories']]
print(tabulate(df.head()))