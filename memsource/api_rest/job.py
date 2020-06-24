import io
import json
import os
import types
import uuid
from typing import Any, Dict, List

from memsource import api_rest, constants, exceptions, models


class Job(api_rest.BaseApi):
    # Document: https://cloud.memsource.com/web/docs/api#tag/Job
    def _create(
            self,
            project_id: int,
            target_langs: List[str],
            files: Dict[str, Any]
    ) -> List[models.JobPart]:
        """Common process of creating job.

        If returning JSON has `unsupportedFiles`,
        this method raise MemsourceUnsupportedFileException

        :param project_id: New job will be in this project.
        :param file_path: Source file of job.
        :param target_langs: List of translation target languages.
        :return: List of models.JobPart
        """

        if isinstance(files["file"], tuple):
            # If value is tuple type, this function called from createFromText.
            # We need to create temporary file for to raise exception.
            file_name, text = files["file"]
            file_path = os.path.join("/", "tmp", file_name)
        else:
            file_name = file_path = files["file"].name

        job_create_extra_headers = {
            "Content-Type": "application/octet-stream",
            "Content-Disposition": "inline; filename=\"{}\"".format(file_name),
            "Memsource": json.dumps({"targetLangs": target_langs})
        }
        if self.headers is None:
            self.headers = job_create_extra_headers
        else:
            self.headers.update(job_create_extra_headers)

        result = self._post("v1/projects/{}/jobs".format(project_id), {
            "targetLangs": target_langs,
        }, files)

        # unsupported file count is 0 mean success.
        unsupported_files = result.get("unsupportedFiles", [])
        if len(unsupported_files) == 0:
            return [models.JobPart(job_parts) for job_parts in result["jobs"]]

        if isinstance(files["file"], tuple):
            with open(file_path, "w+") as f:
                f.write(text)

        raise exceptions.MemsourceUnsupportedFileException(
            unsupported_files,
            file_path,
            self.last_url,
            self.last_params
        )

    def create(
            self, project_id: int, file_path: str, target_langs: List[str]
    ) -> List[models.JobPart]:
        """Create a job.

        If returning JSON has `unsupportedFiles`,
        this method raise MemsourceUnsupportedFileException

        :param project_id: New job will be in this project.
        :param file_path: Source file of job.
        :param target_langs: List of translation target languages.
        :return: List of models.JobPart
        """
        with open(file_path, 'r') as f:
            return self._create(project_id, target_langs, {'file': f})

    def create_from_text(
            self,
            project_id: int,
            text: str,
            target_langs: List[str],
            file_name: str=None,
    ) -> List[models.JobPart]:
        """You can create a job without a file.

        See: Job.create
        If returning JSON has `unsupportedFiles`,
        this method raise MemsourceUnsupportedFileException

        :param project_id: New job will be in this project.
        :param text: Source text of job.
        :param target_langs: List of translation target languages.
        :param file_name: Create file name by uuid1() when file_name parameter is None.
        :return: List of models.JobPart
        """
        return self._create(project_id, target_langs, {
            'file': ('{}.txt'.format(uuid.uuid1().hex) if file_name is None else file_name, text),
        })

    def list_by_project(
            self,
            project_id: int,
            page: int = 0,
    ) -> List[models.JobPart]:
        jobs = self._get("v2/projects/{}/jobs".format(project_id), {"page": page})
        return [models.JobPart(job_part) for job_part in jobs["content"]]

    def pre_translate(
            self,
            project_id: int,
            job_parts: List[Dict[str, str]],
            translation_memory_threshold: float=0.7,
            callback_url: str=None,
    ) -> models.AsynchronousRequest:
        """Call async pre translate API.

        :param job_parts: Dictionary of job_part id with format `{"uid": string}`.
        :param translation_memory_threshold: If matching score is higher than this, it is filled.
        :return: models.AsynchronousRequest
        """
        response = self._post("v1/projects/{}/jobs/preTranslate".format(project_id), {
            "jobs": [{"uid": job_part} for job_part in job_parts],
            "translationMemoryTreshold": translation_memory_threshold,
            "callbackUrl": callback_url,
        })

        return models.AsynchronousRequest(response["asyncRequest"])

    def get_completed_file_text(self, project_id: int, job_uid: str) -> bytes:
        """Download completed file and return it.

        :param job_uid: job UID.
        """
        def get_completed_file_stream() -> types.GeneratorType:
            return self._get_stream(
                "v1/projects/{}/jobs/{}/targetFile".format(project_id, job_uid)
            ).iter_content(constants.CHUNK_SIZE)

        buffer = io.BytesIO()
        [buffer.write(chunk) for chunk in get_completed_file_stream()]

        return buffer.getvalue()

    def get_segments(
            self,
            project_id: int,
            job_uid: str,
            begin_index: int=0,
            end_index: int=0,
    ) -> List[models.Segment]:
        """Call get segments API.

        NOTE: I don't know why this endpoint returns list of list.
        It seems always one item in outer list.

        :param project_id: ID of the project
        :param job_uid: UID of the job
        :param begin_index
        :param end_index
        :return: List of models.Segment
        """
        segments = self._get("v1/projects/{}/jobs/{}/segments".format(project_id, job_uid), {
            "beginIndex": begin_index,
            "endIndex": end_index,
        })

        return [
            models.Segment(segment) for segment in segments["segments"]
        ]

    def get(self, project_id: int, job_uid: str) -> models.Job:
        """Get the job data.

        :param job_uid: ID of the job.
        :return: The retrieved job.
        """
        response = self._get("v1/projects/{}/jobs/{}".format(project_id, job_uid))

        return models.Job(response)

    def list(self, project_id: int) -> List[models.Job]:
        """Get the jobs data.

        :param project_id: ID of the project
        :return: The retrieved jobs.
        """
        response = self._get("v2/projects/{}/jobs".format(project_id))

        return [models.Job(i) for i in response["content"]]

    def delete(
            self,
            project_id: int,
            job_uids: List[int],
            purge: bool=False
    ) -> None:
        """Delete a job

        :param job_uids: ids of job you want to delete.
        :param purge:
        """
        self._delete(
            path="v1/projects/{}/jobs/batch".format(project_id),
            params={"purge": purge},
            data={"jobs": [{"uid": job_uid} for job_uid in job_uids]},
        )

    def set_status(
            self,
            project_id: int,
            job_uid: str,
            status: constants.JobStatusRest,
    ) -> None:
        """Update job status

        JobStatus: New, Emailed, Assigned, Declined_By_Linguist,
                   Completed_By_Linguist, Completed, Cancelled

        :param job_part_id: id of job you want to update.
        :param status: status of job to update. Acceptable type is JobStatus constant.
        """
        self._post("v1/projects/{}/jobs/{}/setStatus".format(project_id, job_uid), {
            'requestedStatus': status.value
        })

    def delete_all_translations(
            self,
            project_id: int,
            job_uids: List[int]
    ) -> None:
        """Delete all translations from a job

        :param job_part_ids: IDs of job_part for the jobs.
        """
        self._delete("v1/projects/{}/jobs/translations".format(project_id), {}, {
            'jobs': [{"uid": job_uid} for job_uid in job_uids],
        })
