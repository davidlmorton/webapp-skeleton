import os

# used by the application to build urls that can be returned
# in HTTP responses.
base_url = os.environ['WEBAPP_BASE_URL']

# host and port are only needed for local testing
host = os.environ.get('WEBAPP_HOST', '0.0.0.0')
port = int(os.environ.get('WEBAPP_PORT', '5200'))

logging = {
    'levels': {
        # application logging (stuff we wrote)
        'webapp': os.environ.get('WEBAPP_LOG_LEVEL', 'WARN'),
        'worker': os.environ.get('WEBAPP_WORKER_LOG_LEVEL', 'INFO'),
        # library logging (stuff others wrote)
        'celery': os.environ.get('WEBAPP_CELERY_LOG_LEVEL', 'WARN'),
        'requests': os.environ.get('WEBAPP_REQUESTS_LOG_LEVEL', 'WARN'),
        'urllib3': os.environ.get('WEBAPP_URLLIB3_LOG_LEVEL', 'WARN'),
        'werkzeug': os.environ.get('WEBAPP_WERKZEUG_LOG_LEVEL', 'WARN'),
    },
    'options': {
        'format_json': int(os.environ.get(
            'WEBAPP_LOG_FORMAT_JSON', '0')),
        'with_timestamps': int(os.environ.get(
            'WEBAPP_LOG_WITH_TIMESTAMPS', '1')),
    }
}

# This is put into the environment by Deis/Heroku
source_version = os.environ.get('SOURCE_VERSION', 'Unknown')
