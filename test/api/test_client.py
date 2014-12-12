import unittest
from unittest.mock import patch, PropertyMock
from memsource import api, exceptions
import requests


class TestApiClient(unittest.TestCase):
    def setUp(self):
        self.url_base = 'https://cloud1.memsource.com/web/api/v2/client'
        self.client = api.Client(None)

    @patch.object(requests, 'get')
    def test_create(self, mock_get):
        test = lambda: mock_get.assert_called_with(
            '{}/create'.format(self.url_base),
            params={
                'token': self.client.token,
                'name': client
            },
            timeout=5
        )

        type(mock_get()).status_code = PropertyMock(return_value=200)

        client = 'test client'
        self.client.token = 'token'
        self.client.create(client)
        test()

        client += '2'
        self.client.token += '2'
        self.client.create(client)
        test()

    @patch.object(requests, 'get')
    def test_get(self, mock_get):
        test_called = lambda: mock_get.assert_called_with(
            '{}/get'.format(self.url_base),
            params={
                'token': self.client.token,
                'client': client
            },
            timeout=5
        )

        type(mock_get()).status_code = PropertyMock(return_value=200)

        client_id = 1
        client_name = 'test name'
        mock_get().json.return_value = {
            'id': client_id,
            'name': client_name,
        }
        client = 'test client'
        self.client.token = 'token'
        r = self.client.get(client)
        test_called()
        self.assertEqual(r.id, client_id)
        self.assertEqual(r.name, client_name)

        mock_get().json.return_value = {
            'id': client_id,
            'name': client_name,
        }
        client += '2'
        self.client.token += '2'
        self.client.get(client)
        test_called()
        self.assertEqual(r.id, client_id)
        self.assertEqual(r.name, client_name)

    @patch.object(requests, 'get')
    def test_list(self, mock_get):
        test = lambda: mock_get.assert_called_with(
            '{}/list'.format(self.url_base),
            params={
                'token': self.client.token,
                'page': 0
            },
            timeout=5
        )

        type(mock_get()).status_code = PropertyMock(return_value=200)

        self.client.token = 'token'
        self.client.list()
        test()

        self.client.token += '2'
        self.client.list()
        test()

    @patch.object(requests, 'get')
    def test_error_response(self, mock_get):
        type(mock_get()).status_code = PropertyMock(return_value=400)

        error_code = 'test error code'
        error_description = 'test error description'

        mock_get().json.return_value = {
            'errorCode': error_code,
            'errorDescription': error_description,
        }

        self.assertRaises(
            exceptions.MemsourceApiException, self.client.get, (None, ))
