
import boto3
import os
import uuid
import json
import base64
import re


s3client = boto3.client("s3")


def prepare_response(code, response):
    return {
        'statusCode': code,
        'headers': {
            "Access-Control-Allow-Credentials" : True,
            "Access-Control-Allow-Origin": "*"
        },
        'body': json.dumps(response)
    }


def handler(event, context):
    media_bucket = os.getenv("MEDIA_BUCKET")

    request_body = json.loads(event['body'])
    audioData = request_body["audio"].split(',')[1]
    extension = re.split(";|/", request_body["audio"])[1]
    audioId = '{}.{}'.format(str(uuid.uuid4()), extension)
    audioKey = 'car-audio/{}'.format(audioId)

    if extension not in ['mp3', 'wav', 'mpeg']:
        return prepare_response(400, {
            'error': 'unsupported-audio-extension',
            'message': 'Given extension is not supported: {}'.format(extension)
        })

    s3client.put_object(
        Bucket=media_bucket,
        Key=audioKey,
        Body=base64.b64decode(audioData)
    )
    
    return prepare_response(200, { "audioId": audioId })