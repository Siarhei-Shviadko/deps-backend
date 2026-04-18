from tests.factories import CommentEntityFactory


class TestAddCommentView:
    def test_post__valid_body__return_200_response(self, client, document_service_mock):
        document_service_mock.add_comment.return_value = CommentEntityFactory()

        response = client.post("/api/document/v1/documents/add-comment", json={"documentId": "1", "text": "comment"})

        assert response.status_code == 200

    def test_post__valid_body__return_proper_response_values(self, client, document_service_mock):
        comment = CommentEntityFactory()
        document_service_mock.add_comment.return_value = comment

        response = client.post("/api/document/v1/documents/add-comment", json={"documentId": "1", "text": comment.text})
        response_json = response.json()

        assert response_json.get("text") == comment.text
        assert response_json.get("createdAt") == comment.created_at.isoformat()
        assert response_json.get("createdBy", {}) == comment.created_by
