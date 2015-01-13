from unittest.mock import patch, PropertyMock
from memsource import api, models, constants
import requests
import api as api_test


class TestApiAsynchronous(api_test.ApiTestCase):
    def setUp(self):
        self.asynchronous = api.Asynchronous(None)

    @patch.object(requests, 'request')
    def test_pre_translate(self, mock_request):
        type(mock_request()).status_code = PropertyMock(return_value=200)

        asynchronous_request_id = self.gen_random_int()
        job_part_ids = [self.gen_random_int() for i in range(0, 2)]

        mock_request().json.return_value = {
            'asyncRequest': {
                'createdBy': {
                    'lastName': 'test',
                    'id': 1,
                    'firstName': 'admin',
                    'role': 'ADMIN',
                    'email': 'test@test.com',
                    'userName': 'admin',
                    'active': True
                },
                'action': 'PRE_TRANSLATE',
                'id': asynchronous_request_id,
                'dateCreated': '2014-11-03T16:03:11Z',
                'asyncResponse': None
            }
        }

        retuned_value = self.asynchronous.preTranslate(job_part_ids)

        self.assertIsInstance(retuned_value, models.AsynchronousRequest)

        mock_request.assert_called_with(
            constants.HttpMethod.post.value,
            'https://cloud1.memsource.com/web/api/async/v2/job/preTranslate',
            params={
                'token': self.asynchronous.token,
                'jobPart': job_part_ids,
            },
            files={},
            timeout=constants.Base.timeout.value
        )

    @patch.object(requests, 'request')
    def test_get_async_request(self, mock_request):
        type(mock_request()).status_code = PropertyMock(return_value=200)

        asynchronous_request_id = self.gen_random_int()

        mock_request().json.return_value = {
            'id': asynchronous_request_id,
            'createdBy': {
                'id': 1,
                'firstName': 'admin',
                'email': 'test@test.com',
                'active': True,
                'userName': 'admin',
                'lastName': 'test',
                'role': 'ADMIN'
            },
            'asyncResponse': None,
            'action': 'PRE_TRANSLATE',
            'dateCreated': '2014-11-03T16:03:11Z'
        }

        retuned_value = self.asynchronous.getAsyncRequest(asynchronous_request_id)

        self.assertIsInstance(retuned_value, models.AsynchronousRequest)

        mock_request.assert_called_with(
            constants.HttpMethod.post.value,
            'https://cloud1.memsource.com/web/api/v2/async/getAsyncRequest',
            params={
                'token': self.asynchronous.token,
                'asyncRequest': asynchronous_request_id,
            },
            files={},
            timeout=constants.Base.timeout.value
        )

    @patch.object(requests, 'request')
    def test_create_analysis(self, mock_request):
        type(mock_request()).status_code = PropertyMock(return_value=200)

        asynchronous_request_id = self.gen_random_int()
        analysis_id = self.gen_random_int()
        mock_request().json.return_value = {
            'asyncRequest': {
                'createdBy': {
                    'lastName': 'test',
                    'id': 1,
                    'firstName': 'admin',
                    'role': 'ADMIN',
                    'email': 'test@test.com',
                    'userName': 'admin',
                    'active': True
                },
                'action': 'PRE_TRANSLATE',
                'id': asynchronous_request_id,
                'dateCreated': '2014-11-03T16:03:11Z',
                'asyncResponse': None
            },
            'analyse': {
                'id': analysis_id,
            },
        }

        job_part_ids = [self.gen_random_int() for i in range(0, 2)]

        async_request, analysis = self.asynchronous.createAnalysis(job_part_ids)

        self.assertEqual(async_request.id, asynchronous_request_id)
        self.assertEqual(analysis.id, analysis_id)

        mock_request.assert_called_with(
            constants.HttpMethod.post.value,
            'https://cloud1.memsource.com/web/api/async/v2/analyse/create',
            params={
                'token': self.asynchronous.token,
                'jobPart': job_part_ids,
            },
            files={},
            timeout=constants.Base.timeout.value
        )
