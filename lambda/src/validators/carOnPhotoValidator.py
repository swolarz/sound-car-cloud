import json
import boto3
import os

rekog = boto3.client('rekognition')
ses = boto3.client('ses')
lambda_client = boto3.client("lambda")

assign_photo_to_car_lambda_arn = os.getenv("AssignPhotoToCarLambdaArn")

def check_label(recog_response, label):
    for i in recog_response['Labels']:
        if i["Name"].lower()  == label.lower() :
            return True
    return False


def validate(event, context):
    print('request: {}'.format(json.dumps(event)))

    for outer_records in event["Records"]:
        inner_records = json.loads(outer_records["body"])
        for photo_data in inner_records["Records"]:
            bucket = photo_data["s3"]["bucket"]["name"]
            key = photo_data["s3"]["object"]["key"]

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

            if check_label(response, 'car') and not check_label(response, 'human'):
                print('Valid photo')
                
                car_id = key.split('_')[0]
                photo_id = key

                lambda_client.invoke(
                    FunctionName = assign_photo_to_car_lambda_arn,
                    InvocationType = "RequestResponse",
                    Payload = json.dumps({
                        "car_id": car_id,
                        "photo_id": photo_id,
                    })
                )
            else:
                print('Invalid photo')
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
