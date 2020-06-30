import os
import json
import logging
logging.getLogger().setLevel(logging.INFO)

import urllib.parse

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


def parse_filters(event):
    logging.info(json.dumps(event))

    params = event['queryStringParameters']
    filters = {}

    if 'q' in params:
        if len(params['q']) > 400:
            raise ValueError('Query length must not exceed 400')
        filters['query'] = params['q']
    
    if 'horsePowerFrom' in params or 'horsePowerTo' in params:
        horsePower = {}
        
        if 'horsePowerFrom' in params:
            horsePower['from'] = int(params['horsePowerFrom'])

        if 'horsePowerTo' in params:
            horsePower['to'] = int(params['horsePowerTo'])

        filters['horsePower'] = horsePower

    if 'mileageFrom' in params or 'mileageTo' in params:
        mileage = {}

        if 'mileageFrom' in params:
            mileage['from'] = int(params['mileageFrom'])

        if 'mileageTo' in params:
            mileage['to'] = int(params['mileageTo'])

        filters['mileage'] = mileage

    if 'yearFrom' in params or 'yearTo' in params:
        year = {}

        if 'yearFrom' in params:
            year['from'] = int(params['yearFrom'])

        if 'yearTo' in params:
            year['to'] = int(params['yearTo'])

        filters['year'] = year

    return filters


def parse_page(event):
    params = event['queryStringParameters']

    page_no = int(params['page']) if 'page' in params else 0
    per_page = int(params['perPage']) if 'perPage' in params else 10

    if page_no < 0:
        raise ValueError('Page number must not be negative')

    if per_page < 1:
        raise ValueError('Page must contain at least one element')

    if per_page > 100:
        raise ValueError('Too many records requested')
    
    return {
        'page_no': page_no,
        'per_page': per_page
    }


def make_filter_range(range_filter):
    ops = {
        'from': 'gte',
        'to': 'lte'
    }
    return {ops[side]: val for side, val in range_filter.items()}


def to_car_result_info(car_hit, photos_base_url):
    return  {
        'id': car_hit.meta.id,
        'owner': {
            'id': car_hit.ownerId,
            'name': car_hit.ownerName
        },
        'carTitle': car_hit.carTitle,
        'carIntro': car_hit.carIntroDescription,
        'photoUrl': urllib.parse.urljoin(photos_base_url, car_hit.photoId),
        # 'engineSoundUrl': car_hit.engineSoundFile,
        'engine': car_hit.engine,
        'horsePower': car_hit.horsePower,
        'year': car_hit.year,
        'mileage': car_hit.mileage
    }


def find_cars(es: Elasticsearch, filters: dict, page: dict, photos_url: str) -> dict:
    search = Search(using=es).index(cars_index_name)

    # Pagination
    page_no = page['page_no']
    per_page = page['per_page']
    first = page_no * per_page
    # pylint: disable=unsubscriptable-object
    search = search[first:first + per_page]

    # Fields projection
    search = search.source([
        'carTitle', 'carIntroDescription',
        'photoId', 'engineSoundFile',
        'ownerId', 'ownerName',
        'engine', 'horsePower', 'year', 'mileage'
    ])

    # Selection
    if 'query' in filters:
        search = search.query('match', fullText=filters['query'])

    if 'horsePower' in filters:
        horse_power_range = make_filter_range(filters['horsePower'])
        search = search.filter('range', horsePower=horse_power_range)

    if 'mileage' in filters:
        mileage_range = make_filter_range(filters['mileage'])
        search = search.filter('range', mileage=mileage_range)

    if 'year' in filters:
        year_range = make_filter_range(filters['year'])
        search = search.filter('range', year=year_range)

    # Results extraction
    response = search.execute()
    results = list(map(lambda hit: to_car_result_info(hit, photos_url), response))

    return {
        'total': response.hits.total.value,
        'page': page_no,
        'per_page': per_page,
        'results': results
    }


def handler(event, context):
    es_endpoint = os.getenv('ELASTICSEARCH_SERVICE_ENDPOINT')
    photo_bucket_url = os.getenv('CAR_PHOTOS_BUCKET_URL')

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
        filters = parse_filters(event)
        page = parse_page(event)
    except Exception as e:
        return response(400, {
            'error': 'car-search-params',
            'message': 'Failed to parse search params: {}'.format(e)
        })

    try:
        car_results_data = find_cars(es, filters, page, photo_bucket_url)
    except:
        logging.exception('Failed to fetch find cars by received filters')
        return response(500, {
            'error': 'car-search-error',
            'message': 'Unexpected error during car search operation'
        })

    return response(200, car_results_data)
