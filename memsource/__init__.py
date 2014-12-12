from . import api


class Memsource(object):
    def __init__(self, username, password):
        self.auth = api.Auth()
        token = self.auth.login(username, password)['token']

        for c in (api.Client, api.Domain, api.Project):
            setattr(self, c.__name__.lower(), c(token))
