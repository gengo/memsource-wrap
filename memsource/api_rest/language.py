from typing import List
from memsource import models, api_rest


class Language(api_rest.BaseApi):
    # Document: https://cloud.memsource.com/web/docs/api#tag/Supported-Languages

    def listSupportedLangs(self) -> List[models.Language]:
        languages = self._get("v1/languages")
        return [models.Language(language) for language in languages.get("languages", [])]
