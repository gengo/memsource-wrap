from . import api


__author__ = 'Gengo'
__version__ = '0.0.1'
__license__ = 'MIT'


class Memsource(object):
    def __init__(self, user_name=None, password=None, token=None):
        """
        If token is given, use the token.
        Otherwise authenticate with user_name and password, and get token.
        """
        self.auth = api.Auth()

        (lambda token: [
            setattr(self, c.__name__.lower(), c(token)) for c in (
                api.Client,
                api.Domain,
                api.Project
            )
        ])(self.auth.login(user_name, password).token if token is None else token)
