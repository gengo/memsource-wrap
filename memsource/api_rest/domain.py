from typing import Any, Dict, List
from memsource import models, api_rest


class Domain(api_rest.BaseApi):
    # Document: https://cloud.memsource.com/web/docs/api#tag/Domain

    def create(self, name: str) -> Dict[str, Any]:
        return self._post("v1/domains", {"name": name})

    def get(self, domainID: int) -> models.Domain:
        return models.Domain(self._get("v1/domains/{}".format(domainID)))

    def list(self, page: int=0) -> List[models.Domain]:
        domains = self._get("v1/domains", {"page": page})
        return [models.Domain(domain) for domain in domains.get("content", [])]
