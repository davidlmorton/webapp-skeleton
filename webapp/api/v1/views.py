from flask import g, request
from flask_restful import Resource
from webapp import nicer_logging
from webapp.api import view_wrappers
from webapp.nicer_logging import getLogger

LOG = getLogger(__name__)

handles_no_such_entity_error = view_wrappers.handles_no_such_entity_error(
        logger=LOG)


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


class JobList(Resource):
    @logged_response(endpoint_name='JobList')
    @query_string_args()
    def post(self):
        body = request.json
        return g.backend.do_work(**body), 201


class JobDetail(Resource):
    @logged_response(endpoint_name='JobDetail')
    @query_string_args()
    @handles_no_such_entity_error
    def get(self, job_id):
        return g.backend.get_work_result(task_uuid=job_id), 200
