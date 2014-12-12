class BaseModel(dict):
    def __getattr__(self, key):
        return self[key]

    def __setattr__(self, key, value):
        self[key] = value

    def __delattr__(self, key):
        del self[key]


class User(BaseModel):
    pass


class Authentication(BaseModel):
    pass


class Client(BaseModel):
    pass


class Domain(BaseModel):
    pass
