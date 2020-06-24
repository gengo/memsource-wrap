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


class ProjectStatus(enum.Enum):
    NEW = "New"
    ASSIGNED = "Assigned"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"
    ACCEPTED_BY_VENDOR = "Accepted_By_Vendor"
    DECLINED_BY_VENDOR = "Declined_By_Vendor"
    COMPLETED_BY_VENDOR = "Completed_By_Vendor"


class AnalysisFormat(enum.Enum):
    CSV = "CSV"
    LOG = "LOG"
    CSV_EXTENDED = "CSV_EXTENDED"


class TermBaseFormat(enum.Enum):
    XLSX = "XLSX"
    TBX = "TBX"


class ApiVersion(enum.Enum):
    v2 = 'v2'
    v3 = 'v3'
    v4 = 'v4'
    v7 = 'v7'


class HttpMethod(enum.Enum):
    get = 'get'
    post = 'post'
    put = 'put'
    delete = "delete"


class BaseRest(enum.Enum):
    url = 'https://cloud.memsource.com/web/api2'
    timeout = 60


class JobStatusRest(enum.Enum):
    NEW = "NEW"
    ACCEPTED = "ACCEPTED"
    DECLINED = "DECLINED"
    REJECTED = "REJECTED"
    DELIVERED = "DELIVERED"
    EMAILED = "EMAILED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


CHUNK_SIZE = 1024
CHAR_SET = "UTF-8"
