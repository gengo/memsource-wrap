import requests
import unittest
from unittest.mock import patch

from memsource import models
from memsource.api_rest.client import Client


class TestClient(unittest.TestCase):
    @patch.object(requests.Session, "request")
    def test_create(self, mock_request: unittest.mock):
        ms_response = unittest.mock.MagicMock(status_code=200)
        ms_response.json.return_value = {
            "id": "mock-id"
        }
        mock_request.return_value = ms_response
        response = Client().create("mock-test")
        self.assertEqual(response, "mock-id")

    @patch.object(requests.Session, "request")
    def test_get(self, mock_request: unittest.mock):
        ms_response = unittest.mock.MagicMock(status_code=200)
        ms_response.json.return_value = {
            "name": "1",
            "netRateScheme": None,
            "priceList": None,
            "displayNoteInProject": False,
            "note": None,
            "id": "1",
            "externalId": None,
            "createdBy": {
                "email": "mock-tm@gengo.com",
                "userName": "mock-tm",
                "uid": "1234",
                "lastName": "mock-last-name",
                "id": "1",
                "firstName": "mock-first-name",
                "role": "ADMIN"
            },
        }
        mock_request.return_value = ms_response

        response = Client().get(1)
        expected = {
            "id": "1",
            "note": None,
            "priceList": None,
            "displayNoteInProject": False,
            "name": "1",
            "createdBy": {
                "id": "1",
                "email": "mock-tm@gengo.com",
                "uid": "1234",
                "firstName": "mock-first-name",
                "lastName": "mock-last-name",
                "userName": "mock-tm", "role": "ADMIN"
            },
            "netRateScheme": None,
            "externalId": None
        }
        self.assertEqual(response, expected)
        self.assertIsInstance(response, models.Client)


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
                "name": "1",
                "netRateScheme": None,
                "priceList": None,
                "displayNoteInProject": False,
                "note": None,
                "id": "1",
                "externalId": None,
                "createdBy": {
                    "email": "mock-tm@gengo.com",
                    "userName": "mock-tm",
                    "uid": "1234",
                    "lastName": "mock-last-name",
                    "id": "1",
                    "firstName": "mock-first-name",
                    "role": "ADMIN"
                }
            }]
        }
        mock_request.return_value = ms_response

        response = Client(token="mock-token").list()
        expected = [{
            "id": "1",
            "note": None,
            "priceList": None,
            "displayNoteInProject": False,
            "name": "1",
            "createdBy": {
                "id": "1",
                "email": "mock-tm@gengo.com",
                "uid": "1234",
                "firstName": "mock-first-name",
                "lastName": "mock-last-name",
                "userName": "mock-tm", "role": "ADMIN"
            },
            "netRateScheme": None,
            "externalId": None
        }]
        self.assertListEqual(response, expected)
        self.assertIsInstance(response[0], models.Client)

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

        response = Client(token="mock-token").list()
        self.assertListEqual(response, [])
