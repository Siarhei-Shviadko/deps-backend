from deps_documents.domain.exceptions import DocumentReviewerError
from tests.factories import DocumentEntityFactory


class TestResetReviewerView:
    def test_post__valid_body__return_200_response(self, client, document_service_mock):
        document_service_mock.reset_reviewer.return_value = [DocumentEntityFactory(labels=None)]

        response = client.post("/api/document/v1/documents/reset-reviewer", json={"documentIds": ["1"]})

        assert response.status_code == 200
        assert response.json() is not None

    def test_post__valid_body__return_proper_response_fields_value(self, client, document_service_mock):
        expected_json = [{"_id": "1", "title": ""}]
        document_service_mock.reset_reviewer.return_value = [DocumentEntityFactory(pk="1", labels=None)]

        response = client.post("/api/document/v1/documents/reset-reviewer", json={"documentIds": ["1"]})
        response_json = response.json()

        assert response_json[0]["_id"] == expected_json[0]["_id"]

    def test_post__document_reviewer_is_null__return__400_response(self, client, document_service_mock):
        document_service_mock.reset_reviewer.side_effect = DocumentReviewerError

        response = client.post("/api/document/v1/documents/reset-reviewer", json={"documentIds": ["1"], "reviewer": None})

        assert response.status_code == 400
