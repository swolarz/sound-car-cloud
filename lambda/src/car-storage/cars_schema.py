index_name = 'scc-cars'

schema = {
    'settings': {
        'number_of_shards': 1,
        'number_of_replicas': 0
    },
    'mappings': {
        'properties': {
            'ownerId': {
                'type': 'keyword'
            },
            'ownerName': {
                'type': 'keyword',
                'copy_to': 'fullText'
            },
            'engineAudioId': {
                'type': 'keyword'
            },
            'photoId': {
                'type': 'keyword'
            },
            'carTitle': {
                'type': 'text',
                'copy_to': 'fullText'
            },
            'carDescription': {
                'type': 'text',
                'copy_to': 'fullText'
            },
            'carIntroDescription': {
                'type': 'text'
            },
            'horsePower': {
                'type': 'integer'
            },
            'mileage': {
                'type': 'integer'
            },
            'year': {
                'type': 'date',
                'format': 'yyyy',
                'ignore_malformed': 'true',
                'copy_to': 'fullText'
            },
            'engine': {
                'type': 'text',
                'copy_to': 'fullText'
            },
            'fullText': {
                'type': 'text'
            }
        }
    }
}
