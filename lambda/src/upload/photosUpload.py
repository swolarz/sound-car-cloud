import boto3
import os
import uuid
import json
import base64
import re

s3client = boto3.client("s3")
bucket = os.getenv("Bucket")

def upload(event, context):

    request_body = json.loads(event['body'])
    imageData = request_body["photo"].split(',')[1]
    extenstion = re.split(";|/", request_body["photo"])[1]
    photoId = str(uuid.uuid4()) + "." + extenstion

    s3client.put_object(
        Bucket=bucket,
        Key=photoId,
        Body=base64.b64decode(imageData)
    )

    return {
        'statusCode': 200,
        'headers': {
            "Access-Control-Allow-Credentials" : True,
            "Access-Control-Allow-Origin": "*"
        },
        'body': json.dumps({ "message":'Upload succesful'})
    }
