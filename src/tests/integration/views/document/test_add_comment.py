import pytest

from tests.factories import DocumentEntityFactory


@pytest.fixture
def document_fixture(uow):
    return uow.document.add(DocumentEntityFactory())


class TestDocumentAddCommentIntegrity:
    def test_request__valid_data__valid_response__auth_disabled(self, client, document_fixture):
        comment_text = "Comment"

        response = client.post(
            "/api/document/v1/documents/add-comment", json={"documentId": document_fixture.pk, "text": comment_text}
        )
        response_json = response.json()

        assert response_json.get("text") == comment_text
        assert response_json.get("createdBy") is None

    def test_request__valid_data__valid_response__auth_enabled(self, client, set_test_user, user_fixture, document_fixture):
        comment_text = "Comment"

        response = client.post(
            "/api/document/v1/documents/add-comment", json={"documentId": document_fixture.pk, "text": comment_text}
        )
        response_json = response.json()

        assert response_json.get("text") == comment_text
        assert response_json.get("createdBy") == user_fixture["subject"]
