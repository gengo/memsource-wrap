import io
import os
import os.path
import shutil
import types
import typing
import uuid

from typing import List

import requests

from memsource import constants, exceptions, models
from memsource.lib import mxliff


__all__ = ('Auth', 'Client', 'Domain', 'Project', 'Job', 'TranslationMemory', 'Asynchronous',
           'Analysis')


class BaseApi(object):
    _session = requests.Session()

    """Inheriting classes must have the api_version attribute"""
    def __init__(self, token: {'Authentication token for using APIs': str}):
        if not hasattr(self, 'api_version'):
            # This exception is for development this library.
            raise NotImplementedError(
                'api_version is not set in {}'.format(self.__class__.__name__))

        self.token = token

    @classmethod
    def use_session(cls, session: requests.Session):
        """
        Configures the session object which is used for API invocation.

        This method is not thread-safe. It is recommended to configure only once.

        Arguments:
        session -- The session object to be used by BaseApi
        """
        cls._session = session

    def _make_url(self, *args, **kwargs):
        return kwargs.get('format', '{base}/{api_version}/{path}').format(**kwargs)

    def _get(
            self, path: str, params: dict={}, *, timeout: int=constants.Base.timeout.value
    ) -> str:
        return self._request(constants.HttpMethod.get, path, None, params, timeout)

    def _post(
            self,
            path: {'Send request to this path': str},
            params: {'Send request with this parameters': dict},
            files: {'Upload this files. Key is filename, value is file object': dict}={},
            timeout: {
                'When takes over this time in one request, raise timeout': (int, float)
            }=constants.Base.timeout.value
    ) -> {'Reponse body': dict}:
        """
        If you want to raw response, you can use _get_stream method.
        TODO: implements _post_stream.
        """
        return self._request(constants.HttpMethod.post, path, files, params, timeout)

    def _get_stream(
            self,
            path: {'Send request to this path': str},
            params: {'Send request with this parameters': dict},
            files: {'Upload this files. Key is filename, value is file object': dict}={},
            timeout: {
                'When takes over this time in one request, raise timeout': (int, float)
            }=constants.Base.timeout.value * 5
    ) -> 'Response object of Requests library':
        """
        This method returns response object of requests library,
        because XML parse or save to file or etc are different will call different method.

        We can switch response by value of stream, but it is not good, I think,
        because type of returning value is only one is easy to use, easy to understand.
        """
        return self._request_stream(constants.HttpMethod.get, path, files, params, timeout)

    def _pre_request(
            self,
            path: {'{api_name}/{method}': str},
            params: {'Insert token in this dict.': dict}
    ) -> (str, dict):
        """
        Create request url and extend param with token for authentication.
        """
        url = self._make_url(
            base=constants.Base.url.value,
            api_version=self.api_version.value,
            path=path
        )
        params['token'] = self.token

        self.last_url = url
        self.last_params = params

        return (url, params, )

    def _request_stream(
            self,
            http_method: {constants.HttpMethod, 'Use this http method'},
            path: {'Send request with this parameters': dict},
            files: {'Upload this files. Key is filename, value is file object': dict},
            params: {'Send request with this parameters': dict},
            timeout: {'When takes over this time in one request, raise timeout': (int, float)}
    ) -> requests.models.Response:
        (url, params_with_token) = self._pre_request(path, params)

        return self._get_response(
            http_method, url, params=params_with_token, files=files, timeout=timeout, stream=True)

    def _get_response(
            self,
            http_method: {'Use this http method': constants.HttpMethod},
            url: {'access to this url': str},
            **kwargs
    ) -> requests.models.Response:
        try:
            response = self._session.request(http_method.value, url, **kwargs)
        except requests.exceptions.Timeout:
            raise exceptions.MemsourceApiException(None, {
                'errorCode': 'Internal',
                'errorDescription': 'The request timed out, timeout is {}'.format(
                    kwargs['timeout'] if 'timeout' in kwargs else 'default'),
            }, self.last_url, self.last_params)
        except requests.exceptions.ConnectionError:
            raise exceptions.MemsourceApiException(None, {
                'errorCode': 'Internal',
                'errorDescription': 'Could not connect',
            }, self.last_url, self.last_params)

        if BaseApi.is_success(response.status_code):
            return response

        # Usually Memsource returns JSON even if the response is error. But they returns
        # "Too many requests.", It's not JSON.
        try:
            result_json = response.json()
        except ValueError:
            result_json = {
                'errorCode': 'Non JSON response',
                'errorDescription': 'Raw response {}'.format(response.text),
            }
        raise exceptions.MemsourceApiException(
            response.status_code, result_json, self.last_url, self.last_params)

    def _request(
            self,
            http_method: {constants.HttpMethod, 'Use this http method'},
            path: {'Send request with this parameters': dict},
            files: {'Upload this files. Key is filename, value is file object': dict},
            params: {'Send request with this parameters': dict},
            timeout: {'When takes over this time in one request, raise timeout': (int, float)}
    ) -> {'Parsed esponse body as JSON': dict}:
        (url, params_with_token) = self._pre_request(path, params)

        # If it is successful, returns response json
        return self._get_response(
            http_method, url, params=params_with_token, files=files, timeout=timeout).json()

    @staticmethod
    def is_success(status_code: {int}):
        # if status_code is float type, we will get unexpected result.
        # but I think it is not big deal.
        return 200 <= status_code < 300


