from typing import Iterator, List
from memsource import api_rest, constants, models


class Analysis(api_rest.BaseApi):
    # Document: https://cloud.memsource.com/web/docs/api#tag/Analysis

    def get(self, analysis_id: int) -> models.Analysis:
        """Call get API.

        :param analysis_id: Get analysis of this id.
        :return: Result of analysis.
        """
        return models.Analysis(self._get("v3/analyses/{}".format(analysis_id)))

    def create(self, jobs: List[int]) -> models.AsynchronousRequest:
        """Create new analysis.

        :param jobs: Target of analysis.
        :return: Result of analysis.
        """
        return models.AsynchronousRequest(self._post("v2/analyses", {
            "jobs": [{"uid": job} for job in jobs],
        }))

    def delete(self, analysis_id: int, purge: bool=False) -> None:
        """Delete an analysis.

        :param analysis_id: Analysis ID you want to delete.
        :param purge:
        """
        self._delete("v1/analyses/{}".format(analysis_id), {"purge": purge})

    def get_by_project(self, project_id: str) -> List[models.Analysis]:
        """List Analyses By Project.

        :param project_id: Project ID for which you want to get the analyses.
        :return: List of Analyses.
        """
        project_analyses = self._get("v2/projects/{}/analyses".format(project_id))
        return [models.Analysis(analysis) for analysis in project_analyses["content"]]

    def download(
            self,
            analysis_id: int,
            dest_file_path: str,
            file_format: constants.AnalysisFormat=constants.AnalysisFormat.CSV,
    ) -> None:
        """Download analysis into specified file format.

        :param analysis_id: Anaylsis ID for which you download.
        :param dest_file_path: Destination path where you want to download the file.
        :param file_format: File format of file.
        :return: Downloaded file with content of the analysis
        """
        with open(dest_file_path, "wb") as f:
            for chunk in self._get_analysis_stream(analysis_id, file_format):
                f.write(chunk)

    def _get_analysis_stream(
            self,
            analysis_id: int,
            file_format: constants.AnalysisFormat
    ) -> Iterator[bytes]:
        """Process bytes return by API

        :param analysis_id: Anaylsis ID for which you download.
        :param file_format: File format of file.
        :return: Downloaded analysis file with iterator.
        """
        return self._get_stream("v1/analyses/{}/download".format(analysis_id), {
            "format": file_format.value,
        }).iter_content(constants.CHUNK_SIZE)
