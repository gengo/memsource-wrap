from memsource import models, api_rest


class Client(api_rest.BaseApi):
    # Document: https://cloud.memsource.com/web/docs/api#tag/Client

    def create(self, name: str) -> str:
        return self._post("v1/client", {"name": name})["id"]

    def get(self, clientID: int):
        return models.Client(self._get("v1/clients/{}".format(clientID)))

    def list(self, page:int=0):
        clients = self._get("v1/clients", {"page": page})
        return [models.Client(client) for client in clients.get("content", [])]
