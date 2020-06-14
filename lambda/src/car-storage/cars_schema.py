schema = {
    'settings': {
        'number_of_shards': 1,
        'number_of_replicas': 0
    },
    'mappings': {
        #'cars': {
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
                                    'thumbnail': 'keyword'
                                }
                            }
                        }
                    }
                },
                'carDescription': {
                    'type': 'text'
                },
                'horsepower': {
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
       # }
    }
}
