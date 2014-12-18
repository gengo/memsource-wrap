import unittest
from unittest.mock import patch, PropertyMock
from memsource import api, exceptions, constants
import requests


class TestApiClient(unittest.TestCase):
    def setUp(self):
        self.url_base = 'https://cloud1.memsource.com/web/api/v2/client'
        self.client = api.Client(None)

    @patch.object(requests, 'request')
    def test_create(self, mock_request):
        test = lambda: mock_request.assert_called_with(
            'post',
            '{}/create'.format(self.url_base),
            params={
                'token': self.client.token,
                'name': client
            },
            files={},
            timeout=constants.Base.timeout.value
        )

        type(mock_request()).status_code = PropertyMock(return_value=200)

        client = 'test client'
        self.client.token = 'token'
        self.client.create(client)
        test()

        client += '2'
        self.client.token += '2'
        self.client.create(client)
        test()

    @patch.object(requests, 'request')
    def test_get(self, mock_request):
        test_called = lambda: mock_request.assert_called_with(
            'post',
            '{}/get'.format(self.url_base),
            params={
                'token': self.client.token,
                'client': client
            },
            files={},
            timeout=constants.Base.timeout.value
        )

        type(mock_request()).status_code = PropertyMock(return_value=200)

        client_id = 1
        client_name = 'test name'
        mock_request().json.return_value = {
            'id': client_id,
            'name': client_name,
        }
        client = 'test client'
        self.client.token = 'token'
        r = self.client.get(client)
        test_called()
        self.assertEqual(r.id, client_id)
        self.assertEqual(r.name, client_name)

        mock_request().json.return_value = {
            'id': client_id,
            'name': client_name,
        }
        client += '2'
        self.client.token += '2'
        self.client.get(client)
        test_called()
        self.assertEqual(r.id, client_id)
        self.assertEqual(r.name, client_name)

    @patch.object(requests, 'request')
    def test_list(self, mock_request):
        test = lambda: mock_request.assert_called_with(
            'post',
            '{}/list'.format(self.url_base),
            params={
                'token': self.client.token,
                'page': 0
            },
            files={},
            timeout=constants.Base.timeout.value
        )

        type(mock_request()).status_code = PropertyMock(return_value=200)

        self.client.token = 'token'
        self.client.list()
        test()

        self.client.token += '2'
        self.client.list()
        test()

    @patch.object(requests, 'request')
    def test_error_response(self, mock_request):
        type(mock_request()).status_code = PropertyMock(return_value=400)

        error_code = 'test error code'
        error_description = 'test error description'

        mock_request().json.return_value = {
            'errorCode': error_code,
            'errorDescription': error_description,
        }

        self.assertRaises(
            exceptions.MemsourceApiException, self.client.get, (None, ))
