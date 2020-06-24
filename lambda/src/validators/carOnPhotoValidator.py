import json
import boto3
import os

rekog = boto3.client('rekognition')
ses = boto3.client('ses')
lambda_client = boto3.client("lambda")
cognito_client = boto3.client('cognito-idp')

get_car_lambda_arn = os.getenv("GetCarLambda")
assign_photo_to_car_lambda_arn = os.getenv("AssignPhotoToCarLambdaArn")
user_pool_id = os.getenv("UserPoolId")

def check_label(recog_response, label):
    for i in recog_response['Labels']:
        if i["Name"].lower()  == label.lower() :
            return True
    return False


def validate(event, context):
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

            car_id = key.split('.')[0]

            if check_label(response, 'car') and not check_label(response, 'human'):
                print('Valid photo')
                
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

                car_get_response = lambda_client.invoke(
                    FunctionName = get_car_lambda_arn,
                    InvocationType = "RequestResponse",
                    Payload = json.dumps({
                        "car_id": car_id
                    })
                )

                response_str = car_get_response['Payload'].read()
                response_dict = json.loads(response_str)
                response_body_dict = json.loads(response_dict['body'])
                car_owner_id = response_body_dict['ownerId']

                filter = "sub = \"{}\"".format(car_owner_id)

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
