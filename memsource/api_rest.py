from typing import (
    Any,
    Dict,
    Optional,
    Tuple,
    Union,
)

import requests

from memsource import constants, exceptions


class BaseApi:
    _session = requests.Session()

    def __init__(
        self,
        token: Optional[str] = None,
        headers: Optional[Dict[str, Any]] = None
    ) -> None:
        self.token = token
        self.headers = headers

    @classmethod
    def use_session(cls, session: requests.Session) -> None:
        """
        Configures the session object which is used for API invocation.
        This method is not thread-safe. It is recommended to configure only once.

        Arguments:
        session -- The session object to be used by BaseApi
        """
        cls._session = session

    def _get(
            self,
            path: str,
            params: Dict[str, Any]={},
            timeout: int=constants.BaseRest.timeout.value
    ) -> Dict[str, Any]:
        return self._request(
            http_method=constants.HttpMethod.get,
            path=path,
            files=None,
            params=params,
            data=None,
            timeout=timeout
        ).json()

    def _get_stream(
            self, path: str, params: Dict[str, Any]={}, files: Optional[Dict[str, Any]]=None,
            timeout: Union[int, float]=constants.BaseRest.timeout.value * 5
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
        return self._request(
            http_method=constants.HttpMethod.get,
            path=path,
            files=files,
            params=params,
            data=None,
            timeout=timeout
        )

    def _post(
            self,
            path: str,
            data: Optional[Dict[str, Any]]=None,
            files: Optional[Dict[str, Any]]=None,
            timeout: Union[int, float]=constants.BaseRest.timeout.value,
    ) -> Dict[str, Any]:
        """Send a post request.

        If you want to raw response, you can use _get_stream method.

        :param path: Send request to this path
        :param data: Send request with this parameters
        :param files: Upload this files. Key is filename, value is file object
        :param timeout: When takes over this time in one request, raise timeout
        :return: parsed response body as JSON
        """
        return self._request(
            http_method=constants.HttpMethod.post,
            path=path,
            files=files,
            params={"token": self.token},
            data=data,
            timeout=timeout
        ).json()

    def _pre_request(self, path: str, params: Dict[str, Any]) -> Tuple[str,  Dict[str, Any]]:
        """Create request url and extend param with token for authentication.

        :param path: API path with this format ({api_name}/{method})
        :param params: Insert token in this dict

        :return: Tuple of URL and params with token.
        """
        url = "{}/{}".format(constants.BaseRest.url.value, path)
        params['token'] = self.token

        self.last_url = url
        self.last_params = params

        return (url, params)

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
                'errorDescription': 'Could not connect: {}'.format(response.text),
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
            http_method: constants.HttpMethod,
            path: str,
            files: Dict[str, Any],
            params: Dict[str, Any],
            data: Dict[str, Any],
            timeout: Tuple[int, float]
    ) -> requests.models.Response:
        """Send a http request.

        :param http_method: Use this http method
        :param path: Send request to this path
        :param data: Send request with this parameters
        :param files: Upload this files. Key is filename, value is file object
        :param timeout: When takes over this time in one request, raise timeout
        :return: response of request module
        """
        (url, params) = self._pre_request(path, params)
        arguments = {
            key: value for key, value in [
                ('files', files), ('params', params), ('json', data), ('headers', self.headers)
            ] if value is not None
        }

        # If it is successful, returns response json
        return self._get_response(http_method, url, timeout=timeout, **arguments)

    @staticmethod
    def is_success(status_code: int) -> bool:
        # if status_code is float type, we will get unexpected result.
        # but I think it is not big deal.
        return 200 <= status_code < 300
