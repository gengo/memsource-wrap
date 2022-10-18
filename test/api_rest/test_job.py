import uuid

import requests
import unittest
from unittest.mock import patch, PropertyMock

from memsource import models, exceptions, constants
from memsource.api_rest.job import Job


class TestApiJob(unittest.TestCase):
    @patch("builtins.open")
    @patch.object(requests.Session, "request")
    def test_create(
        self,
        mock_request: unittest.mock.Mock,
        mock_open: unittest.mock.Mock,
    ):
        type(mock_request()).status_code = PropertyMock(return_value=200)
        mock_request().json.return_value = {
            "unsupportedFiles": [],
            "jobs": [
                {
                    "workflowLevel": 1,
                    "filename": "requirements.txt",
                    "targetLang": "ja",
                    "notificationIntervalInMinutes": -1,
                    "workflowStep": None,
                    "uid": "0khOFZ70PYDzIAz0CvU0Fn",
                    "updateSourceDate": None,
                    "providers": [],
                    "status": "NEW",
                    "continuous": False,
                    "imported": False,
                    "dateDue": None,
                    "jobAssignedEmailTemplate": None,
                    "dateCreated": "2020-06-24T03:40:53+0000"
                },
            ],
            "asyncRequest": {
                "id": "381708066",
                "action": "IMPORT_JOB",
                "dateCreated": "2020-06-24T03:40:53+0000"
            }
        }

        mock_open.return_value.__enter__.return_value.name = "this_is_a_test.txt"
        returned_value = Job(token="mock-token").create(
            1234,
            "test/this_is_a_test.txt",
            ["ja"]
        )

        # Don"t use assert_called_with because files has file object. It is difficult to test.
        self.assertTrue(mock_request.called)
        (called_args, called_kwargs) = mock_request.call_args

        # hard to test
        del called_kwargs["files"]

        self.assertEqual(
            (
                constants.HttpMethod.post.value,
                "https://cloud.memsource.com/web/api2/v1/projects/1234/jobs",
            ),
            called_args
        )

        self.assertEqual({
            "headers": {
                "Content-Disposition": "inline; filename=\"this_is_a_test.txt\"",
                "Content-Type": "application/octet-stream",
                "Memsource": "{\"targetLangs\": [\"ja\"]}",
                "Authorization": "ApiToken mock-token",
            },
            "json": {"targetLangs": ["ja"]},
            "timeout": 60,
        }, called_kwargs)

        self.assertEqual(1, len(returned_value))
        for job_part in returned_value:
            self.assertIsInstance(job_part, models.JobPart)

    @patch("shutil.copy")
    @patch("builtins.open")
    @patch.object(requests.Session, "request")
    def test_create_with_unsupported_file(
        self,
        mock_request: unittest.mock.Mock,
        mock_open: unittest.mock.Mock,
        mock_copy: unittest.mock.Mock,
    ):
        type(mock_request()).status_code = PropertyMock(return_value=200)
        mock_request().json.return_value = {
            "unsupportedFiles": ["test_runner.sh"],
            "jobs": [],
            "asyncRequest": {
                "dateCreated": "2020-06-24T05:12:27+0000",
                "id": "381726629",
                "action": "IMPORT_JOB"
            }
        }

        self.assertRaises(
            exceptions.MemsourceUnsupportedFileException,
            lambda: Job(token="mock-token").create(1234, "failed.txt", ["ja"]),
        )
        self.assertTrue(mock_request.called)

    @patch("builtins.open")
    @patch.object(uuid, "uuid1")
    @patch.object(requests.Session, "request")
    def test_create_from_text(
        self,
        mock_request: unittest.mock.Mock,
        mock_uuid1: unittest.mock.Mock,
        mock_open: unittest.mock.Mock,
    ):
        type(mock_request()).status_code = PropertyMock(return_value=200)
        mock_request().json.return_value = {
            "unsupportedFiles": [],
            "jobs": [
                {
                    "workflowLevel": 1,
                    "filename": "requirements.txt",
                    "targetLang": "ja",
                    "notificationIntervalInMinutes": -1,
                    "workflowStep": None,
                    "uid": "0khOFZ70PYDzIAz0CvU0Fn",
                    "updateSourceDate": None,
                    "providers": [],
                    "status": "NEW",
                    "continuous": False,
                    "imported": False,
                    "dateDue": None,
                    "jobAssignedEmailTemplate": None,
                    "dateCreated": "2020-06-24T03:40:53+0000"
                },
            ],
            "asyncRequest": {
                "id": "381708066",
                "action": "IMPORT_JOB",
                "dateCreated": "2020-06-24T03:40:53+0000"
            }
        }

        mock_uuid1().hex = "test-file-uuid1"

        mock_open.return_value.__enter__.return_value.name = "test-file-uuid1.txt"
        returned_value = Job(token="mock-token").create_from_text(
            1234,
            "this is a test",
            ["ja"]
        )

        # Don"t use assert_called_with because files has file object. It is difficult to test.
        self.assertTrue(mock_request.called)
        (called_args, called_kwargs) = mock_request.call_args

        # hard to test
        del called_kwargs["files"]

        self.assertEqual(
            (
                constants.HttpMethod.post.value,
                "https://cloud.memsource.com/web/api2/v1/projects/1234/jobs",
            ),
            called_args
        )

        self.assertEqual({
            "headers": {
                "Content-Disposition": "inline; filename=\"test-file-uuid1.txt\"",
                "Content-Type": "application/octet-stream",
                "Memsource": "{\"targetLangs\": [\"ja\"]}",
                "Authorization": "ApiToken mock-token",
            },
            "json": {"targetLangs": ["ja"]},
            "timeout": 60,
        }, called_kwargs)

        self.assertEqual(1, len(returned_value))
        for job_part in returned_value:
            self.assertIsInstance(job_part, models.JobPart)

    @patch.object(requests.Session, "request")
    def test_list_by_project(self, mock_request):
        type(mock_request()).status_code = PropertyMock(return_value=200)

        project_id = 1234

        mock_request().json.return_value = {
            "content": [
                {
                    "imported": True,
                    "targetLang": "ja",
                    "dateCreated": "2020-06-24T03:38:31+0000",
                    "filename": "requirements.txt",
                    "uid": "06CcWsyrLLTTgylLQ9DSb6",
                    "providers": [],
                    "status": "NEW",
                    "continuous": False,
                    "dateDue": None,
                    "workflowStep": None
                },
                {
                    "imported": True,
                    "targetLang": "ja",
                    "dateCreated": "2020-06-24T03:40:53+0000",
                    "filename": "requirements.txt",
                    "uid": "0khOFZ70PYDzIAz0CvU0Fn",
                    "providers": [],
                    "status": "NEW",
                    "continuous": False,
                    "dateDue": None,
                    "workflowStep": None
                }
            ],
            "totalElements": 2,
            "pageSize": 50,
            "totalPages": 1,
            "pageNumber": 0,
            "numberOfElements": 2,
        }

        returned_value = Job(token="mock-token").list_by_project(project_id)

        for job_part in returned_value:
            self.assertIsInstance(job_part, models.JobPart)

        mock_request.assert_called_with(
            constants.HttpMethod.get.value,
            "https://cloud.memsource.com/web/api2/v2/projects/1234/jobs",
            headers={"Authorization": "ApiToken mock-token"},
            params={"page": 0},
            timeout=60,
        )

        self.assertEqual(len(returned_value), 2)

    @patch.object(requests.Session, "request")
    def test_pre_translate_no_callback(self, mock_request):
        type(mock_request()).status_code = PropertyMock(return_value=200)

        job_part_ids = [1, 2]

        mock_request().json.return_value = {
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
                "action": "PRE_TRANSLATE",
                "id": 4567,
                "dateCreated": "2014-11-03T16:03:11Z",
                "asyncResponse": None
            }
        }

        retuned_value = Job(token="mock-token").pre_translate(1234, job_part_ids)

        self.assertIsInstance(retuned_value, models.AsynchronousRequest)

        mock_request.assert_called_with(
            constants.HttpMethod.post.value,
            "https://cloud.memsource.com/web/api2/v1/projects/1234/jobs/preTranslate",
            headers={"Authorization": "ApiToken mock-token"},
            json={
                "jobs": [
                    {"uid": 1},
                    {"uid": 2},
                ],
                "translationMemoryTreshold": 0.7,
                "callbackUrl": None,
            },
            timeout=60,
        )

    @patch.object(requests.Session, "request")
    def test_get_completed_file_text(self, mock_request):
        type(mock_request()).status_code = PropertyMock(return_value=200)

        mock_request().iter_content.return_value = [b"test completed content", b"second"]
        returned_value = Job(token="mock-token").get_completed_file_text(1234, 1)

        self.assertEqual(b"test completed contentsecond", returned_value)

        mock_request.assert_called_with(
            constants.HttpMethod.get.value,
            "https://cloud.memsource.com/web/api2/v1/projects/1234/jobs/1/targetFile",
            headers={"Authorization": "ApiToken mock-token"},
            timeout=60 * 5,
        )

    @patch.object(requests.Session, "request")
    def test_get_segments(self, mock_request):
        type(mock_request()).status_code = PropertyMock(return_value=200)
        mock_request().json.return_value = {
            "segments": [
                {
                    "id": "dz0ksG9dBy0TGIYu1_dc6:0",
                    "source": "Hello",
                    "workflowStep": None,
                    "createdBy": {},
                    "modifiedAt": 1592984050930,
                    "translation": "Ola",
                    "modifiedBy": {},
                    "createdAt": 1592984050693,
                    "workflowLevel": None
                },
                {
                    "id": "dz0ksG9dBy0TGIYu1_dc6:1",
                    "source": " World",
                    "workflowStep": None,
                    "createdBy": {},
                    "modifiedAt": 1592985077488,
                    "translation": "",
                    "modifiedBy": {},
                    "createdAt": 1592985077488,
                    "workflowLevel": None
                }
            ]
        }

        returned_value = Job(token="mock-token").get_segments(
            project_id=1234,
            job_uid="mock-uid",
            begin_index=0,
            end_index=1,
        )

        mock_request.assert_called_with(
            constants.HttpMethod.get.value,
            "https://cloud.memsource.com/web/api2/v1/projects/1234/jobs/mock-uid/segments",
            headers={"Authorization": "ApiToken mock-token"},
            params={
                "beginIndex": 0,
                "endIndex": 1,
            },
            timeout=60,
        )

        for segment in returned_value:
            self.assertIsInstance(segment, models.Segment)

    @patch.object(requests.Session, "request")
    def test_get(self, mock_request):
        type(mock_request()).status_code = PropertyMock(return_value=200)
        mock_request().json.return_value = {
            'status': 'NEW',
            'filename': 'requirements.txt',
            'workflowLevel': 1,
            'project': {},
            'workflowStep': None,
            'originalFileDirectory': '',
            'isParentJobSplit': False,
            'endIndex': 12,
            'dateCreated': '2020-06-24T03:38:31+0000',
            'wordsCount': 22,
            'continuousJobInfo': None,
            'workUnit': None,
            'sourceLang': 'en',
            'beginIndex': 0,
            'continuous': False,
            'updateSourceDate': None,
            'targetLang': 'ja',
            'uid': '06CcWsyrLLTTgylLQ9DSb6',
            'lastWorkflowLevel': 1
        }

        returned_value = Job(token="mock-token").get(1234, "06CcWsyrLLTTgylLQ9DSb6")

        mock_request.assert_called_with(
            constants.HttpMethod.get.value,
            "https://cloud.memsource.com/web/api2/v1/projects/1234/jobs/06CcWsyrLLTTgylLQ9DSb6",
            headers={"Authorization": "ApiToken mock-token"},
            timeout=60,
        )

        self.assertEqual("NEW", returned_value.status)

    @patch.object(requests.Session, "request")
    def test_list(self, mock_request):
        type(mock_request()).status_code = PropertyMock(return_value=200)

        mock_request().json.return_value = {
            "totalPages": 1,
            "pageNumber": 0,
            "totalElements": 2,
            "content": [
                {
                    "filename": "requirements.txt",
                    "continuous": False,
                    "dateDue": None,
                    "uid": "06CcWsyrLLTTgylLQ9DSb6",
                    "status": "NEW",
                    "targetLang": "ja",
                    "workflowStep": None,
                    "imported": True,
                    "providers": [],
                    "dateCreated": "2020-06-24T03:38:31+0000"
                },
                {
                    "filename": "requirements.txt",
                    "continuous": False,
                    "dateDue": None,
                    "uid": "0khOFZ70PYDzIAz0CvU0Fn",
                    "status": "NEW",
                    "targetLang": "ja",
                    "workflowStep": None,
                    "imported": True,
                    "providers": [],
                    "dateCreated": "2020-06-24T03:40:53+0000"
                }
            ],
            "pageSize": 50,
            "numberOfElements": 2,
        }

        returned_value = Job(token="mock-token").list(1234)

        mock_request.assert_called_with(
            constants.HttpMethod.get.value,
            "https://cloud.memsource.com/web/api2/v2/projects/1234/jobs",
            headers={"Authorization": "ApiToken mock-token"},
            timeout=60,
        )

        self.assertEqual("NEW", returned_value[0].status)

    @patch.object(requests.Session, "request")
    def test_delete(self, mock_request):
        type(mock_request()).status_code = PropertyMock(return_value=204)
        mock_request().json.return_value = None

        self.assertIsNone(Job(token="mock-token").delete(1234, [1, 2]))

        mock_request.assert_called_with(
            constants.HttpMethod.delete.value,
            "https://cloud.memsource.com/web/api2/v1/projects/1234/jobs/batch",
            headers={"Authorization": "ApiToken mock-token"},
            params={"purge": False},
            json={
                "jobs": [
                    {"uid": 1},
                    {"uid": 2},
                ],
            },
            timeout=60,
        )

    @patch.object(requests.Session, "request")
    def test_set_status(self, mock_request):
        type(mock_request()).status_code = PropertyMock(return_value=204)
        mock_request().json.return_value = None

        self.assertIsNone(Job(token="mock-token").set_status(
            1234, 1, constants.JobStatusRest.DECLINED))

        mock_request.assert_called_with(
            constants.HttpMethod.post.value,
            "https://cloud.memsource.com/web/api2/v1/projects/1234/jobs/1/setStatus",
            headers={"Authorization": "ApiToken mock-token"},
            json={"requestedStatus": "DECLINED"},
            timeout=60
        )

    @patch.object(requests.Session, "request")
    def test_delete_all_translations(self, mock_request):
        type(mock_request()).status_code = PropertyMock(return_value=204)
        self.assertIsNone(Job(token="mock-token").delete_all_translations(1234, ["mock-job-uid"]))

        mock_request.assert_called_with(
            constants.HttpMethod.delete.value,
            "https://cloud.memsource.com/web/api2/v1/projects/1234/jobs/translations",
            headers={"Authorization": "ApiToken mock-token"},
            json={
                "jobs": [{"uid": "mock-job-uid"}],
            },
            timeout=60,
        )
