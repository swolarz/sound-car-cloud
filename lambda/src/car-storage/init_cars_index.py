import os
import json
import logging
from elasticsearch import Elasticsearch

import es_client
from cars_schema import schema as cars_schema


def init_cars_index(es: Elasticsearch):
    index_name = 'sound-car-cloud'
    index_exists = es.indices.exists(index_name)

    if not index_exists:
        es.indices.create(index_name, body=cars_schema)


def handler(event, context):
    es_endpoint = os.getenv('ELASTICSEARCH_SERVICE_ENDPOINT')

    try:
        es: Elasticsearch = es_client.get_elasticsearch_client(es_endpoint)
        init_cars_index(es)

    except Exception as e:
        logging.exception('Failed to initialize elasticsearch index')
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'error': 'elasticsearch-client-connection',
                'message': 'Elasticsearch service client connection error with endpoint = {}'.format(es_endpoint)
            })
        }

    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json'
        },
        'body': json.dumps({
            'message': 'Car index created successfully'
        })
    }
