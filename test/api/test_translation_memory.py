from unittest.mock import patch, PropertyMock
from memsource import api, constants, models
import requests
import api as api_test


class TestApiJob(api_test.ApiTestCase):
    def setUp(self):
        self.url_base = 'https://cloud1.memsource.com/web/api/v4/transMemory'
        self.translation_memory = api.TranslationMemory(None)
        self.test_tmx_file_path = '/tmp/test.tmx'

        self.setCleanUpFiles([self.test_tmx_file_path])

        with open(self.test_tmx_file_path, 'w+') as f:
            f.write('This is test tmx file.')

    @patch.object(requests, 'request')
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
            'post',
            '{}/create'.format(self.url_base),
            params={
                'token': self.translation_memory.token,
                'name': name,
                'sourceLang': source_lang,
                'targetLang': target_langs,
            },
            files={},
            timeout=constants.Base.timeout.value
        )

    @patch.object(requests, 'request')
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
            'post',
            '{}/list'.format(self.url_base),
            params={
                'token': self.translation_memory.token,
            },
            files={},
            timeout=constants.Base.timeout.value
        )

    @patch.object(requests, 'request')
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
        self.assertEqual(('post', '{}/import'.format(self.url_base)), called_args)

        self.assertEqual({
            'params': {
                'token': self.translation_memory.token,
                'transMemory': translation_memory_id,
            },
            'timeout': constants.Base.timeout.value,
        }, called_kwargs)

        self.assertEqual(accepted_segments_count, returned_value)
