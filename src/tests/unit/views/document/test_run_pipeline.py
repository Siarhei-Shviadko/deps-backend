import pytest

from deps_documents.domain.entities import DocumentEntityPk
from tests.factories import DocumentEntityFactory


class TestRunPipelineView:
    def test_post__valid_input__return_200(self, client, document_service_mock):
        document_service_mock.run_pipeline.return_value = [DocumentEntityFactory(labels=None)]

        params = {"documentIds": [DocumentEntityPk("1")], "engineName": "TESSERACT"}
        response = client.post("/api/document/v1/documents/run-pipeline", json=params)

        assert response.status_code == 200

    def test_post__valid_input__return_proper_fields(self, client, document_service_mock):
        document_service_mock.run_pipeline.return_value = [DocumentEntityFactory(labels=None)]

        params = {"documentIds": [DocumentEntityPk("1")], "engineName": "TESSERACT"}
        response = client.post("/api/document/v1/documents/run-pipeline", json=params)
        response_json = response.json()

        assert response_json is not None
        assert document_service_mock.run_pipeline.called
        _, kwargs = document_service_mock.run_pipeline.call_args
        assert kwargs["need_extraction"] == True

    def test_post__valid_input__return_proper_fields_value(self, client, document_service_mock):
        expected_json = [{"_id": "1", "title": ""}]

        document_service_mock.run_pipeline.return_value = [DocumentEntityFactory(pk="1", labels=None)]

        params = {"documentIds": [DocumentEntityPk("1")], "engineName": "TESSERACT"}
        response = client.post("/api/document/v1/documents/run-pipeline", json=params)
        response_json = response.json()

        assert response_json[0]["_id"] == expected_json[0]["_id"]

    @pytest.mark.parametrize("extract_data", [True, False])
    def test_post__valid_input__valid_extract_data_passed(self, client, document_service_mock, extract_data):
        document_service_mock.run_pipeline.return_value = [DocumentEntityFactory(labels=None)]

        params = {
            "documentIds": [DocumentEntityPk("1")],
            "engineName": "TESSERACT",
            "extractData": extract_data,
        }
        response = client.post("/api/document/v1/documents/run-pipeline", json=params)

        assert document_service_mock.run_pipeline.called
        _, kwargs = document_service_mock.run_pipeline.call_args
        assert kwargs["need_extraction"] == extract_data

    def test_post__empty_document_ids__return_422(self, client):
        params = {
            "documentIds": [],
            "engineName": "TESSERACT",
        }
        response = client.post("/api/document/v1/documents/run-pipeline", json=params)

        assert response.status_code == 422

    def test_post__invalid_json__422(self, client):
        params = '"invalid json syntax('

        response = client.post("/api/document/v1/documents/run-pipeline", data=params)

        assert response.status_code == 422
