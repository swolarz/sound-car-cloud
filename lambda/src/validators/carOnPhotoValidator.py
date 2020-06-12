import json
import boto3
import os

rekog = boto3.client('rekognition')
ses = boto3.client('ses')

def validate(event, context):
    print('request: {}'.format(json.dumps(event)))

    for outer_records in event["Records"]:
        inner_records = json.loads(outer_records["body"])
        for photo_data in inner_records["Records"]:
            bucket = photo_data["s3"]["bucket"]["name"]
            key = photo_data["s3"]["object"]["key"]
            print(bucket, key)

            response = rekog.detect_labels(
                Image={
                    "S3Object": {
                        "Bucket": bucket,
                        "Name": key
                    }
                },
                MaxLabels=10,
                MinConfidence=90
            )

            print(response)

            send_failure_email(os.getenv("FromEmail"))


SENDER = os.getenv("FromEmail")
AWS_REGION = os.getenv("SESRegion")
SUBJECT = "Your photo is unacceptable"
TEXT = "Your photo was not accepted by our filters."
CHARSET = "UTF-8"

def send_failure_email(destination_email):
    response = ses.send_email(
        Destination={
            'ToAddresses': [
                destination_email,
            ],
        },
        Message={
            'Body': {
                'Text': {
                    'Charset': CHARSET,
                    'Data': TEXT,
                },
            },
            'Subject': {
                'Charset': CHARSET,
                'Data': SUBJECT,
            },
        },
        Source=SENDER,
    )