class Auth(BaseApi):
    """
    You can see the document http://wiki.memsource.com/wiki/Authentication_API_v3
    """
    api_version = constants.ApiVersion.v3

    def __init__(self, token=None):
        super(Auth, self).__init__(token)

    def login(self, user_name, password):
        r = self._post('auth/login', {
            'userName': user_name,
            'password': password,
        })

        r['user'] = models.User(r.pop('user'))

        return models.Authentication(r)


class Client(BaseApi):
    """
    You can see the document http://wiki.memsource.com/wiki/Client_API_v2
    """
    api_version = constants.ApiVersion.v2

    def create(self, name):
        return self._post('client/create', {
            'name': name,
        })['id']

    def get(self, client):
        return models.Client(self._post('client/get', {
            'client': client,
        }))

    def list(self, page=0):
        return [
            models.Client(client) for client in self._post('client/list', {
                'page': page,
            })
        ]


class Domain(BaseApi):
    """
    You can see the document http://wiki.memsource.com/wiki/Domain_API_v2
    """
    api_version = constants.ApiVersion.v2

    def create(self, name):
        return self._post('domain/create', {
            'name': name,
        })

    def get(self, domain):
        return models.Domain(self._post('domain/get', {
            'domain': domain,
        }))

    def list(self, page=0):
        return [
            models.Domain(domain) for domain in self._post('domain/list', {
                'page': page,
            })
        ]


class Project(BaseApi):
    """
    You can see the document http://wiki.memsource.com/wiki/Project_API_v3
    """
    api_version = constants.ApiVersion.v3

    def create(
            self,
            name: {'project name': str},
            source_lang: str,
            target_langs: {'You can use list for multi target_lang.': (list, tuple, str)},
            client: int=None,
            domain: int=None
    ) -> {'project id', int}:
        """
        Create new project.
        """
        return self._post('project/create', {
            'token': self.token,
            'name': name,
            'sourceLang': source_lang,
            'targetLang': target_langs,
            'client': client,
            'domain': domain,
        })['id']

    def list(self):
        return [models.Project(project) for project in self._post('project/list', {})]

    def getTransMemories(self, project_id):
        return [
            models.TranslationMemory(translation_memory)
            for translation_memory in self._post('project/getTransMemories', {
                'project': project_id
            })
        ]

    def setTransMemories(self, project_id, read_trans_memory_ids=[], write_trans_memory_id=None,
                         penalties=[], target_lang=None):
        """
        You can set translation memory to a project.

        :param project_id :set translation memory to this id of project :int
        :param read_trans_memory_ids :Read these translation memories :[int]
        :param write_trans_memory_id :Write to this translation memory.
        write translation memory must be included in the read translation memories, too :int
        :param penalties :a list of penalties for each read translation memory :[double]
        :param target_lang :set translation memories only for the specific project target language
        :str

        :return :None
        """
        params = {
            'project': project_id,
        }

        # Check the parameters. If the parameter is None or empty list, we ignore it.
        if len(read_trans_memory_ids) != 0:
            params['readTransMemory'] = read_trans_memory_ids

        if write_trans_memory_id is not None:
            params['writeTransMemory'] = write_trans_memory_id

        if len(penalties) != 0:
            params['penalty'] = penalties

        if target_lang is not None:
            params['targetLang'] = target_lang

        # This end-point return nothing.
        self._post('project/setTransMemories', params)

        return None


