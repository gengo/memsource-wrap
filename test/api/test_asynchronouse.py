import uuid
import io
import builtins
from unittest.mock import PropertyMock
from unittest.mock import patch

import requests

import api as api_test
from memsource import api
from memsource import constants
from memsource import models
from memsource import exceptions


class TestApiAsynchronous(api_test.ApiTestCase):
    def setUp(self):
        self.asynchronous = api.Asynchronous(None)

        self.job_parts = [{
            'id': 9371,
            'task': '5023cd08e4b015e0656c4a8f',
            'fileName': 'test_file.txt',
            'targetLang': 'ja',
            'wordCount': 121,
            'beginIndex': 0,
            'endIndex': 14
        }, {
            'id': 9372,
            'task': '5087ab08eac015e0656c4a00',
            'fileName': 'test_file.txt',
            'targetLang': 'ja',
            'wordCount': 121,
            'beginIndex': 0,
            'endIndex': 14
        }]

    @patch.object(requests, 'request')
    def test_pre_translate_no_callback(self, mock_request):
        type(mock_request()).status_code = PropertyMock(return_value=200)

        asynchronous_request_id = self.gen_random_int()
        job_part_ids = [self.gen_random_int() for i in range(0, 2)]

        mock_request().json.return_value = {
            'asyncRequest': {
                'createdBy': {
                    'lastName': 'test',
                    'id': 1,
                    'firstName': 'admin',
                    'role': 'ADMIN',
                    'email': 'test@test.com',
                    'userName': 'admin',
                    'active': True
                },
                'action': 'PRE_TRANSLATE',
                'id': asynchronous_request_id,
                'dateCreated': '2014-11-03T16:03:11Z',
                'asyncResponse': None
            }
        }

        retuned_value = self.asynchronous.preTranslate(job_part_ids)

        self.assertIsInstance(retuned_value, models.AsynchronousRequest)

        mock_request.assert_called_with(
            constants.HttpMethod.post.value,
            'https://cloud1.memsource.com/web/api/async/v2/job/preTranslate',
            params={
                'token': self.asynchronous.token,
                'jobPart': job_part_ids,
                'translationMemoryThreshold': 0.7,
                'callbackUrl': None,
            },
            files={},
            timeout=constants.Base.timeout.value
        )

    @patch.object(requests, 'request')
    def test_pre_translate_callback(self, mock_request):
        type(mock_request()).status_code = PropertyMock(return_value=200)

        asynchronous_request_id = self.gen_random_int()
        job_part_ids = [self.gen_random_int() for i in range(0, 2)]
        callback_url = 'CALLBACK_URL'

        mock_request().json.return_value = {
            'asyncRequest': {
                'createdBy': {
                    'lastName': 'test',
                    'id': 1,
                    'firstName': 'admin',
                    'role': 'ADMIN',
                    'email': 'test@test.com',
                    'userName': 'admin',
                    'active': True
                },
                'action': 'PRE_TRANSLATE',
                'id': asynchronous_request_id,
                'dateCreated': '2014-11-03T16:03:11Z',
                'asyncResponse': None
            }
        }

        retuned_value = self.asynchronous.preTranslate(job_part_ids, callback_url=callback_url)

        self.assertIsInstance(retuned_value, models.AsynchronousRequest)

        mock_request.assert_called_with(
            constants.HttpMethod.post.value,
            'https://cloud1.memsource.com/web/api/async/v2/job/preTranslate',
            params={
                'token': self.asynchronous.token,
                'jobPart': job_part_ids,
                'translationMemoryThreshold': 0.7,
                'callbackUrl': callback_url,
            },
            files={},
            timeout=constants.Base.timeout.value
        )

    @patch.object(requests, 'request')
    def test_get_async_request(self, mock_request):
        type(mock_request()).status_code = PropertyMock(return_value=200)

        asynchronous_request_id = self.gen_random_int()

        mock_request().json.return_value = {
            'id': asynchronous_request_id,
            'createdBy': {
                'id': 1,
                'firstName': 'admin',
                'email': 'test@test.com',
                'active': True,
                'userName': 'admin',
                'lastName': 'test',
                'role': 'ADMIN'
            },
            'asyncResponse': None,
            'action': 'PRE_TRANSLATE',
            'dateCreated': '2014-11-03T16:03:11Z'
        }

        retuned_value = self.asynchronous.getAsyncRequest(asynchronous_request_id)

        self.assertIsInstance(retuned_value, models.AsynchronousRequest)

        mock_request.assert_called_with(
            constants.HttpMethod.post.value,
            'https://cloud1.memsource.com/web/api/v2/async/getAsyncRequest',
            params={
                'token': self.asynchronous.token,
                'asyncRequest': asynchronous_request_id,
            },
            files={},
            timeout=constants.Base.timeout.value
        )

    @patch.object(requests, 'request')
    def test_create_analysis_no_callback(self, mock_request):
        type(mock_request()).status_code = PropertyMock(return_value=200)

        asynchronous_request_id = self.gen_random_int()
        analysis_id = self.gen_random_int()
        mock_request().json.return_value = {
            'asyncRequest': {
                'createdBy': {
                    'lastName': 'test',
                    'id': 1,
                    'firstName': 'admin',
                    'role': 'ADMIN',
                    'email': 'test@test.com',
                    'userName': 'admin',
                    'active': True
                },
                'action': 'PRE_TRANSLATE',
                'id': asynchronous_request_id,
                'dateCreated': '2014-11-03T16:03:11Z',
                'asyncResponse': None
            },
            'analyse': {
                'id': analysis_id,
            },
        }

        job_part_ids = [self.gen_random_int() for i in range(0, 2)]

        async_request, analysis = self.asynchronous.createAnalysis(job_part_ids)

        self.assertEqual(async_request.id, asynchronous_request_id)
        self.assertEqual(analysis.id, analysis_id)

        mock_request.assert_called_with(
            constants.HttpMethod.post.value,
            'https://cloud1.memsource.com/web/api/async/v2/analyse/create',
            params={
                'token': self.asynchronous.token,
                'jobPart': job_part_ids,
                'callbackUrl': None
            },
            files={},
            timeout=constants.Base.timeout.value
        )

    @patch.object(requests, 'request')
    def test_create_analysis_callback(self, mock_request):
        type(mock_request()).status_code = PropertyMock(return_value=200)

        asynchronous_request_id = self.gen_random_int()
        analysis_id = self.gen_random_int()
        callback_url = 'CALLBACK_URL'

        mock_request().json.return_value = {
            'asyncRequest': {
                'createdBy': {
                    'lastName': 'test',
                    'id': 1,
                    'firstName': 'admin',
                    'role': 'ADMIN',
                    'email': 'test@test.com',
                    'userName': 'admin',
                    'active': True
                },
                'action': 'PRE_TRANSLATE',
                'id': asynchronous_request_id,
                'dateCreated': '2014-11-03T16:03:11Z',
                'asyncResponse': None
            },
            'analyse': {
                'id': analysis_id,
            },
        }

        job_part_ids = [self.gen_random_int() for i in range(0, 2)]

        async_request, analysis = self.asynchronous.createAnalysis(
            job_part_ids,
            callback_url=callback_url,
        )

        self.assertEqual(async_request.id, asynchronous_request_id)
        self.assertEqual(analysis.id, analysis_id)

        mock_request.assert_called_with(
            constants.HttpMethod.post.value,
            'https://cloud1.memsource.com/web/api/async/v2/analyse/create',
            params={
                'token': self.asynchronous.token,
                'jobPart': job_part_ids,
                'callbackUrl': callback_url,
            },
            files={},
            timeout=constants.Base.timeout.value
        )

    @patch.object(builtins, 'open')
    @patch.object(io, 'open')
    @patch.object(uuid, 'uuid1')
    @patch.object(requests, 'request')
    def test_create_job_from_text_no_callback(self, mock_request, mock_uuid1, mock_ioopen, mock_open):
        type(mock_request()).status_code = PropertyMock(return_value=200)

        text = 'This is a test text.'
        mock_uuid1().hex = 'file_name'
        target_lang = 'ja'
        project_id = self.gen_random_int()
        asynchronous_request_id = self.gen_random_int()
        mock_file = mock_open().__enter__()

        mock_request().json.return_value = {
            'asyncRequest': {
                'createdBy': {
                    'lastName': 'test',
                    'id': 1,
                    'firstName': 'admin',
                    'role': 'ADMIN',
                    'email': 'test@test.com',
                    'userName': 'admin',
                    'active': True
                },
                'action': 'PRE_TRANSLATE',
                'id': asynchronous_request_id,
                'dateCreated': '2014-11-03T16:03:11Z',
                'asyncResponse': None
            },
            'jobParts': self.job_parts,
            'unsupportedFiles': []
        }

        async_request, job_parts = self.asynchronous.createJobFromText(
            project_id, text, target_lang)

        mock_request.assert_called_with(
            constants.HttpMethod.post.value,
            'https://cloud1.memsource.com/web/api/async/v2/job/create',
            params={
                'token': self.asynchronous.token,
                'project': project_id,
                'targetLang': target_lang,
                'callbackUrl': None,
            },
            files={'file': ('file_name.txt', mock_file)},
            timeout=constants.Base.timeout.value
        )

        mock_ioopen().__enter__().write.assert_called_with(text)
        self.assertEqual(async_request.id, asynchronous_request_id)
        self.assertEqual(job_parts[0].id, 9371)
        self.assertEqual(job_parts[1].id, 9372)

    @patch.object(builtins, 'open')
    @patch.object(io, 'open')
    @patch.object(uuid, 'uuid1')
    @patch.object(requests, 'request')
    def test_create_job_from_text_callback(self, mock_request, mock_uuid1, mock_ioopen, mock_open):
        type(mock_request()).status_code = PropertyMock(return_value=200)

        text = 'This is a test text.'
        mock_uuid1().hex = 'file_name'
        target_lang = 'ja'
        project_id = self.gen_random_int()
        asynchronous_request_id = self.gen_random_int()
        callback_url = 'CALLBACK_URL'
        mock_file = mock_open().__enter__()

        mock_request().json.return_value = {
            'asyncRequest': {
                'createdBy': {
                    'lastName': 'test',
                    'id': 1,
                    'firstName': 'admin',
                    'role': 'ADMIN',
                    'email': 'test@test.com',
                    'userName': 'admin',
                    'active': True
                },
                'action': 'PRE_TRANSLATE',
                'id': asynchronous_request_id,
                'dateCreated': '2014-11-03T16:03:11Z',
                'asyncResponse': None
            },
            'jobParts': self.job_parts,
            'unsupportedFiles': []
        }

        async_request, job_parts = self.asynchronous.createJobFromText(
            project_id, text, target_lang, callback_url=callback_url)

        mock_request.assert_called_with(
            constants.HttpMethod.post.value,
            'https://cloud1.memsource.com/web/api/async/v2/job/create',
            params={
                'token': self.asynchronous.token,
                'project': project_id,
                'targetLang': target_lang,
                'callbackUrl': callback_url,
            },
            files={'file': ('file_name.txt', mock_file)},
            timeout=constants.Base.timeout.value
        )

        mock_ioopen().__enter__().write.assert_called_with(text)
        self.assertEqual(async_request.id, asynchronous_request_id)
        self.assertEqual(job_parts[0].id, 9371)
        self.assertEqual(job_parts[1].id, 9372)

    @patch.object(requests, 'request')
    def test_create_job_from_text_failure(self, mock_request):
        type(mock_request()).status_code = PropertyMock(return_value=200)

        text = 'This is a test text.'
        target_lang = 'ja'
        project_id = self.gen_random_int()

        mock_request().json.return_value = {
            'unsupportedFiles': ['unsupported_file_name']
        }

        self.assertRaises(
            exceptions.MemsourceUnsupportedFileException,
            lambda: self.asynchronous.createJobFromText(project_id, text, target_lang)
        )
