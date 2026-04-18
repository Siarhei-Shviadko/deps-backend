import pytest


@pytest.mark.skip
class TestDocumentAssignType:
    def test_document_states__return_code_200(self, client):
        response = client.get("/api/document/v1/documents/validation-statuses")

        assert response.status_code == 200

    def test_document_states__return_all_document_states(self, client):
        response = client.get("/api/document/v1/documents/validation-statuses")
        response_json = response.json()

        assert "passed" in response_json
        assert "failed" in response_json
        assert "not_applied" in response_json