class Job(BaseApi):
    """
    You can see the document http://wiki.memsource.com/wiki/Job_API_v7
    """
    api_version = constants.ApiVersion.v7

    def create(self, project_id: int, file_path: str, target_langs):
        """
        return: [JobPart]

        If returning JSON has `unsupportedFiles`,
        this method raise MemsourceUnsupportedFileException
        """
        with open(file_path, 'r') as f:
            return self._create(project_id, target_langs, {
                'file': f,
            })

    def createFromText(self, project_id: int, text: str, target_langs, file_name=None):
        """
        You can create a job without a file.
        See: Job.create

        Create file name by uuid1() when file_name parameter is None.
        """
        return self._create(project_id, target_langs, {
            'file': ('{}.txt'.format(uuid.uuid1().hex) if file_name is None else file_name, text),
        })

    def _create(self, project_id: int, target_langs, files: dict):
        result = self._post('job/create', {
            'project': project_id,
            'targetLang': target_langs,
        }, files)

        # unsupported file count is 0 mean success.
        unsupported_files = result.get('unsupportedFiles', [])
        if len(unsupported_files) == 0:
            return [models.JobPart(job_parts) for job_parts in result['jobParts']]

        _, value = files.popitem()
        if isinstance(value, tuple):
            # If value is tuple type, this function called from createFromText.
            # We need to create temporary file for to raise exception.
            file_name, text = value
            file_path = os.path.join('/', 'tmp', file_name)
            with open(file_path, 'w+') as f:
                f.write(text)
        else:
            file_path = value.name

        raise exceptions.MemsourceUnsupportedFileException(
            unsupported_files,
            file_path,
            self.last_url,
            self.last_params
        )

    def listByProject(self, project_id):
        # TODO: wrap inner project
        return [models.JobPart(job_part) for job_part in self._post('job/listByProject', {
            'project': project_id
        })]

    def preTranslate(self, job_parts):
        """
        This API takes long time. you might timed out. You can use Asynchronous.preTranslate
        """
        self._post('job/preTranslate', {'jobPart': job_parts})

    def _getBilingualStream(
            self,
            job_parts: {'Lsit of job_part id': (list, tuple)},
    ) -> types.GeneratorType:
        """
        Common process of bilingualFile.
        """
        return self._get_stream('job/getBilingualFile', {
            'jobPart': job_parts,
        }).iter_content(1024)

    def getBilingualFileXml(self, job_parts: {'Lsit of job_part id': (list, tuple)}) -> bytes:
        buffer = io.BytesIO()
        [buffer.write(chunk) for chunk in self._getBilingualStream(job_parts)]

        return buffer.getvalue()

    def getBilingualFile(
            self,
            job_parts: {'Lsit of job_part id': (list, tuple)},
            dest_file_path: {'Save XML to this file path': str}
    ) -> None:
        """
        Get bilingual file and save it as file.
        """
        with open(dest_file_path, 'wb') as f:
            [f.write(chunk) for chunk in self._getBilingualStream(job_parts)]

    def getCompletedFileText(self, job_parts: list) -> bytes:
        def getCompletedFileStream() -> types.GeneratorType:
            return self._get_stream('job/getCompletedFile', {
                'jobPart': job_parts,
            }).iter_content(1024)

        buffer = io.BytesIO()
        [buffer.write(chunk) for chunk in getCompletedFileStream()]

        return buffer.getvalue()

    def getBilingualAsMxliffUnits(
            self, job_parts: {'Lsit of job_part id': (list, tuple)},
    ) -> models.MxliffUnit:
        """
        Get bilingual file and parse it as [models.MxliffUnit]
        """
        return mxliff.MxliffParser().parse(self.getBilingualFileXml(job_parts))

    def getSegments(self, task, begin_index, end_index):
        """
        TODO: If first argument is JobPart type,
        get task, begin_index and end_index from first argument.

        NOTE: I don't know why this endpoint returns list of list.
        It seems always one item in outer list.

        return [models.Segment]
        """
        return [
            models.Segment(segment[0]) for segment in self._post('job/getSegments', {
                'task': task,
                'beginIndex': begin_index,
                'endIndex': end_index,
            })
        ]

    def uploadBilingualFileFromXml(self, xml: str) -> None:
        self._post('job/uploadBilingualFile', {}, {
            'bilingualFile': ('{}.mxliff'.format(uuid.uuid1().hex), xml),
        })

    def get(self, job_part_id: int) -> models.Job:
        """Get the job data.

        :param job_part_ids: ID of job_part for the job.
        :return: The got job.
        """
        response = self._get('job/get', {
            'jobPart': job_part_id,
        })

        return models.Job(response)

    def list(self, job_part_ids: typing.List[int]) -> typing.List[models.Job]:
        """Get the jobs data.

        :param job_part_ids: IDs of job_part for the jobs.
        :return: The got jobs.
        """
        response = self._get('job/list', {
            'jobPart': job_part_ids,
        })

        return [models.Job(i) for i in response]

    def delete(self, job_part_id: int, purge: bool=False) -> None:
        self._post('job/delete', {
            'jobPart': job_part_id,
            'purge': purge
        })


