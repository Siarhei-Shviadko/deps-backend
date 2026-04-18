from io import BytesIO

import pytest


class TestFileView:
    def test_post__upload_new_document_file__new_document_id(self, client, document_service_mock):
        document_service_mock.add_file.return_value = "1"
        document_service_mock.document_file.return_value = "1"
        data = {
            "file": ("document_file.jpg", BytesIO(b"a new document file content"), "application/jpg"),
        }
        response = client.post("/api/document/v1/documents/document-file", files=data)

        response_json = response.json()

        assert response.status_code == 200
        assert "id" in response_json

    def test_post__no_document_file__return_422(self, client):
        response = client.post("/api/document/v1/documents/document-file", files={})

        assert response.status_code == 422

    def test_post__upload_new_document_file_with_extraction_params__new_document_id(self, client, document_service_mock):
        document_service_mock.add_file.return_value = "1"
        document_service_mock.document_file.return_value = "1"
        files = {
            "file": ("document_file.jpg", BytesIO(b"a new document file content"), "application/jpg"),
        }
        data = {"extractionParams": '{"nerEntities": ["phone"], "ner": "true"}'}
        response = client.post("/api/document/v1/documents/document-file", files=files, data=data)

        response_json = response.json()

        assert response.status_code == 200
        assert "id" in response_json

    def test_post__incorrect_extraction_params__return_422(self, client):
        files = {
            "file": BytesIO(b"a new document file content"),
        }
        data = {"extractionParams": '{"nerEntities": 1, "ocr": "test"}'}
        response = client.post("/api/document/v1/documents/document-file", files=files, data=data)

        assert response.status_code == 422

    def test_post__assign_reviewer__return_200(self, client):
        files = {
            "file": BytesIO(b"a new document file content"),
        }
        data = {"assignedToMe": True}
        response = client.post("/api/document/v1/documents/document-file", files=files, data=data)

        assert response.status_code == 200

    def test_post__upload_new_document_file__document_type_not_exists(self, client, document_service_mock):
        document_service_mock.add_file.return_value = "1"
        document_service_mock.document_file.return_value = "1"
        data = {
            "file": ("document_file.jpg", BytesIO(b"a new document file content"), "application/jpg"),
            "documentType": "very_random_document_type",
        }
        response = client.post("/api/document/v1/documents/document-file", files=data)

        assert response.status_code == 422
