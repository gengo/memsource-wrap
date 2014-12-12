import unittest
from unittest.mock import patch
from memsource import api, exceptions, constants
import requests


class ApiImplements(api.BaseApi):
    """
    api.BaseApi.__init__ is raising NotImplementedError.
    This class implements it for testing.
    """
    api_version = constants.ApiVersion.v2


class TestBaseApi(unittest.TestCase):
    def test_init(self):
        self.assertRaises(NotImplementedError, api.BaseApi, (None, ))

    @patch.object(requests, 'request', side_effect=requests.exceptions.Timeout())
    def test_request_timeout(self, mock_request):
        """
        Raise MemsourceApiException when timed out
        """
        api_implements = ApiImplements(None)
        self.assertRaises(
            exceptions.MemsourceApiException,
            lambda: api_implements._post('path', {})
        )

    @patch.object(requests, 'request', side_effect=requests.exceptions.ConnectionError())
    def test_request_connection_failed(self, mock_request):
        """
        Raise MemsourceApiException when connection failed.
        """
        api_implements = ApiImplements(None)
        self.assertRaises(
            exceptions.MemsourceApiException,
            lambda: api_implements._post('path', {})
        )
