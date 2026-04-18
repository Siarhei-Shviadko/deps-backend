from tests.factories import DocumentEntityFactory


class TestDocumentAddLabelView:
    def test_post__valid_body__return_200_response(self, client, document_service_mock):
        document_service_mock.add_label.return_value = [DocumentEntityFactory(labels=None)]

        response = client.post("/api/document/v1/documents/add-label", json={"documentIds": ["1"], "labelId": "1"})

        assert response.status_code == 200

    def test_post__valid_body__return_proper_response_fields(self, client, document_service_mock):
        document_service_mock.add_label.return_value = [DocumentEntityFactory(labels=None)]

        response = client.post("/api/document/v1/documents/add-label", json={"documentIds": ["1"], "labelId": "1"})
        response_json = response.json()

        assert response_json is not None

    def test_post__valid_body__return_proper_response_fields_value(self, client, document_service_mock):
        expected_json = [{"_id": "1", "title": ""}]
        document_service_mock.add_label.return_value = [DocumentEntityFactory(pk="1", labels=None)]

        response = client.post("/api/document/v1/documents/add-label", json={"documentIds": ["1"], "labelId": "1"})
        response_json = response.json()

        assert response_json[0]["_id"] == expected_json[0]["_id"]

    def test_post__null_label_name__return_422_response(self, client):
        response = client.post("/api/document/v1/documents/add-label", json={"documentIds": ["1"], "labelName": None})

        assert response.status_code == 422

    def test_post__empty_label_name__return_422_response(self, client):
        response = client.post("/api/document/v1/documents/add-label", json={"documentIds": ["1"], "labelName": ""})

        assert response.status_code == 422

    def test_post__empty_pks__return_422_response(self, client):
        response = client.post("/api/document/v1/documents/add-label", json={"documentIds": [], "labelName": ""})

        assert response.status_code == 422
