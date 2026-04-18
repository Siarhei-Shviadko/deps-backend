from deps_documents.domain.exceptions import DocumentLastStepRetrievingError
from tests.factories import DocumentEntityFactory


class TestRetryLastStepView:
    def test_post__valid_body__return_200_response(self, client, document_service_mock):
        document_service_mock.retry_last_step.return_value = DocumentEntityFactory()

        response = client.post("/api/document/v1/documents/retry-last-step", json={"documentId": "1"})

        assert response.status_code == 200
