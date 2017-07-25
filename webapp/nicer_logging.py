from flask import g, request
from pprint import pformat
from requests.exceptions import ConnectionError
from requests.models import Request
import logging
import requests
import sys
import time


def getLogger(*args, **kwargs):
    logger = logging.getLogger(*args, **kwargs)
    return CustomLogger(logger=logger)


class CustomLogger(object):
    def __init__(self, logger):
        self.logger = logger

    def __getattr__(self, attr):
        return getattr(self.logger, attr)

    def debug(self, *args, **kwargs):
        return self._add_correlation_id_and_log('debug', args, kwargs)

    def info(self, *args, **kwargs):
        return self._add_correlation_id_and_log('info', args, kwargs)

    def warn(self, *args, **kwargs):
        return self._add_correlation_id_and_log('warn', args, kwargs)

    def error(self, *args, **kwargs):
        return self._add_correlation_id_and_log('error', args, kwargs)

    def critical(self, *args, **kwargs):
        return self._add_correlation_id_and_log('critical', args, kwargs)

    def _add_correlation_id_and_log(self, level_name, args, kwargs):
        my_extra = {**kwargs.get('extra', {})}
        try:
            my_extra['correlation_id'] = g.correlation_id
        except RuntimeError:
            # outside flask application context, this is OK
            pass
        kwargs['extra'] = my_extra
        log_fn = getattr(self.logger, level_name)
        return log_fn(*args, **kwargs)

    def exception(self, *args, **kwargs):
        if 'extra' in kwargs:
            my_extra = kwargs['extra'].copy()
        else:
            my_extra = {}

        my_extra['exception'] = pformat(sys.exc_info()[1])
        my_extra['correlation_id'] = g.correlation_id

        kwargs['extra'] = my_extra
        self.logger.exception(*args, **kwargs)


def logged_response(logger, endpoint_name, endpoint_version):
    def _log_response(target):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            log_level = logger.getEffectiveLevel()

            source = request.access_route[0]
            label = '[%s] %s %s from %s' % (g.correlation_id, request.method,
                    request.full_path, source)

            extra = {'request.method': request.method,
                     'request.endpoint_name': endpoint_name,
                     'request.endpoint_version': endpoint_version,
                     'request.path': request.path,
                     'request.full_path': request.full_path,
                     'request.source': source}
            if log_level <= logging.DEBUG:
                extra['request.body'] = pformat(request.json)
                extra['request.headers'] = pformat(dict(request.headers))

            try:
                result = target(*args, **kwargs)
            except Exception as e:
                logger.exception("%s while handling %s",
                        e.__class__.__name__, label,
                        extra=extra)
                raise

            names = ('body', 'status_code', 'headers')
            levels = (logging.DEBUG, logging.INFO, logging.DEBUG)
            formatters = (pformat, pformat, lambda x: pformat(dict(x)))
            for value, name, level, formatter in zip(
                    result, names, levels, formatters):
                if log_level <= level:
                    extra['response.%s' % name] = formatter(value)

            end_time = time.time()
            extra['response.took'] = int((end_time - start_time) * 1000)

            logger.info("Responding %s to %s",
                    result[1], label,
                    extra=extra)
            return result
        return wrapper
    return _log_response


def _log_request(target, kind):
    def wrapper(*args, **kwargs):

        logger = kwargs.get('logger', getLogger(__name__))
        if 'logger' in kwargs:
            del kwargs['logger']
        log_level = logger.getEffectiveLevel()

        kwargs_for_constructor = get_args_for_request_constructor(kwargs)
        request = Request(kind.upper(), *args, **kwargs_for_constructor)

        extra = {'request.url': request.url,
                 'request.method': kind.upper()}
        if log_level <= logging.DEBUG:
            extra['request.body'] = pformat(request.data)
            extra['request.headers'] = pformat(dict(request.headers))
            extra['request.params'] = request.params

        label = '%s %s' % (kind.upper(), request.url)

        try:
            response = target(*args, **kwargs)
        except ConnectionError:
            # exception should be logged elsewhere
            raise
        except Exception:
            logger.exception("Exception while sending %s", label,
                    extra=extra)
            raise

        extra['response.status_code'] = response.status_code
        if log_level <= logging.DEBUG:
            extra['response.text'] = pformat(response.text)
            extra['response.headers'] = pformat(dict(response.headers))

        return response
    return wrapper


def get_args_for_request_constructor(kwargs):
    kwargs_for_constructor = kwargs.copy()
    if 'timeout' in kwargs_for_constructor:
        # timout is an argument to requests.get/post/ect but not
        # Request.__init__
        del kwargs_for_constructor['timeout']
    return kwargs_for_constructor


class LoggedRequest(object):
    def __getattr__(self, name):
        return _log_request(getattr(requests, name), name)


logged_request = LoggedRequest()
