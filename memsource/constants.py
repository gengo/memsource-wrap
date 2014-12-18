import enum


class Base(enum.Enum):
    url = 'https://cloud1.memsource.com/web/api'
    timeout = 10


class ApiVersion(enum.Enum):
    v2 = 'v2'
    v3 = 'v3'
    v4 = 'v4'
    v6 = 'v6'
