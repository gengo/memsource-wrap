import unittest
from unittest.mock import patch
from memsource import Memsource
import requests


class TestMemsource(unittest.TestCase):
    def setUp(self):
        self.url_base = 'https://cloud1.memsource.com/web/api/v3/auth/login'

    @patch.object(requests, 'post')
    def test_init_with_user_name_and_password(self, mock_request):
        token = 'test_token'
        mock_request().json.return_value = {
            'token': token,
            'user': {},
        }

        username = 'test_username'
        password = 'test_password'
        m = Memsource(user_name=username, password=password)

        mock_request.assert_called_with(
            self.url_base,
            params={
                'userName': username,
                'password': password,
            })

        for api in ('client', 'domain', 'project', ):
            self.assertEqual(getattr(m, api).token, token)

    @patch.object(requests, 'post')
    def test_init_with_token(self, mock_request):
        token = 'test_token'
        m = Memsource(token=token)

        for api in ('client', 'domain', 'project', ):
            self.assertEqual(getattr(m, api).token, token)

        # When token is given as parameter, never send http request.
        self.assertFalse(mock_request.called)

    @patch.object(requests, 'post')
    def test_init_with_user_name_and_password_and_token(self, mock_request):
        token = 'test_token'
        m = Memsource(user_name='test user name', password='test password', token=token)

        for api in ('client', 'domain', 'project', ):
            self.assertEqual(getattr(m, api).token, token)

        # When token is given as parameter, never send http request.
        self.assertFalse(mock_request.called)
