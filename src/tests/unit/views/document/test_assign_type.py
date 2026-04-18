from deps_documents.domain.exceptions import DocumentStateError
from tests.factories import DocumentEntityFactory


class TestAssignTypeView:
    def test_post__valid_body__return_200(self, client, document_service_mock):
        document_service_mock.assign_type.return_value = [DocumentEntityFactory(labels=None)]

        response = client.post(
            "/api/document/v1/documents/assign-type", json={"documentIds": ["1"], "typeName": "Test type-code"}
        )

        assert response.status_code == 200

    def test_post__valid_body__return_proper_fields(self, client, document_service_mock):
        document_service_mock.assign_type.return_value = [DocumentEntityFactory(labels=None)]

        response = client.post(
            "/api/document/v1/documents/assign-type", json={"documentIds": ["1"], "typeName": "Test type-code"}
        )
        response_json = response.json()

        assert response_json is not None

    def test_post__valid_body__return_proper_fields_value(self, client, document_service_mock):
        expected_json = [{"_id": "1", "title": ""}]
        document_service_mock.assign_type.return_value = [DocumentEntityFactory(pk="1", labels=None)]

        response = client.post(
            "/api/document/v1/documents/assign-type", json={"documentIds": ["1", "2", "a"], "typeName": "Test type-code"}
        )
        response_json = response.json()

        assert response_json[0]["_id"] == expected_json[0]["_id"]

    def test_post__empty_pks__return_422_response(self, client):
        response = client.post("/api/document/v1/documents/assign-type", json={"documentIds": [], "typeName": "Test type-code"})

        assert response.status_code == 422

    def test_post__empty_type__return_422_response(self, client):
        response = client.post("/api/document/v1/documents/assign-type", json={"documentIds": ["1"], "typeName": ""})

        assert response.status_code == 422

    def test_post__document_state_is_new__return__400_response(self, client, document_service_mock):
        document_service_mock.assign_type.side_effect = DocumentStateError

        response = client.post("/api/document/v1/documents/assign-type", json={"documentIds": ["1"], "state": "new"})

        assert response.status_code == 400
