from elasticsearch import Elasticsearch, RequestsHttpConnection


def get_elasticsearch_client(es_endpoint: str) -> Elasticsearch:
    try:
        es = Elasticsearch(
            hosts=[es_endpoint + ":80"],
            connection_class=RequestsHttpConnection
        )

        return es
    except Exception as e:
        raise ConnectionError('Failed to connect to Elasticsearch cluster', e)

