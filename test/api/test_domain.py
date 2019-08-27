import unittest
from unittest.mock import patch, PropertyMock
from memsource import api, constants
import requests


class TestApiDomain(unittest.TestCase):
    def setUp(self):
        self.url_base = 'https://cloud.memsource.com/web/api/v2/domain'
        self.domain = api.Domain()

    @patch.object(requests.Session, 'request')
    def test_create(self, mock_request):
        def test():
            mock_request.assert_called_with(
                constants.HttpMethod.post.value,
                '{}/create'.format(self.url_base),
                data={
                    'token': self.domain.token,
                    'name': domain
                },
                timeout=constants.Base.timeout.value
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

    @patch.object(requests.Session, 'request')
    def test_get(self, mock_request):
        def test():
            mock_request.assert_called_with(
                constants.HttpMethod.post.value,
                '{}/get'.format(self.url_base),
                data={
                    'token': self.domain.token,
                    'domain': domain
                },
                timeout=constants.Base.timeout.value
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

    @patch.object(requests.Session, 'request')
    def test_list(self, mock_request):
        def test():
            mock_request.assert_called_with(
                constants.HttpMethod.post.value,
                '{}/list'.format(self.url_base),
                data={
                    'token': self.domain.token,
                    'page': 0
                },
                timeout=constants.Base.timeout.value
            )

        type(mock_request()).status_code = PropertyMock(return_value=200)

        self.domain.token = 'token'
        self.domain.list()
        test()

        self.domain.token += '2'
        self.domain.list()
        test()
