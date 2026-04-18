from deps_documents.domain.exceptions import DocumentFileNotFoundError


class TestDocumentFileContent:
    def test_existing_file(self, client, blob_service):
        file_path = "test.txt"

        response = client.get(f"/api/document/v1/files/file-content?blob={file_path}")

        assert response.status_code == 200
        assert response.headers["Content-Type"] == "application/octet-stream"

    def test_without_params(self, client):
        response = client.get("/api/document/v1/files/file-content")

        assert response.status_code == 422

    def test_non_existing_file(self, client, document_file_service):
        file_path = "test.txt"
        document_file_service.retrieve_file_content.side_effect = DocumentFileNotFoundError

        response = client.get(f"/api/document/v1/files/file-content?blob={file_path}")

        assert response.status_code == 404
