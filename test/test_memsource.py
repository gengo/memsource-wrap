import unittest
import requests
from memsource import api, constants
from memsource.memsource import Memsource
from unittest.mock import patch, PropertyMock


class TestMemsource(unittest.TestCase):
    def setUp(self):
        self.url_base = 'https://cloud.memsource.com/web/api/v3/auth/login'

    def check_token_and_headers(self, m, token=None, headers=None):
        class_names = [
            'auth', 'client', 'domain', 'project', 'job', 'translation_memory',
            'asynchronous', 'language', 'analysis', 'term_base'
        ]
        for name in class_names:
            self.assertEqual(getattr(m, name).token, token)
            self.assertEqual(getattr(m, name).headers, headers)

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

    @patch.object(api.Auth, 'login')
    def test_init_with_header_with_user_name_password(self, mock_login):
        token = None
        username = 'test_username'
        password = 'test_password'
        headers = {
            'Authorization': 'Bearer test_token'
        }

        self.check_token_and_headers(
            Memsource(
                user_name=username,
                password=password,
                headers=headers,
            ),
            token,
            headers
        )

        # When header is given, should not call login method.
        self.assertFalse(mock_login.called)
