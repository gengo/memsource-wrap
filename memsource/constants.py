import enum


class Base(enum.Enum):
    url = 'https://cloud1.memsource.com/web/api'


class ApiVersion(enum.Enum):
    v2 = 'v2'
    v3 = 'v3'
