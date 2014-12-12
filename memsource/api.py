import requests

from . import constants, exceptions, models


class Auth(object):
    def login(self, user_name, password):
        # TODO: error handling
        r = requests.post(
            '{}/v3/auth/login'.format(constants.Base.url.value),
            params={
                'userName': user_name,
                'password': password,
            }
        ).json()

        r['user'] = models.User(r.pop('user'))

        return models.Authentication(r)


class BaseApi(object):
    api_version = None

    def __init__(self, token):
        if self.api_version is None:
            raise NotImplementedError(
                'api_version is not set in {}'.format(self.__class__.__name__))

        self.token = token

    # Should be public, it is conflict with memsource endpoint.
    def _post(self, path, params, timeout=constants.Base.timeout.value):
        return self._request('post', path, params, timeout)

    def _request(self, method, path, params, timeout):
        params['token'] = self.token

        url = '{}/{}/{}'.format(
            constants.Base.url.value,
            self.api_version.value,
            path
        )

        # If it is successful, returns response json
        try:
            response = requests.request(method, url, params=params, timeout=timeout)
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

    def create(self, name, source_lang, target_lang,
               client, domain, due=0, machine_translation_type=0):
        return self._post('project/create', {
            'token': self.token,
            'name': name,
            'sourceLang': source_lang,
            'targetLang': target_lang,
            'client': client,
            'domain': domain,
            'due': due,
            'machineTranslationType': machine_translation_type,
        })['id']
