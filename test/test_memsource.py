import unittest
import requests
from memsource import constants
from memsource.memsource import Memsource
from unittest.mock import patch, PropertyMock


class TestMemsource(unittest.TestCase):
    def setUp(self):
        self.url_base = 'https://cloud.memsource.com/web/api/v3/auth/login'

    def check_token_and_headers(self, m, token=None, headers=None):
        for api in ('client', 'domain', 'project', 'job', ):
            self.assertEqual(getattr(m, api).token, token)
            self.assertEqual(getattr(m, api).headers, headers)

    @patch.object(requests.Session, 'request')
    def test_init_with_user_name_and_password(self, mock_request):
        type(mock_request()).status_code = PropertyMock(return_value=200)

        token = 'test_token'
        mock_request().json.return_value = {
            'token': token,
            'user': {},
        }

        username = 'test_username'
        password = 'test_password'
        self.check_token_and_headers(Memsource(user_name=username, password=password), token)

        mock_request.assert_called_with(
            constants.HttpMethod.post.value,
            self.url_base,
            data={
                'userName': username,
                'password': password,
                'token': None,
            },
            timeout=constants.Base.timeout.value
        )

    @patch.object(requests.Session, 'request')
    def test_init_with_token(self, mock_request):
        token = 'test_token'
        self.check_token_and_headers(Memsource(token=token), token)

        # When token is given as parameter, never send http request.
        self.assertFalse(mock_request.called)

    @patch.object(requests.Session, 'request')
    def test_init_with_user_name_and_password_and_token(self, mock_request):
        token = 'test_token'
        m = Memsource(user_name='test user name', password='test password', token=token)
        self.check_token_and_headers(m, token)

        # When token is given as parameter, never send http request.
        self.assertFalse(mock_request.called)

    @patch.object(requests.Session, 'request')
    def test_header_memsource_parameter(self, mock_request):
        mock_request.return_value.status_code = 200
        token = None
        mock_request().json.return_value = {
            'token': token,
            'user': {},
        }
        headers = {
            'Authorization': 'Bearer test_token'
        }
        self.check_token_and_headers(Memsource(headers=headers), token, headers)
        mock_request.called
