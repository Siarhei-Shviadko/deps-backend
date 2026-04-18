class TestCreateLabelIntegrity:
    def test_request__valid_data__valid_response(self, client):
        label_name = "Test label"
        response = client.post("/api/document/v1/labels", json={"labelName": label_name})
        response_json = response.json()

        assert response_json["name"] == label_name
