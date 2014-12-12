import unittest
from unittest.mock import patch, PropertyMock
from memsource import api
import requests


class TestApiDomain(unittest.TestCase):
    def setUp(self):
        self.url_base = 'https://cloud1.memsource.com/web/api/v2/domain'
        self.domain = api.Domain(None)

    @patch.object(requests, 'get')
    def test_create(self, mock_get):
        test = lambda: mock_get.assert_called_with(
            '{}/create'.format(self.url_base),
            params={
                'token': self.domain.token,
                'name': domain
            })

        type(mock_get()).status_code = PropertyMock(return_value=200)

        domain = 'test domain'
        self.domain.token = 'token'
        self.domain.create(domain)
        test()

        domain += '2'
        self.domain.token += '2'
        self.domain.create(domain)
        test()

    @patch.object(requests, 'get')
    def test_get(self, mock_get):
        test = lambda: mock_get.assert_called_with(
            '{}/get'.format(self.url_base),
            params={
                'token': self.domain.token,
                'domain': domain
            })

        type(mock_get()).status_code = PropertyMock(return_value=200)

        domain = 'test domain'
        self.domain.token = 'token'
        self.domain.get(domain)
        test()

        domain += '2'
        self.domain.token += '2'
        self.domain.get(domain)
        test()

    @patch.object(requests, 'get')
    def test_list(self, mock_get):
        test = lambda: mock_get.assert_called_with(
            '{}/list'.format(self.url_base),
            params={
                'token': self.domain.token,
                'page': 0
            })

        type(mock_get()).status_code = PropertyMock(return_value=200)

        self.domain.token = 'token'
        self.domain.list()
        test()

        self.domain.token += '2'
        self.domain.list()
        test()
