from deps_documents.domain.constants import DocumentStateEnum


class TestDocumentAssignType:
    def test_document_states__return_code_200(self, client):
        response = client.get("/api/document/v1/documents/states")

        assert response.status_code == 200

    def test_document_states__return_all_document_states(self, client):
        document_states = set(map(lambda x: x.value, list(DocumentStateEnum)))

        response = client.get("/api/document/v1/documents/states")
        response_content = response.json()

        response_states = set(response_content.keys())

        assert response_states == document_states
