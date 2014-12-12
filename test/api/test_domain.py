import unittest
from unittest.mock import patch, PropertyMock
from memsource import api
import requests


class TestApiDomain(unittest.TestCase):
    def setUp(self):
        self.url_base = 'https://cloud1.memsource.com/web/api/v2/domain'
        self.domain = api.Domain(None)

    @patch.object(requests, 'request')
    def test_create(self, mock_request):
        test = lambda: mock_request.assert_called_with(
            'post',
            '{}/create'.format(self.url_base),
            params={
                'token': self.domain.token,
                'name': domain
            },
            timeout=5
        )

        type(mock_request()).status_code = PropertyMock(return_value=200)

        domain = 'test domain'
        self.domain.token = 'token'
        self.domain.create(domain)
        test()

        domain += '2'
        self.domain.token += '2'
        self.domain.create(domain)
        test()

    @patch.object(requests, 'request')
    def test_get(self, mock_request):
        test = lambda: mock_request.assert_called_with(
            'post',
            '{}/get'.format(self.url_base),
            params={
                'token': self.domain.token,
                'domain': domain
            },
            timeout=5
        )

        type(mock_request()).status_code = PropertyMock(return_value=200)

        domain = 'test domain'
        self.domain.token = 'token'
        self.domain.get(domain)
        test()

        domain += '2'
        self.domain.token += '2'
        self.domain.get(domain)
        test()

    @patch.object(requests, 'request')
    def test_list(self, mock_request):
        test = lambda: mock_request.assert_called_with(
            'post',
            '{}/list'.format(self.url_base),
            params={
                'token': self.domain.token,
                'page': 0
            },
            timeout=5
        )

        type(mock_request()).status_code = PropertyMock(return_value=200)

        self.domain.token = 'token'
        self.domain.list()
        test()

        self.domain.token += '2'
        self.domain.list()
        test()
