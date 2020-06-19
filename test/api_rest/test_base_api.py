import unittest
from unittest.mock import patch
from memsource import api_rest, exceptions
import requests


class TestBaseApi(unittest.TestCase):
    @patch.object(requests.Session, "request", side_effect=requests.exceptions.Timeout())
    def test_request_timeout(self, mock_request):
        """
        Raise MemsourceApiException when timed out
        """
        api = api_rest.BaseApi()
        self.assertRaises(
            exceptions.MemsourceApiException,
            lambda: api._post("path", {})
        )

    @patch.object(requests.Session, "request", side_effect=requests.exceptions.ConnectionError())
    def test_request_connection_failed(self, mock_request):
        """
        Raise MemsourceApiException when connection failed.
        """
        api = api_rest.BaseApi()
        self.assertRaises(
            exceptions.MemsourceApiException,
            lambda: api._post("path", {})
        )

    def test_init(self):
        headers = {"Authorization": "Bearer TEST-HEADER-TOKEN"}
        token = "TEST-TOKEN"
        api = api_rest.BaseApi(token=token, headers=headers)
        self.assertEqual(api.token, token)
        self.assertEqual(api.headers, headers)

    def test_use_session(self):
        api = api_rest.BaseApi()
        session = unittest.mock.Mock()
        api.use_session(session)
        self.assertEqual(api._session, session)

    @patch.object(requests.Session, "request")
    def test_get(self, mock_request):
        ms_response = unittest.mock.Mock(status_code=200)
        ms_response.json.return_value = {}
        mock_request.return_value = ms_response

        api = api_rest.BaseApi(token="TEST-TOKEN")
        response = api._get("v1/path", {"jobUID": 1})
        mock_request.assert_called_once_with(
            "get", "https://cloud.memsource.com/web/api2/v1/path",
            params={"jobUID": 1, "token": "TEST-TOKEN"}, timeout=60,
        )
        self.assertIsInstance(response, dict)

    @patch.object(requests.Session, "request")
    def test_get_stream(self, mock_request):
        mock_request.return_value = unittest.mock.Mock(status_code=200)

        api = api_rest.BaseApi(token="TEST-TOKEN")
        api._get_stream("v1/path", {"jobUID": 1})
        mock_request.assert_called_once_with(
            "get", "https://cloud.memsource.com/web/api2/v1/path",
            params={"jobUID": 1, "token": "TEST-TOKEN"}, timeout=300,
        )

    @patch.object(requests.Session, "request")
    def test_post(self, mock_request):
        mock_request.return_value = unittest.mock.Mock(status_code=200)
        api = api_rest.BaseApi(token="TEST-TOKEN")
        api._post("v2/path", {"jobUID": 1})
        mock_request.assert_called_once_with(
            "post", "https://cloud.memsource.com/web/api2/v2/path",
            json={"jobUID": 1}, params={"token": "TEST-TOKEN"}, timeout=60,
        )
