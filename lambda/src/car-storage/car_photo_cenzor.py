import json
import os
import logging
logging.getLogger().setLevel(logging.INFO)

import boto3

from jsonschema import validate, ValidationError
from elasticsearch import Elasticsearch
from elasticsearch_dsl import UpdateByQuery

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


def handler(event, context):
    es_endpoint = os.getenv('ELASTICSEARCH_SERVICE_ENDPOINT')
    photo_id = event["photo_id"]

    # Connect to Elasticsearch service
    try:
        es = es_client.get_elasticsearch_client(es_endpoint)
    except Exception:
        logging.exception('Failed to connect to Elasticsearch cluster')
        return response(500, {
            'error': 'elasticsearch-client-connection',
            'message': 'Elasticsearch service is not available'
        })

    try:
        update = UpdateByQuery(using=es).index(cars_index_name)
        update = update.filter('term', photoId=photo_id)
        update = update.script(source='ctx._source.photoId = params.nullPhoto', params={'nullPhoto': None})
        update.execute()

        return response(200, {'result': 'Update seccessfull'})

    except Exception:
        logging.exception('Failed to cenzor photo')
        return response(500, {
            'error': 'car-photo-cenzor-fail',
            'message': 'Failed to cenzor requested photo'
        })
