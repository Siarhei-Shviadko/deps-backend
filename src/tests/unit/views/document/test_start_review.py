from deps_documents.domain.exceptions import (
    DocumentAlreadyAssignedError,
    DocumentReviewStateError,
)
from tests.factories import DocumentEntityFactory


class TestStartReviewView:
    def test_post__valid_body__return_200_response(self, client, document_service_mock):
        document_service_mock.start_review.return_value = [DocumentEntityFactory(labels=None)]

        response = client.post("/api/document/v1/documents/start-review", json={"documentIds": ["1"]})

        assert response.status_code == 200

    def test_post__valid_body__return_proper_response_fields(self, client, document_service_mock):
        document_service_mock.start_review.return_value = [DocumentEntityFactory(labels=None)]

        response = client.post("/api/document/v1/documents/start-review", json={"documentIds": ["1"]})
        response_json = response.json()

        assert response_json is not None

    def test_post__valid_body__return_proper_response_fields_value(self, client, document_service_mock):
        expected_json = [{"_id": "1", "title": ""}]

        document_service_mock.start_review.return_value = [DocumentEntityFactory(pk="1", labels=None)]

        response = client.post("/api/document/v1/documents/start-review", json={"documentIds": ["1", "2"]})
        response_json = response.json()

        assert response_json[0]["_id"] == expected_json[0]["_id"]

    def test_post__empty_pks__return_422_response(self, client):
        response = client.post("/api/document/v1/documents/start-review", json={"documentIds": []})

        assert response.status_code == 422

    def test_post__document_state_in_review__return__400_response(self, client, document_service_mock):
        document_service_mock.start_review.side_effect = DocumentReviewStateError

        response = client.post("/api/document/v1/documents/start-review", json={"documentIds": ["1"], "state": "inReview"})

        assert response.status_code == 400

    def test_post__document_already_assigned__return_400(self, client, document_service_mock):
        document_service_mock.start_review.side_effect = DocumentAlreadyAssignedError

        response = client.post("/api/document/v1/documents/start-review", json={"documentIds": ["1"], "state": "inReview"})

        assert response.status_code == 400
