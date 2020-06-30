import requests
import unittest
from unittest.mock import patch, PropertyMock

from memsource import constants, models
from memsource.api_rest.analysis import Analysis


class TestAnalysis(unittest.TestCase):
    @patch.object(requests.Session, "request")
    def test_get(self, mock_request: unittest.mock):
        mock_request.return_value = unittest.mock.MagicMock(status_code=200)

        Analysis(token="mock-token").get(1)

        mock_request.assert_called_with(
            constants.HttpMethod.get.value,
            "https://cloud.memsource.com/web/api2/v3/analyses/1",
            params={"token": "mock-token"},
            timeout=60,
        )

    @patch.object(requests.Session, "request")
    def test_create(self, mock_request: unittest.mock.Mock):
        type(mock_request()).status_code = PropertyMock(return_value=200)
        mock_request().json.return_value = {
            "asyncRequests": [
                {
                    "asyncRequest": {
                        "createdBy": {
                            "lastName": "test",
                            "id": 1,
                            "firstName": "admin",
                            "role": "ADMIN",
                            "email": "test@test.com",
                            "userName": "admin",
                            "active": True
                        },
                        "action": "PRE_ANALYSE",
                        "id": "1",
                        "dateCreated": "2014-11-03T16:03:11Z",
                        "asyncResponse": None
                    },
                    "analyse": {"id": "string"},
                }
            ]
        }

        jobs = [1]
        self.assertIsInstance(Analysis(token="mock-token").create(jobs), models.AsynchronousRequest)

        mock_request.assert_called_with(
            constants.HttpMethod.post.value,
            "https://cloud.memsource.com/web/api2/v2/analyses",
            params={"token": "mock-token"},
            json={"jobs": [{"uid": 1}]},
            timeout=60,
        )

    @patch.object(requests.Session, "request")
    def test_delete(self, mock_request: unittest.mock.Mock):
        type(mock_request()).status_code = PropertyMock(return_value=200)
        mock_request().json.return_value = None

        analysis_id = 1234

        self.assertIsNone(Analysis(token="mock-token").delete(analysis_id))

        mock_request.assert_called_with(
            constants.HttpMethod.delete.value,
            "https://cloud.memsource.com/web/api2/v1/analyses/1234",
            params={"token": "mock-token", "purge": False},
            timeout=60,
        )

    @patch.object(requests.Session, "request")
    def test_get_by_project(self, mock_request: unittest.mock.Mock):
        type(mock_request()).status_code = PropertyMock(return_value=200)
        mock_request().json.return_value = {
            "totalElements": 0,
            "totalPages": 0,
            "pageSize": 0,
            "pageNumber": 0,
            "numberOfElements": 0,
            "content": [
                {
                    "id": "1",
                    "type": "PreAnalyse",
                    "name": "analysis",
                    "provider": {},
                    "createdBy": {},
                    "dateCreated": "2014-11-03T16:03:11Z",
                    "netRateScheme": {},
                    "analyseLanguageParts": [],
                },
                {
                    "id": "2",
                    "type": "PreAnalyse",
                    "name": "analysis-2",
                    "provider": {},
                    "createdBy": {},
                    "dateCreated": "2014-11-03T16:03:11Z",
                    "netRateScheme": {},
                    "analyseLanguageParts": [],
                }
            ]
        }

        project_id = 1234

        analyses = Analysis(token="mock-token").get_by_project(project_id)

        self.assertIsInstance(analyses, list)
        for analysis in analyses:
            self.assertIsInstance(analysis, models.Analysis)

        mock_request.assert_called_with(
            constants.HttpMethod.get.value,
            "https://cloud.memsource.com/web/api2/v2/projects/1234/analyses",
            params={"token": "mock-token"},
            timeout=60,
        )

    @patch("builtins.open")
    @patch.object(requests.Session, "request")
    def test_download(self, mock_request: unittest.mock.Mock, mock_open: unittest.mock.Mock):
        type(mock_request()).status_code = PropertyMock(return_value=200)

        analysis = "this is analysis"

        mock_request().iter_content.return_value = [
            bytes(content, 'utf-8') for content in analysis]
        analysis_id = 1234

        Analysis(token="mock-token").download(analysis_id, "test.csv")
        mock_request.assert_called_with(
            constants.HttpMethod.get.value,
            "https://cloud.memsource.com/web/api2/v1/analyses/1234/download",
            params={"token": "mock-token", "format": constants.AnalysisFormat.CSV.value},
            timeout=300,
        )
