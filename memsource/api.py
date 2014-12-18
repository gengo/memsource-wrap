import requests
import uuid
import os

from . import constants, exceptions, models

__all__ = ('Auth', 'Client', 'Domain', 'Project', 'Job', 'TranslationMemory', )


class BaseApi(object):
    api_version = None

    def __init__(self, token):
        if self.api_version is None:
            # This exception is for development this library.
            raise NotImplementedError(
                'api_version is not set in {}'.format(self.__class__.__name__))

        self.token = token

    # Should be public, it is conflict with memsource endpoint.
    def _post(self, path, params, files={}, timeout=constants.Base.timeout.value):
        return self._request('post', path, files, params, timeout)

    def _request(self, method, path, files, params, timeout):
        params['token'] = self.token

        url = '{}/{}/{}'.format(
            constants.Base.url.value,
            self.api_version.value,
            path
        )

        self.last_params = params
        self.last_url = url

        # If it is successful, returns response json
        try:
            response = requests.request(method, url, params=params, files=files, timeout=timeout)
        except requests.exceptions.Timeout:
            raise exceptions.MemsourceApiException(None, {
                'errorCode': 'Internal',
                'errorDescription': 'The request timed out, timeout is {}'.format(timeout),
            }, url, params)
        except requests.exceptions.ConnectionError:
            raise exceptions.MemsourceApiException(None, {
                'errorCode': 'Internal',
                'errorDescription': 'Could not connect',
            }, url, params)

        if BaseApi.is_success(response.status_code):
            return response.json()

        raise exceptions.MemsourceApiException(response.status_code, response.json(), url, params)

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

    def createFromText(self, project_id, text, target_langs):
        """
        Make temporary file and make a job. The temporary file will be removed automatically.
        See: Job.create
        """
        file_path = '/tmp/{}.txt'.format(uuid.uuid1().hex)
        with open(file_path, 'w+') as f:
            f.write(text)

        try:
            return self.create(project_id, file_path, target_langs)
        finally:
            os.remove(file_path)

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

    def import_(self, translation_memory_id, file_path):
        """
        This method name is `_import` because `import` is keyword of Python.
        We cannot use `import` as method name.

        return int accepted segments count
        """

        # Casting because acceptedSegmentsCount seems always number, but it string type.
        with open(file_path, 'rb') as f:
            return int(self._post('transMemory/import', {
                'transMemory': translation_memory_id,
            }, {
                'file': f
            })['acceptedSegmentsCount'])
