from unittest.mock import patch, PropertyMock
from memsource import api, constants, models
import requests
import api as api_test


class TestApiAnalysis(api_test.ApiTestCase):
    def setUp(self):
        self.url_base = 'https://cloud.memsource.com/web/api/v2/analyse'
        self.analysis = api.Analysis('token')

    @patch.object(requests.Session, 'request')
    def test_get(self, mock_request):
        type(mock_request()).status_code = PropertyMock(return_value=200)
        mock_request().json.return_value = {}

        analysis_id = self.gen_random_int()

        self.assertIsInstance(self.analysis.get(analysis_id), models.Analysis)

        mock_request.assert_called_with(
            constants.HttpMethod.get.value,
            '{}/get'.format(self.url_base),
            params={
                'token': self.analysis.token,
                'analyse': analysis_id,
            },
            timeout=constants.Base.timeout.value
        )

    @patch.object(requests.Session, 'request')
    def test_create(self, mock_request):
        type(mock_request()).status_code = PropertyMock(return_value=200)
        mock_request().json.return_value = {}

        job_part_ids = [self.gen_random_int()]

        self.assertIsInstance(self.analysis.create(job_part_ids), models.Analysis)

        mock_request.assert_called_with(
            constants.HttpMethod.post.value,
            '{}/create'.format(self.url_base),
            data={
                'token': self.analysis.token,
                'jobPart': job_part_ids,
            },
            timeout=constants.Base.timeout.value
        )

    @patch.object(requests.Session, 'request')
    def test_delete(self, mock_request):
        type(mock_request()).status_code = PropertyMock(return_value=200)
        mock_request().json.return_value = None

        analysis_id = self.gen_random_int()

        self.assertIsNone(self.analysis.delete(analysis_id))

        mock_request.assert_called_with(
            constants.HttpMethod.post.value,
            '{}/delete'.format(self.url_base),
            data={
                'token': self.analysis.token,
                'analyse': analysis_id,
                'purge': False,
            },
            timeout=constants.Base.timeout.value
        )

    @patch.object(requests.Session, 'request')
    def test_get_by_project(self, mock_request):
        type(mock_request()).status_code = PropertyMock(return_value=200)
        mock_request().json.return_value = [{id: 1}, {id: 2}]

        project_id = self.gen_random_int()

        analyses = self.analysis.get_by_project(project_id)

        self.assertIsInstance(analyses, list)
        for analysis in analyses:
            self.assertIsInstance(analysis, models.Analysis)

        mock_request.assert_called_with(
            constants.HttpMethod.get.value,
            '{}/listByProject'.format(self.url_base),
            params={
                'token': self.analysis.token,
                'project': project_id,
            },
            timeout=constants.Base.timeout.value
        )
