from deps_documents.domain.constants import DocumentStateEnum
from tests.factories import DocumentEntityFactory, ErrorEntityFactory


class TestDocumentRetryLastStepIntegrity:
    def test_request__valid_data__valid_response(self, client, uow):
        document = uow.document.add(DocumentEntityFactory(error=ErrorEntityFactory(in_state=DocumentStateEnum.PREPROCESSING)))
        response = client.post("/api/document/v1/documents/retry-last-step", json={"documentId": document.pk})

        assert response.status_code == 200
