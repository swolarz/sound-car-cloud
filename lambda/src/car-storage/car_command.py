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


def prepare_car_document(car_request: object, user: dict, photo_id: str):
    validate(car_request, {
        'type': 'object',
        'properties': {
            'carTitle': {'type': 'string', 'maxLength': 200},
            'carDescription': {'type': 'string', 'maxLength': 10000},
            'engine': {'type': 'string', 'maxLength': 100},
            'horsePower': {'type': 'integer', 'minimum': 0, 'maximum': 10000},
            'mileage': {'type': 'integer', 'minimum': 0, 'maximum': 2000000},
            'year': {'type': 'integer', 'minimum': 1900, 'maximum': 2100}
        },
        'required': ['carTitle', 'carDescription', 'engine']
    })

    user_id = user['id']
    user_name = user['name']

    car_intro = ' '.join(car_request['carDescription'][:200].split())

    return {
        'carTitle': car_request['carTitle'],
        'carDescription': car_request['carDescription'],
        'carIntroDescription': car_intro,
        'engine': car_request['engine'],
        'horsePower': car_request['horsePower'],
        'mileage': car_request['mileage'],
        'year': str(car_request['year']),
        'ownerId': user_id,
        'ownerName': user_name,
        'photoId': photo_id
    }


def get_car_document(es: Elasticsearch, car_id: str):
    fields = [
        'carTitle', 'carDescription',
        'photoId', 'engineSoundFile',
        'ownerId', 'ownerName',
        'engine', 'horsePower', 'year', 'mileage'
    ]

    result = es.get(index=cars_index_name, id=car_id, _source=fields)
    car_doc = result['_source']
    car_doc['id'] = result['_id']

    return {
        'id': result['_id'],
        'owner': {
            'id': car_doc['ownerId'],
            'name': car_doc['ownerName']
        },
        'carTitle': car_doc['carTitle'],
        'carDescription': car_doc['carDescription'],
        'photoUrl': car_doc['photoId'],
        # 'engineSoundUrl': car_doc['engineSoundFile'],
        'engine': car_doc['engine'],
        'horsePower': car_doc['horsePower'],
        'year': car_doc['year'],
        'mileage': car_doc['mileage']
    }


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


def get_user(event) -> dict:
    return {
        'id': event["requestContext"]["authorizer"]["claims"]["sub"],
        'name': '__user__'
    }


def create_car_document(event_body, user, photo_id):
    # Parse and validate new car request body
    try:
        car_request = json.loads(event_body)
        return (True, prepare_car_document(car_request, user, photo_id))
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


def index_car(es, car_request_data, car_id, user, photo_id):
    success, result = create_car_document(car_request_data, user, photo_id)
    
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


def post_car_handler(event, context):
    es = get_es_client()
    user = get_user(event)
    
    return index_car(es, event['body'], None, user, None)


def put_car_handler(event, context):
    user = get_user(event)
    user_id = user['id']
    car_id = event["pathParameters"]["car_id"]

    es = get_es_client()
    car_doc = get_car_document(es, car_id)

    if car_doc['ownerId'] != user_id:
        return response(403, 'Not authorized to modify this car')

    return index_car(es, event['body'], car_id, user, car_doc['photoId'])


def get_car_handler(event, context):
    car_id = event["car_id"] if "car_id" in event else event["pathParameters"]["car_id"]
    
    es = get_es_client()
    try:
        car_doc = get_car_document(es, car_id)
        return response(200, car_doc)
    except NotFoundError:
        return response(404, 'Not found')
    

def assign_photo_to_car(event, context):
    car_id = event["car_id"]
    photo_id = event["photo_id"]

    es = get_es_client()
    car_doc = get_car_document(es, car_id)
    car_doc['photoId'] = photo_id

    user_id = get_user(event)['id']
    if car_doc['ownerId'] != user_id:
        return response(403, 'Not authorized to modify this car')

    try:
        es.index(index=cars_index_name, body=car_doc, id=car_id)
    except Exception:
        logging.exception('Failed to insert new car photo')
