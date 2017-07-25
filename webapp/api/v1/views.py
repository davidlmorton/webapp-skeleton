from flask import g, request
from flask_restful import Resource
from webapp import nicer_logging
from webapp import settings
from webapp.api import view_wrappers
from webapp.nicer_logging import getLogger
from webapp.urls import url_for

LOG = getLogger(__name__)


def logged_response(**kwargs):
    return nicer_logging.logged_response(logger=LOG,
            endpoint_version='v1', **kwargs)


def query_string_args(**kwargs):
    return view_wrappers.query_string_args(logger=LOG, **kwargs)


class Status(Resource):
    @logged_response(endpoint_name='Status')
    @query_string_args(allowed=['celery'])
    def get(self):
        check_celery = 'celery' in request.args
        return g.backend.server_info(check_celery=check_celery), 200
