import pytest

from deps_documents.domain.constants import DocumentStateEnum
from tests.factories import DocumentEntityFactory


class TestStatusView:
    def test_get__existing_document_id__return_200_response(self, client, document_service_mock):
        document_service_mock.get.return_value = DocumentEntityFactory()
        response = client.get("/api/document/v1/documents/1/status")

        assert response.status_code == 200

    @pytest.mark.parametrize("state", [DocumentStateEnum.COMPLETED])
    def test_get__valid_body__return_proper_status(self, state, client, document_service_mock):
        document = DocumentEntityFactory(state=state)
        document_service_mock.get.return_value = document

        response = client.get("/api/document/v1/documents/2/status")
        response_json = response.json()
        status = response_json.get("status", None)

        assert state.value == status
