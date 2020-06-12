import json
import boto3

rekog = boto3.client('rekognition')

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
