from elasticsearch import Elasticsearch, RequestsHttpConnection


def get_elasticsearch_client(es_endpoint: str) -> Elasticsearch:
    try:
        es = Elasticsearch(
            hosts=[{'host': es_endpoint, 'port': 443}],
            use_ssl=True,
            verify_certs=True,
            connection_class=RequestsHttpConnection
        )

        return es
    except Exception as e:
        raise ConnectionError('Failed to connect to Elasticsearch cluster', e)

