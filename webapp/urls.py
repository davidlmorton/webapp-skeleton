from webapp import settings
from pprint import pformat
import string


BASE_URL = settings.base_url

ENDPOINT_INFO = {
        'v1': {
            'Status': {
                'url': '/status',
                'format': '/status',
            },
        },
}


def relative_url_for(version, endpoint_name, **kwargs):
    info = ENDPOINT_INFO[version][endpoint_name]

    keys = set([t[1] for t in string.Formatter().parse(info['format'])
        if t[1] is not None])

    if set(kwargs) != keys:
        raise TypeError('To format a url for the "{version}" endpoint '
            '"{endpoint_name}" requires exactly the following keys: '
            '{keys}, but you supplied {kwargs} instead'.format(
                version=version,
                endpoint_name=endpoint_name,
                keys=pformat(tuple(keys)),
                kwargs=pformat(tuple(kwargs.keys()))))
    else:
        return info['format'].format(**kwargs)


def url_for(version, endpoint_name, **kwargs):
    route = relative_url_for(version, endpoint_name, **kwargs)
    return "%s/%s%s" % (BASE_URL, version, route)
