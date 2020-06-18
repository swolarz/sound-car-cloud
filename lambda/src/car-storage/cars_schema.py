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
            'engineSoundFile': {
                'type': 'keyword'
            },
            'carPhotos': {
                'properties': {
                    'main': {
                        'type': 'keyword'
                    },
                    'all': {
                        'properties': {
                            'full': {
                                'type': 'keyword',
                            },
                            'thumbnail': {
                                'type': 'keyword'
                            }
                        }
                    }
                }
            },
            'carTitle': {
                'type': 'text'
            },
            'carDescription': {
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
                'format': 'yyyy'
            },
            'engine': {
                'type': 'text'
            }
        }
    }
}