class TranslationMemory(BaseApi):
    """
    You can see the document http://wiki.memsource.com/wiki/Translation_Memory_API_v4
    """
    api_version = constants.ApiVersion.v4

    def create(self, name, source_lang, target_langs):
        return self._post('transMemory/create', {
            'name': name,
            'sourceLang': source_lang,
            'targetLang': target_langs,
        })['id']

    def list(self):
        return [
            models.TranslationMemory(translation_memory)
            for translation_memory in self._post('transMemory/list', {})
        ]

    def _upload(self, translation_memory_id: int, files: dict) -> int:
        # Casting because acceptedSegmentsCount seems always number, but it string type.
        return int(self._post('transMemory/import', {
            'transMemory': translation_memory_id,
        }, files)['acceptedSegmentsCount'])

    def upload(self, translation_memory_id: int, file_path: str) -> int:
        """
        This method calls import endpoint, but method name is `upload`,
        because `import` is keyword of Python. We cannot use `import` as method name.

        return int accepted segments count
        """
        with open(file_path, 'rb') as f:
            return self._upload(translation_memory_id, {
                'file': f,
            })

    def uploadFromText(self, translation_memory_id: int, tmx: str) -> int:
        return self._upload(translation_memory_id, {
            'file': ('{}.tmx'.format(uuid.uuid1().hex), tmx),
        })

    def searchSegmentByTask(
            self,
            task: str,
            segment: str,
            *,
            next_segment: str=None,
            previous_segment: str=None,
            score_threshold: float=0.6,
            **kwargs
    ) -> typing.List[models.SegmentSearchResult]:
        """Get translation matches.

        :param task: task_id
        :param segment: Search by this segment
        :param next_segment: Effect for 101% match
        :param previous_segment: Effect for 101% match
        :param score_threshold: return only high score than this value
        :param kwargs: See the Memsource official document
        http://wiki.memsource.com/wiki/Translation_Memory_API_v4#Search_Segment_By_Task

        :return: list of models.SegmentSearchResult
        """
        parameters = dict(kwargs, task=task, segment=segment, scoreThreshold=score_threshold)
        if next_segment is not None:
            parameters['nextSegment'] = next_segment

        if previous_segment is not None:
            parameters['previousSegment'] = previous_segment

        return [
            models.SegmentSearchResult(item)
            for item in self._post('transMemory/searchSegmentByTask', parameters)
        ]

    def export(
            self,
            translation_memory_id: {'translation memory id for target of exporitng data': int},
            target_langs: {'You can use list for multi target_lang.': (list, tuple, str)},
            file_path: {'Save exported data to this file path': str},
            file_format: {'Export data file format': str}='TMX',
            chunk_size: {'byte size of chunk for response data': int}=1024,
    ) -> None:
        """
        Get translation memory exported data
        """
        params = {
            'transMemory': translation_memory_id,
            'format': file_format,
            'targetLang': target_langs,
        }
        with open(file_path, 'wb') as f:
            [f.write(chunk) for chunk in
                self._get_stream('transMemory/export', params).iter_content(chunk_size)]

    def insert(self, translation_memory_id, target_lang, source_segment, target_segment,
               previous_source_segment=None, next_source_segment=None):
        """
        :param translation_memory_id :Insert new translation to this translation memory :int
        :param target_lang :target_segment is this language :str
        :param source_segment :source text of the translated text :str
        :param target_segment :translated text :str
        :previous_source_segment :optional This is for 101% match :str
        :next_source_segment :optional This is for 101% match :str

        :return :None
        """
        params = {
            'transMemory': translation_memory_id,
            'targetLang': target_lang,
            'sourceSegment': source_segment,
            'targetSegment': target_segment,
        }

        # If optional parameter is passed, include those into post parameter
        if previous_source_segment is not None:
            params['previousSourceSegment'] = previous_source_segment

        if next_source_segment is not None:
            params['nextSourceSegment'] = next_source_segment

        self._post('transMemory/insert', params)

    def deleteSourceAndTranslations(
            self, translation_memory_id: int, segment_ids: List[str]) -> None:
        """Delete segments from a translation memory.

        :param translation_memory_id: Delete the segments from this translation
        memory.
        :param segment_ids: Delete these segments from the translation memory.
        You cannot pass more than 1000 ids one time.
        """
        assert 1000 > len(segment_ids), "You cannot pass more than 1000 ids one time."
        self._post('transMemory/deleteSourceAndTranslations', {
            'transMemory': translation_memory_id,
            'segmentId': segment_ids
        })


