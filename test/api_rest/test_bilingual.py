import os
import requests
import unittest
import uuid
from unittest.mock import patch, PropertyMock

from memsource import constants, models
from memsource.api_rest.bilingual import Bilingual


class TestBilingual(unittest.TestCase):
    @patch("builtins.open")
    @patch.object(requests.Session, "request")
    def test_get_bilingual_file(
            self,
            mock_request: unittest.mock.Mock,
            mock_open: unittest.mock.Mock
    ):
        type(mock_request()).status_code = PropertyMock(return_value=200)

        mxliff_contents = ['test mxliff content', 'second']

        mock_request().iter_content.return_value = [
            bytes(content, 'utf-8') for content in mxliff_contents]

        project_id = 1234
        job_uids = [1, 2]
        Bilingual(token="mock-token").get_bilingual_file(
            project_id, job_uids, "test.xlf"
        )

        mock_request.assert_called_with(
            constants.HttpMethod.post.value,
            "https://cloud.memsource.com/web/api2/v1/projects/1234/jobs/bilingualFile",
            headers={"Authorization": "ApiToken mock-token"},
            json={"jobs": [{"uid": 1}, {"uid": 2}]},
            timeout=60,
        )

    @patch.object(requests.Session, "request")
    def test_get_bilingual_file_xml(self, mock_request):
        type(mock_request()).status_code = PropertyMock(return_value=200)

        mxliff_contents = ['test mxliff content', 'second']

        mock_request().iter_content.return_value = [
            bytes(content, 'utf-8') for content in mxliff_contents]
        project_id = 1234
        job_uids = [1, 2]

        returned_value = Bilingual(token="mock-token").get_bilingual_file_xml(project_id, job_uids)

        self.assertEqual(''.join(mxliff_contents).encode(), returned_value)

        mock_request.assert_called_with(
            constants.HttpMethod.post.value,
            "https://cloud.memsource.com/web/api2/v1/projects/1234/jobs/bilingualFile",
            headers={"Authorization": "ApiToken mock-token"},
            json={"jobs": [{"uid": 1}, {"uid": 2}]},
            timeout=60,
        )

    @patch.object(requests.Session, 'request')
    def test_get_bilingual_as_mxliff_units(self, mock_request):
        type(mock_request()).status_code = PropertyMock(return_value=200)

        mxliff_contents = ['test mxliff content', 'second']

        mock_request().iter_content.return_value = [
            bytes(content, 'utf-8') for content in mxliff_contents]

        base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)))
        with open(os.path.join(base_dir, '..', 'lib', 'mxliff', 'test.mxliff')) as f:
            mxliff = f.read().encode('utf-8')

        mock_request().iter_content.return_value = [
            mxliff[i: i + 100] for i in range(0, len(mxliff), 100)
        ]
        project_id = 1234
        job_uids = [1, 2]

        bi = Bilingual(token="mock-token")
        returned_value = bi.get_bilingual_as_mxliff_units(project_id, job_uids)

        self.assertEqual(len(returned_value), 2)

        self.assertIsInstance(returned_value[0], models.MxliffUnit)
        self.assertEqual(returned_value[0], {
            'id': 'fj4ewiofj3qowjfw:0',
            'score': 0.0,
            'gross_score': 0.0,
            'source': 'Hello World.',
            'target': None,
            'machine_trans': None,
            'memsource_tm': None,
            'tunit_metadata': [],
        })

        self.assertIsInstance(returned_value[1], models.MxliffUnit)
        self.assertEqual(returned_value[1], {
            'id': 'fj4ewiofj3qowjfw:1',
            'score': 1.01,
            'gross_score': 1.01,
            'source': 'This library wraps Memsoruce API for Python.',
            'target': 'このライブラリはMemsourceのAPIをPython用にラップしています。',
            'machine_trans': 'This is machine translation.',
            'memsource_tm': 'This is memsource translation memory.',
            'tunit_metadata': [],
        })

        mock_request.assert_called_with(
            constants.HttpMethod.post.value,
            "https://cloud.memsource.com/web/api2/v1/projects/1234/jobs/bilingualFile",
            headers={"Authorization": "ApiToken mock-token"},
            json={"jobs": [{"uid": 1}, {"uid": 2}]},
            timeout=60,
        )

    @patch.object(uuid, "uuid1")
    @patch.object(requests.Session, "request")
    def test_upload_bilingual_file_from_xml(
            self,
            mock_request: unittest.mock.Mock,
            mock_uuid1: unittest.mock.Mock
    ):
        type(mock_request()).status_code = PropertyMock(return_value=200)

        xml = "<xml>this is test</xml>"
        mock_uuid1().hex = "test_file"

        Bilingual(token="mock-token").upload_bilingual_file_from_xml(xml)

        mock_request.assert_called_with(
            constants.HttpMethod.put.value,
            "https://cloud.memsource.com/web/api2/v1/bilingualFiles",
            headers={"Authorization": "ApiToken mock-token"},
            files={"file": ("test_file.mxliff", xml)},
            timeout=constants.Base.timeout.value
        )
