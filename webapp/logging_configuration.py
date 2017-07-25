from webapp import settings
from pythonjsonlogger import jsonlogger
import logging

levels = settings.logging['levels']
options = settings.logging['options']


def configure_celery_logging():
    configure_logging()
    logging.getLogger('celery').setLevel(levels['celery'])
    logging.getLogger('webapp.implementation.celery.worker').setLevel(
            levels['worker'])
    logging.getLogger('requests').setLevel(levels['requests'])


def configure_web_logging():
    configure_logging()
    logging.getLogger('requests').setLevel(levels['requests'])
    logging.getLogger('urllib3').setLevel(levels['urllib3'])
    logging.getLogger('werkzeug').setLevel(levels['werkzeug'])


def configure_logging():
    if options['with_timestamps']:
        format_str = '%(asctime)s '
    else:
        format_str = ''
    format_str += '%(levelname)5s '
    format_str += '%(message)s'

    if options['format_json']:
        format_str += '%(name)s %s(process)d %s(created)s'
        formatter = jsonlogger.JsonFormatter(format_str)
    else:
        formatter = logging.Formatter(format_str)

    logHandler = logging.StreamHandler()
    logHandler.setFormatter(formatter)

    logger = logging.getLogger()
    logger.addHandler(logHandler)

    logger.setLevel(levels['webapp'])
