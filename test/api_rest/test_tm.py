import unittest
import uuid
from unittest.mock import patch, PropertyMock

import requests

from memsource import constants, models
from memsource.api_rest.tm import TranslationMemory


ANY_ID = 1
ANY_LCS = ["en", "ja"]


class TestApiTranslationMemory(unittest.TestCase):
    @patch.object(requests.Session, "request")
    def test_create(self, mock_request: unittest.mock.Mock):
        type(mock_request()).status_code = PropertyMock(return_value=200)
        returning_id = 1234
        mock_request().json.return_value = {"id": returning_id}

        name = "test translation memory"
        source_lang = "en"
        target_langs = ["ja"]

        returned_id = TranslationMemory(token="mock-token").create(name, source_lang, target_langs)
        self.assertEqual(returning_id, returned_id)

        mock_request.assert_called_with(
            constants.HttpMethod.post.value,
            "https://cloud.memsource.com/web/api2/v1/transMemories",
            params={"token": "mock-token"},
            json={
                "name": name,
                "sourceLang": source_lang,
                "targetLangs": target_langs,
            },
            timeout=60,
        )

    @patch.object(requests.Session, "request")
    def test_list(self, mock_request: unittest.mock.Mock):
        type(mock_request()).status_code = PropertyMock(return_value=200)
        mock_request().json.return_value = {
            "content": [{
                "id": 1,
                "targetLangs": ["ja"],
                "sourceLang": "en",
                "name": "transMem"
            }]
        }

        for translation_memory in TranslationMemory(token="mock-token").list():
            self.assertIsInstance(translation_memory, models.TranslationMemory)

        mock_request.assert_called_with(
            constants.HttpMethod.get.value,
            "https://cloud.memsource.com/web/api2/v1/transMemories",
            params={"token": "mock-token", "pageNumber": 0},
            timeout=60,
        )

    @patch.object(requests.Session, "request")
    def test_list_with_page_id(self, mock_request: unittest.mock.Mock):
        type(mock_request()).status_code = PropertyMock(return_value=200)
        mock_request().json.return_value = {
            "content": [{
                "id": 1,
                "targetLangs": ["ja"],
                "sourceLang": "en",
                "name": "transMem"
            }]
        }
        EXISTING_PAGE_ID = 1
        for translation_memory in TranslationMemory(token="mock-token").list(EXISTING_PAGE_ID):
            self.assertIsInstance(translation_memory, models.TranslationMemory)

        mock_request.assert_called_with(
            constants.HttpMethod.get.value,
            "https://cloud.memsource.com/web/api2/v1/transMemories",
            params={"token": "mock-token", "pageNumber": EXISTING_PAGE_ID},
            timeout=60,
        )

    @patch.object(requests.Session, "request")
    def test_list_with_EMPTY_PAGE_ID(self, mock_request: unittest.mock.Mock):
        type(mock_request()).status_code = PropertyMock(return_value=200)
        mock_request().json.return_value = {"content": []}
        EMPTY_PAGE_ID = 1
        self.assertEqual(0, len(TranslationMemory(token="mock-token").list(EMPTY_PAGE_ID)))

        mock_request.assert_called_with(
            constants.HttpMethod.get.value,
            "https://cloud.memsource.com/web/api2/v1/transMemories",
            params={"token": "mock-token", "pageNumber": EMPTY_PAGE_ID},
            timeout=60,
        )

    @patch("builtins.open")
    @patch.object(requests.Session, "request")
    def test_upload(self, mock_request: unittest.mock.Mock, mock_open: unittest.mock.Mock):
        accepted_segments_count = 100
        type(mock_request()).status_code = PropertyMock(return_value=200)
        mock_request().json.return_value = {"acceptedSegmentsCount": accepted_segments_count}
        mock_open.return_value.__enter__.return_value.name = "this_is_a_test.tmx"

        translation_memory_id = 123
        returned_value = TranslationMemory(token="mock-token").upload(
            translation_memory_id, "test.tmx")

        # Don't use assert_called_with because files has file object. It is difficult to test.
        self.assertTrue(mock_request.called)
        (called_args, called_kwargs) = mock_request.call_args

        # hard to test
        del called_kwargs["files"]
        self.assertEqual(
            (
                constants.HttpMethod.post.value,
                "https://cloud.memsource.com/web/api2/v1/transMemories/123/import",
            ),
            called_args,
        )

        print(called_kwargs)
        self.assertEqual({
            "headers": {
                "Content-Disposition": "inline; filename*=UTF-8''this_is_a_test.tmx",
                "Content-Type": "application/octet-stream",
            },
            "params": {"token": "mock-token"},
            "timeout": 60,
        }, called_kwargs)
        self.assertEqual(accepted_segments_count, returned_value)

    @patch.object(uuid, "uuid1")
    @patch.object(requests.Session, "request")
    def test_upload_from_text(
            self,
            mock_request: unittest.mock.Mock,
            mock_uuid1: unittest.mock.Mock,
    ):
        accepted_segments_count = 123
        type(mock_request()).status_code = PropertyMock(return_value=200)
        mock_request().json.return_value = {"acceptedSegmentsCount": accepted_segments_count}
        mock_uuid1().hex = "file_name"
        translation_memory_id = 1234
        returned_value = TranslationMemory(token="mock-token").upload_from_text(
            translation_memory_id, "<xml/>",
        )

        # Don't use assert_called_with because files has file object. It is difficult to test.
        self.assertTrue(mock_request.called)
        (called_args, called_kwargs) = mock_request.call_args

        # hard to test
        del called_kwargs["files"]
        self.assertEqual(
            (
                constants.HttpMethod.post.value,
                "https://cloud.memsource.com/web/api2/v1/transMemories/1234/import",
            ),
            called_args,
        )

        self.assertEqual({
            "headers": {
                "Content-Disposition": "inline; filename*=UTF-8''file_name.tmx",
                "Content-Type": "application/octet-stream",
            },
            "params": {"token": "mock-token"},
            "timeout": 60,
        }, called_kwargs)

        self.assertEqual(accepted_segments_count, returned_value)

    @patch.object(requests.Session, "request")
    def test_search_segment_by_job(self, mock_request: unittest.mock.Mock):
        type(mock_request()).status_code = PropertyMock(return_value=200)

        segment = "Hello"
        next_segment = "Next segment"
        previous_segment = "Previous Segment"
        project_id = 1234
        job_uid = "1"

        mock_request().json.return_value = {
            "searchResults": [{
                "segmentId": "5023cd08e4b015e0656c4a8f",
                "source": {
                    "id": None,
                    "text": segment,
                    "lang": "en",
                    "rtl": False,
                    "modifiedAt": 1418972812301,
                    "createdAt": 1418972812301,
                    "modifiedBy": {},
                    "createdBy": {},
                    "fileName": None,
                    "project": None,
                    "client": None,
                    "domain": None,
                    "subDomain": None,
                    "tagMetadata": [],
                    "previousSegment": None,
                    "nextSegment": None,
                    "key": "",
                },
                "translations": [{
                    "fileName": None,
                    "modifiedAt": 1340641766000,
                    "project": None,
                    "rtl": False,
                    "previousSegment": None,
                    "createdAt": 1336380000000,
                    "createdBy": {
                        "role": None,
                        "email": None,
                        # Because I got null as string.
                        "userName": "null",
                        "lastName": None,
                        "active": False,
                        "firstName": None,
                        "id": 0
                    },
                    "modifiedBy": {
                        "role": None,
                        "email": None,
                        "userName": "null",
                        "lastName": None,
                        "active": False,
                        "firstName": None,
                        "id": 0
                    },
                    "domain": None,
                    "id": None,
                    "nextSegment": None,
                    "text": "こんにちは",
                    "tagMetadata": [],
                    "subDomain": None,
                    "lang": "ja",
                    "client": None,
                }],
                "transMemory": {
                    "name": "Test translation memory",
                    "id": "5023cb2ee4b015e0656c4a8e",
                    "reverse": False,
                },
                "grossScore": 1.01,
                "score": 1.01,
                "subSegment": False,
            }]
        }

        returned_value = TranslationMemory(token="mock-token").search_segment_by_job(
            project_id=project_id,
            job_uid=job_uid,
            segment=segment,
            next_segment=next_segment,
            previous_segment=previous_segment,
        )

        mock_request.assert_called_with(
            constants.HttpMethod.post.value,
            (
                "https://cloud.memsource.com/web/api2/"
                "v1/projects/1234/jobs/1/transMemories/searchSegment"
            ),
            params={"token": "mock-token"},
            json={
                "segment": segment,
                "nextSegment": next_segment,
                "previousSegment": previous_segment,
                "scoreThreshold": 0.7,
            },
            timeout=60,
        )

        for segment_search_result in returned_value:
            self.assertIsInstance(segment_search_result, models.SegmentSearchResult)

    @patch.object(requests.Session, "request")
    def test_search(self, mock_request: unittest.mock.Mock):
        type(mock_request()).status_code = PropertyMock(return_value=200)

        translation_memory_id = 1234
        query = "Hello"
        source_lang = "en"
        target_langs = ["ja", "en_gb"]
        next_segment = "Next segment"
        previous_segment = "Previous Segment"

        mock_request().json.return_value = {
            "searchResults": [{
                "segmentId": "5023cd08e4b015e0656c4a8f",
                "source": {
                    "id": None,
                    "text": query,
                    "lang": "en",
                    "rtl": False,
                    "modifiedAt": 1418972812301,
                    "createdAt": 1418972812301,
                    "modifiedBy": {},
                    "createdBy": {},
                    "fileName": None,
                    "project": None,
                    "client": None,
                    "domain": None,
                    "subDomain": None,
                    "tagMetadata": [],
                    "previousSegment": None,
                    "nextSegment": None,
                    "key": "",
                },
                "translations": [{
                    "fileName": None,
                    "modifiedAt": 1340641766000,
                    "project": None,
                    "rtl": False,
                    "previousSegment": None,
                    "createdAt": 1336380000000,
                    "createdBy": {
                        "role": None,
                        "email": None,
                        # Because I got null as string.
                        "userName": "null",
                        "lastName": None,
                        "active": False,
                        "firstName": None,
                        "id": 0
                    },
                    "modifiedBy": {
                        "role": None,
                        "email": None,
                        "userName": "null",
                        "lastName": None,
                        "active": False,
                        "firstName": None,
                        "id": 0
                    },
                    "domain": None,
                    "id": None,
                    "nextSegment": None,
                    "text": "こんにちは",
                    "tagMetadata": [],
                    "subDomain": None,
                    "lang": "ja",
                    "client": None,
                }],
                "transMemory": {
                    "name": "Test translation memory",
                    "id": "5023cb2ee4b015e0656c4a8e",
                    "reverse": False,
                },
                "grossScore": 1.01,
                "score": 1.01,
                "subSegment": False,
            }]
        }

        returned_value = TranslationMemory(token="mock-token").search(
            translation_memory_id, query, source_lang,
            target_langs=target_langs, next_segment=next_segment,
            previous_segment=previous_segment
        )

        self.assertEqual(len(returned_value), 1)

        mock_request.assert_called_with(
            constants.HttpMethod.post.value,
            "https://cloud.memsource.com/web/api2/v1/transMemories/1234/search",
            params={"token": "mock-token"},
            json={
                "query": query,
                "sourceLang": source_lang,
                "targetLangs": target_langs,
                "previousSegment": previous_segment,
                "nextSegment": next_segment,
            },
            timeout=60,
        )

        for segment_search_result in returned_value:
            self.assertIsInstance(segment_search_result, models.SegmentSearchResult)

    @patch.object(requests.Session, "request")
    def test_export(self, mock_request: unittest.mock.Mock):
        type(mock_request()).status_code = PropertyMock(return_value=200)

        asynchronous_request_id = 1234
        tm_id = 4567
        target_langs = ["en"]
        callback_url = "CALLBACK_URL"

        mock_request().json.return_value = {
            "asyncRequest": {
                "id": asynchronous_request_id,
                "createdBy": {
                    "lastName": "test",
                    "id": 1,
                    "firstName": "admin",
                    "role": "ADMIN",
                    "email": "test@test.com",
                    "userName": "admin",
                    "active": True
                },
                "dateCreated": "2014-11-03T16:03:11Z",
                "action": "EXPORT_TMX",
                "asyncResponse": {},
                "parent": {},
                "project": {},
            },
            "asyncExport": {
                "transMemory": {"id": tm_id}
            },
            "exportTargetLangs": target_langs,
        }

        returned_value = TranslationMemory(token="mock-token").export(
            translation_memory_id=tm_id,
            target_langs=target_langs,
            callback_url=callback_url
        )

        self.assertIsInstance(returned_value, models.AsynchronousRequest)

        mock_request.assert_called_with(
            constants.HttpMethod.post.value,
            "https://cloud.memsource.com/web/api2/v2/transMemories/4567/export",
            params={"token": "mock-token"},
            json={
                "exportTargetLangs": target_langs,
                "callbackUrl": callback_url,
            },
            timeout=60,
        )

    @patch.object(requests.Session, "request")
    def test_insert(self, mock_request: unittest.mock.Mock):
        type(mock_request()).status_code = PropertyMock(return_value=200)

        translation_memory_id = 1234
        target_lang = "ja"
        source_segment = "this is source segment"
        target_segment = "this is target segment"
        previous_source_segment = "this is previous source segment"
        next_source_segment = "this is next source segment"

        TranslationMemory(token="mock-token").insert(
            translation_memory_id,
            target_lang=target_lang,
            source_segment=source_segment,
            target_segment=target_segment,
            previous_source_segment=previous_source_segment,
            next_source_segment=next_source_segment
        )

        mock_request.assert_called_with(
            constants.HttpMethod.post.value,
            "https://cloud.memsource.com/web/api2/v1/transMemories/1234/segments",
            params={"token": "mock-token"},
            json={
                "targetLang": target_lang,
                "sourceSegment": source_segment,
                "targetSegment": target_segment,
                "previousSourceSegment": previous_source_segment,
                "nextSourceSegment": next_source_segment
            },
            timeout=60,
        )

    @patch.object(requests.Session, "request")
    def test_delete_source_and_translations(self, mock_request: unittest.mock.Mock):
        type(mock_request()).status_code = PropertyMock(return_value=200)
        translation_memory_id = 1
        segment_id = "2"

        TranslationMemory(token="mock-token").delete_source_and_translations(
            translation_memory_id, segment_id
        )

        mock_request.assert_called_with(
            constants.HttpMethod.delete.value,
            "https://cloud.memsource.com/web/api2/v1/transMemories/1/segments/2",
            params={"token": "mock-token"},
            timeout=60,
        )
