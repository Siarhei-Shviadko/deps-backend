from datetime import datetime, timedelta

from deps_documents.domain.constants import DocumentStateEnum
from deps_documents.domain.exceptions import DocumentNotFoundError
from deps_documents.domain.services.document_log import StateInterval


class TestDocumentStateStatisticView:
    def test_get__existing_document__return_200(self, mocker, client, document_log_service_mock):
        now = datetime.now()
        hour = timedelta(hours=1)

        document_log_service_mock.get_document_time_state_intervals.return_value = [
            StateInterval(
                state=DocumentStateEnum.PREPROCESSING,
                start_time=now,
                finish_time=now + hour,
            ),
            StateInterval(
                state=DocumentStateEnum.DATA_EXTRACTION,
                start_time=now + hour,
                finish_time=now + hour + hour,
            ),
            StateInterval(
                state=DocumentStateEnum.IN_REVIEW,
                start_time=now + hour + hour,
                finish_time=now + hour + hour + hour,
            ),
        ]
        response = client.get("/api/document/v1/statistic/states/1")
        response_json = response.json()

        assert len(response_json) == 3
        assert response_json[0]["state"] == "preprocessing"
        assert response_json[1]["state"] == "dataExtraction"
        assert response_json[2]["state"] == "inReview"

    def test_get__not_existing_document__return_404(self, mocker, client, document_log_service_mock):
        document_log_service_mock.get_document_time_state_intervals.side_effect = DocumentNotFoundError

        response = client.get("/api/document/v1/statistic/states/1")

        assert response.status_code == 404
