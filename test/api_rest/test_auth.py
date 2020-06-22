import requests
import unittest
from unittest.mock import patch

from memsource import models
from memsource.api_rest import auth


class TestAuth(unittest.TestCase):
    @patch.object(requests.Session, "request")
    def test_login(self, mock_request: unittest.mock):
        ms_response = unittest.mock.Mock(status_code=200)
        ms_response.json.return_value = {
            "user": {
                "lastName": "mock-last-name",
                "email": "mock-tm@gengo.com",
                "firstName": "mock-first-name",
                "id": "1234",
                "userName": "mock-tm",
                "role": "ADMIN",
                "uid": "QWERTY"
            },
            "token": "mock-token",
            "expires": "2020-06-19T07:31:23+0000"
        }
        mock_request.return_value = ms_response

        response = auth.Auth().login(user_name="mock-user", password="mock-password")
        self.assertIsInstance(response, models.Authentication)
        self.assertIsInstance(response["user"], models.User)
        self.assertDictEqual(response["user"], {
            "lastName": "mock-last-name",
            "email": "mock-tm@gengo.com",
            "firstName": "mock-first-name",
            "id": "1234",
            "userName": "mock-tm",
            "role": "ADMIN",
            "uid": "QWERTY"
        })
