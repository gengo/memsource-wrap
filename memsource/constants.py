import enum


class Base(enum.Enum):
    url = 'https://cloud.memsource.com/web/api'
    timeout = 60


class JobStatus(enum.Enum):
    NEW = "New"
    EMAILED = "Emailed"
    ASSIGNED = "Assigned"
    DECLINED_BY_LINGUIST = "Declined_By_Linguist"
    COMPLETED_BY_LINGUIST = "Completed_By_Linguist"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"


class ApiVersion(enum.Enum):
    v2 = 'v2'
    v3 = 'v3'
    v4 = 'v4'
    v7 = 'v7'


class HttpMethod(enum.Enum):
    get = 'get'
    post = 'post'
