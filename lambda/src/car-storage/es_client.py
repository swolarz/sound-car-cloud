from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
import boto3
import os


service = 'es'
region = os.getenv('AWS_REGION')
credentials = boto3.Session().get_credentials()
awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)


def get_elasticsearch_client(es_endpoint: str) -> Elasticsearch:
    try:
        es = Elasticsearch(
            hosts=[{'host': es_endpoint, 'port': 443, 'use_ssl': True} ],
            connection_class=RequestsHttpConnection,
            http_auth = awsauth,
            verify_certs = True,
        )

        print(es.info())

        return es
    except Exception as e:
        raise ConnectionError('Failed to connect to Elasticsearch cluster', e)

