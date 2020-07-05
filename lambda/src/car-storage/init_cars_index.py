import os
import json
import logging
from elasticsearch import Elasticsearch

import es_client
from cars_schema import schema as cars_schema, index_name as cars_index_name


def init_cars_index(es: Elasticsearch):
    index_name = cars_index_name
    index_exists = es.indices.exists(index_name)

    if index_exists:
        es.indices.delete(index_name)

    es.indices.create(index_name, body=cars_schema)


def handler(event, context):
    es_endpoint = os.getenv('ELASTICSEARCH_SERVICE_ENDPOINT')

    try:
        es: Elasticsearch = es_client.get_elasticsearch_client(es_endpoint)
        init_cars_index(es)

    except Exception:
        logging.exception('Failed to initialize elasticsearch index')
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'error': 'elasticsearch-client-connection',
                'message': 'Elasticsearch service is not available'
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
