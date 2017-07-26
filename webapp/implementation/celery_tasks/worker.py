from webapp import nicer_logging
from webapp.implementation.celery_app import app
import time

__all__ = ['do_work']


LOG = nicer_logging.getLogger(__name__)

# TODO: use python3 required kwargs once celery can support it:
# https://github.com/celery/celery/issues/3657


@app.task()
def do_work(numerator=None, denominator=None, wallclock_time=None):
    time.sleep(wallclock_time)  # pretend we're doing something really hard
    return numerator / denominator
