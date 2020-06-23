import requests
import unittest
from unittest.mock import patch

from memsource import constants, models
from memsource.api_rest.language import Language


class TestLanguage(unittest.TestCase):
    @patch.object(requests.Session, "request")
    def test_list(self, mock_request: unittest.mock):
        ms_response = unittest.mock.MagicMock(status_code=200)
        ms_response.json.return_value = {
            "languages": [
                {"name": "Abkhaz", "code": "ab"},
                {"name": "Afar", "code": "aa"},
            ]
        }
        mock_request.return_value = ms_response

        expected = [
            models.Language(name="Abkhaz", code="ab"),
            models.Language(name="Afar", code="aa"),
        ]
        for lang, expected_lang in zip(
            Language(token="mock-token").listSupportedLangs(), expected
        ):
            self.assertEqual(lang, expected_lang)
            self.assertIsInstance(lang, models.Language)

        mock_request.assert_called_with(
            constants.HttpMethod.get.value,
            "https://cloud.memsource.com/web/api2/v1/languages",
            params={"token": "mock-token"},
            timeout=60,
        )
