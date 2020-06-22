import requests
import unittest
from unittest.mock import patch

from memsource import constants
from memsource.api_rest.term_base import TermBase


class TestTermBase(unittest.TestCase):
    @patch("builtins.open")
    @patch.object(requests.Session, "request")
    def test_download(self, mock_request: unittest.mock, mock_open: unittest.mock.MagicMock):
        mock_request.return_value = unittest.mock.MagicMock(status_code=200)

        TermBase(token="mock-token").download(1, "mock-local-filepath")

        mock_request.assert_called_with(
            constants.HttpMethod.get.value,
            "https://cloud.memsource.com/web/api2/v1/termBases/1/export",
            params={"format": "Xlsx", "charset": "UTF-8", "token": "mock-token"},
            timeout=300,
        )
        mock_open.assert_called_with('mock-local-filepath', 'wb')
