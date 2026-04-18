from deps_documents.domain.exceptions import DocumentImagesAccessError
from tests.factories import DocumentFilesDataFactory


class TestPreprocessedImagesView:
    def test_get__one_file__return_200(self, client, document_service_mock, document_file_service_mock):
        document_service_mock.get_processed_images.return_value = DocumentFilesDataFactory()
        document_file_service_mock.retrieve_file_content.return_value = b"Test value"

        response = client.get("/api/document/v1/documents/1/preprocessed-images")

        assert response.status_code == 200

    def test_get__two_or_more_files__return_200(self, client, document_service_mock, document_file_service_mock, mocker):
        file_names = [
            "path1/fake_file_name_1.jpg",
            "path2/fake_file_name_2.jpg",
        ]
        res = DocumentFilesDataFactory(files_names=file_names)
        document_service_mock.get_processed_images.return_value = res

        document_file_service_mock.retrieve_file_content.return_value = b"Test value"

        mock = mocker.patch("deps_documents.api.models.document.blob_file.get_url")
        mock.return_value = "some_path.jpg"

        response = client.get("/api/document/v1/documents/1/preprocessed-images")

        assert response.status_code == 200

    def test_get__still_processing__return_422(self, client, document_service_mock):
        document_service_mock.get_processed_images.side_effect = DocumentImagesAccessError

        response = client.get("/api/document/v1/documents/1/preprocessed-images")

        assert response.status_code == 400
