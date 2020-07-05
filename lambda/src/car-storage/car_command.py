import json
import os
import logging
logging.getLogger().setLevel(logging.INFO)

import boto3
from botocore.errorfactory import ClientError

import urllib.parse
from jsonschema import validate, ValidationError
from elasticsearch import Elasticsearch
from elasticsearch import NotFoundError

import es_client
from cars_schema import index_name as cars_index_name


s3_client = boto3.client('s3')


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


def does_media_exist(media_bucket, media_key):
    try:
        s3_client.head_object(Bucket=media_bucket, Key=media_key)
        return True
    except ClientError:
        return False


def prepare_car_document(car_request: object, user: dict, media_bucket: str):
    validate(car_request, {
        'type': 'object',
        'properties': {
            'carTitle': {'type': 'string', 'maxLength': 200},
            'carDescription': {'type': 'string', 'maxLength': 10000},
            'engine': {'type': 'string', 'maxLength': 100},
            'horsePower': {'anyOf': [{'type': 'integer', 'minimum': 0, 'maximum': 10000}, {'type': 'null'}]},
            'mileage': {'anyOf': [{'type': 'integer', 'minimum': 0, 'maximum': 2000000}, {'type': 'null'}]},
            'year': {'anyOf': [{'type': 'integer', 'minimum': 1900, 'maximum': 2100}, {'type': 'null'}]},
            'photoId': {'type': 'string', 'maxLength': 200},
            'audioId': {'type': 'string', 'maxLength': 200}
        },
        'required': ['carTitle', 'carDescription', 'engine', 'horsePower', 'mileage', 'year', 'audioId']
    })

    user_id = user['id']
    user_name = user['name']

    car_intro = ' '.join(car_request['carDescription'][:200].split())

    if car_request['photoId']:
        photo_key = 'car-photos/{}'.format(car_request['photoId'])
        photo_exists = does_media_exist(media_bucket, photo_key)
        if not photo_exists:
            car_request['photoId'] = ''

    if not car_request['audioId']:
        raise ValueError('Car audio not uploaded')
    
    audio_key = 'car-audio/{}'.format(car_request['audioId'])
    audio_exists = does_media_exist(media_bucket, audio_key)
    if not audio_exists:
        raise ValueError('car-audio-not-found')

    car_doc = {
        'carTitle': car_request['carTitle'],
        'carDescription': car_request['carDescription'],
        'carIntroDescription': car_intro,
        'engine': car_request['engine'],
        'horsePower': car_request['horsePower'],
        'mileage': car_request['mileage'],
        'year': str(car_request['year']),
        'ownerId': user_id,
        'ownerName': user_name,
        'photoId': car_request['photoId'],
        'engineAudioId': car_request['audioId']
    }
    logging.info('Parsed and validated car document: {}'.format(json.dumps(car_doc, indent=2)))
    return car_doc


def get_car_document(es: Elasticsearch, car_id: str):
    fields = [
        'carTitle', 'carDescription',
        'photoId', 'engineAudioId',
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
        'photoId': car_doc['photoId'],
        'audioId': car_doc['engineAudioId'],
        'engine': car_doc['engine'],
        'horsePower': car_doc['horsePower'],
        'year': car_doc['year'],
        'mileage': car_doc['mileage']
    }


def get_es_client() -> (bool, Elasticsearch):
    es_endpoint = os.getenv('ELASTICSEARCH_SERVICE_ENDPOINT')

    # Connect to Elasticsearch service
    try:
        return True, es_client.get_elasticsearch_client(es_endpoint)
    except Exception:
        logging.exception('Failed to connect to Elasticsearch cluster')
        return False, response(500, {
            'error': 'elasticsearch-client-connection',
            'message': 'Elasticsearch service is not available'
        })


def get_user(event) -> dict:
    auth_claim = event["requestContext"]["authorizer"]["claims"]
    return {
        'id': auth_claim["sub"],
        'name': auth_claim["cognito:username"]
    }


