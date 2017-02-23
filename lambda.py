from __future__ import print_function

import json
import urllib
import boto3
import gzip

print('Loading function')

s3 = boto3.client('s3')

def lambda_handler(event, context):
    # print("Received event: " + json.dumps(event, indent=2))
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.unquote_plus(event['Records'][0]['s3']['object']['key'].encode('utf8'))
    name = urllib.unquote_plus(event['Records'][0]['s3']['bucket']['name'].encode('utf8'))
    print("KEY:" + key) # this is path to s3 object
    print("NAME:" + name) # this is iam user name
    try:
        tag_bucket(name, key)
        return True
    except Exception as e:
        print(e)
        raise e

def tag_bucket(name, key):
    response = s3.get_object(Bucket=name,Key=key)
    f = open('/tmp/json.gz', 'wb')
    f.write(response['Body'].read())
    f.close()
    with gzip.open('/tmp/json.gz', "rb") as f:
        content = json.loads(f.read().decode("ascii"))
    # content is events from s3 object
    # print(json.dumps(content, indent=2))
    events = [x for x in content['Records'] if x['eventName'] == 'CreateBucket']
    # event are list of eventName with Create*
    for eve in events:
        print(json.dumps(eve, indent=2))
        bucket_name = eve["requestParameters"]["bucketName"]
        owner = eve["userIdentity"]["userName"]
        Tagging = {'TagSet': [{'Value': owner, 'Key': 'Onwer'}]}
        print("now I'm going to add" + json.dumps(Tagging, indent=2) + "to " + bucket_name)
        s3.put_bucket_tagging(Bucket=bucket_name, Tagging=Tagging)
