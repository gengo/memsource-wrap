from . import api
from memsource.api_rest import (
    auth,
    client,
    domain,
    language,
    term_base,
    project,
    job,
    bilingual,
    tm,
    analysis,
)


class Memsource(object):
    def __init__(self, user_name=None, password=None, token=None, headers=None, use_rest=False):
        if use_rest:
            self._init_rest(
                user_name=user_name,
                password=password,
                token=token,
                headers=headers,
            )
            return

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

    def _init_rest(self, user_name, password, token, headers):
        """
        If token is given, use the token.
        Otherwise authenticate with user_name and password, and get token.
        """
        if user_name and password and not token and not headers:
            token = auth.Auth().login(user_name, password).token

        # make api class instances
        self.auth = auth.Auth(token, headers)
        self.client = client.Client(token, headers)
        self.domain = domain.Domain(token, headers)
        self.project = project.Project(token, headers)
        self.job = job.Job(token, headers)
        self.translation_memory = tm.TranslationMemory(token, headers)
        self.language = language.Language(token, headers)
        self.analysis = analysis.Analysis(token, headers)
        self.term_base = term_base.TermBase(token, headers)
        self.bilingual = bilingual.Bilingual(token, headers)
