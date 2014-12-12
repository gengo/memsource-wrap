from . import api


class Memsource(object):
    def __init__(self, user_name, password):
        self.auth = api.Auth()
        token = self.auth.login(user_name, password)['token']

        for c in (api.Client, api.Domain, api.Project):
            setattr(self, c.__name__.lower(), c(token))
