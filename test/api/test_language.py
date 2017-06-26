from unittest.mock import PropertyMock, patch

import api as api_test
import requests

from memsource import api, constants, models


class TestApiLanguage(api_test.ApiTestCase):
    def setUp(self):
        self.url_base = 'https://cloud.memsource.com/web/api/v2/language'
        self.language = api.Language(None)

    @patch.object(requests.Session, 'request')
    def test_list(self, mock_request):
        type(mock_request()).status_code = PropertyMock(return_value=200)

        mock_request().json.return_value = [
            {
                "name": "Abkhaz",
                "code": "ab"
            },
            {
                "name": "Afar",
                "code": "aa"
            }
        ]

        for language in self.language.listSupportedLangs():
            self.assertIsInstance(language, models.Language)

        mock_request.assert_called_with(
            constants.HttpMethod.post.value,
            '{}/listSupportedLangs'.format(self.url_base),
            data={
                'token': self.language.token,
            },
            timeout=constants.Base.timeout.value
        )
