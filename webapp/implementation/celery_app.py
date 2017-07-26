from celery import signals
from webapp import nicer_logging
from webapp.ids import generate_id
from webapp.implementation.utils import get_celery_config
from webapp.logging_configuration import configure_celery_logging
from pprint import pformat
import celery
import flask

LOG = nicer_logging.getLogger(__name__)

TASK_PATH = 'webapp.implementation.celery_tasks'

app = celery.Celery('WEBAPP-celery', include=TASK_PATH)
flask_app = flask.Flask('webapp-celery-stub')
flask_app_context = flask_app.app_context()

app.conf['CELERY_ROUTES'] = ({
    TASK_PATH + '.worker.do_work': {'queue': 'worker'},
})

app.conf['CELERY_ANNOTATIONS'] = ({
    TASK_PATH + '.worker.do_work': {
        'ignore_result': False,
        'max_retries': 5,
    },
})

config = get_celery_config()
app.conf.update(config)

# This has to be imported AFTER the app.conf is set up or
# the tasks will default to using pickle serialization which is forbidden by
# this configuration.
from . import celery_tasks  # noqa


@signals.setup_logging.connect
def setup_celery_logging(**kwargs):
    configure_celery_logging()
    LOG.debug("Celery Configuration: %s", pformat(dict(app.conf)))


@signals.task_prerun.connect
def setup_flask_context(**kwargs):
    flask_app_context.push()
    correlation_id = generate_id()[:7]  # unique "enough" and short
    flask.g.correlation_id = correlation_id


@signals.task_postrun.connect
def teardown_flask_context(**kwargs):
    flask_app_context.pop()


@signals.worker_init.connect
def prefork_worker_startup(**kwargs):
    # prefork workers are used in production and in testing
    return _setup_celery_connections(**kwargs)


@signals.eventlet_pool_started.connect
def eventlet_worker_startup(**kwargs):
    # eventlet workers are used only in testing, so we can collect code
    # coverage metrics
    return _setup_celery_connections(**kwargs)


def _setup_celery_connections(**kwargs):
    # this is where you'd set up connections to backing services
    pass
