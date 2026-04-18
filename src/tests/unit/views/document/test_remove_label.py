class TestDocumentRemoveLabelView:
    def test_post__valid_body__return_200_response(self, client, document_service_mock):
        document_service_mock.remove_label.return_value = True

        response = client.post("/api/document/v1/documents/remove-label", json={"documentId": "1", "labelId": "1"})

        assert response.status_code == 200

    def test_post__valid_body__return_proper_response_values(self, client, document_service_mock):
        document_service_mock.remove_label.return_value = True

        response = client.post("/api/document/v1/documents/remove-label", json={"documentId": "1", "labelName": "Test label"})
        response_json = response.json()

        assert response_json

    def test_post__null_label_name__return_422_response(self, client):
        response = client.post("/api/document/v1/documents/remove-label", json={"documentId": "1", "labelName": None})

        assert response.status_code == 422

    def test_post__empty_label_name__return_422_response(self, client):
        response = client.post("/api/document/v1/documents/remove-label", json={"documentId": "1", "labelName": ""})

        assert response.status_code == 422

    def test_post__empty_pk__return_422_response(self, client):
        response = client.post("/api/document/v1/documents/remove-label", json={"documentId": "", "labelName": ""})

        assert response.status_code == 422
