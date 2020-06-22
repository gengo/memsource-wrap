from memsource import constants, api_rest


class TermBase(api_rest.BaseApi):
    # Document: https://cloud.memsource.com/web/docs/api#tag/Term-Base

    def download(
        self,
        termbase_id: int,
        filepath: str,
        file_format: constants.TermBaseFormat=constants.TermBaseFormat.XLSX,
        chunk_size: int=constants.CHUNK_SIZE,
        charset: str=constants.CHAR_SET,
    ) -> None:
        """Download a term base.

        :param termbase_id: ID of the term base to be downloaded.
        :param filepath: Save exported data to this file path.
        :param file_format: TBX or XLSX. Defaults to XLSX.
        :param chunk_size: byte size of chunk for response data.
        """
        params = {
            "format": file_format.value.capitalize(),
            "charset": charset,
        }

        with open(filepath, 'wb') as f:
            data_stream = self._get_stream(
                "v1/termBases/{}/export".format(termbase_id), params
            ).iter_content(chunk_size)

            for chunk in data_stream:
                f.write(chunk)
