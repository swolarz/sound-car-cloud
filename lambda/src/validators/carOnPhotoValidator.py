import json

def validate(event, context):
    print('request: {}'.format(json.dumps(event)))
