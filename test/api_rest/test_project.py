import requests
import unittest
from unittest.mock import patch

from memsource import constants, models
from memsource.api_rest.project import Project


class TestProject(unittest.TestCase):
    @patch.object(requests.Session, "request")
    def test_create(self, mock_request: unittest.mock):
        ms_response = unittest.mock.MagicMock(status_code=200)
        ms_response.json.return_value = {
            "uid": "1234",
            "internalId": 0,
            "id": "1234",
            "name": "mock-project",
            "dateCreated": "2020-06-22T01:44:04Z",
            "domain": {"name": "mock-domain", "id": "1"},
            "sourceLang": "en",
            "targetLangs": ["ja", "de"],
        }
        mock_request.return_value = ms_response

        response = Project(token="mock-token").create(
            name="mock-project",
            source_lang="en",
            target_langs=["ja", "de"],
        )
        self.assertEqual(response, "1234")

        mock_request.assert_called_with(
            constants.HttpMethod.post.value,
            "https://cloud.memsource.com/web/api2/v1/projects",
            json={
                "sourceLang": "en",
                "targetLangs": ["ja", "de"],
                "client": None,
                "name": "mock-project",
                "domain": None
            },
            params={"token": "mock-token"},
            timeout=60,
        )

    @patch.object(requests.Session, "request")
    def test_list(self, mock_request: unittest.mock):
        ms_response = unittest.mock.MagicMock(status_code=200)
        ms_response.json.return_value = {
            "totalPages": 1,
            "numberOfElements": 2,
            "totalElements": 2,
            "pageSize": 50,
            "pageNumber": 0,
            "content": [
                {
                    "uid": "1",
                    "internalId": 0,
                    "id": "1",
                    "name": "mock-project-1",
                    "dateCreated": "2020-06-22T01:44:04Z",
                    "domain": {},
                    "subDomain": {},
                    "owner": {},
                    "sourceLang": "en",
                    "targetLangs": ["ja"],
                    "references": [],
                    "mtSettingsPerLanguageList": [],
                    "userRole": "string",
                },
                {
                    "uid": "2",
                    "internalId": 0,
                    "id": "2",
                    "name": "mock-project-2",
                    "dateCreated": "2020-06-22T01:44:04Z",
                    "domain": {},
                    "subDomain": {},
                    "owner": {},
                    "sourceLang": "en",
                    "targetLangs": ["ja"],
                    "references": [],
                    "mtSettingsPerLanguageList": [],
                    "userRole": "string",
                }
            ]
        }
        mock_request.return_value = ms_response

        expected = [
            models.Project(
                uid="1",
                internalId=0,
                id="1",
                name="mock-project-1",
                dateCreated="2020-06-22T01:44:04Z",
                domain={},
                subDomain={},
                owner={},
                sourceLang="en",
                targetLangs=["ja"],
                references=[],
                mtSettingsPerLanguageList=[],
                userRole="string",
            ),
            models.Project(
                uid="2",
                internalId=0,
                id="2",
                name="mock-project-2",
                dateCreated="2020-06-22T01:44:04Z",
                domain={},
                subDomain={},
                owner={},
                sourceLang="en",
                targetLangs=["ja"],
                references=[],
                mtSettingsPerLanguageList=[],
                userRole="string",
            )
        ]

        response = Project(token="mock-token").list(statuses=["NEW", "ASSIGNED"])
        for project, expected_project in zip(response, expected):
            self.assertEqual(project, expected_project)

        mock_request.assert_called_with(
            constants.HttpMethod.get.value,
            "https://cloud.memsource.com/web/api2/v1/projects",
            params={"token": "mock-token", "statuses": ["NEW", "ASSIGNED"]},
            timeout=60,
        )

    @patch.object(requests.Session, "request")
    def test_get_trans_memories(self, mock_request: unittest.mock):
        ms_response = unittest.mock.MagicMock(status_code=200)
        ms_response.json.return_value = {
            "transMemories": [
                {
                    "targetLocale": "ja",
                    "workflowStep": {},
                    "readMode": True,
                    "writeMode": True,
                    "transMemory": {
                        "id": "1",
                        "internalId": 0,
                        "name": "mock-tm-1",
                        "sourceLang": "en",
                        "targetLangs": ["ja"],
                        "client": {},
                        "businessUnit": {},
                        "domain": {},
                        "subDomain": {},
                        "note": "string",
                        "dateCreated": "2020-06-22T03:16:36Z",
                        "createdBy": {}
                    },
                    "penalty": 0,
                    "applyPenaltyTo101Only": True,
                },
                {
                    "targetLocale": "de",
                    "workflowStep": {},
                    "readMode": True,
                    "writeMode": True,
                    "transMemory": {
                        "id": "2",
                        "internalId": 0,
                        "name": "mock-tm-2",
                        "sourceLang": "en",
                        "targetLangs": ["de"],
                        "client": {},
                        "businessUnit": {},
                        "domain": {},
                        "subDomain": {},
                        "note": "string",
                        "dateCreated": "2020-06-22T03:16:36Z",
                        "createdBy": {}
                    },
                    "penalty": 0,
                    "applyPenaltyTo101Only": True,
                },
            ]
        }
        mock_request.return_value = ms_response

        expected = [
            models.TranslationMemory(
                targetLocale="ja",
                workflowStep={},
                readMode=True,
                writeMode=True,
                transMemory={
                    "id": "1",
                    "internalId": 0,
                    "name": "mock-tm-1",
                    "sourceLang": "en",
                    "targetLangs": ["ja"],
                    "client": {},
                    "businessUnit": {},
                    "domain": {},
                    "subDomain": {},
                    "note": "string",
                    "dateCreated": "2020-06-22T03:16:36Z",
                    "createdBy": {}
                },
                penalty=0,
                applyPenaltyTo101Only=True,
            ),
            models.TranslationMemory(
                targetLocale="de",
                workflowStep={},
                readMode=True,
                writeMode=True,
                transMemory={
                    "id": "2",
                    "internalId": 0,
                    "name": "mock-tm-2",
                    "sourceLang": "en",
                    "targetLangs": ["de"],
                    "client": {},
                    "businessUnit": {},
                    "domain": {},
                    "subDomain": {},
                    "note": "string",
                    "dateCreated": "2020-06-22T03:16:36Z",
                    "createdBy": {}
                },
                penalty=0,
                applyPenaltyTo101Only=True,
            ),
        ]

        response = Project(token="mock-token").get_trans_memories(1)
        for trans_memories, expected_trans_memories in zip(response, expected):
            self.assertEqual(trans_memories, expected_trans_memories)

        mock_request.assert_called_with(
            constants.HttpMethod.get.value,
            "https://cloud.memsource.com/web/api2/v1/projects/1/transMemories",
            params={"token": "mock-token"},
            timeout=60,
        )

    @patch.object(requests.Session, "request")
    def test_set_trans_memories(self, mock_request: unittest.mock):
        mock_request.return_value = unittest.mock.MagicMock(status_code=200)

        Project(token="mock-token").set_trans_memories(
            project_id=1,
            translation_memories=[{
                "transMemory": {"id": "1180298"},
                "readMode": True,
                "writeMode": True,
            }],
            target_lang="ja",
        )

        mock_request.assert_called_with(
            constants.HttpMethod.put.value,
            "https://cloud.memsource.com/web/api2/v2/projects/1/transMemories",
            json={
                "targetLang": "ja",
                "transMemories": [
                    {"readMode": True, "transMemory": {"id": "1180298"}, "writeMode": True}
                ],
            },
            params={"token": "mock-token"},
            timeout=60,
        )

    @patch.object(requests.Session, "request")
    def test_set_status(self, mock_request: unittest.mock):
        mock_request.return_value = unittest.mock.MagicMock(status_code=204)

        Project(token="mock-token").set_status(
            project_id=1,
            status=constants.ProjectStatus.NEW,
        )

        mock_request.assert_called_with(
            constants.HttpMethod.post.value,
            "https://cloud.memsource.com/web/api2/v1/projects/1/setStatus",
            json={"status": "NEW"},
            params={"token": "mock-token"},
            timeout=60,
        )

    @patch.object(requests.Session, "request")
    def test_get_term_bases(self, mock_request: unittest.mock):
        ms_response = unittest.mock.MagicMock(status_code=200)
        ms_response.json.return_value = {
            "termBases": [
                {
                    "targetLocale": "ja",
                    "readMode": True,
                    "writeMode": True,
                    "termBase": {
                        "id": "1",
                        "internalId": 0,
                        "name": "mock-term-base-1",
                        "langs": ["ja"],
                        "dateCreated": "2020-06-22T03:16:36Z",
                        "note": "string"
                    },
                    "qualityAssurance": True
                },
                {
                    "targetLocale": "de",
                    "readMode": True,
                    "writeMode": True,
                    "termBase": {
                        "id": "2",
                        "internalId": 0,
                        "name": "mock-term-base-2",
                        "langs": ["de"],
                        "dateCreated": "2020-06-22T03:16:36Z",
                        "note": "string"
                    },
                    "qualityAssurance": True
                }
            ]
        }
        mock_request.return_value = ms_response

        expected = [
            models.TermBase(
                targetLocale="ja",
                readMode=True,
                writeMode=True,
                termBase={
                    "id": "1",
                    "internalId": 0,
                    "name": "mock-term-base-1",
                    "langs": ["ja"],
                    "dateCreated": "2020-06-22T03:16:36Z",
                    "note": "string"
                },
                qualityAssurance=True,
            ),
            models.TermBase(
                targetLocale="de",
                readMode=True,
                writeMode=True,
                termBase={
                    "id": "2",
                    "internalId": 0,
                    "name": "mock-term-base-2",
                    "langs": ["de"],
                    "dateCreated": "2020-06-22T03:16:36Z",
                    "note": "string"
                },
                qualityAssurance=True,
            )
        ]

        term_bases = Project(token="mock-token").get_term_bases(1)
        for term_base, expected_term_base in zip(term_bases, expected):
            self.assertEqual(term_base, expected_term_base)

        mock_request.assert_called_with(
            constants.HttpMethod.get.value,
            "https://cloud.memsource.com/web/api2/v1/projects/1/termBases",
            params={"token": "mock-token"},
            timeout=60,
        )
