import io
import os
import os.path
import shutil
import types
import uuid

from typing import (
    Iterator,
    List,
    Tuple,
    Union,
)

import requests

from memsource import constants, exceptions, models
from memsource.lib import mxliff


__all__ = ['Auth', 'Client', 'Domain', 'Project', 'Job', 'TranslationMemory', 'Asynchronous',
           'Language', 'Analysis']


class BaseApi:
    _session = requests.Session()

    def __init__(self, token: str) -> None:
        """Inheriting classes must have the api_version attribute

        :param token: Authentication token for using APIs
        """
        if not hasattr(self, 'api_version'):
            # This exception is for development this library.
            raise NotImplementedError(
                'api_version is not set in {}'.format(self.__class__.__name__))

        self.token = token

    @classmethod
    def use_session(cls, session: requests.Session) -> None:
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
        return self._request(constants.HttpMethod.get, path,
                             files=None, params=params, data=None, timeout=timeout)

    def _post(self, path: str, data: dict=None, files: dict=None,
              timeout: Union[int, float]=constants.Base.timeout.value) -> dict:
        """Send a post request.

        If you want to raw response, you can use _get_stream method.

        :param path: Send request to this path
        :param data: Send request with this parameters
        :param files: Upload this files. Key is filename, value is file object
        :param timeout: When takes over this time in one request, raise timeout
        :return: parsed response body as JSON
        """
        return self._request(constants.HttpMethod.post, path,
                             files=files, params=None, data=data, timeout=timeout)

    def _get_stream(
            self, path: str, params: dict, files: dict=None,
            timeout: Union[int, float]=constants.Base.timeout.value * 5
    ) -> requests.models.Response:
        """
        This method returns response object of requests library,
        because XML parse or save to file or etc are different will call different method.

        We can switch response by value of stream, but it is not good, I think,
        because type of returning value is only one is easy to use, easy to understand.

        :param path: Send request to this path
        :param params: Send request with this parameters
        :param files: Upload this files. Key is filename, value is file object
        :param timeout: When takes over this time in one request, raise timeout
        :return: Response object of Requests library
        """
        return self._request_stream(constants.HttpMethod.get, path, files, params, None, timeout)

    def _pre_request(self, path: str, params: dict) -> Tuple[str, dict]:
        """Create request url and extend param with token for authentication.

        :param path: API path with this format ({api_name}/{method})
        :param params: Insert token in this dict

        :return: Tuple of URL and params with token.
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
            self, http_method: constants.HttpMethod, path: dict, files: dict,
            params: dict, data: dict, timeout: Tuple[int, float]
    ) -> requests.models.Response:
        """Send a stream request.

        :param http_method: Use this http method
        :param path: Send request with this parameters
        :param files: Upload this files. Key is filename, value is file object
        :param params: Send request with this parameters
        :param data: Send request with this data
        :param timeout: When takes over this time in one request, raise timeout
        :return: response of request module
        """
        if params:
            (url, params) = self._pre_request(path, params)
        else:
            (url, data) = self._pre_request(path, data)

        arguments = {
            key: value for key, value in [
                ('files', files), ('params', params), ('data', data)
            ] if value is not None
        }

        return self._get_response(http_method, url, timeout=timeout, stream=True, **arguments)

    def _get_response(
            self, http_method: constants.HttpMethod, url: str, **kwargs
    ) -> requests.models.Response:
        """Request with error handling.

        :param http_method: Use this http method
        :param url: access to this url
        :param kwargs: optional parameters
        :return: response of request module
        """
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

    def _request(self, http_method: constants.HttpMethod, path: str, files: dict, params: dict,
                 data: dict, timeout: Tuple[int, float]) -> dict:
        """Send a http request.

        :param http_method: Use this http method
        :param path: Send request to this path
        :param data: Send request with this parameters
        :param files: Upload this files. Key is filename, value is file object
        :param timeout: When takes over this time in one request, raise timeout
        :return: parsed response body as JSON
        """
        if params:
            (url, params) = self._pre_request(path, params)
        else:
            (url, data) = self._pre_request(path, data)

        arguments = {
            key: value for key, value in [
                ('files', files), ('params', params), ('data', data)
            ] if value is not None
        }

        # If it is successful, returns response json
        return self._get_response(http_method, url, timeout=timeout, **arguments).json()

    @staticmethod
    def is_success(status_code: {int}):
        # if status_code is float type, we will get unexpected result.
        # but I think it is not big deal.
        return 200 <= status_code < 300


class Auth(BaseApi):
    """You can see the document http://wiki.memsource.com/wiki/Authentication_API_v3
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
    """You can see the document http://wiki.memsource.com/wiki/Client_API_v2
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
    """You can see the document http://wiki.memsource.com/wiki/Domain_API_v2
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