class Asynchronous(BaseApi):
    """
    You can see the documents:
    * http://wiki.memsource.com/wiki/Asynchronous_API_v2
    * http://wiki.memsource.com/wiki/Job_Asynchronous_API_v2
    * http://wiki.memsource.com/wiki/Analysis_Asynchronous_API_v2
    """
    api_version = constants.ApiVersion.v2

    def _make_url(self, *args, **kwargs):
        """
        Because only this endpoint has different format with other endpoints.
        like these:
        * https://cloud.memsource.com/web/api/async/v2/job/preTranslate
        * https://cloud.memsource.com/web/api/v2/async/getAsyncRequest

        This is example of other endpoints
        * https://cloud.memsource.com/web/api/v3/project/create
        """
        if kwargs['path'] != 'async/getAsyncRequest':
            kwargs['format'] = '{base}/async/{api_version}/{path}'

        return super(Asynchronous, self)._make_url(**kwargs)

    def preTranslate(self, job_parts, translation_memory_threshold=0.7, callback_url=None):
        """
        return models.AsynchronousRequest
        """
        return models.AsynchronousRequest(self._post('job/preTranslate', {
            'jobPart': job_parts,
            'translationMemoryThreshold': translation_memory_threshold,
            'callbackUrl': callback_url,
        })['asyncRequest'])

    def createAnalysis(
            self, job_parts: int, callback_url: str=None, **kwargs) -> models.AsynchronousRequest:
        """Create analysis asynchronously.

        :param job_parts: Make analysis for these job_part ids.
        :param callback_url: Memsource will send a callback when they finish analyzing.
        :param kwags: Another non required parameters, you can pass.
        """
        res = self._post(
            'analyse/create', dict(kwargs, jobPart=job_parts, callbackUrl=callback_url))

        return models.AsynchronousRequest(res['asyncRequest']), models.Analysis(res['analyse'])

    def getAsyncRequest(self, asynchronous_request_id):
        asyncRequest = self._post('async/getAsyncRequest', {
            'asyncRequest': asynchronous_request_id,
        })
        asyncRequest['asyncResponse'] = models.AsynchronousResponse(asyncRequest['asyncResponse'])

        return models.AsynchronousRequest(asyncRequest)

    def createJobFromText(self, project_id: int, text: str, target_langs, file_name=None,
                          extension='.txt', *, callback_url=None,
                          **kwargs: dict) -> (models.AsynchronousResponse, list):
        """
        See: Job.create

        Create file name by uuid1() when file_name parameter is None.
        """

        file_path = os.path.join('/', 'tmp', 'memsource-wrap', uuid.uuid1().hex,
                                 file_name or '{}{}'.format(uuid.uuid1().hex, extension))

        # make tmp file for upload the text. This tmp file and parent directory will delete after
        # uploading even if uploading failed.
        file_parent = os.path.dirname(file_path)
        os.makedirs(file_parent)
        with io.open(file_path, 'w', encoding='utf-8') as f:
            f.write(text)

        try:
            return self.createJob(
                project_id, file_path, target_langs, callback_url=callback_url, **kwargs)
        finally:
            shutil.rmtree(file_parent)

    def createJob(self, project_id: int, file_path: str, target_langs: (str, list), *,
                  callback_url=None, **kwargs: dict) -> (models.AsynchronousResponse, list):
        """\
        Create new Job on Memsource asynchronously.

        @param project_id Project ID of target project.
        @param file_path Absolute path of translation target file.
        @param target_langs Translation target languages.
        @param callback_url Memsource will hit this url when finished to create the job.
        @param kwargs See Memsource official document \
            http://wiki.memsource.com/wiki/Job_Asynchronous_API_v2

        @return models.AsynchronousResponse and list of models.JobPart
        """
        with open(file_path, 'rb') as f:
            files = {
                'file': (os.path.basename(file_path), f),
            }

            result = self._post('job/create', dict(kwargs, **{
                'project': project_id,
                'targetLang': target_langs,
                'callbackUrl': callback_url,
            }), files)

        # unsupported file count is 0 mean success.
        unsupported_files = result.get('unsupportedFiles', [])
        if len(unsupported_files) == 0:
            return (models.AsynchronousRequest(result['asyncRequest']),
                    [models.JobPart(job_parts) for job_parts in result['jobParts']])

        raise exceptions.MemsourceUnsupportedFileException(
            unsupported_files,
            file_path,
            self.last_url,
            self.last_params
        )


class Analysis(BaseApi):
    """
    You can see the document http://wiki.memsource.com/wiki/Analysis_API_v2
    """
    api_version = constants.ApiVersion.v2

    def get(self, analysis_id: {'Get analysis of this id', int}) -> models.Analysis:
        return models.Analysis(self._get('analyse/get', {
            'analyse': analysis_id,
        }))

    def create(self, job_part_ids: typing.List[int]) -> models.Analysis:
        return models.Analysis(self._post('analyse/create', {
            'jobPart': job_part_ids,
        }))

    def delete(self, analysis_id: int, purge: bool=False) -> None:
        self._post('analyse/delete', {
            'analyse': analysis_id,
            'purge': purge,
        })
