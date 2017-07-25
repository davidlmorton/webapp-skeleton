from webapp.implementation.server_info import get_server_info


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