class Language(BaseApi):
    """You can see the document https://wiki.memsource.com/wiki/Language_API_v2
    """

    api_version = constants.ApiVersion.v2

    def listSupportedLangs(self):
        return [
            models.Language(language)
            for language in self._post('language/listSupportedLangs', {})
        ]


class Project(BaseApi):
    """You can see the document http://wiki.memsource.com/wiki/Project_API_v3
    """
    api_version = constants.ApiVersion.v3

    def create(self, name: str, source_lang: str, target_langs: Union[List[str], Tuple[str], str],
               client: int=None, domain: int=None) -> int:
        """Create new project.

        :param name: project name
        :param source_lang:
        :param target_langs: You can use list for multi target_lang.
        :param client:
        :param domain:
        :return: created project id
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

    def setTransMemories(self, project_id, read_trans_memory_ids: List[int]=[],
                         write_trans_memory_id: int=None, penalties: List[float]=[],
                         target_lang: str=None) -> None:
        """You can set translation memory to a project.

        :param project_id: set translation memory to this id of project
        :param read_trans_memory_ids: Read these translation memories
        :param write_trans_memory_id: Write to this translation memory.
        write translation memory must be included in the read translation memories, too
        :param penalties: a list of penalties for each read translation memory
        :param target_lang: set translation memories only for the specific project target language
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


class Job(BaseApi):
    """You can see the document http://wiki.memsource.com/wiki/Job_API_v7
    """

    api_version = constants.ApiVersion.v7

    def create(
            self, project_id: int, file_path: str, target_langs: List[str]
    ) -> List[models.JobPart]:
        """Create a job.

        If returning JSON has `unsupportedFiles`,
        this method raise MemsourceUnsupportedFileException

        :param project_id: New job will be in this project.
        :param file_path: Source file of job.
        :param target_langs: List of translation target languages.
        :return: List of models.JobPart
        """
        with open(file_path, 'r') as f:
            return self._create(project_id, target_langs, {
                'file': f,
            })

    def createFromText(
            self, project_id: int, text: str, target_langs: List[str], file_name: str=None
    ) -> List[models.JobPart]:
        """You can create a job without a file.

        See: Job.create
        If returning JSON has `unsupportedFiles`,
        this method raise MemsourceUnsupportedFileException

        :param project_id: New job will be in this project.
        :param text: Source text of job.
        :param target_langs: List of translation target languages.
        :param file_name: Create file name by uuid1() when file_name parameter is None.
        :return: List of models.JobPart
        """
        return self._create(project_id, target_langs, {
            'file': ('{}.txt'.format(uuid.uuid1().hex) if file_name is None else file_name, text),
        })

    def _create(
            self, project_id: int, target_langs: List[str], files: dict) -> List[models.JobPart]:
        """Common process of creating job.

        If returning JSON has `unsupportedFiles`,
        this method raise MemsourceUnsupportedFileException

        :param project_id: New job will be in this project.
        :param file_path: Source file of job.
        :param target_langs: List of translation target languages.
        :return: List of models.JobPart
        """
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

    def listByProject(self, project_id: int) -> List[models.JobPart]:
        return [models.JobPart(job_part) for job_part in self._post('job/listByProject', {
            'project': project_id
        })]

    def preTranslate(self, job_parts: List[int]) -> None:
        """Request pre translate.

        This API takes long time. you might timed out. You can use Asynchronous.preTranslate.

        :param job_parts: List of job_part id.
        """
        self._post('job/preTranslate', {'jobPart': job_parts})

    def _getBilingualStream(self, job_parts: List[int]) -> Iterator[bytes]:
        """Common process of bilingualFile.

        :param job_parts: List of job_part id.
        :return: Downloaded bilingual file with iterator.
        """
        return self._get_stream('job/getBilingualFile', {
            'jobPart': job_parts,
        }).iter_content(1024)

    def getBilingualFileXml(self, job_parts: List[int]) -> bytes:
        """Download bilingual file and return it as bytes.

        This method might use huge memory.

        :param job_parts: List of job_part id.
        :return: Downloaded bilingual file.
        """
        buffer = io.BytesIO()
        [buffer.write(chunk) for chunk in self._getBilingualStream(job_parts)]

        return buffer.getvalue()

    def getBilingualFile(self, job_parts: List[int], dest_file_path: str) -> None:
        """Download bilingual file and save it as a file.

        :param job_parts: List of job_part id.
        :param dest_file_path: Save bilingual file to there.
        """
        with open(dest_file_path, 'wb') as f:
            [f.write(chunk) for chunk in self._getBilingualStream(job_parts)]

    def getCompletedFileText(self, job_parts: List[int]) -> bytes:
        """Download completed file and return it.

        :param job_parts: List of job_part id.
        """
        def getCompletedFileStream() -> types.GeneratorType:
            return self._get_stream('job/getCompletedFile', {
                'jobPart': job_parts,
            }).iter_content(1024)

        buffer = io.BytesIO()
        [buffer.write(chunk) for chunk in getCompletedFileStream()]

        return buffer.getvalue()

    def getBilingualAsMxliffUnits(self, job_parts: List[str]) -> models.MxliffUnit:
        """Download bilingual file and parse it as [models.MxliffUnit]

        :param job_parts: List of job_part id.
        :returns: MxliffUnit
        """
        return mxliff.MxliffParser().parse(self.getBilingualFileXml(job_parts))

    def getSegments(self, task: str, begin_index: int, end_index: int) -> List[models.Segment]:
        """Call get segments API.

        NOTE: I don't know why this endpoint returns list of list.
        It seems always one item in outer list.

        :param task:
        :param begin_index:
        :param end_index:
        :return: List of models.Segment
        """
        return [
            models.Segment(segment[0]) for segment in self._post('job/getSegments', {
                'task': task,
                'beginIndex': begin_index,
                'endIndex': end_index,
            })
        ]

    def uploadBilingualFileFromXml(self, xml: str) -> None:
        """Call uploadBilingualFile API.

        :param xml: Upload this text.
        """
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

    def list(self, job_part_ids: List[int]) -> List[models.Job]:
        """Get the jobs data.

        :param job_part_ids: IDs of job_part for the jobs.
        :return: The got jobs.
        """
        response = self._get('job/list', {
            'jobPart': job_part_ids,
        })

        return [models.Job(i) for i in response]

    def delete(self, job_part_id: int, purge: bool=False) -> None:
        """Delete a job

        :param job_part_id: id of job you want to delete.
        :param purge:
        """
        self._post('job/delete', {
            'jobPart': job_part_id,
            'purge': purge
        })


