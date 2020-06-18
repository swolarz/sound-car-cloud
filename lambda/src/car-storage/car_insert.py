import json
import os
import logging
logging.getLogger().setLevel(logging.INFO)

from jsonschema import validate, ValidationError
from elasticsearch import Elasticsearch

import es_client
from cars_schema import index_name as cars_index_name


def response(status_code: int, response: object):
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json'
        },
        'body': json.dumps(response)
    }


def prepare_car_document(car_request: object, user_id: str):
    validate(car_request, {
        'type': 'object',
        'properties': {
            'carTitle': {'type': 'string', 'maxLength': 200},
            'carDescription': {'type': 'string', 'maxLength': 10000},
            'engine': {'type': 'string', 'maxLength': 100},
            'horsePower': {'type': 'integer', 'minimum': 0, 'maximum': 10000},
            'mileage': {'type': 'integer', 'minimum': 0, 'maximum': 2000000},
            'year': {'type': 'integer', 'minimum': 1900, 'maximum': 2100}
        }
    })

    return {
        'carTitle': car_request['carTitle'],
        'carDescription': car_request['carDescription'],
        'engine': car_request['engine'],
        'horsePower': car_request['horsePower'],
        'mileage': car_request['mileage'],
        'year': str(car_request['year']),
        'ownerId': user_id
    }


def handler(event, context):
    es_endpoint = os.getenv('ELASTICSEARCH_SERVICE_ENDPOINT')

    try:
        es: Elasticsearch = es_client.get_elasticsearch_client(es_endpoint)

        car_request = event['body']
        car_doc = prepare_car_document(car_request, context.identity.cognitoIdentityId)

        car_doc = es.index(index=cars_index_name, body=car_doc)
        return response(200, car_doc)

    except ValidationError as e:
        logging.exception('Invalid request body for new car document')
        return response(400, {
            'error': 'car-invalid-request-data',
            'message': 'Invalid car data: {}'.format(e.message)
        })
        
    except Exception:
        logging.exception('Failed to initialize elasticsearch index')
        return response(500, {
            'error': 'elasticsearch-client-connection',
            'message': 'Elasticsearch service client connection error with endpoint = {}'.format(es_endpoint)
        })

    return response(200, {
        'message': 'Car index created successfully'
    })