def create_car_document(event_body, user, media_bucket):
    # Parse and validate new car request body
    try:
        car_request = json.loads(event_body)
        return True, prepare_car_document(car_request, user, media_bucket)
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
    except ValueError as e:
        msg = str(e)
        if msg == 'car-audio-not-found':
            return False, response(404, {
                'error': 'car-audio-not-found',
                'message': 'Specified audio file not found'
            })
        return False, response(400, {
            'error': 'car-validation-error',
            'message': msg
        })


def index_car(es, car_request_data, car_id, user, media_bucket):
    success, result = create_car_document(car_request_data, user, media_bucket)
    
    if not success:
        return False, result

    # Index new car document in the Elasticsearch service
    try:
        index_result = es.index(index=cars_index_name, body=result, id=car_id)
    except Exception:
        logging.exception('Failed to insert new car')
        return False, response(500, {
            'error': 'car-insert-failed',
            'message': 'Unexpected car insert failure'
        })

    car_doc = get_car_document(es, index_result['_id'])
    return True, response(200, car_doc)


def post_car_handler(event, context):
    media_bucket = os.getenv('CAR_MEDIA_BUCKET')

    success, es_result = get_es_client()
    if not success:
        return es_result

    es = es_result
    user = get_user(event)

    if not user['id']:
        return response(403, {
            'error': 'not-authorized',
            'message': 'Not authorized'
        })
    
    success, resp = index_car(es, event['body'], None, user, media_bucket)
    return resp


def put_car_handler(event, context):
    media_bucket = os.getenv('CAR_MEDIA_BUCKET')

    user = get_user(event)
    user_id = user['id']
    car_id = event["pathParameters"]["car_id"]

    success, result = get_es_client()
    if not success:
        return result

    es = result
    car_doc = get_car_document(es, car_id)

    if car_doc['owner']['id'] != user_id:
        return response(403, 'Not authorized to modify this car')

    success, resp = index_car(es, event['body'], car_id, user, media_bucket)

    if not success:
        return resp

    try:
        old_audio_id = car_doc['audioId']
        new_audio_id = json.loads(event['body'])['audioId']

        if old_audio_id and old_audio_id != new_audio_id:
            s3_client.delete_object(Bucket=media_bucket, Key='car-audio/{}'.format(old_audio_id))
    except:
        logging.warn('Failed to cleanup old audio file')

    return resp


def delete_car_handler(event, context):
    media_bucket = os.getenv('CAR_MEDIA_BUCKET')
    car_id = event['pathParameters']['car_id']

    success, es_result = get_es_client()
    if not success:
        return es_result

    user = get_user(event)

    es = es_result
    try:
        car_doc = get_car_document(es, car_id)

        if car_doc['owner']['id'] != user['id']:
            return response(403, {
                'error': 'car-delete-not-owner',
                'message': 'Not authorized to delete specified car'
            })

        photo_id = car_doc['photoId']
        audio_id = car_doc['audioId']

        es.delete(index=cars_index_name, id=car_id)

        if photo_id:
            try:
                s3_client.delete_object(Bucket=media_bucket, Key='car-photos/{}'.format(photo_id))
            except ClientError:
                logging.warn('Failed to cleanup car photo')

        if audio_id:
            try:
                s3_client.delete_object(Bucket=media_bucket, Key='car-audio/{}'.format(audio_id))
            except ClientError:
                logging.warn('Faied to cleanup car audio')

        return response(200, {
            'message': 'Car deleted successfully'
        })

    except NotFoundError:
        return response(404, 'Car not found')
    except Exception:
        logging.exception('Failed to remove car')
        return response(500, {
            'error': 'car-remove',
            'message': 'Failed to remove car'
        })


def get_car_handler(event, context):
    car_id = event["car_id"] if "car_id" in event else event["pathParameters"]["car_id"]
    
    success, es_result = get_es_client()
    if not success:
        return es_result
    
    es = es_result
    try:
        car_doc = get_car_document(es, car_id)
        return response(200, car_doc)
    except NotFoundError:
        return response(404, 'Car not found')
    
