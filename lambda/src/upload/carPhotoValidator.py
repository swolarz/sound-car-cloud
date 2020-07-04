import json
import boto3
import os
import logging
logging.getLogger().setLevel(logging.INFO)

rekog = boto3.client('rekognition')
ses = boto3.client('ses')
lambda_client = boto3.client("lambda")
cognito_client = boto3.client('cognito-idp')

car_photo_owner_lambda_arn = os.getenv("CarPhotoOwnerLambdaArn")
cenzor_car_photo_lambda_arn = os.getenv("CenzorCarPhotoLambdaArn")
user_pool_id = os.getenv("UserPoolId")


def check_label(recog_response, label):
    for i in recog_response['Labels']:
        if i["Name"].lower()  == label.lower() :
            return True
    return False


def handler(event, context):
    if 'Records' not in event:
        return

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

            photo_id = key

            if check_label(response, 'car') and not check_label(response, 'human'):
                logging.info('Valid photo')
            else:
                logging.info('Invalid photo')

                owner_response = lambda_client.invoke(
                    FunctionName = car_photo_owner_lambda_arn,
                    InvocationType = "RequestResponse",
                    Payload = json.dumps({
                        "photo_id": photo_id
                    })
                )

                lambda_client.invoke(
                    FunctionName = cenzor_car_photo_lambda_arn,
                    InvocationType = "RequestResponse",
                    Payload = json.dumps({
                        "photo_id": photo_id
                    })
                )

                response_str = owner_response['Payload'].read()
                response_dict = json.loads(response_str)
                response_body_dict = json.loads(response_dict['body'])
                photo_owner_id = response_body_dict['owner']['id']

                filter = "sub = \"{}\"".format(photo_owner_id)

                users = cognito_client.list_users(
                    UserPoolId=user_pool_id, 
                    AttributesToGet=[
                        'email'
                    ],
                    Filter = filter)

                user = users['Users'][0]
                mail = user['Attributes'][0]['Value']
                send_failure_email(mail)


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
