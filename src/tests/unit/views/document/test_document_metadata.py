from deps_documents.domain.exceptions import DocumentMetadataNotFoundError
from tests.factories import DocumentMetadataFactory


class TestDocumentMetadataView:
    def test_get_existing_metadata__return_200(self, client, document_service_mock):
        document_metadata = DocumentMetadataFactory()
        document_service_mock.get_document_metadata.return_value = document_metadata
        response = client.get(f"/api/document/v1/documents/123/metadata")
        response_json = response.json()

        assert response.status_code == 200
        assert response_json["id"] == str(document_metadata.document_id)
        assert response_json["metadata"] == document_metadata.metadata

    def test_get_not_existing_metadata__return_404(self, client, document_service_mock):
        document_service_mock.get_document_metadata.side_effect = DocumentMetadataNotFoundError
        response = client.get(f"/api/document/v1/documents/123/metadata")

        assert response.status_code == 404