class TranslationMemory(BaseApi):
    """You can see the document http://wiki.memsource.com/wiki/Translation_Memory_API_v4
    """
    api_version = constants.ApiVersion.v4

    def create(self, name: str, source_lang: str, target_langs: Union[List[str], str]) -> int:
        """Create a translation memory.

        :param name: Name of new translation memory.
        :param source_lang: Soruce language of new translation memory.
        :param target_langs: Target languages of new translation memory.
        :return: ID of created translation memory.
        """
        return self._post('transMemory/create', {
            'name': name,
            'sourceLang': source_lang,
            'targetLang': target_langs,
        })['id']

    def list(self, page: int=0) -> List[models.TranslationMemory]:
        """List translation memories.

        :page: index of pager.
        :return: List of translation memory.
        """
        return [
            models.TranslationMemory(translation_memory)
            for translation_memory in self._post('transMemory/list', {'page': page})
        ]

    def _upload(self, translation_memory_id: int, files: dict) -> int:
        # Casting because acceptedSegmentsCount seems always number, but it string type.
        return int(self._post('transMemory/import', {
            'transMemory': translation_memory_id,
        }, files)['acceptedSegmentsCount'])

    def upload(self, translation_memory_id: int, file_path: str) -> int:
        """Call **import** API.

        This method calls import endpoint, but method name is `upload`,
        because `import` is keyword of Python. We cannot use `import` as method name.

        :param translation_memory_id: Uploaded translation units are into here.
        :param file_path: Import this file into the translation memory.
        :return: accepted segments count.
        """
        with open(file_path, 'rb') as f:
            return self._upload(translation_memory_id, {
                'file': f,
            })

    def uploadFromText(self, translation_memory_id: int, tmx: str) -> int:
        """Import tmx text into a translation memory.

        :param translation_memory_id: Uploaded translation units are into here.
        :param tmx: Import this tmx text into the translation memory.
        :return: accepted segments count.
        """
        return self._upload(translation_memory_id, {
            'file': ('{}.tmx'.format(uuid.uuid1().hex), tmx),
        })

    def searchSegmentByTask(
            self, task: str, segment: str, *, next_segment: str=None,
            previous_segment: str=None, score_threshold: float=0.6, **kwargs
    ) -> List[models.SegmentSearchResult]:
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

    def search(
            self, translation_memory_id: int, query: str,
            source_lang: str, target_langs: Union[List[str], str],
            next_segment: str=None, previous_segment: str=None, **kwargs
    ) -> List[models.SegmentSearchResult]:
        """Get translation matches.

        :param translation_memory_id: Search translation units are into here.
        :param query: Search query
        :param source_lang: Soruce language of translation memory.
        :param target_langs: Target languages of translation memory.
        :param next_segment: Effect for 101% match
        :param previous_segment: Effect for 101% match
        :param kwargs: See the Memsource official document
        https://wiki.memsource.com/wiki/Translation_Memory_API_v4#Search

        :return: list of models.SegmentSearchResult
        """
        parameters = dict(
            kwargs, transMemory=translation_memory_id,
            query='"{}"'.format(query), sourceLang=source_lang)

        if target_langs is not None:
            parameters['targetLang'] = target_langs

        if next_segment is not None:
            parameters['nextSegment'] = next_segment

        if previous_segment is not None:
            parameters['previousSegment'] = previous_segment

        return [
            models.SegmentSearchResult(item)
            for item in self._post('transMemory/search', parameters)
        ]

    def export(self, translation_memory_id: int, target_langs: Union[List[str], str],
               file_path: str, file_format: str='TMX', chunk_size: int=1024) -> None:
        """Get translation memory exported data

        :param translation_memory_id: translation memory id for target of exporitng data.
        :param target_langs: Export target languages.
        :param file_path: Save exported data to this file path.
        :param file_format: Export data file format. Default is TMX.
        :param chunk_size: byte size of chunk for response data.
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
               previous_source_segment=None, next_source_segment=None) -> None:
        """
        :param translation_memory_id :Insert new translation to this translation memory :int
        :param target_lang :target_segment is this language :str
        :param source_segment :source text of the translated text :str
        :param target_segment :translated text :str
        :previous_source_segment :optional This is for 101% match :str
        :next_source_segment :optional This is for 101% match :str
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
        assert 1000 >= len(segment_ids), "You cannot pass more than 1000 ids one time."
        self._post('transMemory/deleteSourceAndTranslations', {
            'transMemory': translation_memory_id,
            'segmentId': segment_ids
        })


