import os
from . import api


class Configuration:
    def __init__(self):
        """
        Parses webapp configuration from the environment. Key variables:

        - ELASTICSEARCH_HOST
        - ELASTICSEARCH_EXPLAIN
        - STATIC_ROOT
        """

        self.es_host = os.environ['ELASTICSEARCH_HOST']
        if not self.es_host:
            raise Exception('No elasticsearch host')
        self.es_explain = os.environ.get('ELASTICSEARCH_EXPLAIN', False)

        self.static_root = os.environ.get('STATIC_ROOT')
        if not self.static_root or not os.path.isdir(self.static_root):
            raise Exception(
                "No static directory found. STATIC_ROOT=%r" % 
                self.static_root
            )


config = Configuration()
application = api.create_api(config)
