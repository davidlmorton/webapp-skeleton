from pprint import pprint
import abc
import json
import os
import requests
import unittest

__all__ = ['BaseAPITest']


class BaseAPITest(unittest.TestCase):
    __metaclass__ = abc.ABCMeta
    session = requests.Session()
    session.verify = True

    def get(self, url, **kwargs):
        response = self.deserialize_response(self.session.get(url, **kwargs))
        self.print_response(response, **kwargs)
        return response

    def patch(self, url, data, **kwargs):
        response = self.deserialize_response(
            self.session.patch(url,
                headers={'content-type': 'application/json'},
                data=json.dumps(data),
                **kwargs))
        self.print_response(response)
        return response

    def post(self, url, data, **kwargs):
        response = self.deserialize_response(
            self.session.post(url,
                    allow_redirects=False,
                    headers={'content-type': 'application/json'},
                    data=json.dumps(data), **kwargs))
        self.print_response(response, **kwargs)
        return response

    def put(self, url, data, **kwargs):
        response = self.deserialize_response(
            self.session.put(url,
                allow_redirects=False,
                headers={'content-type': 'application/json'},
                data=json.dumps(data), **kwargs))
        self.print_response(response, **kwargs)
        return response

    def delete(self, url, **kwargs):
        response = self.deserialize_response(
                self.session.delete(url,
                    allow_redirects=False,
                    **kwargs))
        self.print_response(response, **kwargs)
        return response

    @staticmethod
    def print_response(response, auth=None, **kwargs):
        pad = '==========================='
        dpad = pad.replace('=', '-')
        request = response.request
        print("\n#===================================================" + pad)
        print("# %s %s %s" % (response.status_code,
                    request.method, get_endpoint_name(request.url)))
        print("# Url: %s" % request.url)
        print("#---------------------------------------------------" + dpad)
        if 'Authorization' in request.headers:
            print("# Authorization: %s" % request.headers['Authorization'])
        if auth:
            print("# BasicAuth: USER=%s PASS=%s" % auth)
        if request.body:
            print("#----------[ Request ]------------------------------" + dpad)
            pprint(json.loads(request.body))
        print("#----------[ Response: %s ]------------------------" %
                response.status_code + dpad)
        pprint(response.DATA)

    @staticmethod
    def deserialize_response(response):
        response.DATA = response.json()
        return response