class Asynchronous(BaseApi):
    """You can see the documents:
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

    def preTranslate(self, job_parts: List[int], translation_memory_threshold: float=0.7,
                     callback_url: str=None) -> models.AsynchronousRequest:
        """Call async pre translate API.

        :param job_parts: List of job_part id.
        :param translation_memory_threshold: If matching score is higher than this, it filled.
        :return: models.AsynchronousRequest
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
        :return: models.AsynchronousRequest
        """
        res = self._post(
            'analyse/create', dict(kwargs, jobPart=job_parts, callbackUrl=callback_url))

        return models.AsynchronousRequest(res['asyncRequest']), models.Analysis(res['analyse'])

    def getAsyncRequest(self, asynchronous_request_id: int) -> models.AsynchronousRequest:
        asyncRequest = self._post('async/getAsyncRequest', {
            'asyncRequest': asynchronous_request_id,
        })
        asyncRequest['asyncResponse'] = models.AsynchronousResponse(asyncRequest['asyncResponse'])

        return models.AsynchronousRequest(asyncRequest)

    def createJobFromText(self, project_id: int, text: str, target_langs, file_name=None,
                          extension='.txt', *, callback_url=None,
                          **kwargs: dict) -> (models.AsynchronousResponse, list):
        """Call async job create API.

        See: Job.create
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

    def createJob(
            self, project_id: int, file_path: str, target_langs: (str, list), *, callback_url=None,
            **kwargs: dict
    ) -> Tuple[models.AsynchronousResponse, List[models.JobPart]]:
        """Create new Job on Memsource asynchronously.

        :param project_id: Project ID of target project.
        :param file_path: Absolute path of translation target file.
        :param target_langs: Translation target languages.
        :param callback_url: Memsource will hit this url when finished to create the job.
        :param kwargs: See Memsource official document
        http://wiki.memsource.com/wiki/Job_Asynchronous_API_v2

        :return: models.AsynchronousResponse and list of models.JobPart
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
    """You can see the document http://wiki.memsource.com/wiki/Analysis_API_v2
    """
    api_version = constants.ApiVersion.v2

    def get(self, analysis_id: int) -> models.Analysis:
        """Call get API.

        :param analysis_id: Get analysis of this id.
        :return: Result of analysis.
        """
        return models.Analysis(self._get('analyse/get', {
            'analyse': analysis_id,
        }))

    def create(self, job_part_ids: List[int]) -> models.Analysis:
        """Create new analysis.

        :param job_part_ids: Target of analysis.
        :return: Result of analysis.
        """
        return models.Analysis(self._post('analyse/create', {
            'jobPart': job_part_ids,
        }))

    def delete(self, analysis_id: int, purge: bool=False) -> None:
        """Delete an analysis.

        :param analysis_id: Analysis ID you want to delete.
        :param purge:
        """
        self._post('analyse/delete', {
            'analyse': analysis_id,
            'purge': purge,
        })
