from webapp import settings
import datetime
import psutil
import subprocess


def get_server_info(celery_app_import_path=None):
    p = psutil.Process()
    started = datetime.datetime.fromtimestamp(p.create_time())
    uptime = str(datetime.datetime.now() - started)
    started_str = started.strftime("%Y-%m-%d %H:%M:%S")

    if celery_app_import_path is not None:
        try:
            celery_status = subprocess.check_output(['celery', '-A',
                    celery_app_import_path, '--no-color', 'status'],
                    universal_newlines=True)
            celery_status_list = [s for s in str(celery_status).split('\n')
                    if len(s)]
        except subprocess.CalledProcessError:
            celery_status_list = ['Could not reach any celery nodes!']
    else:
        celery_status_list = ['Did not query for celery nodes.']

    return {
            'celeryStatus': celery_status_list,
            'sourceVersion': settings.source_version,
            'startedAt': started_str,
            'uptime': uptime}
