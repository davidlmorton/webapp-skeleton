from webapp import nicer_logging
import os
import re

LOG = nicer_logging.getLogger(__name__)

_CONFIGURATION_NAMES = {
        'CELERY_BROKER_CONNECTION_TIMEOUT': 'BROKER_CONNECTION_TIMEOUT',
        'CELERY_BROKER_HEARTBEAT': 'BROKER_HEARTBEAT',
        'CELERY_BROKER_HEARTBEAT_CHECKRATE': 'BROKER_HEARTBEAT_CHECKRATE',
        'CELERY_BROKER_POOL_LIMIT': 'BROKER_POOL_LIMIT',
        'CELERY_BROKER_URL': 'BROKER_URL',
        'CELERY_BROKER_USE_SSL': 'BROKER_USE_SSL',
        'CELERY_BACKEND_USE_SSL': 'BACKEND_USE_SSL',
}


def _default_celery_config_name(env_var_name):
    m = re.search('CELERY', env_var_name)
    return env_var_name[m.start():]


def _get_celery_config_name(env_var_name):
    default = _default_celery_config_name(env_var_name)
    return _CONFIGURATION_NAMES.get(default, default)


def _default_formatter(value):
    return value


def _list_formatter(value):
    return value.split(':')


def _bool_formatter(value):
    return bool(int(value))


def _maybe_float_formatter(value):
    if value == '':
        return None
    else:
        return float(value)


def _maybe_string_formatter(value):
    if value == '':
        return None
    else:
        return value


_FORMATTERS = {
        'BACKEND_USE_SSL': _bool_formatter,
        'BROKER_CONNECTION_TIMEOUT': int,
        'BROKER_HEARTBEAT': _maybe_float_formatter,
        'BROKER_HEARTBEAT_CHECKRATE': float,
        'BROKER_POOL_LIMIT': int,
        'BROKER_USE_SSL': _bool_formatter,
        'CELERY_ACCEPT_CONTENT': _list_formatter,
        'CELERY_ACKS_LATE': _bool_formatter,
        'CELERY_EVENT_QUEUE_EXPIRES': int,
        'CELERY_PREFETCH_MULTIPLIER': int,
        'CELERY_RESULT_BACKEND': _maybe_string_formatter,
        'CELERY_SEND_EVENTS': _bool_formatter,
        'CELERY_TRACK_STARTED': _bool_formatter,
}


def _get_formatter(config_name):
    return _FORMATTERS.get(config_name, _default_formatter)


def _get_config_from_env():
    result = {}
    for env_var_name, env_var_value in os.environ.items():
        if re.match('WEBAPP_CELERY', env_var_name):
            config_name = _get_celery_config_name(env_var_name)
            formatter = _get_formatter(config_name)
            config_value = formatter(env_var_value)

            result[config_name] = config_value
            LOG.debug("Celery config %s=%s derived based on shell environment "
                "%s=%s",
                    config_name, str(config_value), env_var_name, env_var_value)

    return result


def get_celery_config():
    config = _get_config_from_env()
    config.update({
        'BROKER_TRANSPORT_OPTIONS': {'confirm_publish': True},
        'CELERY_ACCEPT_CONTENT': ['json'],
        'CELERY_ACKS_LATE': True,
        'CELERY_RESULT_SERIALIZER': 'json',
        'CELERY_TASK_SERIALIZER': 'json',
        })
    return config
