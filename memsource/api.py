import requests
import uuid

from . import constants, exceptions, models

__all__ = ('Auth', 'Client', 'Domain', 'Project', 'Job', 'TranslationMemory', 'Asynchronous', )


class BaseApi(object):
    """Inheriting classes must have the api_version attribute"""
    def __init__(self, token):
        if not hasattr(self, 'api_version'):
            # This exception is for development this library.
            raise NotImplementedError(
                'api_version is not set in {}'.format(self.__class__.__name__))

        self.token = token

    def _make_url(self, *args, **kwargs):
        return kwargs.get('format', '{base}/{api_version}/{path}').format(**kwargs)

    # Should be public, it is conflict with memsource endpoint.
    def _post(self, path, params, files={}, timeout=constants.Base.timeout.value):
        """
        return response as dict

        If you want to raw response, you can use _get_stream method.
        TODO: implements _post_stream.
        """
        return self._request(constants.HttpMethod.post, path, files, params, timeout)

    def _get_stream(self, path, params, files={}, timeout=constants.Base.timeout.value * 5):
        """
        return response object of requests library

        This method returns response object of requests library,
        because XML parse or save to file or etc are different will call different method.

        We can switch response by value of stream, but it is not good, I think,
        because type of returning value is only one is easy to use, easy to understand.
        """
        return self._request_stream(constants.HttpMethod.get, path, files, params, timeout)

    def _pre_request(self, path, params):
        url = self._make_url(
            base=constants.Base.url.value,
            api_version=self.api_version.value,
            path=path
        )
        params['token'] = self.token

        self.last_url = url
        self.last_params = params

        return (url, params, )

    def _request_stream(self, http_method, path, files, params, timeout):
        (url, params_with_token) = self._pre_request(path, params)

        return self._get_response(
            http_method, url, params=params_with_token, files=files, timeout=timeout, stream=True)

    def _get_response(self, http_method, url, **kwargs):
        try:
            response = requests.request(http_method.value, url, **kwargs)
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

        raise exceptions.MemsourceApiException(
            response.status_code, response.json(), self.last_url, self.last_params)

    def _request(self, http_method, path, files, params, timeout):
        (url, params_with_token) = self._pre_request(path, params)

        # If it is successful, returns response json
        return self._get_response(
            http_method, url, params=params_with_token, files=files, timeout=timeout).json()

    @staticmethod
    def is_success(status_code):
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

    def create(self, name, source_lang, target_lang, client, domain):
        """
        Return project id.
        """
        return self._post('project/create', {
            'token': self.token,
            'name': name,
            'sourceLang': source_lang,
            'targetLang': target_lang,
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


class Job(BaseApi):
    """
    You can see the document http://wiki.memsource.com/wiki/Job_API_v6
    """
    api_version = constants.ApiVersion.v6

    def create(self, project_id, file_path, target_langs):
        """
        return: [JobPart]

        If returning JSON has `unsupportedFiles`,
        this method raise MemsourceUnsupportedFileException
        """
        with open(file_path, 'r') as f:
            result = self._post('job/create', {
                'project': project_id,
                'targetLang': target_langs,
            }, {
                'file': f,
            })

        unsupportedFiles = result.get('unsupportedFiles', [])
        if len(unsupportedFiles) > 0:
            raise exceptions.MemsourceUnsupportedFileException(
                unsupportedFiles,
                file_path,
                self.last_url,
                self.last_params
            )

        return [models.JobPart(job_parts) for job_parts in result['jobParts']]

    def createFromText(self, project_id, text, target_langs, file_name=None):
        """
        You can create a job without a file.
        See: Job.create

        Create file name by uuid1() when file_name parameter is None.
        """
        return [
            models.JobPart(job_parts) for job_parts in self._post('job/create', {
                'project': project_id,
                'targetLang': target_langs,
            }, {
                'file': (uuid.uuid1().hex if file_name is None else file_name, text),
            })['jobParts']
        ]

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

    def getBilingualFile(self, job_parts, dest_file_path):
        response = self._get_stream('job/getBilingualFile', {
            'jobPart': job_parts,
        })
        with open(dest_file_path, 'wb') as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)

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

    def upload(self, translation_memory_id, file_path):
        """
        This method calls import endpoint, but method name is `upload`,
        because `import` is keyword of Python. We cannot use `import` as method name.

        return int accepted segments count
        """

        # Casting because acceptedSegmentsCount seems always number, but it string type.
        with open(file_path, 'rb') as f:
            return int(self._post('transMemory/import', {
                'transMemory': translation_memory_id,
            }, {
                'file': f
            })['acceptedSegmentsCount'])

    def searchSegmentByTask(self, task, segment_source, score_threshold=0.6):
        """
        You can get translation memory that related with segment_source.

        :param task :task :str
        :param segment_source :Segment.source :str
        :param score_threshold :optional(0.6) :return only high score than this value :double

        :return [models.SegmentSearchResult]
        """
        return [
            models.SegmentSearchResult(segment)
            for segment in self._post('transMemory/searchSegmentByTask', {
                'task': task,
                'segment': segment_source,
                'scoreThreshold': score_threshold,
            })
        ]


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
        * https://cloud1.memsource.com/web/api/async/v2/job/preTranslate
        * https://cloud1.memsource.com/web/api/v2/async/getAsyncRequest

        This is example of other endpoints
        * https://cloud1.memsource.com/web/api/v3/project/create
        """
        if kwargs['path'] != 'async/getAsyncRequest':
            kwargs['format'] = '{base}/async/{api_version}/{path}'

        return super(Asynchronous, self)._make_url(**kwargs)

    def preTranslate(self, job_parts):
        """
        return models.AsynchronousRequest
        """
        return models.AsynchronousRequest(self._post('job/preTranslate', {
            'jobPart': job_parts,
        })['asyncRequest'])

    def getAsyncRequest(self, asynchronous_request_id):
        asyncRequest = self._post('async/getAsyncRequest', {
            'asyncRequest': asynchronous_request_id,
        })
        asyncRequest['asyncResponse'] = models.AsynchronousResponse(asyncRequest['asyncResponse'])

        return models.AsynchronousRequest(asyncRequest)
