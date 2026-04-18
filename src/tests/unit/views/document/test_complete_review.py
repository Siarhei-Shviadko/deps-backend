from tests.factories import DocumentEntityFactory


class TestCompleteReviewView:
    def test_post__valid_body__return_200_response(self, client, document_service_mock):
        document_service_mock.complete_review.return_value = DocumentEntityFactory()

        response = client.post("/api/document/v1/documents/complete", json={"documentId": "1"})

        assert response.status_code == 200

    def test_post__valid_body__return_proper_value(self, client, document_service_mock):
        document = DocumentEntityFactory()
        document_service_mock.complete_review.return_value = document

        response = client.post("/api/document/v1/documents/complete", json={"documentId": "1"})

        json_response = response.json()

        assert json_response.get("_id") == document.pk
        assert json_response.get("parentId") == document.parent_id
        assert json_response.get("title") == document.title
        assert json_response.get("state") == document.state
        assert json_response.get("documentType") == document.document_type
        assert json_response.get("date") == document.date.isoformat()
        assert json_response.get("reviewer") == document.reviewer
        assert isinstance(json_response.get("labels"), list)
        assert len(json_response.get("labels")) == len(document.labels)
        assert json_response.get("language") == document.language
        assert json_response.get("engine") == document.engine
        assert isinstance(json_response.get("previewDocuments"), dict)
        assert isinstance(json_response.get("processingDocuments"), dict)
        assert json_response.get("priority") == document.priority.value
