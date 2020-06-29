import io
from typing import Iterator, List

from memsource import api_rest, constants, models
from memsource.lib import mxliff


class Bilingual(api_rest.BaseApi):
    # Document: https://cloud.memsource.com/web/docs/api#tag/Bilingual-File

    def _get_bilingual_stream(self, project_id: int, job_uids: List[str]) -> Iterator[bytes]:
        """Common process of bilingualFile.

        :param project_id: ID of the project.
        :param job_uids: List of job uids.
        :return: Downloaded bilingual file with iterator.
        """
        return self._post_stream(
            path="v1/projects/{}/jobs/bilingualFile".format(project_id),
            data={"jobs": [{"uid": job_uid} for job_uid in job_uids]},
        ).iter_content(constants.CHUNK_SIZE)

    def get_bilingual_file_xml(self, project_id: int, job_uids: List[str]) -> bytes:
        """Download bilingual file and return it as bytes.

        This method might use huge memory.

        :param project_id: ID of the project.
        :param job_uids: List of job uids.
        :return: Downloaded bilingual file.
        """
        buffer = io.BytesIO()

        for chunk in self._get_bilingual_stream(project_id, job_uids):
            buffer.write(chunk)

        return buffer.getvalue()

    def get_bilingual_file(
            self,
            project_id: int,
            job_uids: List[int],
            dest_file_path: str
    ) -> None:
        """Download bilingual file and save it as a file.

        :param project_id: ID of the project.
        :param job_uids: List of job uids.
        :param dest_file_path: Save bilingual file to there.
        """
        with open(dest_file_path, "wb") as f:
            for chunk in self._get_bilingual_stream(project_id, job_uids):
                f.write(chunk)

    def get_bilingual_as_mxliff_units(
            self,
            project_id: int,
            job_uids: List[str]
    ) -> models.MxliffUnit:
        """Download bilingual file and parse it as [models.MxliffUnit]

        :param project_id: ID of the project.
        :param job_uids: List of job uids.
        :returns: MxliffUnit
        """
        return mxliff.MxliffParser().parse(self.get_bilingual_file_xml(project_id, job_uids))
