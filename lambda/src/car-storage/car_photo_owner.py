import json
import os
import logging
logging.getLogger().setLevel(logging.INFO)

from jsonschema import validate, ValidationError
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search

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
        search = Search(using=es, index=cars_index_name)
        search = search.source(['owner'])
        search = search[0:1]
        search = search.filter('term', photoId=photo_id)
        result = search.execute()

        if result.hits.total.value == 0:
            return response(404, {'message': 'Photo owner not found'})

        return response(200, {
            'owner': {
                'id': result[0].ownerId
            }
        })

    except Exception:
        logging.exception('Failed to retrieve photo owner')
        return response(500, {
            'error': 'photo-owner-fail',
            'message': 'Failed to retrieve owner of the given photo'
        })
