import iso8601


class BaseModel(dict):
    def __getattr__(self, key):
        return self[key]

    def _iso8601_to_datetime(self, source):
        return iso8601.parse_date(source)


class User(BaseModel):
    pass


class Authentication(BaseModel):
    pass


class Client(BaseModel):
    pass


class Domain(BaseModel):
    pass


class Project(BaseModel):
    @property
    def date_created(self):
        return self._iso8601_to_datetime(self.dateCreated)


class JobPart(BaseModel):
    pass


class TranslationMemory(BaseModel):
    pass


class AsynchronousRequest(BaseModel):
    """
    You can know progress when hit api.Asynchronous.getAsyncRequest with id of this class instance.
    """
    pass


class AsynchronousResponse(BaseModel):
    def __init__(self, source):
        super(AsynchronousResponse, self).__init__({} if source is None else source)

    def is_complete(self):
        return 'error' in self

    def has_error(self):
        return self.is_complete() and self.error is not None
