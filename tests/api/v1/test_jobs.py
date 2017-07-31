from ..base import BaseAPITest
from webapp import urls
import time


class TestJobs(BaseAPITest):
    def test_success(self):
        url = urls.url_for('v1', 'JobList')
        data = {'numerator': 10,
                'denominator': 11,
                'wallclock_time': 5}
        post_response = self.post(url, data=data)
        self.assertEqual(201, post_response.status_code)

        self.assertIn('id', post_response.DATA)
        job_id = post_response.DATA['id']

        with self.subTest('get'):
            url = urls.url_for('v1', 'JobDetail', job_id=job_id)
            response = self.get(url)
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.DATA['result_status'] in
                    ('PENDING', 'STARTED'))

        with self.subTest('get missing'):
            url = urls.url_for('v1', 'JobDetail',
                    job_id=job_id[:-2])
            response = self.get(url)
            self.assertEqual(404, response.status_code)

        with self.subTest('get result'):
            url = urls.url_for('v1', 'JobDetail', job_id=job_id)
            for sleep_time in (3, 1, 1, 1, 1, 1):
                time.sleep(sleep_time)
                response = self.get(url)
                self.assertEqual(200, response.status_code)
                if response.DATA['result_status'] == 'SUCCESS':
                    self.assertEqual(str(10 / 11.0), response.DATA['result'])
                    return
            self.fail("Timed out waiting for result")

    def test_fail(self):
        url = urls.url_for('v1', 'JobList')
        data = {'numerator': 1,
                'denominator': 0,
                'wallclock_time': 0}
        post_response = self.post(url, data=data)
        self.assertEqual(201, post_response.status_code)

        self.assertIn('id', post_response.DATA)
        job_id = post_response.DATA['id']

        with self.subTest('get'):
            time.sleep(1)
            url = urls.url_for('v1', 'JobDetail', job_id=job_id)
            response = self.get(url)
            self.assertEqual(200, response.status_code)
            self.assertEqual(response.DATA['result_status'], 'FAILURE')
