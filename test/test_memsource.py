import unittest
from unittest.mock import patch
from memsource import Memsource
import requests


class TestMemsource(unittest.TestCase):
    def setUp(self):
        self.url_base = 'https://cloud1.memsource.com/web/api/v3/auth/login'

    @patch.object(requests, 'get')
    def test_init(self, mock_get):
        token = 'test_token'
        mock_get().json.return_value = {'token': token}

        username = 'test_username'
        password = 'test_password'
        m = Memsource(username, password)

        mock_get.assert_called_with(
            self.url_base,
            params={
                'userName': username,
                'password': password,
            })

        for api in ('client', 'domain', 'project', ):
            self.assertEqual(getattr(m, api).token, token)
