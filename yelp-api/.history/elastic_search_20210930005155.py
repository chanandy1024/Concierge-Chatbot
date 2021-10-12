import boto3
from dynamodb_json import json_util as json
from pandas import pd
client = boto3.client('dynamodb')

def dump_table(table_name):
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
        print(response)
        results.extend(response['Items'])
        break
        if not last_evaluated_key:
            break
    return results

# Usage
data = dump_table('coms6998_hw1_yelp_restaurants')
# do something with data
df = pd.DataFrame(json.loads(data))
df = df[['business_id', 'categories']]
