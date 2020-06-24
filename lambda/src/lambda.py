import json
import logging
logging.getLogger().setLevel(logging.DEBUG)


def handler(event, context):
    logging.debug('request: {}'.format(json.dumps(event)))
    return {
        'statusCode': 200,
        'headers': {
            "Access-Control-Allow-Credentials" : True,
            "Access-Control-Allow-Origin": "*"
        },
        'body': json.dumps({ "message":'Hello, CDK!'})
    }