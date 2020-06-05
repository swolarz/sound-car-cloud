import json

def handler(event, context):
    print('request: {}'.format(json.dumps(event)))
    return {
        'statusCode': 200,
        'headers': {
            "Access-Control-Allow-Credentials" : True,
            "Access-Control-Allow-Origin": "*"
        },
        'body': json.dumps({ "message":'Hello, CDK!'})
    }