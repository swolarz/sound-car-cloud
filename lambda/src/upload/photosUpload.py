import boto3
import os
import uuid
import json
import base64
import re

s3client = boto3.client("s3")
lambda_client = boto3.client("lambda")

bucket = os.getenv("Bucket")
get_car_lambda_arn = os.getenv("GetCarLambda")


def get_user_id(event): 
    return event["requestContext"]["authorizer"]["claims"]["sub"]


def prepare_response(code, message):
    return {
            'statusCode': code,
            'headers': {
                "Access-Control-Allow-Credentials" : True,
                "Access-Control-Allow-Origin": "*"
            },
            'body': json.dumps({ "message":message})
        }


def upload(event, context):
    request_body = json.loads(event['body'])
    car_id = request_body['carId']
    imageData = request_body["photo"].split(',')[1]
    extenstion = re.split(";|/", request_body["photo"])[1]
    photoId = str(uuid.uuid4()) + "." + extenstion

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
    user_id = get_user_id(event)

    if user_id != car_owner_id:
        return prepare_response(403, 'It\'s not your car!')

    s3client.put_object(
        Bucket=bucket,
        Key=photoId,
        Body=base64.b64decode(imageData)
    )
    
    return prepare_response(200, 'Upload succesful')
