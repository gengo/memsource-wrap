from memsource import models, api_rest


class Auth(api_rest.BaseApi):
    # Document: https://cloud.memsource.com/web/docs/api#tag/Authentication

    def login(self, user_name: str, password: str) -> models.Authentication:
        response = self._post("v1/auth/login", {
            "userName": user_name,
            "password": password,
        })
        response["user"] = models.User(response.pop("user"))

        return models.Authentication(response)
