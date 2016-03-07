import enum


class Base(enum.Enum):
    url = 'https://cloud.memsource.com/web/api'
    timeout = 60


class ApiVersion(enum.Enum):
    v2 = 'v2'
    v3 = 'v3'
    v4 = 'v4'
    v7 = 'v7'


class HttpMethod(enum.Enum):
    get = 'get'
    post = 'post'
