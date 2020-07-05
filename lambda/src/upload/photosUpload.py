import boto3
import os
import uuid
import json
import base64
import re

s3client = boto3.client("s3")
bucket = os.getenv("Bucket")


def prepare_response(code, response):
    return {
        'statusCode': code,
        'headers': {
            "Access-Control-Allow-Credentials" : True,
            "Access-Control-Allow-Origin": "*"
        },
        'body': json.dumps(response)
    }


def get_user_id(event):
    return event["requestContext"]["authorizer"]["claims"]["sub"]


def handler(event, context):
    request_body = json.loads(event['body'])
    imageData = request_body["photo"].split(',')[1]
    extenstion = re.split(";|/", request_body["photo"])[1]

    owner_id = get_user_id(event)
    if not owner_id:
        return prepare_response(403, {
            'error': 'photo-upload-not-authorized',
            'message': 'Not authorized to upload photo'
        })

    photoId = '{}.{}.{}'.format(owner_id, str(uuid.uuid4()), extenstion)
    photoKey = 'car-photos/{}'.format(photoId)

    s3client.put_object(
        Bucket=bucket,
        Key=photoKey,
        Body=base64.b64decode(imageData)
    )
    
    return prepare_response(200, { "photoId": photoId })
