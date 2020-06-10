import boto3
import os
import uuid
import json
import base64

s3client = boto3.client("s3")
bucket = os.getenv("Bucket")

def upload(event, context):

    print(event)

    photoId = str(uuid.uuid4()) + ".jpg"

    request_body = json.loads(event['body'])

    s3client.put_object(
        Bucket=bucket,
        Key=photoId,
        Body=base64.b64decode(request_body["photo"])
    )

    return {
        'statusCode': 200,
        'headers': {
            "Access-Control-Allow-Credentials" : True,
            "Access-Control-Allow-Origin": "*"
        },
        'body': json.dumps({ "message":'Upload succesful'})
    }
