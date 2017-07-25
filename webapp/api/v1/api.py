from flask_restful import Api
from webapp.urls import ENDPOINT_INFO
from webapp.api.v1 import views

__all__ = ['api']

api = Api(default_mediatype='application/json')

for endpoint_name, info in ENDPOINT_INFO['v1'].items():
    api.add_resource(getattr(views, endpoint_name),
            info['url'], endpoint=endpoint_name)
