from webapp import urls
from ..base import BaseAPITest


class TestStatus(BaseAPITest):
    def test_successfully_get_status(self):
        url = urls.url_for('v1', 'Status')
        response = self.get(url)
        self.assertEqual(200, response.status_code)

        self.assertIn('uptime', response.DATA)
        self.assertIn('celeryStatus', response.DATA)

    def test_successfully_get_status_with_celery(self):
        url = urls.url_for('v1', 'Status')
        response = self.get(url, params={'celery': 'true'})
        self.assertEqual(200, response.status_code)

        self.assertIn('uptime', response.DATA)
        self.assertIn('celeryStatus', response.DATA)
        self.assertTrue(len(response.DATA['celeryStatus']) > 1)
