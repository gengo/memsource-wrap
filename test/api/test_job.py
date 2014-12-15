from unittest.mock import patch, PropertyMock
from memsource import api, models
import requests
import os
import api as api_test


class TestApiJob(api_test.ApiTestCase):
    def setUp(self):
        self.url_base = 'https://cloud1.memsource.com/web/api/v6/job'
        self.job = api.Job(None)
        self.test_file_path = '/tmp/test_file.txt'
        with open(self.test_file_path, 'w+') as f:
            f.write('This is test file.')

        self.create_return_value = {
            'jobParts': [{
                'id': 9371,
                'task': '5023cd08e4b015e0656c4a8f',
                'fileName': 'test_file.txt',
                'targetLang': 'ja',
                'wordCount': 121,
                'beginIndex': 0,
                'endIndex': 14
            }, {
                'id': 9372,
                'task': '5087ab08eac015e0656c4a00',
                'fileName': 'test_file.txt',
                'targetLang': 'ja',
                'wordCount': 121,
                'beginIndex': 0,
                'endIndex': 14
            }]
        }

    def tearDonw(self):
        os.remove(self.test_file_path)

    @patch.object(requests, 'request')
    def test_create(self, mock_request):
        type(mock_request()).status_code = PropertyMock(return_value=200)
        mock_request().json.return_value = self.create_return_value

        target_lang = 'ja'
        project_id = self.gen_random_int()

        returned_value = self.job.create(project_id, self.test_file_path, target_lang)

        # Don't use assert_called_with because files has file object. It is difficult to test.
        self.assertTrue(mock_request.called)
        (called_args, called_kwargs) = mock_request.call_args

        del called_kwargs['files']
        self.assertEqual(('post', '{}/create'.format(self.url_base)), called_args)

        self.assertEqual({
            'params': {
                'token': self.job.token,
                'project': project_id,
                'targetLang': target_lang,
            },
            'timeout': 5,
        }, called_kwargs)

        self.assertEqual(2, len(returned_value))
        for job_part in returned_value:
            self.assertIsInstance(job_part, models.JobPart)
