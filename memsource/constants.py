import enum


class Base(enum.Enum):
    url = 'https://cloud1.memsource.com/web/api'
    timeout = 5


class ApiVersion(enum.Enum):
    v2 = 'v2'
    v3 = 'v3'
    v6 = 'v6'
