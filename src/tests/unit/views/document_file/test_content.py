from deps_documents.domain.exceptions import DocumentFileNotFoundError


class TestDocumentFileContentView:
    def test_existing_file(self, client, document_file_service_mock):
        file_path = "test.txt"
        file_content = b"The quick brown fox jumps over the lazy dog"
        document_file_service_mock.retrieve_file_content.return_value = file_content

        response = client.get(f"/api/document/v1/files/file-content?blob={file_path}")

        assert response.status_code == 200
        assert response.headers["Content-Type"] == "application/octet-stream"
        assert response.content == file_content

    def test_without_params(self, client):
        response = client.get("/api/document/v1/files/file-content")

        assert response.status_code == 422

    def test_invalid_params(self, client):
        file_path = "test.txt"
        response = client.get(f"/api/document/v1/files/file-content?blob_name{file_path}")

        assert response.status_code == 422

    def test_non_existing_file(self, client, document_file_service_mock):
        file_path = "test.txt"
        document_file_service_mock.retrieve_file_content.side_effect = DocumentFileNotFoundError

        response = client.get(f"/api/document/v1/files/file-content?blob={file_path}")

        assert response.status_code == 404
