from flask import request
from functools import wraps
from pprint import pformat
from webapp.exceptions import NoSuchEntityError


def query_string_args(logger, allowed=None, required=None):
    if allowed is None:
        allowed = []
    if required is None:
        required = []

    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            allowed_keys = set(allowed)
            required_keys = set(required)
            valid_keys = allowed_keys | required_keys

            given_keys = set(request.args.keys())
            extra_keys = given_keys - valid_keys
            missing_keys = required_keys - given_keys

            if extra_keys:
                return {'error': 'Invalid query arguments: %s' %
                        pformat(extra_keys)}, 400

            if missing_keys:
                return {'error': 'Missing required query arguments: %s' %
                        pformat(missing_keys)}, 400

            return f(*args, **kwargs)
        return decorated
    return decorator


def handles_no_such_entity_error(logger):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            try:
                result = f(*args, **kwargs)
            except NoSuchEntityError as e:
                return {'error': e.message}, 404
            return result
        return decorated
    return decorator
