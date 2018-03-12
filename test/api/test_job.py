from unittest.mock import patch, PropertyMock
from memsource import api, models, exceptions, constants
import requests
import os
import os.path
import uuid
import api as api_test


class TestApiJob(api_test.ApiTestCase):
    def setUp(self):
        self.url_base = "https://cloud.memsource.com/web/api/{}/job".format(
            api.Job.api_version.value)
        self.job = api.Job(None)
        self.test_file_path = '/tmp/test_file.txt'
        self.test_file_uuid1_name = 'test-file-uuid1'
        self.test_file_copy_path = '/var/tmp/{}'.format(self.test_file_uuid1_name)
        self.test_mxllif_file_path = '/tmp/test.mxliff'

        self.setCleanUpFiles((
            self.test_file_path,
            self.test_file_copy_path,
            self.test_mxllif_file_path,
        ))

        with open(self.test_file_path, 'w+') as f:
            f.write('This is test file.')

        self.create_return_value = {
            'jobParts': [{
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
        }

    @patch.object(requests.Session, 'request')
    def test_create(self, mock_request):
        type(mock_request()).status_code = PropertyMock(return_value=200)
        mock_request().json.return_value = self.create_return_value

        target_lang = 'ja'
        project_id = self.gen_random_int()

        returned_value = self.job.create(project_id, self.test_file_path, target_lang)

        # Don't use assert_called_with because files has file object. It is difficult to test.
        self.assertTrue(mock_request.called)
        (called_args, called_kwargs) = mock_request.call_args

        # hard to test
        del called_kwargs['files']
        self.assertEqual(
            (constants.HttpMethod.post.value, '{}/create'.format(self.url_base)), called_args)

        self.assertEqual({
            'data': {
                'token': self.job.token,
                'project': project_id,
                'targetLang': target_lang,
            },
            'timeout': constants.Base.timeout.value,
        }, called_kwargs)

        self.assertEqual(2, len(returned_value))
        for job_part in returned_value:
            self.assertIsInstance(job_part, models.JobPart)

    @patch.object(uuid, 'uuid1')
    @patch.object(requests.Session, 'request')
    def test_create_with_unsupported_file(self, mock_request, mock_uuid1):
        type(mock_request()).status_code = PropertyMock(return_value=200)
        mock_request().json.return_value = {
            'unsupportedFiles': ['test_file.txt'],
        }
        mock_uuid1().hex = self.test_file_uuid1_name

        self.assertRaises(
            exceptions.MemsourceUnsupportedFileException,
            lambda: self.job.create(self.gen_random_int(), self.test_file_path, 'ja')
        )

        # Check the copy exists
        self.assertTrue(os.path.isfile(self.test_file_copy_path))

    @patch.object(uuid, 'uuid1')
    @patch.object(requests.Session, 'request')
    def test_create_from_text(self, mock_request, mock_uuid1):
        type(mock_request()).status_code = PropertyMock(return_value=200)
        mock_request().json.return_value = self.create_return_value
        mock_uuid1().hex = self.test_file_uuid1_name

        target_lang = 'ja'
        project_id = self.gen_random_int()

        returned_value = self.job.createFromText(project_id, self.test_file_path, target_lang)

        # Don't use assert_called_with because files has file object. It is difficult to test.
        self.assertTrue(mock_request.called)
        (called_args, called_kwargs) = mock_request.call_args

        del called_kwargs['files']
        self.assertEqual(
            (constants.HttpMethod.post.value, '{}/create'.format(self.url_base)), called_args)

        self.assertEqual({
            'data': {
                'token': self.job.token,
                'project': project_id,
                'targetLang': target_lang,
            },
            'timeout': constants.Base.timeout.value,
        }, called_kwargs)

        self.assertEqual(2, len(returned_value))
        for job_part in returned_value:
            self.assertIsInstance(job_part, models.JobPart)

    @patch.object(uuid, 'uuid1')
    @patch.object(requests.Session, 'request')
    def test__create(self, mock_request, mock_uuid1):
        type(mock_request()).status_code = PropertyMock(return_value=200)
        file_name = 'filename.txt'
        mock_uuid1().hex = self.test_file_uuid1_name
        mock_request().json.return_value = {
            'unsupportedFiles': [file_name],
        }
        text = "This is test text."
        target_lang = 'ja'
        files = {
            'file': (file_name, text),
        }
        self.assertRaises(
            exceptions.MemsourceUnsupportedFileException,
            lambda: self.job._create(self.gen_random_int(), target_lang, files)
        )

        with open(self.test_file_copy_path) as f:
            self.assertEqual(f.read(), text)

    @patch.object(requests.Session, 'request')
    def test_list_by_project(self, mock_request):
        type(mock_request()).status_code = PropertyMock(return_value=200)

        project_id = self.gen_random_int()

        mock_request().json.return_value = [{
            'targetLang': 'de',
            'endIndex': 14,
            'project': {
                'domain': None,
                'machineTranslateSettings': None,
                'status': 'NEW',
                'name': 'project',
                'note': None,
                'dateDue': None,
                'sourceLang': 'en',
                'client': None,
                'subDomain': None,
                'id': project_id,
                'targetLangs': ['ja'],
                'workflowSteps': [],
                'dateCreated': '2013-10-31T10:15:05Z'
            },
            'isParentJobSplit': False,
            'beginIndex': 0,
            'task': 'U8llA7UOMiKGJ8Dk',
            'dateDue': None,
            'fileName': 'small.properties',
            'assignedTo': {
                'email': 'test@test.com',
                'firstName': 'linguist',
                'id': 2,
                'lastName': 'test',
                'role': 'LINGUIST',
                'userName': 'linguist',
                'active': True
            },
            'id': 1,
            'wordsCount': 331,
            'status': 'NEW',
            'dateCreated': '2013-10-31T10:15:06Z',
            'workflowLevel': 1
        }]

        returned_value = self.job.listByProject(project_id)

        for job_part in returned_value:
            self.assertIsInstance(job_part, models.JobPart)

        mock_request.assert_called_with(
            constants.HttpMethod.post.value,
            '{}/listByProject'.format(self.url_base),
            data={
                'token': self.job.token,
                'project': project_id
            },
            timeout=constants.Base.timeout.value
        )

        self.assertEqual(len(returned_value), len(mock_request().json()))

    @patch.object(requests.Session, 'request')
    def test_pre_translate(self, mock_request):
        type(mock_request()).status_code = PropertyMock(return_value=200)
        mock_request().json.return_value = {}
        job_part_ids = [self.gen_random_int()]

        returned_value = self.job.preTranslate(job_part_ids)

        mock_request.assert_called_with(
            constants.HttpMethod.post.value,
            '{}/preTranslate'.format(self.url_base),
            data={
                'token': self.job.token,
                'jobPart': job_part_ids
            },
            timeout=constants.Base.timeout.value
        )

        self.assertIsNone(returned_value)

    @patch.object(requests.Session, 'request')
    def test_get_bilingual_file(self, mock_request):
        type(mock_request()).status_code = PropertyMock(return_value=200)

        mxliff_contents = ['test mxliff content', 'second']

        mock_request().iter_content.return_value = [
            bytes(content, 'utf-8') for content in mxliff_contents]
        job_part_ids = [self.gen_random_int()]

        self.assertFalse(os.path.isfile(self.test_mxllif_file_path))
        returned_value = self.job.getBilingualFile(job_part_ids, self.test_mxllif_file_path)
        self.assertTrue(os.path.isfile(self.test_mxllif_file_path))

        self.assertIsNone(returned_value)

        with open(self.test_mxllif_file_path) as f:
            self.assertEqual(''.join(mxliff_contents), f.read())

        mock_request.assert_called_with(
            constants.HttpMethod.get.value,
            "{}/getBilingualFile".format(self.url_base),
            params={
                'token': self.job.token,
                'jobPart': job_part_ids,
            },
            timeout=constants.Base.timeout.value * 5,
            stream=True
        )

    @patch.object(requests.Session, 'request')
    def test_get_bilingual_file_xml(self, mock_request):
        type(mock_request()).status_code = PropertyMock(return_value=200)

        mxliff_contents = ['test mxliff content', 'second']

        mock_request().iter_content.return_value = [
            bytes(content, 'utf-8') for content in mxliff_contents]
        job_part_ids = [self.gen_random_int()]

        self.assertFalse(os.path.isfile(self.test_mxllif_file_path))
        returned_value = self.job.getBilingualFileXml(job_part_ids)

        self.assertEqual(''.join(mxliff_contents).encode(), returned_value)

        mock_request.assert_called_with(
            constants.HttpMethod.get.value,
            "{}/getBilingualFile".format(self.url_base),
            params={
                'token': self.job.token,
                'jobPart': job_part_ids,
            },
            timeout=constants.Base.timeout.value * 5,
            stream=True
        )

    @patch.object(requests.Session, 'request')
    def test_get_bilingual_as_mxliff_units(self, mock_request):
        type(mock_request()).status_code = PropertyMock(return_value=200)

        base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)))
        with open(os.path.join(base_dir, '..', 'lib', 'mxliff', 'test.mxliff')) as f:
            mxliff = f.read().encode('utf-8')

        mock_request().iter_content.return_value = [
            mxliff[i: i + 100] for i in range(0, len(mxliff), 100)
        ]
        job_part_ids = [self.gen_random_int()]

        returned_value = self.job.getBilingualAsMxliffUnits(job_part_ids)

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
            constants.HttpMethod.get.value,
            "{}/getBilingualFile".format(self.url_base),
            params={
                'token': self.job.token,
                'jobPart': job_part_ids,
            },
            timeout=constants.Base.timeout.value * 5,
            stream=True
        )

    @patch.object(requests.Session, 'request')
    def test_get_segments(self, mock_request):
        type(mock_request()).status_code = PropertyMock(return_value=200)

        task = 'this is test task'
        begin_index = self.gen_random_int()
        end_index = self.gen_random_int()

        mock_request().json.return_value = [[{
            'createdAt': 0,
            'source': 'Hello World.',
            # I don't know why createdBy is None, but I got it.
            'createdBy': None,
            'workflowStep': None,
            'translation': '',
            'modifiedAt': 0,
            'id': '1wHy5zBpxBsb1omg1:0',
            'modifiedBy': None
        }], [{
            'createdAt': 0,
            'source': 'Hello World second.',
            'createdBy': None,
            'workflowStep': None,
            'translation': '',
            'modifiedAt': 0,
            'id': '1wHy5zBpxBsb1omg1:1',
            'modifiedBy': None
        }]]

        returned_value = self.job.getSegments(task, begin_index, end_index)

        mock_request.assert_called_with(
            constants.HttpMethod.post.value,
            "{}/getSegments".format(self.url_base),
            data={
                'token': self.job.token,
                'task': task,
                'beginIndex': begin_index,
                'endIndex': end_index,
            },
            timeout=constants.Base.timeout.value
        )

        for segment in returned_value:
            self.assertIsInstance(segment, models.Segment)

        self.assertEqual('Hello World.', returned_value[0].source)

    @patch.object(uuid, 'uuid1')
    @patch.object(requests.Session, 'request')
    def test_upload_bilingual_file_from_xml(self, mock_request, mock_uuid1):
        type(mock_request()).status_code = PropertyMock(return_value=200)

        xml = '<xml>this is test</xml>'
        mock_uuid1().hex = self.test_file_uuid1_name

        self.job.uploadBilingualFileFromXml(xml)

        mock_request.assert_called_with(
            constants.HttpMethod.post.value,
            "{}/uploadBilingualFile".format(self.url_base),
            data={
                'token': self.job.token,
            },
            files={'bilingualFile': ('{}.mxliff'.format(self.test_file_uuid1_name), xml)},
            timeout=constants.Base.timeout.value
        )

    @patch.object(requests.Session, 'request')
    def test_get_completed_file_text(self, mock_request):
        type(mock_request()).status_code = PropertyMock(return_value=200)

        mock_request().iter_content.return_value = [b'test completed content', b'second']
        job_part_ids = [self.gen_random_int()]

        self.assertFalse(os.path.isfile(self.test_mxllif_file_path))
        returned_value = self.job.getCompletedFileText(job_part_ids)

        self.assertEqual(b'test completed contentsecond', returned_value)

        mock_request.assert_called_with(
            constants.HttpMethod.get.value,
            "{}/getCompletedFile".format(self.url_base),
            params={
                'token': self.job.token,
                'jobPart': job_part_ids,
            },
            timeout=constants.Base.timeout.value * 5,
            stream=True
        )

    @patch.object(requests.Session, 'request')
    def test_get(self, mock_request):
        type(mock_request()).status_code = PropertyMock(return_value=200)

        mock_request().json.return_value = {
            'status': 'NEW',
        }

        job_part_id = 12345

        returned_value = self.job.get(job_part_id)

        mock_request.assert_called_with(
            constants.HttpMethod.get.value,
            '{}/get'.format(self.url_base),
            params={
                'token': self.job.token,
                'jobPart': job_part_id
            },
            timeout=constants.Base.timeout.value
        )

        self.assertEqual('NEW', returned_value.status)

    @patch.object(requests.Session, 'request')
    def test_list(self, mock_request):
        type(mock_request()).status_code = PropertyMock(return_value=200)

        mock_request().json.return_value = [{
            'status': 'NEW',
        }]

        job_part_ids = [12345, 23456]

        returned_value = self.job.list(job_part_ids)

        mock_request.assert_called_with(
            constants.HttpMethod.get.value,
            '{}/list'.format(self.url_base),
            params={
                'token': self.job.token,
                'jobPart': job_part_ids
            },
            timeout=constants.Base.timeout.value
        )

        self.assertEqual('NEW', returned_value[0].status)

    @patch.object(requests.Session, 'request')
    def test_delete(self, mock_request):
        type(mock_request()).status_code = PropertyMock(return_value=200)
        mock_request().json.return_value = None

        job_part_id = self.gen_random_int()

        self.assertIsNone(self.job.delete(job_part_id))

        mock_request.assert_called_with(
            constants.HttpMethod.post.value,
            '{}/delete'.format(self.url_base),
            data={
                'token': self.job.token,
                'jobPart': job_part_id,
                'purge': False,
            },
            timeout=constants.Base.timeout.value
        )

    @patch.object(requests.Session, 'request')
    def test_setStatus(self, mock_request):
        type(mock_request()).status_code = PropertyMock(return_value=200)
        mock_request().json.return_value = None

        job_part_id = self.gen_random_int()

        self.assertIsNone(self.job.setStatus(job_part_id, constants.JobStatus.COMPLETED))

        mock_request.assert_called_with(
            constants.HttpMethod.post.value,
            '{}/setStatus'.format(self.url_base),
            data={
                'token': self.job.token,
                'jobPart': job_part_id,
                'status': constants.JobStatus.COMPLETED.value,
            },
            timeout=constants.Base.timeout.value
        )
