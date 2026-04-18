from deps_documents.domain.exceptions import DocumentNotFoundError
from tests.factories import DocumentFilesDataFactory


class TestFilesView:
    def test_get__one_file__return_200(self, client, document_service_mock, document_file_service_mock):
        document_service_mock.get_document_files.return_value = DocumentFilesDataFactory()
        document_file_service_mock.retrieve_file_content.return_value = b"test"

        response = client.get("/api/document/v1/documents/1/files")

        assert response.status_code == 200

    def test_get__two_or_more_files__return_200(self, client, document_service_mock, blob_storage_mock, mocker):
        file_names = [
            "path1/fake_file_name_1.jpg",
        ]
        document_service_mock.get_document_files.return_value = DocumentFilesDataFactory(files_names=file_names)

        blob_storage_mock.upload("path1/fake_file_name_1.jpg", b"Test value", replace_if_exists=True)

        mock = mocker.patch("deps_documents.api.models.document.blob_file.get_url")
        mock.return_value = "some_path.jpg"

        response = client.get("/api/document/v1/documents/1/files")

        assert response.status_code == 200

    def test_get__still_processing__return_404(self, client, document_service_mock):
        document_service_mock.get_document_files.side_effect = DocumentNotFoundError

        response = client.get("/api/document/v1/documents/1/files")

        assert response.status_code == 404

    def test_get__one_file_with_cyrillic_doc_title__return_200(self, client, document_service_mock, document_file_service_mock):
        document_service_mock.get_document_files.return_value = DocumentFilesDataFactory(document_name="тест.pdf")
        document_file_service_mock.retrieve_file_content.return_value = b"test"

        response = client.get("/api/document/v1/documents/1/files")

        assert response.status_code == 200

    def test_get__two_files_with_cyrillic_doc_title__return_200(self, client, document_service_mock, document_file_service_mock):
        document_service_mock.get_document_files.return_value = DocumentFilesDataFactory(
            document_name="тест.pdf", files_names=["path1/fake_file_name_1.jpg", "path1/fake_file_name_2.jpg"]
        )
        document_file_service_mock.retrieve_file_content.return_value = b"test"

        response = client.get("/api/document/v1/documents/1/files")

        assert response.status_code == 200
