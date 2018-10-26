import os
from unittest.mock import patch, PropertyMock

import requests

import api as api_test
from memsource import api, constants


class TestApiTermBase(api_test.ApiTestCase):
    def setUp(self):
        self.url_base = 'https://cloud.memsource.com/web/api/v2/termBase'
        self.termbase = api.TermBase(None)
        self.test_termbase_filepath = '/tmp/test_termbase.xlsx'

        self.setCleanUpFiles((self.test_termbase_filepath,))

    @patch.object(requests.Session, 'request')
    def test_get_term_bases(self, mock_request):
        type(mock_request()).status_code = PropertyMock(return_value=200)

        termbase_contents = ['test termbase content', 'second']

        mock_request().iter_content.return_value = [
            bytes(content, 'utf-8') for content in termbase_contents]

        self.assertFalse(os.path.isfile(self.test_termbase_filepath))
        returned_value = self.termbase.download(
            termbase_id=123,
            filepath=self.test_termbase_filepath,
        )
        self.assertTrue(os.path.isfile(self.test_termbase_filepath))

        self.assertIsNone(returned_value)

        with open(self.test_termbase_filepath) as f:
            self.assertEqual(''.join(termbase_contents), f.read())

        mock_request.assert_called_with(
            constants.HttpMethod.get.value,
            "{}/export".format(self.url_base),
            params={
                'token': self.termbase.token,
                'termBase': 123,
                'format': constants.TermBaseFormat.XLSX,
            },
            timeout=constants.Base.timeout.value * 5,
            stream=True,
        )
