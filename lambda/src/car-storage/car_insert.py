import json
import os
import logging
logging.getLogger().setLevel(logging.INFO)

from jsonschema import validate, ValidationError
from elasticsearch import Elasticsearch
from elasticsearch import NotFoundError

import es_client
from cars_schema import index_name as cars_index_name


def response(status_code: int, response: object):
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            "Access-Control-Allow-Credentials" : True,
            "Access-Control-Allow-Origin": "*"
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


def get_car_document(es: Elasticsearch, car_id: str):
    result = es.get(index=cars_index_name, id=car_id)
    car_doc = result['_source']
    car_doc['id'] = result['_id']

    return car_doc


def get_es_client() -> Elasticsearch:
    es_endpoint = os.getenv('ELASTICSEARCH_SERVICE_ENDPOINT')

    # Connect to Elasticsearch service
    try:
        return es_client.get_elasticsearch_client(es_endpoint)
    except Exception:
        logging.exception('Failed to connect to Elasticsearch cluster')
        return response(500, {
            'error': 'elasticsearch-client-connection',
            'message': 'Elasticsearch service is not available'
        })


def get_user_id(event): 
    return event["requestContext"]["authorizer"]["claims"]["sub"]


def prepare_car_doc(event_body, user_id):
    # Parse and validate new car request body
    try:
        car_request = json.loads(event_body)
        return (True, prepare_car_document(car_request, user_id))
    except json.decoder.JSONDecodeError:
        logging.exception('Failed to decode request body json')
        return (False, response(400, {
            'error': 'car-invalid-request-format',
            'message': 'Invalid request body format - json expected'
        }))
    except ValidationError as e:
        logging.exception('Invalid request body for new car document')
        return (False, response(400, {
            'error': 'car-invalid-request-data',
            'message': 'Invalid car data: {}'.format(e.message)
        }))


def index_car(es, car_request_data, car_id, user_id):
    success, result = prepare_car_doc(car_request_data, user_id)
    
    if not success:
        return result

    # Index new car document in the Elasticsearch service
    try:
        index_result = es.index(index=cars_index_name, body=result, id=car_id)
    except Exception:
        logging.exception('Failed to insert new car')
        return response(500, {
            'error': 'car-insert-failed',
            'message': 'Unexpected car insert failure'
        })

    car_doc = get_car_document(es, index_result['_id'])
    return response(200, car_doc)


def handler(event, context):
    es = get_es_client()
    user_id = get_user_id(event)
    
    return index_car(es, event['body'], None, user_id)


def put_car_handler(event, context):
    user_id = get_user_id(event)
    car_id = event["pathParameters"]["car_id"]

    es = get_es_client()
    car_doc = get_car_document(es, car_id)

    if car_doc['ownerId'] != user_id:
        return response(403, car_doc)

    return index_car(es, event['body'], car_id, user_id)



def get_car_handler(event, context):
    car_id = event["pathParameters"]["car_id"]
    
    es = get_es_client()
    try:
        car_doc = get_car_document(es, car_id)
        return response(200, car_doc)
    except NotFoundError:
        return response(404, 'Not found')
    