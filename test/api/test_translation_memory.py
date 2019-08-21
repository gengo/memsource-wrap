import os
from unittest.mock import patch, PropertyMock
import urllib.request

import requests

import api as api_test
from memsource import api, constants, models

ANY_ID = 1
ANY_LCS = ['en', 'ja']


class TestApiTranslationMemory(api_test.ApiTestCase):
    def setUp(self):
        self.url_base = 'https://cloud.memsource.com/web/api/v4/transMemory'
        self.translation_memory = api.TranslationMemory()
        self.test_tmx_file_path = '/tmp/test.tmx'
        self.test_export_file_path = '/tmp/export.tmx'

        self.setCleanUpFiles([self.test_tmx_file_path, self.test_export_file_path])

        with open(self.test_tmx_file_path, 'w+') as f:
            f.write('This is test tmx file.')

    @patch.object(requests.Session, 'request')
    def test_create(self, mock_request):
        type(mock_request()).status_code = PropertyMock(return_value=200)
        returning_id = self.gen_random_int()
        mock_request().json.return_value = {'id': returning_id}

        name = 'test translation memory'
        source_lang = 'en'
        target_langs = ['ja']

        returned_id = self.translation_memory.create(name, source_lang, target_langs)
        self.assertEqual(returning_id, returned_id)

        mock_request.assert_called_with(
            constants.HttpMethod.post.value,
            '{}/create'.format(self.url_base),
            data={
                'token': self.translation_memory.token,
                'name': name,
                'sourceLang': source_lang,
                'targetLang': target_langs,
            },
            timeout=constants.Base.timeout.value
        )

    @patch.object(requests.Session, 'request')
    def test_list(self, mock_request):
        type(mock_request()).status_code = PropertyMock(return_value=200)
        mock_request().json.return_value = [{
            'id': 1,
            'targetLangs': [
                'ja'
            ],
            'sourceLang': 'en',
            'name': 'transMem'
        }]

        for translation_memory in self.translation_memory.list():
            self.assertIsInstance(translation_memory, models.TranslationMemory)

        mock_request.assert_called_with(
            constants.HttpMethod.post.value,
            '{}/list'.format(self.url_base),
            data={
                'token': self.translation_memory.token,
                'page': 0
            },
            timeout=constants.Base.timeout.value
        )

    @patch.object(requests.Session, 'request')
    def test_list_with_page_id(self, mock_request):
        type(mock_request()).status_code = PropertyMock(return_value=200)
        mock_request().json.return_value = [{
            'id': 1,
            'targetLangs': [
                'ja'
            ],
            'sourceLang': 'en',
            'name': 'transMem'
        }]
        EXISTING_PAGE_ID = 1
        for translation_memory in self.translation_memory.list(EXISTING_PAGE_ID):
            self.assertIsInstance(translation_memory, models.TranslationMemory)

        mock_request.assert_called_with(
            constants.HttpMethod.post.value,
            '{}/list'.format(self.url_base),
            data={
                'token': self.translation_memory.token,
                'page': EXISTING_PAGE_ID
            },
            timeout=constants.Base.timeout.value
        )

    @patch.object(requests.Session, 'request')
    def test_list_with_EMPTY_PAGE_ID(self, mock_request):

        type(mock_request()).status_code = PropertyMock(return_value=200)
        mock_request().json.return_value = []
        EMPTY_PAGE_ID = 1
        self.assertEqual(0, len(self.translation_memory.list(EMPTY_PAGE_ID)))

        mock_request.assert_called_with(
            constants.HttpMethod.post.value,
            '{}/list'.format(self.url_base),
            data={
                'token': self.translation_memory.token,
                'page': EMPTY_PAGE_ID
            },
            timeout=constants.Base.timeout.value
        )

    @patch.object(requests.Session, 'request')
    def test_upload(self, mock_request):
        accepted_segments_count = self.gen_random_int()
        type(mock_request()).status_code = PropertyMock(return_value=200)
        mock_request().json.return_value = {'acceptedSegmentsCount': accepted_segments_count}

        translation_memory_id = self.gen_random_int()
        returned_value = self.translation_memory.upload(
            translation_memory_id, self.test_tmx_file_path)

        # Don't use assert_called_with because files has file object. It is difficult to test.
        self.assertTrue(mock_request.called)
        (called_args, called_kwargs) = mock_request.call_args

        # hard to test
        del called_kwargs['files']
        self.assertEqual(
            (constants.HttpMethod.post.value, '{}/import'.format(self.url_base)), called_args)

        self.assertEqual({
            'data': {
                'token': self.translation_memory.token,
                'transMemory': translation_memory_id,
            },
            'timeout': constants.Base.timeout.value,
        }, called_kwargs)

        self.assertEqual(accepted_segments_count, returned_value)

    @patch.object(requests.Session, 'request')
    def test_upload_from_text(self, mock_request):
        accepted_segments_count = self.gen_random_int()
        type(mock_request()).status_code = PropertyMock(return_value=200)
        mock_request().json.return_value = {'acceptedSegmentsCount': accepted_segments_count}

        translation_memory_id = self.gen_random_int()
        returned_value = self.translation_memory.uploadFromText(translation_memory_id, '<xml/>')

        # Don't use assert_called_with because files has file object. It is difficult to test.
        self.assertTrue(mock_request.called)
        (called_args, called_kwargs) = mock_request.call_args

        # hard to test
        del called_kwargs['files']
        self.assertEqual(
            (constants.HttpMethod.post.value, '{}/import'.format(self.url_base)), called_args)

        self.assertEqual({
            'data': {
                'token': self.translation_memory.token,
                'transMemory': translation_memory_id,
            },
            'timeout': constants.Base.timeout.value,
        }, called_kwargs)

        self.assertEqual(accepted_segments_count, returned_value)

    @patch.object(requests.Session, 'request')
    def test_search(self, mock_request):
        type(mock_request()).status_code = PropertyMock(return_value=200)

        translation_memory_id = 1234
        query = "Hello"
        source_lang = "en"
        target_langs = ["ja", 'en_gb']
        next_segment = "Next segment"
        previous_segment = "Previous Segment"

        mock_request().json.return_value = [{
            'score': 1.01,
            'grossScore': 1.01,
            'segmentId': '5023cd08e4b015e0656c4a8f',
            'source': {
                'fileName': None,
                'modifiedAt': 1418972812301,
                'project': None,
                'rtl': False,
                'previousSegment': None,
                'createdAt': 1418972812301,
                'createdBy': None,
                'modifiedBy': None,
                'domain': None,
                'id': None,
                'nextSegment': None,
                'text': query,
                'tagMetadata': [],
                'subDomain': None,
                'lang': 'en',
                'client': None
            },
            'subSegment': False,
            'translations': [{
                'fileName': None,
                'modifiedAt': 1340641766000,
                'project': None,
                'rtl': False,
                'previousSegment': None,
                'createdAt': 1336380000000,
                'createdBy': {
                    'role': None,
                    'email': None,
                    # Because I got null as string.
                    'userName': 'null',
                    'lastName': None,
                    'active': False,
                    'firstName': None,
                    'id': 0
                },
                'modifiedBy': {
                    'role': None,
                    'email': None,
                    'userName': 'null',
                    'lastName': None,
                    'active': False,
                    'firstName': None,
                    'id': 0
                },
                'domain': None,
                'id': None,
                'nextSegment': None,
                'text': 'こんにちは',
                'tagMetadata': [],
                'subDomain': None,
                'lang': 'ja',
                'client': None
            }],
            'transMemory': {
                'name': 'Test translation memory',
                'id': '5023cb2ee4b015e0656c4a8e',
                'reverse': False
            }
        }]

        returned_value = self.translation_memory.search(
            translation_memory_id, query, source_lang,
            target_langs=target_langs, next_segment=next_segment,
            previous_segment=previous_segment
        )

        self.assertEqual(len(returned_value), 1)

        mock_request.assert_called_with(
            constants.HttpMethod.post.value,
            'https://cloud.memsource.com/web/api/v4/transMemory/search',
            data={
                'token': self.translation_memory.token,
                'transMemory': translation_memory_id,
                'query': query,
                'sourceLang': source_lang,
                'targetLang': target_langs,
                'nextSegment': next_segment,
                'previousSegment': previous_segment
            },
            timeout=constants.Base.timeout.value
        )

        for segment_search_result in returned_value:
            self.assertIsInstance(segment_search_result, models.SegmentSearchResult)

    @patch.object(requests.Session, 'request')
    def test_search_segment_by_task(self, mock_request):
        type(mock_request()).status_code = PropertyMock(return_value=200)

        segment = "Hello"
        next_segment = "Next segment"
        previous_segment = "Previous Segment"
        task = 'test task'

        mock_request().json.return_value = [{
            'score': 1.01,
            'grossScore': 1.01,
            'segmentId': '5023cd08e4b015e0656c4a8f',
            'source': {
                'fileName': None,
                'modifiedAt': 1418972812301,
                'project': None,
                'rtl': False,
                'previousSegment': None,
                'createdAt': 1418972812301,
                'createdBy': None,
                'modifiedBy': None,
                'domain': None,
                'id': None,
                'nextSegment': None,
                'text': segment,
                'tagMetadata': [],
                'subDomain': None,
                'lang': 'en',
                'client': None
            },
            'subSegment': False,
            'translations': [{
                'fileName': None,
                'modifiedAt': 1340641766000,
                'project': None,
                'rtl': False,
                'previousSegment': None,
                'createdAt': 1336380000000,
                'createdBy': {
                    'role': None,
                    'email': None,
                    # Because I got null as string.
                    'userName': 'null',
                    'lastName': None,
                    'active': False,
                    'firstName': None,
                    'id': 0
                },
                'modifiedBy': {
                    'role': None,
                    'email': None,
                    'userName': 'null',
                    'lastName': None,
                    'active': False,
                    'firstName': None,
                    'id': 0
                },
                'domain': None,
                'id': None,
                'nextSegment': None,
                'text': 'こんにちは',
                'tagMetadata': [],
                'subDomain': None,
                'lang': 'ja',
                'client': None
            }],
            'transMemory': {
                'name': 'Test translation memory',
                'id': '5023cb2ee4b015e0656c4a8e',
                'reverse': False
            }
        }]

        returned_value = self.translation_memory.searchSegmentByTask(
            task, segment, next_segment=next_segment, previous_segment=previous_segment
        )

        mock_request.assert_called_with(
            constants.HttpMethod.post.value,
            'https://cloud.memsource.com/web/api/v4/transMemory/searchSegmentByTask',
            data={
                'token': self.translation_memory.token,
                'task': task,
                'segment': segment,
                'nextSegment': next_segment,
                'previousSegment': previous_segment,
                'scoreThreshold': 0.6,
            },
            timeout=constants.Base.timeout.value
        )

        for segment_search_result in returned_value:
            self.assertIsInstance(segment_search_result, models.SegmentSearchResult)

    @patch.object(requests.Session, 'request')
    def test_insert(self, mock_request):
        type(mock_request()).status_code = PropertyMock(return_value=200)

        translation_memory_id = self.gen_random_int()
        target_lang = 'ja'
        source_segment = 'this is source segment'
        target_segment = 'this is target segment'
        previous_source_segment = 'this is previous source segment'
        next_source_segment = 'this is next source segment'

        self.translation_memory.insert(
            translation_memory_id,
            target_lang=target_lang,
            source_segment=source_segment,
            target_segment=target_segment,
            previous_source_segment=previous_source_segment,
            next_source_segment=next_source_segment
        )

        mock_request.assert_called_with(
            constants.HttpMethod.post.value,
            'https://cloud.memsource.com/web/api/v4/transMemory/insert',
            data={
                'token': self.translation_memory.token,
                'transMemory': translation_memory_id,
                'targetLang': target_lang,
                'sourceSegment': source_segment,
                'targetSegment': target_segment,
                'previousSourceSegment': previous_source_segment,
                'nextSourceSegment': next_source_segment
            },
            timeout=constants.Base.timeout.value
        )

    @patch.object(requests.Session, 'request')
    def test_export(self, mock_request):
        type(mock_request()).status_code = PropertyMock(return_value=200)

        translation_memory_id = ANY_ID
        target_langs = ANY_LCS
        file_format = 'TMX'

        tmx_contents = ['test first chunk', 'second chunk']
        mock_request().iter_content.return_value = [
            bytes(content, 'utf-8') for content in tmx_contents]

        self.assertFalse(os.path.isfile(self.test_export_file_path))

        returned_value = self.translation_memory.export(
            translation_memory_id=translation_memory_id,
            file_format=file_format,
            target_langs=target_langs,
            file_path=self.test_export_file_path
        )
        self.assertTrue(os.path.isfile(self.test_export_file_path))

        self.assertIsNone(returned_value)

        with open(self.test_export_file_path) as f:
            self.assertEqual(''.join(tmx_contents), f.read())

        mock_request.assert_called_with(
            constants.HttpMethod.get.value,
            "{}/export".format(self.url_base),
            params={
                'token': self.translation_memory.token,
                'transMemory': translation_memory_id,
                'format': file_format,
                'targetLang': target_langs,
            },
            timeout=constants.Base.timeout.value * 5,
            stream=True
        )

    @patch.object(requests.Session, 'request')
    def test_delete_source_and_translations(self, mock_request):
        type(mock_request()).status_code = PropertyMock(return_value=200)
        translation_memory_id = 1
        segment_ids = ['2', '3']

        self.translation_memory.deleteSourceAndTranslations(translation_memory_id, segment_ids)

        mock_request.assert_called_with(
            constants.HttpMethod.post.value,
            urllib.request.urljoin(self.url_base, "transMemory/deleteSourceAndTranslations"),
            data={
                'token': self.translation_memory.token,
                'transMemory': translation_memory_id,
                'segmentId': segment_ids
            },
            timeout=constants.Base.timeout.value
        )
