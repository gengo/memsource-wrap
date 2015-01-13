from unittest.mock import patch, PropertyMock
from memsource import api, constants, models
import requests
import api as api_test


class TestApiAnalysis(api_test.ApiTestCase):
    def setUp(self):
        self.url_base = 'https://cloud1.memsource.com/web/api/v2/analyse'
        self.analysis = api.Analysis('token')

    @patch.object(requests, 'request')
    def test_get(self, mock_request):
        type(mock_request()).status_code = PropertyMock(return_value=200)

        mock_request().json.return_value = {
        }

        analysis_id = self.gen_random_int()

        self.assertIsInstance(self.analysis.get(analysis_id), models.Analysis)

        mock_request.assert_called_with(
            constants.HttpMethod.post.value,
            '{}/get'.format(self.url_base),
            params={
                'token': self.analysis.token,
                'analyse': analysis_id,
            },
            files={},
            timeout=constants.Base.timeout.value
        )
