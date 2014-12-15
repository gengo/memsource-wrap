import shutil


class MemsourceException(Exception):
    """
    This class is base of All Memsource exceptions.
    """
    message_prefix = "The Memsource API returns an error."


class MemsourceApiException(MemsourceException):
    def __init__(self, status_code, result_json, url, params):
        self.status_code = status_code
        self.result_json = result_json
        self.url = url
        self.params = params

        message = "{} ".format(self.message_prefix) +\
                  "http status code: {} ".format(status_code) +\
                  "error code: {} ".format(self.get_error_code()) +\
                  "error description: {} ".format(self.get_error_description()) +\
                  "requested url: {} with {}".format(url, params)

        super(MemsourceApiException, self).__init__(message)

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


class MemsourceUnsupportedFileException(MemsourceException):
    def __init__(self, unsupported_files, original_file_path, url, params):
        # I don't know why Memsource API is returning unsupported_file as array type.
        # It seems always one element.
        unsupported_file = unsupported_files[0]

        # Make a copy the unsupported file. It is helpful for debugging.
        file_path = shutil.copy(original_file_path, '/var/tmp/{}'.format(unsupported_file))

        message = "{} ".format(self.message_prefix) +\
                  "error code: {} ".format('UnsupportedFile') +\
                  "error description: {} is unsupproted. You can see the copy at {} ".format(
                      unsupported_file, file_path) +\
                  "requested url: {} with {}".format(url, params)

        super(MemsourceUnsupportedFileException, self).__init__(message)
