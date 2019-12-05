from . import api


class Memsource(object):
    def __init__(self, user_name=None, password=None, token=None, headers=None):
        """
        If token is given, use the token.
        Otherwise authenticate with user_name and password, and get token.
        """
        if user_name and password and not token and not headers:
            token = api.Auth().login(user_name, password).token

        # make api class instances
        self.auth = api.Auth(token, headers)
        self.client = api.Client(token, headers)
        self.domain = api.Domain(token, headers)
        self.project = api.Project(token, headers)
        self.job = api.Job(token, headers)
        self.translation_memory = api.TranslationMemory(token, headers)
        self.asynchronous = api.Asynchronous(token, headers)
        self.language = api.Language(token, headers)
        self.analysis = api.Analysis(token, headers)
        self.term_base = api.TermBase(token, headers)
