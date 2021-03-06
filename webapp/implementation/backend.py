from webapp.exceptions import NoSuchEntityError
from webapp.implementation.server_info import get_server_info
from webapp.nicer_logging import getLogger

LOG = getLogger(__name__)


class Backend:
    """
    All methods are expected to return pure data, no Models.  This helps
    to isolate it from the api.
    """

    def __init__(self, celery_app):
        self.celery_app = celery_app

    @property
    def do_work_task(self):
        return self.celery_app.tasks[
                'webapp.implementation.celery_tasks.worker.do_work']

    def cleanup(self):
        # this is where you'd close persistent connections to backing services
        pass

    def server_info(self, check_celery):
        if check_celery:
            return get_server_info('webapp.implementation.celery_app')
        else:
            return get_server_info()

    def get_work_result(self, task_uuid):
        async_result = self.do_work_task.AsyncResult(task_uuid)
        async_result_status = async_result.status
        if async_result_status == 'PENDING':
            inspector = self.celery_app.control.inspect()
            tasks_per_worker = inspector.query_task(task_uuid)
            if tasks_per_worker is not None:
                for task_dict in tasks_per_worker.values():
                    if task_uuid in task_dict:
                        status, task_info = task_dict[task_uuid]
                        return {
                            'result_status': async_result_status,
                            'task_status': status,
                            **task_info,
                        }
            raise NoSuchEntityError("No job with id (%s) could be found" %
                    task_uuid)
        else:
            return {
                    'result_status': async_result.status,
                    'result': str(async_result.info),
            }

    def do_work(self, numerator, denominator, wallclock_time):
        celery_params = {
                'numerator': numerator,
                'denominator': denominator,
                'wallclock_time': wallclock_time}
        LOG.debug('Queueing work to divide %s by %s',
                numerator, denominator,
                extra={'webapp.celery_params': celery_params,
                       'webapp.celery_task': 'worker.do_work'})
        async_result = self.do_work_task.delay(**celery_params)
        return {'id': async_result.id}
