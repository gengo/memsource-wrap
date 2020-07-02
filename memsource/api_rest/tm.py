import io
import tempfile
from typing import Any, Dict, List, Optional, Union

from memsource import api_rest, constants, models


class TranslationMemory(api_rest.BaseApi):
    # Document: https://cloud.memsource.com/web/docs/api#tag/Translation-Memory
    def create(self, name: str, source_lang: str, target_langs: Union[List[str], str]) -> int:
        """Create a translation memory.

        :param name: Name of new translation memory.
        :param source_lang: Soruce language of new translation memory.
        :param target_langs: Target languages of new translation memory.
        :return: ID of created translation memory.
        """
        return self._post("v1/transMemories", {
            "name": name,
            "sourceLang": source_lang,
            "targetLangs": target_langs,
        })["id"]

    def list(self, page: int=0) -> List[models.TranslationMemory]:
        """List translation memories.

        :page: index of pager.
        :return: List of translation memory.
        """
        tms = self._get("v1/transMemories", {"pageNumber": page})
        return [
            models.TranslationMemory(translation_memory)
            for translation_memory in tms["content"]
        ]

    def _upload(self, translation_memory_id: int, files: Dict[str, Any]) -> int:
        # Casting because acceptedSegmentsCount seems always number, but it string type.
        file_name = files["file"].name

        tm_create_extra_headers = {
            "Content-Type": "application/octet-stream",
            "Content-Disposition": "inline; filename*=UTF-8''{}".format(file_name),
        }
        self.add_headers(tm_create_extra_headers)

        """An error persists on importing segments to Memsource:
        memsource.exceptions.MemsourceApiException:
        http status code: 500
        description: com.ctc.wstx.exc.WstxUnexpectedCharException: Unexpected character '-'
        (code 45) in prolog; expected '<' at [row,col {unknown-source}]: [1,1]
        Sending it via "data" instead of "file" works fine.
        """

        path = "v1/transMemories/{}/import".format(translation_memory_id)
        (url, params) = self._pre_request(path, {})
        arguments = {
            "params": params,
            "data": files["file"],
            "headers": self.headers,
        }
        response = self._get_response(
            http_method=constants.HttpMethod.post,
            url=url,
            timeout=constants.BaseRest.timeout.value,
            **arguments
        )
        response.raise_for_status()

        return int(response.json()["acceptedSegmentsCount"])

    def upload(self, translation_memory_id: int, file_path: str) -> int:
        """Call **import** API.

        This method calls import endpoint, but method name is `upload`,
        because `import` is keyword of Python. We cannot use `import` as method name.

        :param translation_memory_id: Uploaded translation units are into here.
        :param file_path: Import this file into the translation memory.
        :return: accepted segments count.
        """

        with open(file_path, "rb") as f:
            return self._upload(translation_memory_id, {"file": f})

    def upload_from_text(self, translation_memory_id: int, tmx: str) -> int:
        """Import tmx text into a translation memory.

        :param translation_memory_id: Uploaded translation units are into here.
        :param tmx: Import this tmx text into the translation memory.
        :return: accepted segments count.
        """
        with tempfile.NamedTemporaryFile(suffix=".tmx") as temp_file:
            temp_file.write(tmx.encode("utf-8"))
            temp_file.seek(0)
            return self._upload(translation_memory_id, {
                "file": temp_file,
            })

    def search_segment_by_job(
            self,
            project_id: int,
            job_uid: str,
            segment: str,
            next_segment: Optional[str]=None,
            previous_segment: Optional[str]=None,
            score_threshold: float=constants.TM_THRESHOLD,
            **kwargs
    ) -> List[models.SegmentSearchResult]:
        """Get translation matches.

        :param project_id: project ID
        :param job_uid: job UID
        :param segment: Search by this segment
        :param next_segment: Effect for 101% match
        :param previous_segment: Effect for 101% match
        :param score_threshold: return only high score than this value
        :param kwargs: See the Memsource official document
            https://cloud.memsource.com/web/docs/api#operation/searchSegmentByJob

        :return: list of models.SegmentSearchResult
        """
        parameters = {
            "segment": segment,
            "scoreThreshold": score_threshold,
        }
        parameters.update(kwargs)

        if next_segment is not None:
            parameters["nextSegment"] = next_segment

        if previous_segment is not None:
            parameters["previousSegment"] = previous_segment

        url = "v1/projects/{}/jobs/{}/transMemories/searchSegment".format(project_id, job_uid)
        response = self._post(url, parameters)
        return [
            models.SegmentSearchResult(item)
            for item in response["searchResults"]
        ]

    def search(
            self,
            translation_memory_id: int,
            query: str,
            source_lang: str,
            target_langs: Union[List[str], str],
            next_segment: Optional[str]=None,
            previous_segment: Optional[str]=None,
            **kwargs
    ) -> List[models.SegmentSearchResult]:
        """Get translation matches.

        :param translation_memory_id: Search translation units are into here.
        :param query: Search query
        :param source_lang: Soruce language of translation memory.
        :param target_langs: Target languages of translation memory.
        :param next_segment: Effect for 101% match
        :param previous_segment: Effect for 101% match
        :param kwargs: See the Memsource official document
            https://cloud.memsource.com/web/docs/api#operation/search

        :return: list of models.SegmentSearchResult
        """
        parameters = {
            "query": query,
            "sourceLang": source_lang,
        }
        parameters.update(kwargs)

        if target_langs is not None:
            parameters["targetLangs"] = target_langs

        if next_segment is not None:
            parameters["nextSegment"] = next_segment

        if previous_segment is not None:
            parameters["previousSegment"] = previous_segment

        result = self._post("v1/transMemories/{}/search".format(translation_memory_id), parameters)
        return [
            models.SegmentSearchResult(item)
            for item in result["searchResults"]
        ]

    def export(
            self,
            translation_memory_id: int,
            target_langs: List[str],
            callback_url: Optional[str]=None,
    ) -> models.AsynchronousRequest:
        """Get translation memory exported data

        :param translation_memory_id: translation memory id for target of exporting data.
        :param target_langs: Export target languages.
        :param callback_url
        """

        response = self._post("v2/transMemories/{}/export".format(translation_memory_id), {
            "exportTargetLangs": target_langs,
            "callbackUrl": callback_url,
        })

        return models.AsynchronousRequest(response["asyncRequest"])

    def download_export(self, async_request_id: str) -> bytes:
        """Download export file
        :param async_request_id: ID of the async request.
        """
        data_stream = self._get_stream(
            "v1/transMemories/downloadExport/{}".format(async_request_id)
        ).iter_content(constants.CHUNK_SIZE)

        buffer = io.BytesIO()
        for chunk in data_stream:
            buffer.write(chunk)

        return buffer.getvalue()

    def insert(
            self,
            translation_memory_id: int,
            target_lang: str,
            source_segment: str,
            target_segment: str,
            previous_source_segment: Optional[str]=None,
            next_source_segment: Optional[str]=None,
    ) -> None:
        """
        :param translation_memory_id :Insert new translation to this translation memory :int
        :param target_lang :target_segment is this language :str
        :param source_segment :source text of the translated text :str
        :param target_segment :translated text :str
        :previous_source_segment :optional This is for 101% match :str
        :next_source_segment :optional This is for 101% match :str
        """
        params = {
            "sourceSegment": source_segment,
            "targetLang": target_lang,
            "targetSegment": target_segment,
        }

        # If optional parameter is passed, include those into post parameter
        if previous_source_segment is not None:
            params["previousSourceSegment"] = previous_source_segment

        if next_source_segment is not None:
            params["nextSourceSegment"] = next_source_segment

        self._post("v1/transMemories/{}/segments".format(translation_memory_id), params)

    def delete_source_and_translations(self, translation_memory_id: int, segment_id: str) -> None:
        """Delete segments from a translation memory.

        :param translation_memory_id: ID of the translation memory.
        :param segment_id: ID of the segment.
        """
        self._delete("v1/transMemories/{}/segments/{}".format(translation_memory_id, segment_id))
