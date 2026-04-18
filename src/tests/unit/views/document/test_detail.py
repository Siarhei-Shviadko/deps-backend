import json
from http import HTTPStatus

from deps_documents.domain.exceptions import DocumentNotFoundError
from tests.factories import DocumentEntityFactory
from tests.serializers import dump_document_for_request


class TestDetailView:
    def test_get__existing_document__return_200(self, client, document_service_mock):
        document_service_mock.get.return_value = DocumentEntityFactory()
        response = client.get("/api/document/v1/documents/1")

        assert response.status_code == 200

    def test_get__not_existing_document__return_404(self, client, document_service_mock):
        document_service_mock.get.side_effect = DocumentNotFoundError
        response = client.get("/api/document/v1/documents/1")

        assert response.status_code == 404

    def test_delete__existing_document_and_deleted__return_200(self, client, document_service_mock):
        document_service_mock.delete.return_value = True
        response = client.delete("/api/document/v1/documents/1")

        assert response.status_code == 200
        assert response.text == "true"

    def test_delete__existing_document_but_not_deleted__return_200(self, client, document_service_mock):
        document_service_mock.delete.return_value = False
        response = client.delete("/api/document/v1/documents/1")

        assert response.status_code == 200
        assert response.text == "false"

    def test_delete__not_existing_document__return_404(self, client, document_service_mock):
        document_service_mock.delete.side_effect = DocumentNotFoundError
        response = client.delete("/api/document/v1/documents/1")

        assert response.status_code == HTTPStatus.NOT_FOUND

    def test_put__valid_document__return_200(self, client, document_service_mock):
        document = DocumentEntityFactory()
        document_dump = dump_document_for_request(document)
        request_dump = {
            "document": {
                **document_dump,
            }
        }
        request_data = json.dumps(request_dump)

        document_service_mock.update.return_value = "1"
        response = client.put(
            "/api/document/v1/documents/1",
            data=request_data,
        )

        assert response.status_code == 200

    def test_put__valid_document__return_doc_id(self, client, document_service_mock):
        document = DocumentEntityFactory()
        document_dump = dump_document_for_request(document)
        request_dump = {
            "document": {
                **document_dump,
            }
        }
        request_data = json.dumps(request_dump)

        document_service_mock.update.return_value = "1"
        response = client.put(
            "/api/document/v1/documents/1",
            data=request_data,
        )
        response_json = response.json()

        assert response_json["_id"] == "1"

    def test_put__invalid_document__return_422(self, client, document_service_mock):
        request_dump = {"document": {1: 1}}
        request_data = json.dumps(request_dump)

        response = client.put(
            "/api/document/v1/documents/1",
            data=request_data,
        )
        response = client.put("/api/document/v1/documents/1")

        assert response.status_code == 422

    def test_patch__valid_document__return_200(self, client, document_service_mock):
        document = DocumentEntityFactory()
        document_dump = dump_document_for_request(document)
        request_dump = {
            "document": {
                **document_dump,
            }
        }
        request_data = json.dumps(request_dump)

        document_service_mock.partially_update.return_value = "1"
        response = client.patch(
            "/api/document/v1/documents/1",
            data=request_data,
        )

        assert response.status_code == 200

    def test_patch__valid_document__return_doc_id(self, client, document_service_mock):
        document = DocumentEntityFactory()
        document_dump = dump_document_for_request(document)
        request_dump = {
            "document": {
                **document_dump,
            }
        }
        request_data = json.dumps(request_dump)

        document_service_mock.partially_update.return_value = "1"
        response = client.patch(
            "/api/document/v1/documents/1",
            data=request_data,
        )
        response_json = response.json()

        assert response_json["_id"] == "1"

    def test_patch__invalid_document__return_422(self, client, document_service_mock):
        request_dump = {"document": {1: 1}}
        request_data = json.dumps(request_dump)

        response = client.put(
            "/api/document/v1/documents/1",
            data=request_data,
        )
        response = client.patch("/api/document/v1/documents/1")

        assert response.status_code == 422
