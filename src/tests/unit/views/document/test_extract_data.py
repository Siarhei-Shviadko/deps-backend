import pytest

from deps_documents.domain.dtos import FullBatchResponseObject
from deps_documents.domain.entities import DocumentEntityPk
from deps_documents.domain.exceptions import DocumentExtractDataError
from tests.factories import DocumentEntityFactory


class TestExtractDataView:
    def test_post__valid_body__return_200(self, client, document_service_mock):
        document_service_mock.extract_data.return_value = [DocumentEntityFactory(labels=None)]

        response = client.post("/api/document/v1/documents/extract-data", json={"documentIds": ["1"]})

        assert response.status_code == 200

    def test_post__valid_body__return_proper_fields(self, client, document_service_mock):
        document_service_mock.extract_data.return_value = [DocumentEntityFactory(labels=None)]

        response = client.post("/api/document/v1/documents/extract-data", json={"documentIds": ["1"]})
        response_json = response.json()

        assert response_json is not None

    def test_post__valid_body__return_proper_fields_value(self, client, document_service_mock):
        expected_json = [{"_id": "1", "title": ""}]
        document_service_mock.extract_data.return_value = [DocumentEntityFactory(pk="1", labels=None)]

        response = client.post("/api/document/v1/documents/extract-data", json={"documentIds": ["1", "2", "a"]})
        response_json = response.json()

        assert response_json[0]["_id"] == expected_json[0]["_id"]

    def test_post__extract_data__valid_engine_name(self, client, document_service_mock):
        document_service_mock.extract_data.return_value = [DocumentEntityFactory(labels=None)]
        params = {"documentIds": ["1"], "engineName": "TESSERACT"}
        response = client.post("/api/document/v1/documents/extract-data", json=params)
        assert response.status_code == 200

    def test_post__empty_list__return_422(self, client):
        params = {"documentIds": []}
        response = client.post("/api/document/v1/documents/extract-data", json=params)

        assert response.status_code == 422

    def test_post__list_with_empty_str__return_422(self, client):
        params = {"documentIds": [""]}
        response = client.post("/api/document/v1/documents/extract-data", json=params)

        assert response.status_code == 422

    def test_post__document_type_is_unknown__return__400_response(self, client, document_service_mock):
        document_service_mock.extract_data.side_effect = DocumentExtractDataError

        response = client.post(
            "/api/document/v1/documents/extract-data", json={"documentIds": ["1"], "type": "Some Document Type"}
        )

        assert response.status_code == 400
