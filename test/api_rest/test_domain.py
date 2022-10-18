import requests
import unittest
from unittest.mock import patch

from memsource import constants, models
from memsource.api_rest.domain import Domain


class TestDomain(unittest.TestCase):
    @patch.object(requests.Session, "request")
    def test_create(self, mock_request: unittest.mock):
        ms_response = unittest.mock.MagicMock(status_code=200)
        ms_response.json.return_value = {
            "id": "mock-id",
            "name": "mock-test",
        }
        mock_request.return_value = ms_response
        response = Domain(token="mock-token").create("mock-test")
        self.assertEqual(response, {
            "id": "mock-id",
            "name": "mock-test",
        })

        mock_request.assert_called_with(
            constants.HttpMethod.post.value,
            "https://cloud.memsource.com/web/api2/v1/domains",
            json={"name": "mock-test"},
            headers={"Authorization": "ApiToken mock-token"},
            timeout=60
        )

    @patch.object(requests.Session, "request")
    def test_get(self, mock_request: unittest.mock):
        ms_response = unittest.mock.MagicMock(status_code=200)
        ms_response.json.return_value = {
            "id": "1",
            "name": "1",
        }
        mock_request.return_value = ms_response

        response = Domain(token="mock-token").get(1)
        expected = {
            "name": "1",
            "id": "1",
        }
        self.assertEqual(response, expected)
        self.assertIsInstance(response, models.Domain)
        mock_request.assert_called_with(
            constants.HttpMethod.get.value,
            "https://cloud.memsource.com/web/api2/v1/domains/1",
            headers={"Authorization": "ApiToken mock-token"},
            timeout=60
        )

    @patch.object(requests.Session, "request")
    def test_list(self, mock_request: unittest.mock):
        ms_response = unittest.mock.MagicMock(status_code=200)
        ms_response.json.return_value = {
            "totalPages": 1,
            "numberOfElements": 1,
            "totalElements": 1,
            "pageSize": 50,
            "pageNumber": 0,
            "content": [{
                "id": "1",
                "name": "1",
            }]
        }
        mock_request.return_value = ms_response

        response = Domain(token="mock-token").list()
        expected = [
            models.Domain(id="1", name="1")
        ]
        for domain, expected_domain in zip(response, expected):
            self.assertEqual(domain, expected_domain)

        mock_request.assert_called_with(
            constants.HttpMethod.get.value,
            "https://cloud.memsource.com/web/api2/v1/domains",
            headers={"Authorization": "ApiToken mock-token"},
            params={"page": 0},
            timeout=60
        )

    @patch.object(requests.Session, "request")
    def test_list_none(self, mock_request: unittest.mock):
        ms_response = unittest.mock.MagicMock(status_code=200)
        ms_response.json.return_value = {
            "totalPages": 0,
            "numberOfElements": 0,
            "totalElements": 0,
            "pageSize": 50,
            "pageNumber": 0,
            "content": []
        }
        mock_request.return_value = ms_response

        response = Domain(token="mock-token").list()
        self.assertListEqual(response, [])
