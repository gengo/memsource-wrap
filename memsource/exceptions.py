class MemsourceApiException(Exception):
    def __init__(self, status_code, result_json, url, params):
        self.status_code = status_code
        self.result_json = result_json
        self.url = url
        self.params = params

        message = "The Memsource API returns an error. " +\
                  "http status code: {} ".format(status_code) +\
                  "error code: {} ".format(self.get_error_code()) +\
                  "error description: {} ".format(self.get_error_description()) +\
                  "requested url: {} with {}".format(url, params)

        super(Exception, self).__init__(message)

    def get_error_code(self):
        """
        returns errorCode from API response JSON.
        If it is unavailable, it returns None.
        """
        return self.result_json.get('errorCode')

    def get_error_description(self):
        """
        returns errorDescription from API response JSON.
        If it is unavailable, it returns None.
        """
        return self.result_json.get('errorDescription')
