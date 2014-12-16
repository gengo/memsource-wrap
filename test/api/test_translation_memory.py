from unittest.mock import patch, PropertyMock
from memsource import api, constants
import requests
import api as api_test


class TestApiJob(api_test.ApiTestCase):
    def setUp(self):
        self.url_base = 'https://cloud1.memsource.com/web/api/v4/transMemory'
        self.translation_memory = api.TranslationMemory(None)

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
